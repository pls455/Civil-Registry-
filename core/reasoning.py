"""Deterministic local reasoning helpers. No network or model API required."""
import ast, operator as op, re

_BIN = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.Pow: op.pow,
        ast.Mod: op.mod, ast.FloorDiv: op.floordiv}
_UN = {ast.UAdd: op.pos, ast.USub: op.neg}

def safe_math(expr: str):
    expr = expr.replace("×", "*").replace("÷", "/").replace("^", "**")
    if not re.fullmatch(r"[0-9\s+\-*/().%^]+", expr):
        return None
    try:
        return _eval(ast.parse(expr, mode="eval").body)
    except Exception:
        return None

def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN:
        return _BIN[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UN:
        return _UN[type(node.op)](_eval(node.operand))
    raise ValueError("unsafe expression")

def explain(doc):
    title = doc.get("title", "الموضوع")
    content = doc.get("content", "")
    return f"شرح مبسط عن {title}:\n\n{content}" if content else f"لا توجد مادة كافية عن {title} في قاعدة المعرفة المحلية."
