# Copyright 2025 - present Trilitech Limited, 2022-2024 Morum LLC, 2019-2022 Smart Chain Arena LLC

from types import FunctionType
import atexit
import importlib
import importlib.metadata
import inspect
import os
import pathlib
import sys
import traceback
import subprocess
import typing
from enum import Enum, unique, auto
from collections import OrderedDict

from smartpy.metadata import (
    normalize_micheline,
    CodeMismatchException,
    are_equivalent_micheline,
    check_sp_version,
    # Exposed to users
    create_tzip16_metadata,
    pin_on_ipfs,
    get_metadata_uri,
    get_ipfs_data,
    get_metadata,
    get_metadata_code,
    get_michelson_code,
)
from smartpy.environment import (
    Environment,
    init_environment,
    get_disabled_server,
    get_debug,
    get_make_file_dependencies,
)
from smartpy.utils import (
    showTraceback,
    LineNo,
    get_file_line_no,
    make_relative,
)
from smartpy.state import init_state, get_state
from smartpy.types import *
import smartpy.scenario_utils as scenario_utils
from smartpy.syntax import *
from smartpy.services import *
from smartpy.modules import Module, read_smartpy_code, ParseKind


__version__ = importlib.metadata.version("tezos-smartpy")


stdlib = None

init_state()
init_environment()


def evalRun(withTests):
    get_state().unknownIds = 0
    if "main" in sys.modules:
        import main

        importlib.reload(main)
    else:
        import main


def toException(x):
    return Exception(x)


def shutdown():
    interact({"request": "exit"})


if not get_disabled_server():
    atexit.register(shutdown)


exception_optimization_levels = [
    "full-debug",
    "debug-message",
    "verify-or-line",
    "default-line",
    "line",
    "default-unit",
    "unit",
]


default_verify_message = None
wrap_verify_messages = None

normalMax = max
max = spmax
min = spmin


class Dynamic_contract:
    def __init__(self, scenario, id, views):
        self.contractId = static_contract_id(id)
        self.data = contract_data(self.contractId)
        self.balance = contract_balance(self.contractId)
        self.address = contract_address(self.contractId)
        self.baker = contract_baker(self.contractId)
        self.typed = contract_typed(self.contractId)
        self.scenario = scenario
        self.views = views

    # TODO __getattribute__, to hide "name", "args" etc.
    def __getattr__(self, attr):
        if attr in self.views:
            return View(self, attr)
        if attr == "address":
            return contract_address(self.contractId)
        if attr == "baker":
            return contract_baker(self.contractId)
        if attr == "balance":
            return contract_balance(self.contractId)
        if attr == "data":
            return contract_data(self.contractId)
        if attr == "private":
            return contract_private(self.contractId)
        if attr == "instantiation_result":
            return self.__dict__["instantiation_result"]
        return Method(self, attr)  # TODO limit to parser-obtained list of methods


@unique
class SimulationMode(Enum):
    NATIVE = "native"
    MOCKUP = "mockup"
    GHOSTNET = "ghostnet"

    @classmethod
    def from_string(cls, s):
        return cls(s.lower())


def test_account(seed):
    return TestAccount(seed)


