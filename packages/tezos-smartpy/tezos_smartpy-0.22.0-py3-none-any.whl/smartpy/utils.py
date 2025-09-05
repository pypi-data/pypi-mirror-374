import os
import pathlib
import inspect


def formatErrorLine(line):
    i = -1
    while i + 2 < len(line) and line[i + 1] == " ":
        i += 1
    if 0 <= i:
        line = i * "&nbsp;" + line[i + 1 :]
    return line


def showTraceback(title, trace):
    title = "Error: " + str(title)
    lines = []
    skip = False
    print(trace)
    for line in trace.split("\n"):
        if not line:
            continue
        if skip:
            skip = False
            continue
        skip = "module smartpy line" in line or (
            "module __main__" in line and "in run" in line
        )
        if "Traceback (most recent call last):" in line:
            line = ""
        if not skip:
            lineStrip = line.strip()
            lineId = None
            line = formatErrorLine(line)
            if lineStrip.startswith("module <module>") or lineStrip.startswith(
                "File <string>"
            ):
                lineId = line.strip().split()[3].strip(",")
            line = line.replace("module <module>", "SmartPy code").replace(
                "File <string>", "SmartPy code"
            )
            if "SmartPy code" in line:
                line = "<span class='partialType'>%s</span>" % (line)
            if lineId:
                line = (
                    line
                    + " <button class=\"text-button\" onClick='showLine(%s)'>(line %s)</button>"
                    % (lineId, lineId)
                )
            lines.append(line)
    error = title + "\n\n" + lines[0] + "\n\n" + "\n".join(lines[1:-1])

    import js

    js.window.smartpyContext.showError(
        "<div class='michelson'>%s</div>" % (error.replace("\n", "\n<br>"))
    )


# -- LineNo --


def make_relative(path):
    cwd = os.getcwd()
    try:
        return pathlib.Path(path).relative_to(cwd)
    except ValueError:
        return path


def expand_resolve(pth):
    try:
        return pathlib.Path(pth).expanduser().resolve()
    except RuntimeError:
        return pth


# -- LineNo --


class LineNo:
    def __init__(self, filename, line_no):
        self.filename = make_relative(filename)
        self.line_no = line_no

    def export(self):
        return f'("{self.filename}" {self.line_no})'


def get_file_line_no(line_no=None):
    if line_no is not None:
        return line_no
    frame = inspect.currentframe().f_back
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while frame:
        fn = frame.f_code.co_filename
        if os.path.dirname(fn) != current_dir and "<frozen " not in fn and "init" != fn:
            if ":" in fn:
                fn = fn[fn.rindex(":") + 1 :]
            fn = os.path.relpath(fn)
            return LineNo(fn, frame.f_lineno)
        frame = frame.f_back
    return LineNo("", -1)


def get_file_line_no_direct():
    frame = inspect.currentframe()
    frame = frame.f_back
    frame = frame.f_back
    fn = frame.f_code.co_filename
    fn = os.path.relpath(fn)
    return LineNo(fn, frame.f_lineno)


def get_id_from_line_no():
    l = get_file_line_no()
    if not l.filename:
        return str(l.line_no)
    return (
        l.filename.replace("/", " ").replace(".py", "").strip("<>./,'").split()[-1]
        + "_"
        + str(l.line_no)
    )


def pretty_line_no():
    line_no = get_file_line_no()
    if line_no.filename:
        of_file = f" of {line_no.filename}"
    else:
        of_file = ""
    line_no = line_no.line_no
    return "(line %i%s)" % (line_no, of_file)
