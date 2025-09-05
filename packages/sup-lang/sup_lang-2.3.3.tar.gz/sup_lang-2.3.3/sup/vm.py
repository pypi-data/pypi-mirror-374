from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Tuple, Dict

from . import ast as AST


@dataclass
class Code:
    instructions: List[Tuple[str, Any]]
    functions: Dict[str, Tuple[List[Tuple[str, Any]], List[str]]]


def compile_ast(program: AST.Program) -> Code:
    instructions: List[Tuple[str, Any]] = []
    functions: Dict[str, Tuple[List[Tuple[str, Any]], List[str]]] = {}

    def emit(op: str, arg: Any = None) -> None:
        instructions.append((op, arg))

    def compile_fn(fn: AST.FunctionDef) -> None:
        fn_insts: List[Tuple[str, Any]] = []
        def emitf(op: str, arg: Any = None) -> None:
            fn_insts.append((op, arg))
        # Mark current function instruction list for conditional patching
        functions["__current__"] = (fn_insts, [p.lower() for p in fn.params])
        # Body
        for s in fn.body:
            compile_node_into(s, emitf)
        emitf("RETURN_NONE")
        functions[fn.name.lower()] = (fn_insts, [p.lower() for p in fn.params])
        functions.pop("__current__", None)

    def compile_node_into(node: AST.Node, emit_func) -> None:
        if isinstance(node, AST.Number):
            emit_func("LOAD_CONST", node.value)
            return
        if isinstance(node, AST.String):
            emit_func("LOAD_CONST", node.value)
            return
        if isinstance(node, AST.Identifier):
            emit_func("LOAD_NAME", node.name.lower())
            return
        if isinstance(node, AST.Binary):
            compile_node_into(node.left, emit_func)
            compile_node_into(node.right, emit_func)
            if node.op == "+":
                emit_func("BINARY_ADD")
            elif node.op == "-":
                emit_func("BINARY_SUB")
            elif node.op == "*":
                emit_func("BINARY_MUL")
            elif node.op == "/":
                emit_func("BINARY_DIV")
            else:
                emit_func("NOP")
            return
        if isinstance(node, AST.Compare):
            compile_node_into(node.left, emit_func)
            compile_node_into(node.right, emit_func)
            emit_func("COMPARE", node.op)
            return
        if isinstance(node, AST.BoolBinary):
            compile_node_into(node.left, emit_func)
            compile_node_into(node.right, emit_func)
            if node.op == "and":
                emit_func("BOOL_AND")
            else:
                emit_func("BOOL_OR")
            return
        if isinstance(node, AST.NotOp):
            compile_node_into(node.expr, emit_func)
            emit_func("NOT")
            return
        if isinstance(node, AST.MakeList):
            # compile items in order, then build list (leave on stack)
            for it in node.items:
                compile_node_into(it, emit_func)
            emit_func("BUILD_LIST", len(node.items))
            return
        if isinstance(node, AST.MakeMap):
            emit_func("BUILD_MAP")
            return
        if isinstance(node, AST.Push):
            compile_node_into(node.target, emit_func)
            compile_node_into(node.item, emit_func)
            emit_func("LIST_PUSH")
            return
        if isinstance(node, AST.Pop):
            compile_node_into(node.target, emit_func)
            emit_func("LIST_POP")
            return
        if isinstance(node, AST.GetKey):
            compile_node_into(node.target, emit_func)
            compile_node_into(node.key, emit_func)
            emit_func("GET_KEY")
            return
        if isinstance(node, AST.SetKey):
            compile_node_into(node.target, emit_func)
            compile_node_into(node.key, emit_func)
            compile_node_into(node.value, emit_func)
            emit_func("SET_KEY")
            return
        if isinstance(node, AST.DeleteKey):
            compile_node_into(node.target, emit_func)
            compile_node_into(node.key, emit_func)
            emit_func("DEL_KEY")
            return
        if isinstance(node, AST.Length):
            compile_node_into(node.target, emit_func)
            emit_func("LENGTH")
            return
        if isinstance(node, AST.Ask):
            emit_func("ASK", node.name.lower())
            return
        if isinstance(node, AST.Import):
            emit_func("IMPORT", (node.module, node.alias))
            return
        if isinstance(node, AST.FromImport):
            emit_func("FROM_IMPORT", (node.module, node.names))
            return
        if isinstance(node, AST.ForEach):
            compile_node_into(node.iterable, emit_func)
            emit_func("FOREACH_START", node.var.lower())
            # prime the loop to set first item and jump to body
            # body start is filled at runtime using current pc in VM; we still pass a placeholder
            body_start_placeholder = -1
            emit_func("FOREACH_NEXT", body_start_placeholder)
            for s in node.body:
                compile_node_into(s, emit_func)
            emit_func("FOREACH_NEXT", body_start_placeholder)
            return
        if isinstance(node, AST.ExprStmt):
            if isinstance(node.expr, AST.MakeList):
                # 'make list ...' statement: assign to implicit name 'list'
                compile_node_into(node.expr, emit_func)
                emit_func("SET_LAST_RESULT")
                emit_func("STORE_NAME", "list")
                return
            compile_node_into(node.expr, emit_func)
            emit_func("SET_LAST_RESULT")
            emit_func("POP_TOP")
            return
        if isinstance(node, AST.Assignment):
            compile_node_into(node.expr, emit_func)
            emit_func("STORE_NAME", node.name.lower())
            emit_func("SET_LAST_RESULT")
            return
        if isinstance(node, AST.Print):
            if node.expr is None:
                emit_func("PRINT_RESULT")
            else:
                compile_node_into(node.expr, emit_func)
                emit_func("PRINT")
            return
        if isinstance(node, AST.If):
            # cond
            cond_node = node.cond if node.cond is not None else AST.Compare(op=node.op, left=node.left, right=node.right)  # type: ignore[arg-type]
            compile_node_into(cond_node, emit_func)
            # placeholder jump
            # Emit placeholder; record index in the correct list depending on context
            if emit_func == emit:
                jmp_if_false_idx = len(instructions)
                emit_func("JUMP_IF_FALSE", None)
                then_start_idx = len(instructions)
            else:
                # function-local emission
                jmp_if_false_idx = len(functions.get("__current__", ([], []))[0])
                emit_func("JUMP_IF_FALSE", None)
                then_start_idx = len(functions.get("__current__", ([], []))[0])
            # then body
            for s in node.body or []:
                compile_node_into(s, emit_func)
            # optional else
            if node.else_body is not None:
                if emit_func == emit:
                    jmp_end_idx = len(instructions)
                    emit_func("JUMP", None)
                    instructions[jmp_if_false_idx] = ("JUMP_IF_FALSE", len(instructions))
                else:
                    lst = functions.get("__current__", ([], []))[0]
                    jmp_end_idx = len(lst)
                    emit_func("JUMP", None)
                    lst[jmp_if_false_idx] = ("JUMP_IF_FALSE", len(lst))
                for s in node.else_body:
                    compile_node_into(s, emit_func)
                # patch end jump
                if emit_func == emit:
                    instructions[jmp_end_idx] = ("JUMP", len(instructions))
                else:
                    lst = functions.get("__current__", ([], []))[0]
                    lst[jmp_end_idx] = ("JUMP", len(lst))
            else:
                if emit_func == emit:
                    instructions[jmp_if_false_idx] = ("JUMP_IF_FALSE", len(instructions))
                else:
                    lst = functions.get("__current__", ([], []))[0]
                    lst[jmp_if_false_idx] = ("JUMP_IF_FALSE", len(lst))
            return
        if isinstance(node, AST.While):
            loop_start = len(instructions)
            compile_node_into(node.cond, emit_func)
            jfalse_idx = len(instructions)
            emit_func("JUMP_IF_FALSE", None)
            for s in node.body:
                compile_node_into(s, emit_func)
            emit_func("JUMP", loop_start)
            instructions[jfalse_idx] = ("JUMP_IF_FALSE", len(instructions))
            return
        if isinstance(node, AST.Repeat):
            # Evaluate count and start loop frame
            compile_node_into(node.count_expr, emit_func)
            emit_func("SET_LOOP")
            loop_body_start = len(instructions)
            for s in node.body:
                compile_node_into(s, emit_func)
            emit_func("LOOP_NEXT", loop_body_start)
            return
        if isinstance(node, AST.FunctionDef):
            compile_fn(node)
            return
        if isinstance(node, AST.Call):
            for a in node.args:
                compile_node_into(a, emit_func)
            emit_func("CALL", (node.name.lower(), len(node.args)))
            return
        if isinstance(node, AST.Return):
            if node.expr is None:
                emit_func("RETURN_NONE")
            else:
                compile_node_into(node.expr, emit_func)
                emit_func("RETURN_VALUE")
            return
        if isinstance(node, AST.BuiltinCall):
            for a in node.args:
                compile_node_into(a, emit_func)
            emit_func("BUILTIN", (node.name, len(node.args)))
            return
        if isinstance(node, AST.TryCatch):
            # Setup handler with placeholder catch address
            try_idx = len(instructions) if emit_func is emit else None
            emit_func("TRY_PUSH", (None, node.catch_name))
            # try body
            for s in node.body:
                compile_node_into(s, emit_func)
            # normal completion: pop handler
            emit_func("TRY_POP")
            # finally after normal path
            if node.finally_body is not None:
                for s in node.finally_body:
                    compile_node_into(s, emit_func)
            # jump over catch/finally on normal path
            end_jmp_idx = len(instructions) if emit_func is emit else None
            emit_func("JUMP", None)
            # catch block start
            catch_start = len(instructions) if emit_func is emit else None
            if emit_func is emit and try_idx is not None and catch_start is not None:
                instructions[try_idx] = ("TRY_PUSH", (catch_start, node.catch_name))
            if node.catch_body is not None:
                for s in node.catch_body:
                    compile_node_into(s, emit_func)
            # finally after catch path
            if node.finally_body is not None:
                for s in node.finally_body:
                    compile_node_into(s, emit_func)
            # end label
            if emit_func is emit and end_jmp_idx is not None:
                instructions[end_jmp_idx] = ("JUMP", len(instructions))
            return
        if isinstance(node, AST.Throw):
            compile_node_into(node.value, emit_func)
            emit_func("THROW")
            return
        # Unsupported nodes: raise for clarity
        if isinstance(node, (AST.Ask, AST.Import, AST.FromImport)):
            raise NotImplementedError("VM backend: this construct is not supported yet (IO/imports).")
        emit_func("NOP")

    for s in program.statements:
        compile_node_into(s, emit)
    emit("RETURN_NONE")
    return Code(instructions, functions)


