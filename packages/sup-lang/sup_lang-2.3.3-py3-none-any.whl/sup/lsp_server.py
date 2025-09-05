from __future__ import annotations

import json
import sys
from typing import Any, Dict

from .supfmt import format_text
from .suplint import lint_text
from .lsp_utils import word_at, build_index, offset_to_position, position_to_offset, BUILTIN_DOCS, KEYWORDS


def _read_message() -> Dict[str, Any] | None:
    header = sys.stdin.readline()
    if not header:
        return None
    if not header.lower().startswith("content-length:"):
        return None
    length = int(header.split(":", 1)[1].strip())
    # Consume CRLF
    _ = sys.stdin.readline()
    body = sys.stdin.read(length)
    return json.loads(body)


def _send_message(payload: Dict[str, Any]) -> None:
    data = json.dumps(payload)
    sys.stdout.write(f"Content-Length: {len(data)}\r\n\r\n{data}")
    sys.stdout.flush()


def main() -> int:
    # Minimal LSP server handling initialize, shutdown, textDocument events, formatting, and diagnostics
    documents: Dict[str, str] = {}
    indexes: Dict[str, Dict[str, Any]] = {}
    diagnostics_backend = "interp"  # or 'vm'
    while True:
        msg = _read_message()
        if msg is None:
            break
        method = msg.get("method")
        if method == "initialize":
            _send_message({
                "jsonrpc": "2.0",
                "id": msg.get("id"),
                "result": {
                    "capabilities": {
                        "documentFormattingProvider": True,
                        "textDocumentSync": 1,
                        "hoverProvider": True,
                        "completionProvider": {"triggerCharacters": [" "]},
                        "signatureHelpProvider": {"triggerCharacters": ["(", " "]},
                        "definitionProvider": True,
                        "renameProvider": True,
                        "codeActionProvider": True,
                        "inlayHintProvider": True,
                        "documentSymbolProvider": True,
                        "workspaceSymbolProvider": True,
                        "foldingRangeProvider": True,
                        "semanticTokensProvider": {
                            "legend": {"tokenTypes": ["function", "keyword"], "tokenModifiers": []},
                            "range": False,
                            "full": True
                        }
                    }
                }
            })
        elif method == "workspace/didChangeConfiguration":
            # Expect { diagnosticsBackend: 'interp' | 'vm' }
            cfg = ((msg.get("params", {}) or {}).get("settings", {}) or {}).get("sup", {})
            db = cfg.get("diagnosticsBackend")
            if db in {"interp", "vm"}:
                diagnostics_backend = db
            _send_message({"jsonrpc": "2.0", "id": msg.get("id"), "result": None})
        elif method == "textDocument/formatting":
            params = msg.get("params", {})
            doc = params.get("textDocument", {})
            uri = doc.get("uri", "")
            src = documents.get(uri, "")
            formatted = format_text(src)
            # Whole document edit
            line_count = max(1, src.count("\n"))
            edit = {
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 10**9, "character": 0}
                },
                "newText": formatted,
            }
            _send_message({
                "jsonrpc": "2.0",
                "id": msg.get("id"),
                "result": [edit]
            })
        elif method == "textDocument/didOpen":
            params = msg.get("params", {})
            doc = params.get("textDocument", {})
            uri = doc.get("uri", "")
            text = doc.get("text", "")
            documents[uri] = text
            indexes[uri] = build_index(uri, text)
            diags = []
            for d in lint_text(uri, text):
                diags.append({
                    "range": {
                        "start": {"line": max(0, d.line - 1), "character": max(0, d.column - 1)},
                        "end": {"line": max(0, d.line - 1), "character": max(0, d.column)}
                    },
                    "severity": 2,
                    "code": d.code,
                    "source": "suplint",
                    "message": d.message,
                })
            _send_message({
                "jsonrpc": "2.0",
                "method": "textDocument/publishDiagnostics",
                "params": {"uri": uri, "diagnostics": diags}
            })
        elif method == "textDocument/didChange":
            params = msg.get("params", {})
            uri = (params.get("textDocument", {}) or {}).get("uri", "")
            changes = params.get("contentChanges", []) or []
            if changes:
                # Assume full document change (common in many clients). Use first change's text.
                text = changes[0].get("text", "")
                documents[uri] = text
                indexes[uri] = build_index(uri, text)
                diags = []
                for d in lint_text(uri, text):
                    diags.append({
                        "range": {
                            "start": {"line": max(0, d.line - 1), "character": max(0, d.column - 1)},
                            "end": {"line": max(0, d.line - 1), "character": max(0, d.column)}
                        },
                        "severity": 2,
                        "code": d.code,
                        "source": "suplint",
                        "message": d.message,
                    })
                _send_message({
                    "jsonrpc": "2.0",
                    "method": "textDocument/publishDiagnostics",
                    "params": {"uri": uri, "diagnostics": diags}
                })
        elif method == "textDocument/hover":
            p = msg.get("params", {})
            doc = p.get("textDocument", {})
            pos = p.get("position", {})
            uri = doc.get("uri", "")
            text = documents.get(uri, "")
            wd = word_at(text, pos.get("line", 0), pos.get("character", 0))
            contents = None
            if wd:
                low = wd.lower()
                if low in (indexes.get(uri, {}).get("functions", {}) or {}):
                    fn = indexes[uri]["functions"][low]
                    sig = f"{low}({', '.join(fn['params'])})"
                    contents = {"kind": "markdown", "value": f"```sup\n{sig}\n```"}
                elif low in BUILTIN_DOCS:
                    contents = {"kind": "markdown", "value": f"```sup\n{BUILTIN_DOCS[low]}\n```"}
                elif wd in KEYWORDS:
                    contents = {"kind": "plaintext", "value": wd}
            _send_message({"jsonrpc": "2.0", "id": msg.get("id"), "result": {"contents": contents}})
        elif method == "textDocument/completion":
            p = msg.get("params", {})
            doc = p.get("textDocument", {})
            uri = doc.get("uri", "")
            items = []
            # functions
            for name, data in (indexes.get(uri, {}).get("functions", {}) or {}).items():
                items.append({"label": name, "kind": 3, "detail": f"fn({', '.join(data['params'])})"})
            # builtins/keywords
            for b, ex in BUILTIN_DOCS.items():
                items.append({"label": b, "kind": 14, "detail": ex})
            for kw in KEYWORDS:
                items.append({"label": kw, "kind": 14})
            _send_message({"jsonrpc": "2.0", "id": msg.get("id"), "result": items})
        elif method == "textDocument/definition":
            p = msg.get("params", {})
            doc = p.get("textDocument", {})
            pos = p.get("position", {})
            uri = doc.get("uri", "")
            text = documents.get(uri, "")
            wd = word_at(text, pos.get("line", 0), pos.get("character", 0)).lower()
            loc = None
            fn = (indexes.get(uri, {}).get("functions", {}) or {}).get(wd)
            if fn:
                loc = {"uri": uri, "range": {"start": {"line": fn["def"]["line"], "character": fn["def"]["character"]}, "end": {"line": fn["def"]["line"], "character": fn["def"]["character"] + len(wd)}}}
            _send_message({"jsonrpc": "2.0", "id": msg.get("id"), "result": loc})
        elif method == "textDocument/codeAction":
            p = msg.get("params", {})
            doc = (p.get("textDocument", {}) or {})
            uri = doc.get("uri", "")
            text = documents.get(uri, "")
            actions = []
            src = text.strip().lower()
            needs_wrap = not (src.startswith("sup") and src.endswith("bye"))
            if needs_wrap:
                new_text = ("sup\n" + text.rstrip("\n") + "\nbye\n") if text else "sup\nbye\n"
                edit = {
                    "changes": {
                        uri: [{
                            "range": {"start": {"line": 0, "character": 0}, "end": {"line": 10**9, "character": 0}},
                            "newText": new_text
                        }]
                    }
                }
                actions.append({"title": "Wrap file with sup/bye", "kind": "quickfix", "edit": edit})
            _send_message({"jsonrpc": "2.0", "id": msg.get("id"), "result": actions})
        elif method == "textDocument/documentSymbol":
            p = msg.get("params", {})
            doc = p.get("textDocument", {})
            uri = doc.get("uri", "")
            idx = indexes.get(uri, {})
            items = []
            for name, data in (idx.get("functions", {}) or {}).items():
                line = data["def"]["line"]
                ch = data["def"]["character"]
                items.append({
                    "name": name,
                    "kind": 12,  # Function
                    "range": {"start": {"line": line, "character": ch}, "end": {"line": line, "character": ch + max(1, len(name))}},
                    "selectionRange": {"start": {"line": line, "character": ch}, "end": {"line": line, "character": ch + max(1, len(name))}},
                })
            _send_message({"jsonrpc": "2.0", "id": msg.get("id"), "result": items})
        elif method == "workspace/symbol":
            p = msg.get("params", {})
            query = (p.get("query") or "").lower()
            items = []
            for uri, idx in indexes.items():
                for name, data in (idx.get("functions", {}) or {}).items():
                    if query and query not in name:
                        continue
                    line = data["def"]["line"]
                    ch = data["def"]["character"]
                    items.append({
                        "name": name,
                        "kind": 12,
                        "location": {"uri": uri, "range": {"start": {"line": line, "character": ch}, "end": {"line": line, "character": ch + max(1, len(name))}}}
                    })
            _send_message({"jsonrpc": "2.0", "id": msg.get("id"), "result": items})
        elif method == "textDocument/foldingRange":
            p = msg.get("params", {})
            doc = p.get("textDocument", {})
            uri = doc.get("uri", "")
            text = documents.get(uri, "")
            # naive folding: fold from 'sup' to 'bye' if present, and function bodies
            lines = text.splitlines()
            folds = []
            start_sup = None
            for i, line in enumerate(lines):
                low = line.strip().lower()
                if low == "sup":
                    start_sup = i
                elif low == "bye" and start_sup is not None and i > start_sup:
                    folds.append({"startLine": start_sup, "endLine": i})
                    start_sup = None
            # function folding: look for 'define function' ... 'end function'
            start_fn = None
            for i, line in enumerate(lines):
                low = line.strip().lower()
                if low.startswith("define function"):
                    start_fn = i
                elif low.startswith("end function") and start_fn is not None and i > start_fn:
                    folds.append({"startLine": start_fn, "endLine": i})
                    start_fn = None
            _send_message({"jsonrpc": "2.0", "id": msg.get("id"), "result": folds})
        elif method == "textDocument/inlayHint":
            p = msg.get("params", {})
            doc = (p.get("textDocument", {}) or {})
            uri = doc.get("uri", "")
            text = documents.get(uri, "")
            idx = indexes.get(uri, {})
            hints = []
            lines = text.splitlines()
            import re as _re
            pat = _re.compile(r"\bcall\s+([A-Za-z_][A-Za-z0-9_]*)\b")
            for i, line in enumerate(lines):
                for m in pat.finditer(line):
                    name = m.group(1).lower()
                    fn = (idx.get("functions", {}) or {}).get(name)
                    if fn:
                        params = fn.get("params", [])
                        label = "(" + ", ".join(params) + ")"
                        pos = m.start(1) + len(name)
                        hints.append({"position": {"line": i, "character": pos}, "label": label, "kind": 2})
            _send_message({"jsonrpc": "2.0", "id": msg.get("id"), "result": hints})
        elif method == "textDocument/semanticTokens/full":
            p = msg.get("params", {})
            doc = (p.get("textDocument", {}) or {})
            uri = doc.get("uri", "")
            text = documents.get(uri, "")
            idx = indexes.get(uri, {})
            tokens = []
            lines = text.splitlines()
            kw = set()
            for phrase in KEYWORDS:
                for w in phrase.split():
                    kw.add(w)
            import re as _re
            word_re = _re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
            for i, line in enumerate(lines):
                for m in word_re.finditer(line):
                    w = m.group(0)
                    if w in kw:
                        tokens.append((i, m.start(), len(w), 1, 0))
            for name, data in (idx.get("functions", {}) or {}).items():
                i = data["def"]["line"]
                ch = data["def"]["character"]
                tokens.append((i, ch, max(1, len(name)), 0, 0))
            call_pat = _re.compile(r"\bcall\s+([A-Za-z_][A-Za-z0-9_]*)\b")
            for i, line in enumerate(lines):
                for m in call_pat.finditer(line):
                    name = m.group(1)
                    tokens.append((i, m.start(1), len(name), 0, 0))
            tokens.sort()
            data = []
            prev_line = 0
            prev_char = 0
            for line, char, length, ttype, mods in tokens:
                if line == prev_line:
                    delta_line = 0
                    delta_start = char - prev_char
                else:
                    delta_line = line - prev_line
                    delta_start = char
                data.extend([delta_line, delta_start, length, ttype, mods])
                prev_line = line
                prev_char = char
            _send_message({"jsonrpc": "2.0", "id": msg.get("id"), "result": {"data": data}})
        elif method == "textDocument/rename":
            p = msg.get("params", {})
            text_doc = p.get("textDocument", {})
            pos = p.get("position", {})
            new_name = p.get("newName", "")
            uri = text_doc.get("uri", "")
            text = documents.get(uri, "")
            wd = word_at(text, pos.get("line", 0), pos.get("character", 0)).lower()
            idx = indexes.get(uri, {})
            fn = (idx.get("functions", {}) or {}).get(wd)
            edits = []
            if fn and new_name:
                # naive replace of definition name on the def line only
                line_no = fn["def"]["line"]
                lines = text.splitlines()
                if 0 <= line_no < len(lines):
                    line = lines[line_no]
                    start = line.lower().find(wd)
                    if start >= 0:
                        edits.append({
                            "range": {"start": {"line": line_no, "character": start}, "end": {"line": line_no, "character": start + len(wd)}},
                            "newText": new_name,
                        })
                # also rename simple references in the file (best-effort)
                for i, line in enumerate(lines):
                    pos = line.lower().find(wd)
                    if pos >= 0 and i != line_no:
                        edits.append({
                            "range": {"start": {"line": i, "character": pos}, "end": {"line": i, "character": pos + len(wd)}},
                            "newText": new_name,
                        })
            _send_message({"jsonrpc": "2.0", "id": msg.get("id"), "result": {"documentChanges": [{"textDocument": {"uri": uri, "version": None}, "edits": edits}]}})
        elif method == "textDocument/signatureHelp":
            p = msg.get("params", {})
            doc = p.get("textDocument", {})
            pos = p.get("position", {})
            uri = doc.get("uri", "")
            text = documents.get(uri, "")
            wd = word_at(text, pos.get("line", 0), pos.get("character", 0)).lower()
            sigs = []
            fn = (indexes.get(uri, {}).get("functions", {}) or {}).get(wd)
            if fn:
                sigs.append({
                    "label": f"{wd}({', '.join(fn['params'])})",
                    "parameters": [{"label": p} for p in fn["params"]],
                })
            elif wd in BUILTIN_DOCS:
                sigs.append({"label": BUILTIN_DOCS[wd], "parameters": []})
            _send_message({"jsonrpc": "2.0", "id": msg.get("id"), "result": {"signatures": sigs, "activeSignature": 0, "activeParameter": 0}})
        elif method == "shutdown":
            _send_message({"jsonrpc": "2.0", "id": msg.get("id"), "result": None})
        elif method == "exit":
            break
        else:
            # Respond to unknown methods to avoid client hangs
            if "id" in msg:
                _send_message({"jsonrpc": "2.0", "id": msg.get("id"), "result": None})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


