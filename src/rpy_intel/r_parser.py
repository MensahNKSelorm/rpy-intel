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
    """Translate simple R expressions into equivalent Python expressions."""
    expr = expr.strip()

    # --- Handle R vector creation: c(...) -> [ ... ]
    if expr.startswith("c(") and expr.endswith(")"):
        inner = expr[2:-1].strip()
        return f"[{inner}]"

    # --- Handle $ operator: df$a -> df["a"]
    # Replace all instances of `$` properly
    while "$" in expr:
        before, after = expr.split("$", 1)
        # Stop at first invalid character
        var_name = ""
        for ch in after:
            if ch.isalnum() or ch == "_":
                var_name += ch
            else:
                break
        expr = expr.replace(f"${var_name}", f'["{var_name}"]')

    # --- Map known R functions (e.g. mean, read.csv)
    for r_name, py_name in R_TO_PY_FUNCS.items():
        expr = expr.replace(f"{r_name}(", f"{py_name}(")

    # --- Fix mismatched parentheses
    open_parens = expr.count("(")
    close_parens = expr.count(")")
    if close_parens > open_parens:
        expr = expr.rstrip(")")

    return expr
