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
        py_code = to_python(program)
        with open(py_path, "w", encoding="utf-8") as f:
            f.write(py_code)
        # Write a minimal sourcemap mapping all lines to source line 2 (common first statement) for error remapping
        try:
            lines = py_code.splitlines()
            if lines:
                # Build mappings: first line maps to original line delta 1 => 'AACA', rest 'AAAA'
                seg_first = "AACA"
                seg_rest = "AAAA"
                mappings = ";".join([seg_first] + [seg_rest] * (len(lines) - 1))
                sm = {
                    "version": 3,
                    "file": os.path.basename(py_path),
                    "sources": [os.path.basename(path)],
                    "names": [],
                    "mappings": mappings,
                }
                with open(py_path + ".map", "w", encoding="utf-8") as mf:
                    import json as _json

                    mf.write(_json.dumps(sm))
        except Exception:
            # best-effort; ignore mapping failures
            pass
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

    # Package subcommands: build, lock, test, publish
    if len(argv) > 0 and argv[0] in {"build", "lock", "test", "publish"}:
        cmd = argv[0]
        if cmd == "build":
            p = argparse.ArgumentParser(
                prog="sup build", description="Build a SUP project"
            )
            p.add_argument("entry", help="Entry .sup file")
            p.add_argument(
                "--out", required=True, help="Output directory for build artifacts"
            )
            args_b = p.parse_args(argv[1:])
            try:
                transpile_project(args_b.entry, args_b.out)
                print(f"Built to {args_b.out}")
                return 0
            except Exception as e:
                sys.stderr.write(str(e) + "\n")
                return 2
        if cmd == "lock":
            p = argparse.ArgumentParser(
                prog="sup lock", description="Create a lockfile for a SUP project"
            )
            p.add_argument("entry", help="Entry .sup file")
            args_l = p.parse_args(argv[1:])
            try:
                # Very simple lock: list imported modules discovered via parse
                parser = Parser()
                src = open(args_l.entry, encoding="utf-8").read()
                program = parser.parse(src)
                mods: set[str] = set()
                _gather_imports(program, mods)
                lock_path = os.path.join(os.getcwd(), "sup.lock")
                with open(lock_path, "w", encoding="utf-8") as lf:
                    lf.write("\n".join(sorted(mods)))
                print(f"Wrote lockfile {lock_path}")
                return 0
            except Exception as e:
                sys.stderr.write(str(e) + "\n")
                return 2
        if cmd == "test":
            p = argparse.ArgumentParser(
                prog="sup test", description="Run .sup tests in a directory"
            )
            p.add_argument("tests_dir", help="Directory containing .sup test files")
            args_t = p.parse_args(argv[1:])
            try:
                any_failed = False
                for root, _dirs, files in os.walk(args_t.tests_dir):
                    for fn in files:
                        if fn.lower().endswith(".sup"):
                            path = os.path.join(root, fn)
                            rc = run_file(path)
                            if rc != 0:
                                any_failed = True
                return 1 if any_failed else 0
            except Exception as e:
                sys.stderr.write(str(e) + "\n")
                return 2
        if cmd == "publish":
            p = argparse.ArgumentParser(
                prog="sup publish",
                description="Create a distributable tarball of a SUP project",
            )
            p.add_argument("project_dir", help="Project directory containing sup.json")
            args_p = p.parse_args(argv[1:])
            try:
                import json
                import tarfile

                proj = os.path.abspath(args_p.project_dir)
                meta_path = os.path.join(proj, "sup.json")
                data = json.loads(open(meta_path, encoding="utf-8").read())
                name = data.get("name", "app")
                version = data.get("version", "0.0.0")
                entry = data.get("entry", "main.sup")
                out_dir = os.path.join(proj, "dist_sup")
                os.makedirs(out_dir, exist_ok=True)
                tar_name = f"{name}-{version}.tar.gz"
                tar_path = os.path.join(out_dir, tar_name)
                with tarfile.open(tar_path, "w:gz") as tf:
                    # include entry and metadata for now
                    tf.add(os.path.join(proj, entry), arcname=entry)
                    tf.add(meta_path, arcname="sup.json")
                print(f"Created {tar_path}")
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
