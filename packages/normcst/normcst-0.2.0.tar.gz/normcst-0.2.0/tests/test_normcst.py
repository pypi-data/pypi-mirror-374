import re
import typing as t

import libcst
import libcst._nodes.expression as l__n_expression

import normcst
import normcst.utils as n_utils


def add_line_prefix(string: str, prefix: str) -> str:
    return re.sub("^", prefix, string, flags=re.MULTILINE)


# a .. assign target
# d .. delete target
# e .. expression
# k .. key
# n .. as name
# p .. pattern

_v_ = [
    "name",
    "(e).attribute",
    "await (e)",
    "yield (e)",
    "(e) if (e) else (e)",
    "lambda _=(e): (e)",
    "(e)((e), *(e), _=(e), **(e))",
    "_((e))",
    "...",
    "0",
    "0.",
    "0j",
    "''",
    "'' ''",
    "f'{(e)}'",
    "f'{(e)!s}'",
    "f'{(e):0}'",
    "f'{(e)=}'",
    "(e), *(e)",
    "[(e), *(e)]",
    "{(e), *(e)}",
    "{(e): (e), **(e)}",
    "(e) for (a) in (e) if (e)",
    "[(e) for (a) in (e) if (e)]",
    "{(e) for (a) in (e) if (e)}",
    "{(e): (e) for (a) in (e) if (e)}",
    "(e)[(k), *(e)]",
    "~(e)",
    "-(e)",
    "not (e)",
    "+(e)",
    "(e) and (e)",
    "(e) or (e)",
    "(e) + (e)",
    "(e) & (e)",
    "(e) | (e)",
    "(e) ^ (e)",
    "(e) / (e)",
    "(e) // (e)",
    "(e) << (e)",
    "(e) @ (e)",
    "(e) % (e)",
    "(e) * (e)",
    "(e) ** (e)",
    "(e) >> (e)",
    "(e) - (e)",
    "(e) == (e)",
    "(e) > (e)",
    "(e) >= (e)",
    "(e) in (e)",
    "(e) is (e)",
    "(e) < (e)",
    "(e) <= (e)",
    "(e) != (e)",
    "(e) is not (e)",
    "(e) not in (e)",
    "_ := (e)",
]
_v_ = [n_utils.parse(f"({e})", libcst.BaseExpression) for e in _v_]
_EXPRS = t.cast(list[libcst.BaseExpression], _v_)

_INDEXES = [libcst.Index(value=e) for e in _EXPRS]
_KEYS = _INDEXES + [n_utils.parse("(e):(e):(e)", libcst.BaseSlice)]

_v_ = ["name", "(e).attribute", "(e)[(k), *(e)]", "(e), *(e)", "[(e), *(e)]"]
_ASSIGN_TARGETS = [n_utils.parse(f"({a})", libcst.BaseExpression) for a in _v_]

_v_ = ["name", "(e).attribute", "(e)[(k), *(e)]", "(e)", "[(e)]"]
_DEL_TARGETS = [n_utils.parse(f"({d})", libcst.BaseExpression) for d in _v_]

_v_ = ["name", "(name),", "[(name)]"]
_AS_NAMES = [n_utils.parse(f"({n})", libcst.BaseExpression) for n in _v_]

_v_ = [
    "0",
    "None",
    "((p),)",
    "(p),",
    "[(p)]",
    "{0: (p)}",
    "C((p), p=(p))",
    "(p) as name",
    "(p) | (p)",
]
_PATTERNS = [n_utils.parse(f"({p})", libcst.MatchPattern) for p in _v_]

_statements = [
    "_: (e) = (e)",
    "assert (e), (e)",
    "(a) = (e)",
    "del (d)",
    "(e)",
    "raise (e) from (e)",
    "return (e)",
    "@(e)\nclass _[_: (e)=(e)]((e), *(e), _=(e), **(e)):\n pass",
    "for (a) in (e):\n pass",
    "@(e)\ndef _[_: (e)=(e)](_: (e)=(e)) -> (e):\n pass",
    "if (e):\n pass",
    "try:\n pass\nexcept (e):\n pass",
    "while (e):\n pass",
    "with (e) as (n):\n pass",
    "match (e):\n case (p) if (e):\n  pass",
]
_STATEMENTS = [n_utils.parse(s, libcst.BaseStatement) for s in _statements]


def _get_case_statements():
    nodes = dict(
        a=_ASSIGN_TARGETS,
        d=_DEL_TARGETS,
        e=_EXPRS,
        k=_KEYS,
        n=_AS_NAMES,
        p=_PATTERNS,
        s=_STATEMENTS,
    )
    for name, _nodes in sorted(nodes.items()):
        print(f"{name}: {len(_nodes)}")

    e_statement = n_utils.parse("e", libcst.BaseStatement)
    k_statement = n_utils.parse("_[k]", libcst.BaseStatement)
    p_statement = n_utils.parse("match _:\n case p:\n  pass", libcst.BaseStatement)
    return [
        (
            statement.deep_replace(
                statement_node, node.deep_replace(old_node, new_node)
            )
            if statement_node is not None
            else node.deep_replace(old_node, new_node)
        )
        for statement, statement_node, _nodes in [
            (e_statement, _get_nodes(e_statement)["e"][0], _EXPRS),
            (k_statement, _get_nodes(k_statement)["k"][0], set(_KEYS) - set(_INDEXES)),
            (p_statement, _get_nodes(p_statement)["p"][0], _PATTERNS),
            (None, None, _STATEMENTS),
        ]
        for node in _nodes
        for name, old_nodes in _get_nodes(node).items()
        for new_node in nodes[name]
        for old_node in old_nodes
    ]


