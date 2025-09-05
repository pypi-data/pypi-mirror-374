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
                        "renameProvider": True
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