def run(program: AST.Program) -> str:
    code = compile_ast(program)
    env: dict[str, Any] = {}
    stack: list[Any] = []
    last_result: Any | None = None
    outputs: list[str] = []
    loop_stack: list[dict[str, Any]] = []
    call_stack: list[Tuple[List[Tuple[str, Any]], int, list[dict[str, Any]] | None]] = []  # (instr, return_pc, locals_chain)
    locals_env: list[dict[str, Any]] | None = None
    try_stack: list[dict[str, Any]] = []
    for_stack: list[dict[str, Any]] = []

    def pop() -> Any:
        if not stack:
            return None
        return stack.pop()

    def load_name(name: str) -> Any:
        # Support dotted access: module.symbol
        if "." in name:
            mod, sym = name.split(".", 1)
            # check local scopes first for module dict
            if locals_env is not None:
                for scope in locals_env:
                    if mod in scope and isinstance(scope.get(mod), dict):
                        return scope.get(mod).get(sym)
            # then globals
            mval = env.get(mod)
            if isinstance(mval, dict):
                return mval.get(sym)
        if locals_env is not None:
            for scope in locals_env:
                if name in scope:
                    return scope.get(name)
        return env.get(name)

    def store_name(name: str, value: Any) -> None:
        if locals_env is not None and len(locals_env) > 0:
            locals_env[0][name] = value
        else:
            env[name] = value

    for op, arg in code.instructions:
        if op == "LOAD_CONST":
            stack.append(arg)
        elif op == "LOAD_NAME":
            stack.append(load_name(arg))
        elif op == "STORE_NAME":
            val = pop()
            store_name(arg, val)
        elif op == "BINARY_ADD":
            b = pop(); a = pop()
            stack.append(float(a) + float(b))
        elif op == "BINARY_SUB":
            b = pop(); a = pop()
            stack.append(float(a) - float(b))
        elif op == "BINARY_MUL":
            b = pop(); a = pop()
            stack.append(float(a) * float(b))
        elif op == "BINARY_DIV":
            b = pop(); a = pop()
            stack.append(float(a) / float(b))
        elif op == "COMPARE":
            b = pop(); a = pop()
            if arg == ">":
                stack.append(float(a) > float(b))
            elif arg == "<":
                stack.append(float(a) < float(b))
            elif arg == "==":
                stack.append(a == b)
            elif arg == "!=":
                stack.append(a != b)
            elif arg == ">=":
                stack.append(float(a) >= float(b))
            elif arg == "<=":
                stack.append(float(a) <= float(b))
            else:
                stack.append(False)
        elif op == "NOT":
            v = pop(); stack.append(not bool(v))
        elif op == "BOOL_AND":
            b = pop(); a = pop(); stack.append(bool(a) and bool(b))
        elif op == "BOOL_OR":
            b = pop(); a = pop(); stack.append(bool(a) or bool(b))
        elif op == "PRINT":
            v = pop()
            last_result = v
            outputs.append(f"{v}\n")
        elif op == "PRINT_RESULT":
            outputs.append(f"{last_result}\n")
        elif op == "SET_LAST_RESULT":
            last_result = pop()
            stack.append(last_result)
        elif op == "POP_TOP":
            _ = pop()
        elif op == "JUMP":
            # arg is absolute index
            # Adjust PC: Python for-loop increments automatically; emulate by manipulating index
            target = int(arg)
            # set up to jump by setting a variable; we'll use a while loop to control
            # This block will be handled by converting to manual index loop below
            pass
        elif op == "JUMP_IF_FALSE":
            v = pop()
            if not bool(v):
                # same as JUMP
                pass
        elif op == "SET_LOOP":
            count = pop()
            try:
                iterations = int(float(count))
            except Exception:
                iterations = 0
            loop_stack.append({"remaining": iterations, "start": None})
        elif op == "LOOP_NEXT":
            # arg holds loop body start index
            if not loop_stack:
                continue
            frame = loop_stack[-1]
            if frame["start"] is None:
                frame["start"] = int(arg)
            frame["remaining"] -= 1
            if frame["remaining"] > 0:
                # jump to start
                pass
            else:
                loop_stack.pop()
        elif op == "RETURN_NONE":
            break
        else:
            # NOP or unknown
            pass
    # The above loop lacks actual JUMP mechanics due to Python for-loop; re-run using manual pc
    env = {}
    stack = []
    last_result = None
    outputs = []
    loop_stack = []
    pc = 0
    instr = code.instructions
    n = len(instr)
    while pc < n:
        # refresh n every loop in case instr was switched by CALL/tail-call
        n = len(instr)
        op, arg = instr[pc]
        if op == "LOAD_CONST":
            stack.append(arg)
        elif op == "LOAD_NAME":
            # Use same dotted/global/lexical resolution as in the first pass
            stack.append(load_name(arg))
        elif op == "STORE_NAME":
            val = stack.pop() if stack else None
            if locals_env is not None and len(locals_env) > 0:
                locals_env[0][arg] = val
            else:
                env[arg] = val
        elif op == "BINARY_ADD":
            b = stack.pop(); a = stack.pop(); stack.append(float(a) + float(b))
        elif op == "BINARY_SUB":
            b = stack.pop(); a = stack.pop(); stack.append(float(a) - float(b))
        elif op == "BINARY_MUL":
            b = stack.pop(); a = stack.pop(); stack.append(float(a) * float(b))
        elif op == "BINARY_DIV":
            b = stack.pop(); a = stack.pop(); stack.append(float(a) / float(b))
        elif op == "COMPARE":
            b = stack.pop(); a = stack.pop()
            if arg == ">":
                stack.append(float(a) > float(b))
            elif arg == "<":
                stack.append(float(a) < float(b))
            elif arg == "==":
                stack.append(a == b)
            elif arg == "!=":
                stack.append(a != b)
            elif arg == ">=":
                stack.append(float(a) >= float(b))
            elif arg == "<=":
                stack.append(float(a) <= float(b))
            else:
                stack.append(False)
        elif op == "NOT":
            v = stack.pop(); stack.append(not bool(v))
        elif op == "BOOL_AND":
            b = stack.pop(); a = stack.pop(); stack.append(bool(a) and bool(b))
        elif op == "BOOL_OR":
            b = stack.pop(); a = stack.pop(); stack.append(bool(a) or bool(b))
        elif op == "PRINT":
            v = stack.pop(); last_result = v; outputs.append(f"{v}\n")
        elif op == "PRINT_RESULT":
            outputs.append(f"{last_result}\n")
        elif op == "SET_LAST_RESULT":
            last_result = stack.pop() if stack else None
            stack.append(last_result)
        elif op == "POP_TOP":
            if stack:
                stack.pop()
        elif op == "JUMP":
            pc = int(arg)
            continue
        elif op == "JUMP_IF_FALSE":
            v = stack.pop() if stack else None
            if not bool(v):
                pc = int(arg)
                continue
        elif op == "SET_LOOP":
            count = stack.pop() if stack else 0
            try:
                rem = int(float(count))
            except Exception:
                rem = 0
            loop_stack.append({"remaining": rem, "start": pc + 1})
        elif op == "LOOP_NEXT":
            if not loop_stack:
                pass
            else:
                frame = loop_stack[-1]
                frame["remaining"] -= 1
                if frame["remaining"] > 0:
                    pc = int(frame["start"])
                    continue
                else:
                    loop_stack.pop()
        elif op == "TRY_PUSH":
            catch_pc, catch_name = arg
            try_stack.append({"catch_pc": catch_pc, "catch_name": catch_name})
        elif op == "TRY_POP":
            if try_stack:
                try_stack.pop()
        elif op == "THROW":
            val = stack.pop() if stack else None
            if not try_stack:
                raise RuntimeError(f"Uncaught throw: {val}")
            handler = try_stack.pop()
            # bind catch var if provided
            cname = handler.get("catch_name")
            if cname:
                if locals_env is not None and len(locals_env) > 0:
                    locals_env[0][cname.lower()] = val
                else:
                    env[cname.lower()] = val
            pc = int(handler["catch_pc"]) if handler.get("catch_pc") is not None else pc + 1
            continue
        elif op == "BUILD_LIST":
            nitems = int(arg) if arg is not None else 0
            vals = [stack.pop() if stack else None for _ in range(nitems)][::-1]
            stack.append(vals)
        elif op == "BUILD_MAP":
            stack.append({})
        elif op == "LIST_PUSH":
            item = stack.pop() if stack else None
            target = stack.pop() if stack else None
            if isinstance(target, list):
                target.append(item)
                last_result = target
                stack.append(target)
            else:
                stack.append(target)
        elif op == "LIST_POP":
            target = stack.pop() if stack else None
            if isinstance(target, list) and target:
                val = target.pop()
                last_result = val
                stack.append(val)
            else:
                stack.append(None)
        elif op == "GET_KEY":
            key = stack.pop() if stack else None
            target = stack.pop() if stack else None
            if isinstance(target, list):
                try:
                    idx = int(float(key)) if key is not None else 0
                    val = target[idx]
                except Exception:
                    val = None
                last_result = val
                stack.append(val)
            elif isinstance(target, dict):
                val = target.get(key)
                last_result = val
                stack.append(val)
            else:
                stack.append(None)
        elif op == "SET_KEY":
            value = stack.pop() if stack else None
            key = stack.pop() if stack else None
            target = stack.pop() if stack else None
            if isinstance(target, dict):
                target[key] = value
                last_result = target
                stack.append(target)
            else:
                stack.append(target)
        elif op == "DEL_KEY":
            key = stack.pop() if stack else None
            target = stack.pop() if stack else None
            if isinstance(target, dict):
                target.pop(key, None)
                last_result = target
                stack.append(target)
            else:
                stack.append(target)
        elif op == "LENGTH":
            target = stack.pop() if stack else None
            try:
                ln = len(target)  # type: ignore[arg-type]
            except Exception:
                ln = 0
            last_result = ln
            stack.append(ln)
        elif op == "ASK":
            name = str(arg)
            try:
                val = input()
            except Exception:
                val = ""
            if locals_env is not None and len(locals_env) > 0:
                locals_env[0][name] = val
            else:
                env[name] = val
            last_result = val
            stack.append(val)
        elif op == "IMPORT":
            module, alias = arg
            try:
                # Use interpreter to load module namespace for now
                from .parser import Parser as _Parser
                from .interpreter import Interpreter as _Interp
                import os as _os

                search_paths = [_os.getcwd()]
                env_path = _os.environ.get("SUP_PATH")
                if env_path:
                    search_paths = env_path.split(_os.pathsep) + search_paths
                path = None
                for base in search_paths:
                    cand = _os.path.join(base, f"{module}.sup")
                    if _os.path.exists(cand):
                        path = cand
                        break
                ns = {}
                if path:
                    src = open(path, encoding="utf-8").read()
                    program = _Parser().parse(src)
                    inter = _Interp()
                    inter.run(program)
                    ns.update(inter.env)
                    for fn_name, fn_def in inter.functions.items():
                        ns[fn_name] = fn_def
                    # Also compile module functions for VM and register namespaced entries
                    mcode = compile_ast(program)
                    bind = (alias or module).lower()
                    for fname, fdata in mcode.functions.items():
                        code.functions[f"{bind}.{fname}"] = fdata
                bind = (alias or module).lower()
                env[bind] = ns
                # expose flat dotted scalars for second-pass LOAD_NAME fallback
                for k, v in ns.items():
                    if not isinstance(v, dict):
                        env[f"{bind}.{k}"] = v
            except Exception:
                env[(alias or module).lower()] = {}
        elif op == "FROM_IMPORT":
            module, names = arg
            try:
                from .parser import Parser as _Parser
                from .interpreter import Interpreter as _Interp
                import os as _os

                search_paths = [_os.getcwd()]
                env_path = _os.environ.get("SUP_PATH")
                if env_path:
                    search_paths = env_path.split(_os.pathsep) + search_paths
                path = None
                for base in search_paths:
                    cand = _os.path.join(base, f"{module}.sup")
                    if _os.path.exists(cand):
                        path = cand
                        break
                ns = {}
                if path:
                    src = open(path, encoding="utf-8").read()
                    program = _Parser().parse(src)
                    inter = _Interp()
                    inter.run(program)
                    ns.update(inter.env)
                    for fn_name, fn_def in inter.functions.items():
                        ns[fn_name] = fn_def
                    mcode = compile_ast(program)
                for name, alias in names:
                    sym = ns.get(name)
                    env[(alias or name).lower()] = sym
                    # Register compiled function for direct calls if present
                    if name in (mcode.functions if path else {}):
                        code.functions[(alias or name).lower()] = mcode.functions[name]
            except Exception:
                for name, alias in names:
                    env[(alias or name).lower()] = None
        elif op == "FOREACH_START":
            iterable = stack.pop() if stack else None
            try:
                items = list(iterable) if iterable is not None else []
            except Exception:
                items = []
            for_stack.append({"items": items, "index": 0, "var": str(arg), "start": None})
        elif op == "FOREACH_NEXT":
            if not for_stack:
                pass
            else:
                frame = for_stack[-1]
                if frame["start"] is None:
                    frame["start"] = int(arg)
                items = frame["items"]
                idx = frame["index"]
                if idx < len(items):
                    # bind loop var in nearest scope
                    if locals_env is not None and len(locals_env) > 0:
                        locals_env[0][frame["var"]] = items[idx]
                    else:
                        env[frame["var"]] = items[idx]
                    frame["index"] = idx + 1
                    pc = int(frame["start"])
                    continue
                else:
                    for_stack.pop()
        elif op == "RETURN_NONE":
            if call_stack:
                # return to caller with None
                last_result = None
                instr, pc, locals_env = call_stack.pop()
                n = len(instr)
                continue
            break
        elif op == "RETURN_VALUE":
            ret = stack.pop() if stack else None
            last_result = ret
            if call_stack:
                instr, pc, locals_env = call_stack.pop()
                stack.append(ret)
                n = len(instr)
                continue
            else:
                # top-level return prints nothing; end program
                break
        elif op == "BUILTIN":
            name, argc = arg
            args_vals = [stack.pop() if stack else None for _ in range(argc)][::-1]
            res = None
            if name == "power":
                a, b = args_vals
                res = float(a) ** float(b)
            elif name == "sqrt":
                a = args_vals[0]
                res = float(a) ** 0.5
            elif name == "abs":
                a = args_vals[0]
                res = abs(float(a))
            elif name == "upper":
                a = args_vals[0]
                res = str(a).upper()
            elif name == "lower":
                a = args_vals[0]
                res = str(a).lower()
            elif name == "concat":
                a, b = args_vals
                res = str(a) + str(b)
            elif name == "min":
                a, b = args_vals
                res = float(a) if float(a) <= float(b) else float(b)
            elif name == "max":
                a, b = args_vals
                res = float(a) if float(a) >= float(b) else float(b)
            elif name == "floor":
                import math

                a = args_vals[0]
                res = float(math.floor(float(a)))
            elif name == "ceil":
                import math

                a = args_vals[0]
                res = float(math.ceil(float(a)))
            elif name == "trim":
                a = args_vals[0]
                res = str(a).strip()
            elif name == "contains":
                a, b = args_vals
                if isinstance(a, list):
                    res = any(item == b for item in a)
                else:
                    res = str(b) in str(a)
            elif name == "join":
                sep, lst = args_vals
                if isinstance(lst, list):
                    res = str(sep).join(str(x) for x in lst)
                else:
                    res = str(lst)
            # FFI: files/env/path/json/regex/glob (deterministic subset)
            elif name == "read_file":
                path = str(args_vals[0])
                with open(path, encoding="utf-8") as f:
                    res = f.read()
            elif name == "write_file":
                path = str(args_vals[0]); data = str(args_vals[1])
                with open(path, "w", encoding="utf-8") as f:
                    f.write(data)
                res = True
            elif name == "json_parse":
                import json as _json

                res = _json.loads(str(args_vals[0]))
            elif name == "json_stringify":
                import json as _json

                res = _json.dumps(args_vals[0])
            elif name == "env_get":
                import os as _os

                res = _os.environ.get(str(args_vals[0]))
            elif name == "env_set":
                import os as _os

                _os.environ[str(args_vals[0])] = str(args_vals[1])
                res = True
            elif name == "cwd":
                import os as _os

                res = _os.getcwd()
            elif name == "join_path":
                import os as _os

                res = _os.path.join(str(args_vals[0]), str(args_vals[1]))
            elif name == "basename":
                import os as _os

                res = _os.path.basename(str(args_vals[0]))
            elif name == "dirname":
                import os as _os

                res = _os.path.dirname(str(args_vals[0]))
            elif name == "exists":
                import os as _os

                res = _os.path.exists(str(args_vals[0]))
            elif name == "glob":
                import glob as _glob

                res = _glob.glob(str(args_vals[0]))
            elif name == "regex_match":
                import re as _re

                res = bool(_re.match(str(args_vals[0]), str(args_vals[1])))
            elif name == "regex_search":
                import re as _re

                res = bool(_re.search(str(args_vals[0]), str(args_vals[1])))
            elif name == "regex_replace":
                import re as _re

                res = _re.sub(str(args_vals[0]), str(args_vals[2]), str(args_vals[1]))
            else:
                raise NotImplementedError(f"VM builtin '{name}' not supported")
            last_result = res
            stack.append(res)
        elif op == "CALL":
            fname, argc = arg
            if fname not in code.functions:
                raise NotImplementedError(f"VM backend: function '{fname}' not defined")
            fn_insts, params = code.functions[fname]
            # collect args
            args_vals = [stack.pop() if stack else None for _ in range(argc)][::-1]
            # Tail-call detection: next instruction is RETURN_VALUE
            next_pc = pc + 1
            is_tail = next_pc < len(instr) and instr[next_pc][0] == "RETURN_VALUE"
            frame_locals: dict[str, Any] = {}
            for pname, pval in zip(params, args_vals):
                frame_locals[pname] = pval
            if is_tail:
                # Reuse current frame: replace top scope with callee's params
                if locals_env is None:
                    locals_env = [frame_locals]
                else:
                    # drop current frame (head) and prepend callee frame
                    outer_chain = locals_env[1:]
                    locals_env = [frame_locals] + outer_chain
                instr = fn_insts
                pc = 0
                n = len(instr)
                continue
            else:
                # Regular call: push current frame and create new
                call_stack.append((instr, pc + 1, locals_env))
                if locals_env is None:
                    locals_env = [frame_locals]
                else:
                    locals_env = [frame_locals] + locals_env
                instr = fn_insts
                pc = 0
                n = len(instr)
                continue
        pc += 1
    return "".join(outputs)


