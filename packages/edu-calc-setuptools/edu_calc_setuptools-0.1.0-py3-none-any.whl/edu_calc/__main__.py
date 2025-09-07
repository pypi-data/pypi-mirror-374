from __future__ import annotations
import argparse
from .core import eval_expr
def main() -> None:
    p = argparse.ArgumentParser(prog="calc", description="Evaluate simple math expressions safely.")
    p.add_argument("expression", help='Expression, e.g. "2 + 3*5"')
    p.add_argument("-r", "--round", type=int, default=None, dest="round_digits", help="Round result to N digits")
    args = p.parse_args()
    try:
        result = eval_expr(args.expression)
        if args.round_digits is not None: result = round(result, args.round_digits)
        print(result)
    except Exception as e:
        p.error(str(e))
if __name__ == "__main__": main()