class Scenario:
    # special modules that need to behave like inline modules with a certain name
    STDLIB_MODULES = {
        "smartpy/stdlib/utils.spy": "utils",
        "smartpy/stdlib/statistics.spy": "statistics",
        "smartpy/stdlib/math.spy": "math",
        "smartpy/stdlib/rational.spy": "rational",
        "smartpy/stdlib/fixed_point.spy": "fp",
        "smartpy/stdlib/list_utils.spy": "list_utils",
        "smartpy/stdlib/string_utils.spy": "string_utils",
        "smartpy/stdlib/address_utils.spy": "address_utils",
    }

    # holds sets of deps for each module added with add_module
    _FILE_DEPENDENCIES = {}

    def __init__(self):
        self.messages = []
        self.exceptions = []
        self.nextId = 0
        self.failed = False
        self.entrypoint_calls = []
        self.modules = []

    @staticmethod
    def _load(fn):
        if get_disabled_server():
            return None
        else:
            # Backward compatibility for old stdlib
            fn_path = fn if isinstance(fn, pathlib.Path) else pathlib.Path(fn)
            if fn_path.is_relative_to(pathlib.Path("smartpy/lib/")):
                fn = pathlib.Path("smartpy/stdlib/") / fn_path.relative_to(
                    pathlib.Path("smartpy/lib/")
                )
            filename, code = read_smartpy_code(fn)
            name = Scenario.STDLIB_MODULES.get(str(fn))
            if name:
                return Module.make_smartpy_stdlib_module(filename, code, name)
            else:
                return Module.make_smartpy_module(filename, code)

    def simulation_mode(self):
        data = {}
        data["action"] = "get_config"
        self.messages += [data]
        r = self.action(data)
        return SimulationMode.from_string(r["mode"][0])

    def add_module(self, m):
        load_library_id_needed()
        if not isinstance(m, Module):
            p = pathlib.Path(m)
            m = Scenario._load(p)
        assert m is not None
        if m in self.modules:
            return m
        data = {}
        data["action"] = "add_module"
        data["module_id"] = m.module_id.export()
        data["module"] = m.sexpr
        data["imports"] = m.export_imports()
        data["line_no"] = get_file_line_no().export()
        self.messages += [data]
        self.action(data)
        self._get_dependencies(m)
        self.modules.append(m)
        return m

    def _gen_dependencies(self, module):
        filenames = pySet()
        for m in module.ordered_imports():
            filename = m.module_id.filename
            if filename not in filenames:
                filenames.add(filename)
                yield filename, [
                    Module._make_filename(mm)[0] for mm in m.ordered_imports()
                ]
        filename = module.module_id.filename
        # last one shouldnt be in here - that would indicate a circular import - but check anyway
        if filename not in filenames:
            filenames.add(filename)
            yield filename, [
                Module._make_filename(mm)[0] for mm in module.ordered_imports()
            ]

    def _clean(self, nm):
        # note this is specific to our CI setup
        if "templates" in nm:
            return "templates" + nm.split("templates")[-1]
        x = "wheels/tezos-smartpy/"
        if "smartpy" in nm:
            return x + "smartpy" + nm.split("smartpy")[-1]
        return nm

    def _get_dependencies(self, m):
        if get_make_file_dependencies() is None:
            return

        ky = self._clean(make_relative(m.module_id.filename))
        self._FILE_DEPENDENCIES[ky] = pySet()
        sections = pyList()
        for nm, deps in self._gen_dependencies(m):
            if not deps:
                continue
            nm = self._clean(make_relative(nm))
            if nm in self._FILE_DEPENDENCIES[ky]:
                continue
            self._FILE_DEPENDENCIES[ky].add(nm)
            deps = [self._clean(make_relative(d)) for d in deps]
            sections.append((nm, [d for d in deps]))
        try:
            # the scenario file that is calling this run
            # if multiple calls to add_module then last one overrides others
            nm = self._clean(make_relative(sys.argv[0]))
            sections.append(
                (nm, [ky for ky in self._FILE_DEPENDENCIES.keys() if ky != nm])
            )
        except IndexError as e:
            print(e, file=sys.stderr)

        try:
            # we need append mode as there maybe multiple calls to add_module
            # each make_file_dependencies is specific to a scenario
            # so append mode is ok here
            if sections and any(s for _, s in sections):
                with open(get_make_file_dependencies(), "a") as fh:
                    for nm, deps in sections:
                        if not deps:
                            continue
                        fh.write(f"\n{nm}:\n")
                        for d in deps:
                            fh.write(f"  {d}\n")
        except OSError as e:
            print(e, file=sys.stderr)

    def action(self, x):
        if not self.failed:
            return interact({"request": "scenario_action", "ix": self.ix, "action": x})

    def __iadd__(self, x):
        if isinstance(x, Instance):
            if x.scenario != self:
                raise Exception("The contract was instantiated in a different scenario")
            x.originate()
        else:
            raise Exception("Cannot add value of type %s to scenario" % str(type(x)))
        return self

    def dynamic_contract(self, template_ref, offset=None):
        data = {}
        data["action"] = "dynamic_contract"
        data["offset"] = str(offset) if offset is not None else "-1"
        data["line_no"] = get_file_line_no().export()
        data["module_id"] = template_ref.module.module_id.export()
        data["contract_name"] = template_ref.name
        self.messages += [data]
        id_ = self.action(data)

        # NOTE this returns all views, not just offchain ones
        data = {
            "action": "getOffchainViews",
            "id": static_contract_id(id_).export(),
            "line_no": get_file_line_no().export(),
        }
        self.messages += [data]
        xs = self.action(data)
        views = {x["name"] for x in xs}

        return Dynamic_contract(self, id_, views)

    def verify(self, condition):
        if isinstance(condition, pyBool):
            if not condition:
                raise Exception("Assert Failure")
        else:
            data = {}
            data["action"] = "verify"
            data["condition"] = spExpr(condition).export()
            data["line_no"] = get_file_line_no().export()
            self.messages += [data]
            self.action(data)

    def verify_equal(self, v1, v2):
        data = {}
        data["action"] = "verify"
        data["condition"] = poly_equal_expr(v1, v2).export()
        data["line_no"] = get_file_line_no().export()
        self.messages += [data]
        self.action(data)

    def compute(
        self,
        expression,
        sender=None,
        source=None,
        now=None,
        level=None,
        chain_id=None,
        voting_powers=None,
    ):
        id = "scenario_var" + str(self.nextId)
        self.nextId += 1
        data = {}
        data["action"] = "compute"
        data["expression"] = spExpr(expression).export()
        data["id"] = id
        data["line_no"] = get_file_line_no().export()
        if chain_id is not None:
            data["chain_id"] = spExpr(chain_id).export()
        if level is not None:
            data["level"] = spExpr(level).export()
        if sender is not None:
            data["sender"] = parse_account_or_address(sender)
        if source is not None:
            data["source"] = parse_account_or_address(source)
        if now is not None:
            data["time"] = spExpr(now).export()
        if voting_powers is not None:
            data["voting_powers"] = spExpr(voting_powers).export()
        self.messages += [data]
        self.action(data)
        return Expr("var", [id], get_file_line_no())

    def show(self, expression, html=True, stripStrings=False, compile=False):
        data = {}
        data["action"] = "show"
        data["compile"] = compile
        data["expression"] = spExpr(expression).export()
        data["html"] = html
        data["line_no"] = get_file_line_no().export()
        self.messages += [data]
        self.action(data)

    def p(self, s):
        return self.tag("p", s)

    def h1(self, s):
        return self.tag("h1", s)

    def h2(self, s):
        return self.tag("h2", s)

    def h3(self, s):
        return self.tag("h3", s)

    def h4(self, s):
        return self.tag("h4", s)

    def tag(self, tag, s):
        data = {}
        data["action"] = "textBlock"
        data["inner"] = s
        data["line_no"] = get_file_line_no().export()
        data["tag"] = tag
        self.messages += [data]
        self.action(data)
        return self

    def add_flag(self, flag, *args):
        data = {}
        data["action"] = "flag"
        data["flag"] = [flag] + pyList(args)
        data["line_no"] = get_file_line_no().export()
        self.action(data)
        self.messages += [data]

    def prepare_constant_value(self, value, hash=None):
        id = "scenario_var" + str(self.nextId)
        self.nextId += 1
        data = {}
        data["id"] = id
        data["action"] = "constant"
        data["kind"] = "value"
        data["hash"] = "None" if hash is None else hash
        data["expression"] = spExpr(value).export()
        data["line_no"] = get_file_line_no().export()
        self.messages += [data]
        self.action(data)
        return Expr("var", [id], get_file_line_no())

    def simulation(self, c):
        self.p("No interactive simulation available out of browser.")

    def test_account(self, seed, initial_balance=None, as_delegate=None):
        data = {}
        data["action"] = "register_account"
        data["seed"] = seed
        if initial_balance is not None:
            data["initial_balance"] = spExpr(initial_balance).export()
        if as_delegate is not None:
            data["as_delegate"] = pyBool(as_delegate)
        data["line_no"] = get_file_line_no().export()
        self.messages += [data]
        self.action(data)
        return test_account(seed)