def _get_nodes(node: libcst.CSTNode) -> dict[str, list[libcst.Name]]:
    visitor = _NodesVisitor()
    node.visit(visitor)
    return visitor._nodes


class _NodesVisitor(libcst.CSTVisitor):
    def __init__(self):
        super().__init__()

        self._nodes = {}

    def visit_Name(self, node: libcst.Name) -> bool:
        if node.value in ("a", "d", "e", "n"):
            self._nodes.setdefault(node.value, []).append(node)

        return True

    def visit_Index(self, node: libcst.Index) -> bool:
        if isinstance(_value := node.value, libcst.Name) and _value.value == "k":
            self._nodes.setdefault("k", []).append(node)

        return True

    def visit_MatchAs(self, node: libcst.MatchAs) -> bool:
        if isinstance(_name := node.name, libcst.Name) and _name.value == "p":
            self._nodes.setdefault("p", []).append(node)

        return True


_CASE_STATEMENTS = _get_case_statements()
print(f"case_statements: {len(_CASE_STATEMENTS)}")


def test_ParenthesisTransformer():
    case_statements = {s: n_utils.to_string(s) for s in _CASE_STATEMENTS}

    _v_ = enumerate(sorted(case_statements.items(), key=lambda item: item[1]))
    for index, (case_statement, case_code) in _v_:
        case_statement = case_statement.visit(normcst.NoParenthesisTransformer())
        case_code = n_utils.to_string(case_statement)

        transformed_statement = case_statement.visit(normcst.ParenthesisTransformer())

        unchanged = None
        roundtriped = None
        minimal = None
        while True:
            _v_ = transformed_statement.visit(normcst.NoParenthesisTransformer())
            unchanged = _v_.deep_equals(case_statement)

            if not unchanged:
                break

            roundtriped = n_utils.roundtrips(transformed_statement)
            if not roundtriped:
                break

            visitor = _ParenthesisVisitor()
            transformed_statement.visit(visitor)
            for node in visitor._nodes:
                _v_ = node.with_changes(lpar=[], rpar=[])
                if n_utils.roundtrips(transformed_statement.deep_replace(node, _v_)):
                    minimal = node
                    break

            break

        if not (unchanged and roundtriped and minimal is None):
            transformed_code = n_utils.to_string(transformed_statement)
            print()
            print("case:")
            print(case_statement)
            print(f"index: {index}")
            print(f"case: {repr(case_code)}")
            print(add_line_prefix(case_code.strip(), "| "))
            print(f"transformed: {repr(transformed_code)}")
            print(add_line_prefix(transformed_code.strip(), "| "))
            print(f"unchanged: {unchanged}")
            print(f"roundtriped: {roundtriped}")
            print(f"minimal: {minimal}")
            raise Exception


def test_NoParenthesisTransformer():
    _v_ = """
(
    0,
    1,
) #
""".strip()
    for code, expected_code in [
        (
            """
(
    0,
    1,
)
""".strip(),
            "0, 1,",
        ),
        (
            """
( #
    0,
    1,
)
""".strip(),
            """
( #
    0, 1, )
""".strip(),
        ),
        (
            """
(
    0, #
    1,
)
""".strip(),
            """
( 0, #
    1, )
""".strip(),
        ),
        (
            """
(
    0,
    1, #
)
""".strip(),
            """
( 0, 1, #
)
""".strip(),
        ),
        (_v_, "0, 1, #"),
    ]:
        _v_ = n_utils.parse(code, libcst.BaseStatement)
        transformed_node = _v_.visit(normcst.NoParenthesisTransformer())

        assert (
            n_utils.to_string(t.cast(libcst.CSTNode, transformed_node)).strip()
            == expected_code
        ), dict(code=code, transformed=transformed_node, expected=expected_code)

    for case_statement in _CASE_STATEMENTS:
        transformed_node = case_statement.visit(normcst.NoParenthesisTransformer())
        visitor = _ParenthesisVisitor()
        transformed_node.visit(visitor)
        assert (
            len(visitor._nodes) == 0
            and n_utils.to_string(transformed_node).count("(") - visitor._count == 0
        ), dict(case=case_statement, transformed=transformed_node, nodes=visitor._nodes)


class _ParenthesisVisitor(libcst.CSTVisitor):
    def __init__(self):
        super().__init__()

        self._nodes = []
        self._dont = []
        self._count = 0

    def on_visit(self, node: libcst.CSTNode) -> bool:
        result = super().on_visit(node)

        if isinstance(node, l__n_expression._BaseParenthesizedNode):
            parens = len(node.lpar)
            if isinstance(node, libcst.MatchTuple):
                self._count += parens

            elif parens != 0:
                if node in self._dont:
                    self._dont.remove(node)
                    self._count += parens

                else:
                    self._nodes.append(node)

        elif isinstance(getattr(node, "lpar", None), libcst.LeftParen):
            self._count += 1

        return result

    def visit_FormattedStringExpression(
        self, node: libcst.FormattedStringExpression
    ) -> bool:
        _v_ = isinstance(_expression := node.expression, libcst.GeneratorExp)
        if _v_ and len(_expression.lpar) != 0:
            self._dont.append(node.expression)

        return True

    def _visit_parens(
        self, node: t.Union[libcst.Call, libcst.FunctionDef, libcst.MatchClass]
    ) -> bool:
        self._count += 1
        return True

    visit_Call = _visit_parens
    visit_MatchClass = _visit_parens
    visit_FunctionDef = _visit_parens
