import ast
from typing import List, Any
from .ir import Assign, Call, Import
from typing import Union


def emit_python(ir_nodes: List[Any]) -> str:
    """Turn intermediate nodes into real Python source code (works on Python 3.14+)."""
    module = ast.Module(body=[], type_ignores=[])
    body = module.body

    for node in ir_nodes:
        stmt: ast.stmt  # ✅ flexible type
        if isinstance(node, Import):
            stmt = ast.Import(names=[ast.alias(name=node.module, asname=node.alias)])
        elif isinstance(node, Assign):
            stmt = ast.Assign(
                targets=[ast.Name(id=node.target, ctx=ast.Store())],
                value=_emit_expr(node.expr),
            )
        elif isinstance(node, Call):
            stmt = ast.Expr(value=_emit_call(node))
        else:
            continue

        ast.fix_missing_locations(stmt)
        body.append(stmt)

    ast.fix_missing_locations(module)
    return ast.unparse(module)


def _emit_expr(expr):
    if isinstance(expr, Call):
        return _emit_call(expr)
    try:
        return ast.parse(expr, mode="eval").body
    except Exception:
        return ast.Name(id=str(expr), ctx=ast.Load())


def _emit_call(c: Call):
    func = _dotted_name(c.func)
    args = [ast.parse(a, mode="eval").body for a in c.args]
    return ast.Call(func=func, args=args, keywords=[])


def _dotted_name(name: str) -> ast.expr:
    parts = name.split(".")
    node: Union[ast.Name, ast.Attribute] = ast.Name(id=parts[0], ctx=ast.Load())
    for p in parts[1:]:
        node = ast.Attribute(value=node, attr=p, ctx=ast.Load())
    return node
