from __future__ import annotations

from . import ast as AST


def optimize(program: AST.Program) -> AST.Program:
    """Apply simple AST optimizations in-place and return the program.

    Currently implements:
    - Constant folding for arithmetic Binary nodes when both sides are Number
    - Constant folding for Compare when both sides are Number
    """

    def fold(node: AST.Node) -> AST.Node:
        # Recurse into child nodes
        if isinstance(node, AST.Program):
            node.statements = [fold(s) for s in node.statements]
            return node
        if isinstance(node, AST.ExprStmt):
            node.expr = fold(node.expr)
            return node
        if isinstance(node, AST.Assignment):
            node.expr = fold(node.expr)
            return node
        if isinstance(node, AST.Print):
            if node.expr is not None:
                node.expr = fold(node.expr)
            return node
        if isinstance(node, AST.If):
            if node.cond is not None:
                node.cond = fold(node.cond)
            node.body = [fold(s) for s in (node.body or [])]
            if node.else_body is not None:
                node.else_body = [fold(s) for s in node.else_body]
            return node
        if isinstance(node, AST.While):
            node.cond = fold(node.cond)
            node.body = [fold(s) for s in node.body]
            return node
        if isinstance(node, AST.ForEach):
            node.iterable = fold(node.iterable)
            node.body = [fold(s) for s in node.body]
            return node
        if isinstance(node, AST.Repeat):
            node.count_expr = fold(node.count_expr)
            node.body = [fold(s) for s in node.body]
            return node
        if isinstance(node, AST.Call):
            node.args = [fold(a) for a in node.args]
            return node
        if isinstance(node, AST.MakeList):
            node.items = [fold(it) for it in node.items]
            return node
        if isinstance(node, AST.MakeMap):
            return node
        if isinstance(node, AST.Push):
            node.item = fold(node.item)
            node.target = fold(node.target)
            return node
        if isinstance(node, AST.Pop):
            node.target = fold(node.target)
            return node
        if isinstance(node, AST.GetKey):
            node.key = fold(node.key)
            node.target = fold(node.target)
            return node
        if isinstance(node, AST.SetKey):
            node.key = fold(node.key)
            node.value = fold(node.value)
            node.target = fold(node.target)
            return node
        if isinstance(node, AST.DeleteKey):
            node.key = fold(node.key)
            node.target = fold(node.target)
            return node
        if isinstance(node, AST.Length):
            node.target = fold(node.target)
            return node
        if isinstance(node, AST.BoolBinary):
            node.left = fold(node.left)
            node.right = fold(node.right)
            return node
        if isinstance(node, AST.NotOp):
            node.expr = fold(node.expr)
            return node
        if isinstance(node, AST.Compare):
            node.left = fold(node.left)
            node.right = fold(node.right)
            if isinstance(node.left, AST.Number) and isinstance(node.right, AST.Number):
                l = node.left.value
                r = node.right.value
                if node.op == ">":
                    return AST.Number(1.0 if l > r else 0.0)
                if node.op == "<":
                    return AST.Number(1.0 if l < r else 0.0)
                if node.op == "==":
                    return AST.Number(1.0 if l == r else 0.0)
                if node.op == "!=":
                    return AST.Number(1.0 if l != r else 0.0)
                if node.op == ">=":
                    return AST.Number(1.0 if l >= r else 0.0)
                if node.op == "<=":
                    return AST.Number(1.0 if l <= r else 0.0)
            return node
        if isinstance(node, AST.Binary):
            node.left = fold(node.left)
            node.right = fold(node.right)
            if isinstance(node.left, AST.Number) and isinstance(node.right, AST.Number):
                l = node.left.value
                r = node.right.value
                if node.op == "+":
                    return AST.Number(l + r)
                if node.op == "-":
                    return AST.Number(l - r)
                if node.op == "*":
                    return AST.Number(l * r)
                if node.op == "/":
                    return AST.Number(float(l) / float(r))
            return node
        return node

    return fold(program)


