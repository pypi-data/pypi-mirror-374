from __future__ import annotations
import ast
import operator as _op

_ops = {
    ast.Add: _op.add, ast.Sub: _op.sub, ast.Mult: _op.mul, ast.Div: _op.truediv,
    ast.Pow: _op.pow, ast.USub: _op.neg, ast.UAdd: _op.pos, ast.Mod: _op.mod,
}

def add(a: float, b: float) -> float: return a + b
def sub(a: float, b: float) -> float: return a - b
def mul(a: float, b: float) -> float: return a * b
def div(a: float, b: float) -> float:
    if b == 0: raise ZeroDivisionError("division by zero")
    return a / b

def _eval(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)): return node.value
        raise TypeError("Only numbers are allowed")
    if isinstance(node, ast.BinOp):
        op_type = type(node.op); 
        if op_type not in _ops: raise TypeError(f"Operator {op_type.__name__} not allowed")
        return _ops[op_type](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _ops: raise TypeError(f"Operator {op_type.__name__} not allowed")
        return _ops[op_type](_eval(node.operand))
    if isinstance(node, ast.Expr): return _eval(node.value)
    raise TypeError(f"Unsupported expression node: {type(node).__name__}")

def eval_expr(expr: str) -> float:
    tree = ast.parse(expr, mode="eval")
    for n in ast.walk(tree):
        if isinstance(n, (ast.Call, ast.Name, ast.Attribute, ast.Subscript)):
            raise TypeError("Names, calls, attributes, and indexing are not allowed")
    return float(_eval(tree.body))