def test_scenario(name, modules=None):
    load_library_id_needed()
    if modules is None:
        modules = []
    name = name.replace(" ", "_")
    scenario = Scenario()
    action = {"request": "new_scenario"}
    flags = []
    output_dir = os.environ.get("SMARTPY_OUTPUT_DIR")
    if name is not None:
        if output_dir is None:
            output_dir = name
        else:
            output_dir = str(pathlib.Path(output_dir, name))
    if get_state().environment == Environment.NATIVE and output_dir is not None:
        r = subprocess.run(["mkdir", "-p", output_dir])
        assert r.returncode == 0
        flags += ["--output", output_dir]
    more_flags = os.environ.get("SMARTPY_FLAGS")
    if more_flags is not None:
        flags += more_flags.split()
    action["flags"] = flags
    r = interact(action)
    scenario.ix = r

    if type(modules) != pyList:
        modules = [modules]
    for module in modules:
        scenario.add_module(module)
    get_state().current_scenario = scenario
    return scenario


def add_test(name=None):
    if name:
        raise Exception(
            "sp.add_test no longer takes the name argument. Please provide it to sp.test_scenario instead."
        )

    def r(f):
        if not get_disabled_server():
            get_state().current_scenario = None
            f()
            get_state().current_scenario = None

    return r


