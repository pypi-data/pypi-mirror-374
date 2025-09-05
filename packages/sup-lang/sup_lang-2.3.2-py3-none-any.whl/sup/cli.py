from __future__ import annotations

import argparse
import os
import re
import sys

from . import __version__
from .errors import SupError
from .interpreter import Interpreter
from .parser import AST  # type: ignore
from .parser import Parser
from .transpiler import to_python


def run_source(
    source: str, *, stdin: str | None = None, emit: str | None = None
) -> str:
    parser = Parser()
    program = parser.parse(source)
    if emit == "python":
        return to_python(program)
    interpreter = Interpreter()
    return interpreter.run(program, stdin=stdin)


def run_file(path: str) -> int:
    try:
        with open(path, encoding="utf-8") as f:
            source = f.read()
        output = run_source(source)
        if output:
            sys.stdout.write(output)
        return 0
    except SupError as e:
        sys.stderr.write(str(e) + "\n")
        return 2
    except Exception as e:
        # Catch-all to avoid hanging on unexpected exceptions
        sys.stderr.write(str(e) + "\n")
        return 2


def repl() -> int:
    print("sup (type 'bye' to exit)")
    buffer: list[str] = []
    while True:
        try:
            line = input("> ")
        except EOFError:
            print()
            break
        if line.strip().lower() == "bye":
            break
        buffer.append(line)
        if line.strip().lower() == "bye":
            # unreachable due to break above, kept for clarity
            pass
        # Execute when a program block is complete: detect lines starting with 'sup' and ending with 'bye'
        src = "\n".join(buffer)
        if (
            "\n" in src
            and src.strip().lower().startswith("sup")
            and src.strip().lower().endswith("bye")
        ):
            try:
                out = run_source(src)
                if out:
                    print(out, end="")
            except SupError as e:
                print(str(e))
            except Exception as e:
                print(str(e))
            buffer.clear()
    return 0


def _resolve_module_path(module: str) -> str:
    # Search SUP_PATH then CWD for module.sup
    search_paths: list[str] = []
    env_path = os.environ.get("SUP_PATH")
    if env_path:
        search_paths.extend(env_path.split(os.pathsep))
    search_paths.append(os.getcwd())
    for base in search_paths:
        candidate = os.path.join(base, f"{module}.sup")
        if os.path.exists(candidate):
            return candidate
    raise FileNotFoundError(f"Cannot find module '{module}' (searched {search_paths})")


def _gather_imports(program: AST.Program, acc: set[str]) -> None:
    def walk(node: AST.Node) -> None:  # type: ignore[override]
        if isinstance(node, AST.Import):
            acc.add(node.module)
        elif isinstance(node, AST.FromImport):
            acc.add(node.module)
        # Recurse into composite nodes
        for attr in (
            "statements",
            "body",
            "else_body",
            "count_expr",
            "expr",
            "left",
            "right",
            "iterable",
        ):
            if hasattr(node, attr):
                val = getattr(node, attr)
                if isinstance(val, list):
                    for x in val:
                        if isinstance(x, AST.Node):
                            walk(x)
                elif isinstance(val, AST.Node):
                    walk(val)
        # Also check common fields that are lists of nodes
        if isinstance(node, AST.Program):
            for s in node.statements:
                walk(s)

    walk(program)  # type: ignore[arg-type]


def transpile_project(entry_file: str, out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    parser = Parser()

    visited: set[str] = set()

    entry_module: str | None = None
    entry_module_py: str | None = None

    def sanitize_module(name: str) -> str:
        safe = re.sub(r"[^0-9A-Za-z_]", "_", name)
        if not re.match(r"[A-Za-z_]", safe):
            safe = "m_" + safe
        return safe

    def transpile_file(path: str) -> None:
        src = open(path, encoding="utf-8").read()
        program = parser.parse(src)
        # Write .py next to out_dir with module name
        module_name = os.path.splitext(os.path.basename(path))[0]
        py_module = sanitize_module(module_name)
        py_path = os.path.join(out_dir, f"{py_module}.py")
        with open(py_path, "w", encoding="utf-8") as f:
            f.write(to_python(program))
        nonlocal entry_module
        nonlocal entry_module_py
        if entry_module is None:
            entry_module = module_name
            entry_module_py = py_module
        # Recurse into imports
        imports: set[str] = set()
        _gather_imports(program, imports)
        for mod in imports:
            if mod not in visited:
                visited.add(mod)
                mod_path = _resolve_module_path(mod)
                transpile_file(mod_path)

    visited.add(os.path.splitext(os.path.basename(entry_file))[0])
    transpile_file(entry_file)
    # Write a simple runner that calls entry_module.__main__()
    if entry_module_py:
        run_path = os.path.join(out_dir, "run.py")
        with open(run_path, "w", encoding="utf-8") as rf:
            rf.write(
                f"from {entry_module_py} import __main__ as _m\n\nif __name__ == '__main__':\n    _m()\n"
            )


def main(argv: list[str] | None = None) -> int:
    # Make CLI robust: treat 'transpile' as a dedicated mode; otherwise accept 'file' and '--emit'.
    if argv is None:
        argv = sys.argv[1:]

    # Route explicitly to transpile mode if first token is 'transpile'
    if len(argv) > 0 and argv[0] == "transpile":
        p_tr = argparse.ArgumentParser(
            prog="sup transpile",
            description="Transpile a sup program (and its imports) to Python files",
        )
        p_tr.add_argument("entry", help="Entry .sup file")
        p_tr.add_argument("--out", required=True, help="Output directory for .py files")
        tr_args = p_tr.parse_args(argv[1:])
        try:
            transpile_project(tr_args.entry, tr_args.out)
            print(f"Transpiled to {tr_args.out}")
            return 0
        except Exception as e:
            sys.stderr.write(str(e) + "\n")
            return 2

    # Default mode: run a file or start a REPL; optional --emit python; --version
    parser = argparse.ArgumentParser(prog="sup", description="Sup language CLI")
    parser.add_argument("file", nargs="?", help="Path to .sup file to run")
    parser.add_argument(
        "--emit", choices=["python"], help="Transpile to target language and print"
    )
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    args = parser.parse_args(argv)

    if args.version:
        print(__version__)
        return 0

    if args.file:
        if args.emit:
            with open(args.file, encoding="utf-8") as f:
                src = f.read()
            try:
                out = run_source(src, emit=args.emit)
                if out:
                    sys.stdout.write(out)
                return 0
            except SupError as e:
                sys.stderr.write(str(e) + "\n")
                return 2
        return run_file(args.file)
    return repl()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
