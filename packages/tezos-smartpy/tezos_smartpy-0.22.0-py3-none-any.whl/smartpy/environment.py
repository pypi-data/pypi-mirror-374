import sys
import os
from enum import Enum, unique, auto
import platform
import subprocess
import smartpy.config as config
from smartpy.state import get_state


@unique
class Environment(Enum):
    JUPYTER = auto()
    IDE = auto()
    NATIVE = auto()


def _init_jupyter():
    """Initialize Jupyter-specific settings and load necessary JavaScript files."""
    from IPython.display import display, HTML
    import js
    import pyodide

    def get_wheel_file(file_name):
        """Load and evaluate a JavaScript file."""
        file_path = os.path.join(os.path.dirname(__file__), "static", file_name)
        with open(file_path, "r") as file:
            return file.read()

    oasisLibsCode = get_wheel_file("browserOasisLibs.js")
    oasisCode = get_wheel_file("browserOasis.js")
    canopyCode = get_wheel_file("browserCanopy.js")

    js.module = pyodide.ffi.to_js({})
    r = js.eval(oasisLibsCode)

    js.module = pyodide.ffi.to_js({})
    r = js.eval(oasisCode)
    js.smartpy = js.Oasis.smartpy
    js.parse = js.smartpy.step

    js.module = pyodide.ffi.to_js({})
    r = js.eval(canopyCode)

    js.eval("globalThis.smartpyContext.addOutput = (x) => console.log(x)")

    o = '<script type="module" src="../files/.static/jupyter-web-components.js" />'
    display(HTML(o))
    gtagEvent = """<script>
    if (window.trackGoogleAnalyticsEvent) {
        window.trackGoogleAnalyticsEvent({
        category: 'smartpy code execution',
        action: 'import smartpy',
        label: 'execute the import smartpy in Jupyter',
        });
    }
    </script>"""
    display(HTML(gtagEvent))


def _init_oasis():
    state = get_state()
    if state.environment == Environment.NATIVE and not get_disabled_server():
        state.oasis = subprocess.Popen(
            get_command("oasis"),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            encoding="utf-8",
        )
    else:
        state.oasis = get_command("oasis")


def _init_canopy():
    state = get_state()
    state.canopy = get_command("canopy")


def init_environment():
    # Detect the environment
    state = get_state()
    state.environment = (
        Environment.IDE if sys.platform == "emscripten" else Environment.NATIVE
    )

    if state.environment == Environment.NATIVE:
        _init_oasis()
        _init_canopy()
    else:
        try:
            # If ipywidgets can be imported, we're in Jupyter environment
            from IPython.display import display, HTML

            state.environment = Environment.JUPYTER
            _init_jupyter()
        except ImportError:
            pass


def get_command(name):
    use_docker = os.environ.get("SMARTPY_USE_DOCKER") is not None
    _system = platform.system()
    _machine = platform.machine()
    c = os.environ.get("SMARTPY_" + name.upper())
    if c:
        return c.split()
    else:
        if use_docker or (_system, _machine) == ("Darwin", "x86_64"):
            return [
                os.path.dirname(__file__) + "/smartpy-docker",
                config.docker_image,
                name,
            ]
        elif (_system, _machine) == ("Linux", "x86_64"):
            return [os.path.dirname(__file__) + "/smartpy-" + name + "-linux.exe"]
        elif (_system, _machine) == ("Darwin", "arm64"):
            return [os.path.dirname(__file__) + "/smartpy-" + name + "-macOS.exe"]
        else:
            raise Exception(f"Platform {_system}-{_machine} not supported.")


def get_disabled_server():
    return os.environ.get("SMARTPY_DISABLE_SERVER") is not None


def get_debug():
    return os.environ.get("SMARTPY_DEBUG") is not None


def get_make_file_dependencies():
    return os.environ.get("SMARTPY_DEPENDENCIES_FILE")
