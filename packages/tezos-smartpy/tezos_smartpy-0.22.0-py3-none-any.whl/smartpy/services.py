import subprocess
import json
import sys
import base64
from enum import Enum, unique, auto
from smartpy.environment import (
    get_debug,
    Environment,
)
from smartpy.state import get_state

_DN2 = [
    "ok_int",
    "ok_config",
    "ok_instantiation_result",
    "ok_originate_contract",
    "ok_show_value",
    "ok_message",
    "ok_offchain_views",
]


@unique
class ParseKind(Enum):
    SMARTPY = auto()
    SMARTPY_STDLIB = auto()
    MODULE = auto()
    EXPR = auto()

    def to_string(self):
        if self is ParseKind.SMARTPY:
            return "load"
        elif self is ParseKind.SMARTPY_STDLIB:
            return "load"
        elif self is ParseKind.MODULE:
            return "module"
        elif self is ParseKind.EXPR:
            return "expr"


class FailwithException(Exception):
    def __init__(self, value, line_no, message, expansion):
        self.value = value
        self.line_no = line_no
        self.message = message
        self.expansion = expansion

    def __str__(self):
        code = (
            "    (source code not available)"
            if self.line_no[2] is None
            else self.line_no[2]
        )
        expansion = "" if self.expansion is None else f"{self.expansion}"
        return f"(SmartPy)\n  File \"{self.line_no[0]}\", line {self.line_no[1]}, in <module>\n{code}\nReachedFailwith: '{self.value}'{expansion}"


class RuntimeException(Exception):
    def __init__(self, line_no, message):
        self.line_no = line_no
        self.message = message

    def __str__(self):
        code = (
            "    (source code not available)"
            if self.line_no[2] is None
            else self.line_no[2]
        )
        return f'(SmartPy)\n  File "{self.line_no[0]}", line {self.line_no[1]}, in <module>\n    {code.strip()}\n{self.message}'


class TypeError_(Exception):
    def __init__(self, line_no, message):
        self.line_no = line_no
        self.message = message

    def __str__(self):
        code = (
            "(source code not available)"
            if self.line_no[2] is None
            else self.line_no[2].lstrip()
        )
        return f'(SmartPy)\n  File "{self.line_no[0]}", line {self.line_no[1]}, in <module>\n    {code.strip()}\n{self.message}'


class ParseError(Exception):
    pass


def parser_via_exe(filename, row_offset, col_offset, kind, code):
    proc = subprocess.Popen(
        get_state().canopy
        + [
            "parse",
            filename,
            str(row_offset),
            str(col_offset),
            kind,
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        encoding="utf-8",
    )
    r, _stderr = proc.communicate(code)
    if proc.returncode:
        raise Exception(f"parser interaction error: exit status {proc.returncode}")
    return json.loads(r)


def parser_via_js(filename, row_offset, col_offset, kind, code):
    import js
    import pyodide

    # NOTE https://pyodide.org/en/0.22.1/usage/api/python-api/ffi.html#pyodide.ffi.JsProxy
    x1 = pyodide.ffi.to_js((filename, row_offset, col_offset))
    x2 = pyodide.ffi.to_js((kind, code))
    y = js.parse(x1, x2)
    return y.to_py()


def parse_via_exe_or_js(filename, row_offset, col_offset, kind, code):
    if sys.platform == "emscripten":
        (status, result) = parser_via_js(
            filename, row_offset, col_offset, kind.to_string(), code
        )
    else:
        (status, result) = parser_via_exe(
            filename, row_offset, col_offset, kind.to_string(), code
        )
    if status == "ok":
        return result
    elif status == "error":
        print(result, file=sys.stderr)
        raise ParseError(result)
    else:
        raise Exception(f"parser interaction error: {status} {result}")


def display_action_result(action, output):
    from IPython.display import display, HTML

    r = base64.b64encode(
        f'[["{action}", {json.dumps(output)}]]'.encode("utf-8")
    ).decode("utf-8")
    o = f"""<jupyter-output dark="false" compilation_state="compiled" output="{r}"></jupyter-output>"""
    display(HTML(o))


def interact(up):
    debug = get_debug()
    if debug:
        print("[smartpy] up %s" % up, file=sys.stderr)
    up = json.dumps(up)
    environment = get_state().environment
    if environment == Environment.IDE or environment == Environment.JUPYTER:
        import js

        dn = js.smartpy.step(up)
    else:
        oasis = get_state().oasis
        oasis.stdin.write(up)
        oasis.stdin.write("\n")
        oasis.stdin.flush()
        dn = oasis.stdout.readline().rstrip("\n")
    if debug:
        print("[smartpy] dn %s" % dn, file=sys.stderr)
    dn = json.loads(dn)
    if dn[0] == "ok_unit":
        assert len(dn) == 1
        return
    elif dn[0] in _DN2:
        assert len(dn) == 2
        if environment == Environment.JUPYTER:
            if dn[0] == "ok_originate_contract":
                display_action_result("Originate_contract", dn[1])
            elif dn[0] == "ok_message":
                display_action_result("Message_node", dn[1])
            elif dn[0] == "ok_show_value":
                display_action_result("Show_value", dn[1])
        return dn[1]
    elif dn[0] == "error":
        assert len(dn) == 2
        if dn[1][0] == "SmartPy_error":
            error = dn[1][1]
            if error["type_"][0] == "Type_error":
                raise TypeError_(**error["context"])
            elif error["type_"][0] == "Runtime_error":
                raise RuntimeException(**error["context"])
            elif error["type_"][0] == "Reached_failwith":
                raise FailwithException(**error["context"], **error["type_"][1])
            else:
                raise Exception("Unknown SmartPy error, please report: " + str(dn))
        elif dn[1][0] == "Failure":
            raise Exception("Internal SmartPy error, please report: " + dn[1][1])
        else:
            raise Exception("Unknown SmartPy error, please report: " + str(dn))
    else:
        raise Exception("Unknown response tag '%s'" % dn[0])