class Verbatim:
    def __init__(self, s):
        self.s = s

    def export(self):
        return self.s


def load_module_from_metadata(module):
    filename, line = module["line_no"][0], module["line_no"][1]
    line_no = LineNo(filename, line)
    code = module["source"]
    kind = module["module_kind"]
    name = module["name"]
    if kind == "inline_python":
        return Module.make_inline_module(filename, line - 3, 0, code)
    elif kind == "smartpy":
        return Module.make_smartpy_module(filename, code)
    elif kind == "smartpy_stdlib":
        return Module.make_smartpy_stdlib_module(filename, code, name)
    else:
        raise ValueError(f"Unknown module ID kind: {kind} for {name}")


def instantiate_from_metadata(
    metadata: typing.Dict[str, typing.Any], code_metadata: typing.Dict[str, typing.Any]
):
    check_sp_version(metadata)
    offset = 0
    file = get_file_line_no().filename
    args = [
        parse_via_exe_or_js(file, offset, 0, ParseKind.EXPR, p)
        for p in code_metadata["param"]
    ]
    sc = test_scenario("Check validity")
    sc.h2("Check validity")
    # Add flags
    for flag in code_metadata["flags"]:
        sc.add_flag(*flag)
    # Add modules - imports first
    for module in code_metadata["imports"]:
        m = load_module_from_metadata(module)
        sc.add_module(m)
    # Add modules - then main one
    main_module = load_module_from_metadata(code_metadata["module_"])
    sc.add_module(main_module)
    # Instantiate the contract
    c1 = main_module.__getattr__(code_metadata["name"])(*args)
    # Originate the contract
    sc += c1
    return c1.get_generated_michelson()


def check_validity(
    metadata: typing.Dict[str, typing.Any],
    code_metadata: typing.Dict[str, typing.Any],
    onchain_michelson: typing.List[typing.Any],
):
    """Checks that the code given in the metadata generates the same onchain code.

    Args:
        metadata (dict): Metadata dictionary.
            Can be obtained from `sp.get_metadata()`.
        code_metadata (dict): Code metadata dictionary.
            Can be obtained from `sp.get_metadata_code()`.
        onchain_michelson (List[any]): On-chain Michelson representation in the micheline (JSON) format.
            Can be obtained from `sp.get_michelson_code()`.

    Returns:
        A tuple containing the generated michelson and details of the first difference
        if a mismatch is found (diff path, generated value, onchain value), or None if
        the generated code matches the on-chain code.

    Raises:
        CodeMismatchException: If the generated code from metadata does not match the on-chain code.
                               The exception contains the generated michelson and details of the first difference.

    Example:
        >>> import smartpy as sp
        ...
        ... address = "KT1EQLe6AbouoX9RhFYHKeYQUAGAdGyFJXoi"
        ... metadata = sp.get_metadata(address, network="ghostnet")
        ... code_metadata = sp.get_metadata_code(metadata)
        ... onchain_michelson = sp.get_michelson_code(address, network="ghostnet")
        ... try:
        ...     sp.check_validity(metadata, code_metadata, onchain_michelson)
        ...     print("Metadata code is valid")
        ... except CodeMismatchException as e:
        ...     print(e)
        ...     print("Generated michelson:", e.generated_michelson)
        ...     print("Details of the first difference:", e.diff_details)
    """

    def get_value_at_path(micheline, diff_path):
        for p in diff_path:
            micheline = micheline[p]
        return micheline

    generated_michelson = normalize_micheline(
        instantiate_from_metadata(metadata, code_metadata)
    )
    onchain_michelson = normalize_micheline(onchain_michelson)
    is_equal, first_diff = are_equivalent_micheline(
        generated_michelson, onchain_michelson
    )
    if not is_equal:
        raise CodeMismatchException(
            generated_michelson,
            (
                first_diff,
                get_value_at_path(generated_michelson, first_diff),
                get_value_at_path(onchain_michelson, first_diff),
                get_value_at_path(generated_michelson, first_diff),
            ),
        )


