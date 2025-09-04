
import re


class StrTool:

    _NON_WORD_PATTERN = re.compile(r"[^a-zA-Z0-9]")
    _SAFE_EVAL_SCOPE = {
        '__builtins__': None,
        'int': int,
        'str': str
    }

    @classmethod
    def to_py_field(cls, src_field: str):
        return cls._NON_WORD_PATTERN.sub("_", src_field)

    @classmethod
    def safe_eval(cls, expr: str):
        return str(eval(expr, cls._SAFE_EVAL_SCOPE))