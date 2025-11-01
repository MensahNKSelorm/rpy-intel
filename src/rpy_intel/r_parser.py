from typing import List, Any
from .ir import Assign, Call, Import
from .mappings import R_TO_PY_FUNCS, LIBRARY_MAP


def parse_r_to_ir(code: str) -> List[Any]:
    """Parse a tiny subset of R syntax into an intermediate representation."""
    ir_nodes: List[Any] = []

    for line in code.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue

        # --- Handle library() calls ---
        if s.startswith("library(") and s.endswith(")"):
            pkg = s[len("library(") : -1].strip()
            mapped = LIBRARY_MAP.get(pkg, pkg)
            if mapped:
                ir_nodes.append(Import(module=mapped))
            continue

        # --- Handle assignments (<-) ---
        if "<-" in s:
            left, right = [x.strip() for x in s.split("<-", 1)]
            right = translate_r_expr(right)
            ir_nodes.append(Assign(target=left, expr=right))
            continue

        # --- Handle bare function calls ---
        if "(" in s and s.endswith(")"):
            ir_nodes.append(Call(func="unknown", args=[translate_r_expr(s)], kwargs={}))
            continue

    return ir_nodes


def translate_r_expr(expr: str) -> str:
    """Translate simple R expressions to equivalent Python expressions."""
    expr = expr.strip()

    # Convert c(...) → [...]
    if expr.startswith("c(") and expr.endswith(")"):
        inner = expr[2:-1]
        return f"[{inner}]"

    # Replace df$a → df["a"]
    if "$" in expr:
        parts = expr.split("$")
        return f'{parts[0]}["{parts[1]}"]'

    # Replace known function names
    for r_name, py_name in R_TO_PY_FUNCS.items():
        if expr.startswith(f"{r_name}("):
            expr = expr.replace(r_name, py_name, 1)

    # Handle nested calls like data.frame(a=c(...))
    if "c(" in expr:
        expr = expr.replace("c(", "[").replace(")", "]", 1)

    return expr
