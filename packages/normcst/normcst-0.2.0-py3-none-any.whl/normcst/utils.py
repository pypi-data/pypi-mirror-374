import collections.abc as c_abc
import typing as t

import libcst


class _ParenthesizedNode(t.Protocol):
    lpar: c_abc.Sequence[libcst.LeftParen]
    rpar: c_abc.Sequence[libcst.RightParen]

    def with_changes(self, **kwargs) -> libcst.CSTNode: ...


def add_parens(node: _ParenthesizedNode, first: bool = False) -> libcst.CSTNode:
    if first and len(node.lpar) != 0:
        return t.cast(libcst.CSTNode, node)

    lpar = [libcst.LeftParen()]
    lpar.extend(node.lpar)
    rpar = list(node.rpar)
    rpar.append(libcst.RightParen())
    return node.with_changes(lpar=lpar, rpar=rpar)


def remove_parens(node: _ParenthesizedNode) -> libcst.CSTNode:
    return node.with_changes(lpar=node.lpar[1:], rpar=node.rpar[:-1])


_RoundtripNodeT = t.Union[
    libcst.BaseExpression, libcst.BaseStatement, libcst.BaseSlice, libcst.MatchPattern
]
_RoundtripTypeT = type[_RoundtripNodeT]


def parse(code: str, expect: _RoundtripTypeT) -> libcst.CSTNode:
    if issubclass(expect, libcst.BaseExpression):
        return remove_parens(libcst.parse_expression(f"({code})"))

    if issubclass(expect, libcst.BaseStatement):
        return libcst.parse_statement(code)

    if issubclass(expect, libcst.BaseSlice):
        _v_ = t.cast(libcst.Subscript, libcst.parse_expression(f"_[{code}]")).slice[0]
        return _v_.slice

    if issubclass(expect, libcst.MatchPattern):
        _v_ = libcst.parse_statement(f"match _:\n case {code}:\n  pass")
        return t.cast(libcst.Match, _v_).cases[0].pattern

    raise ValueError(expect)


def to_string(node: libcst.CSTNode, module=libcst.Module(body=[])) -> str:
    return module.code_for_node(node)


def roundtrips(node: _RoundtripNodeT, raise_: bool = False) -> bool:
    code = to_string(node)
    try:
        roundtrip_node = parse(code, type(node))

    except libcst.ParserSyntaxError as error:
        if raise_:
            raise RoundtripSyntaxError(code, error)

        return False

    if not roundtrip_node.deep_equals(node):
        if raise_:
            raise RoundtripChangedError(code, roundtrip_node)

        return False

    return True


class RoundtripSyntaxError(Exception):
    def __init__(self, code: str, error: libcst.ParserSyntaxError):
        super().__init__()

        self.code = code
        self.error = error


class RoundtripChangedError(Exception):
    def __init__(self, code: str, roundtrip_node: libcst.CSTNode):
        super().__init__()

        self.code = code
        self.roundtrip_node = roundtrip_node