# decorator for inline modules
def module(f):
    load_library_id_needed()
    if get_disabled_server():
        return None
    else:
        filename = make_relative(f.__code__.co_filename)
        line_no = LineNo(filename, f.__code__.co_firstlineno)
        code = inspect.getsource(f.__code__)
        return Module.make_inline_module(filename, line_no.line_no - 1, 0, code)


class _Stdlib:
    def __init__(self):
        self.utils = Scenario._load("smartpy/stdlib/utils.spy")
        self.statistics = Scenario._load("smartpy/stdlib/statistics.spy")
        self.math = Scenario._load("smartpy/stdlib/math.spy")
        self.rational = Scenario._load("smartpy/stdlib/rational.spy")
        self.fp = Scenario._load("smartpy/stdlib/fixed_point.spy")
        self.list_utils = Scenario._load("smartpy/stdlib/list_utils.spy")
        self.string_utils = Scenario._load("smartpy/stdlib/string_utils.spy")
        self.address_utils = Scenario._load("smartpy/stdlib/address_utils.spy")


def load_library_id_needed():
    global stdlib, utils, statistics, math, rational, fp, list_utils, string_utils, address_utils
    if stdlib is None:
        if os.environ.get("SMARTPY_NEW_TYPE_CHECKER") is None:
            stdlib = _Stdlib()
            utils = stdlib.utils
            statistics = stdlib.statistics
            math = stdlib.math
            rational = stdlib.rational
            fp = stdlib.fp
            list_utils = stdlib.list_utils
            string_utils = stdlib.string_utils
            address_utils = stdlib.address_utils
            _library_loaded = True


class ParsedExpr(BaseParsedExpr):
    def __init__(self, sexpr):
        self.sexpr = sexpr

    def export(self):
        return self.sexpr


def expr(e):
    sexpr = parse_via_exe_or_js("<expr>", 0, 0, ParseKind.EXPR, e)
    return ParsedExpr(sexpr)


class Contract:
    def __init_subclass__(cls, **kwargs):
        raise ModuleNotFoundError(
            "`sp.Contract` can only be accessed within a .spy file or a function decorated with @sp.module. Please refer to the SmartPy documentation for more information."
        )


if get_state().environment == Environment.IDE:
    import js

    js.window.evalRun = evalRun
    js.window.showTraceback = showTraceback
    js.window.toException = toException

    if hasattr(js.window, "dispatchEvent"):
        js.window.dispatchEvent(js.window.CustomEvent.new("smartpy_ready"))


# -- Handling exceptions --
def scrub_traceback(tb):
    while tb and tb.tb_frame.f_code.co_filename == __file__:
        tb = tb.tb_next
    if tb:
        tb.tb_next = scrub_traceback(tb.tb_next)
    return tb


def handle_exception(exc_type, exc_value, exc_traceback):
    if not get_debug():
        exc_traceback = scrub_traceback(exc_traceback)
    tb_list = traceback.extract_tb(exc_traceback)
    print("Traceback (most recent call last):", file=sys.stderr)
    for item in tb_list:
        print(
            f'  File "{item.filename}", line {item.lineno}, in {item.name}\n    {item.line}',
            file=sys.stderr,
        )
    print(f"{exc_type.__name__}: {exc_value}", file=sys.stderr)


sys.excepthook = handle_exception
