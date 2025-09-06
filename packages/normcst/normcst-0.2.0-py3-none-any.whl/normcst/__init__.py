import typing as t

import libcst
import libcst._nodes.expression as l__n_expression

import normcst.utils as n_utils


class ParenthesisTransformer(libcst.CSTTransformer):
    _v_ = libcst.MatrixMultiply
    _v_ = [
        [libcst.Subscript, libcst.Call, libcst.Attribute],
        [libcst.Await],
        [libcst.Power],
        [libcst.Plus, libcst.Minus, libcst.BitInvert],
        [libcst.Multiply, _v_, libcst.Divide, libcst.FloorDivide, libcst.Modulo],
        [libcst.Add, libcst.Subtract],
        [libcst.LeftShift, libcst.RightShift],
        [libcst.BitAnd],
        [libcst.BitXor],
        [libcst.BitOr],
        [
            libcst.In,
            libcst.NotIn,
            libcst.Is,
            libcst.IsNot,
            libcst.LessThan,
            libcst.LessThanEqual,
            libcst.GreaterThan,
            libcst.GreaterThanEqual,
            libcst.NotEqual,
            libcst.Equal,
        ],
        [libcst.Not],
        [libcst.And],
        [libcst.Or],
        [libcst.IfExp],
        [libcst.Lambda],
        [libcst.Tuple],
    ]
    _v_ = {type: index for index, types in enumerate(_v_) for type in types}
    _PRECEDENCES: dict[type, int] = _v_

    @classmethod
    def get_precedence(cls, node: libcst.CSTNode) -> t.Optional[int]:
        _v_ = (libcst.BinaryOperation, libcst.BooleanOperation, libcst.UnaryOperation)
        if isinstance(node, _v_):
            node = node.operator

        elif isinstance(node, libcst.Comparison):
            _v_ = (
                _precedence
                for comparison in node.comparisons
                if (_precedence := cls._PRECEDENCES.get(type(comparison.operator)))
                is not None
            )
            return min(_v_, default=None)

        return cls._PRECEDENCES.get(type(node))

    def __init__(self):
        super().__init__()

        self._do = []
        self._dont = []

    def on_leave(
        self, original_node: libcst.CSTNode, updated_node: libcst.CSTNode
    ) -> libcst.CSTNode:
        if original_node in self._do:
            self._do.remove(original_node)
            if original_node in self._dont:
                self._dont.remove(original_node)

            else:
                _v_ = t.cast(n_utils._ParenthesizedNode, updated_node)
                updated_node = n_utils.add_parens(_v_, first=True)

        return updated_node

    def _visit_outside(
        self, node: t.Union[libcst.AnnAssign, libcst.Expr, libcst.Assign]
    ) -> bool:
        if isinstance(node.value, (libcst.Tuple, libcst.Yield)):
            self._dont.append(node.value)

        return True

    visit_AnnAssign = _visit_outside

    def visit_Arg(self, node: libcst.Arg) -> bool:
        _v_ = node.keyword is None and node.star == ""
        if _v_ and isinstance(node.value, libcst.NamedExpr):
            self._dont.append(node.value)

        return True

    def visit_Assign(self, node: libcst.Assign) -> bool:
        for target in node.targets:
            if isinstance(target.target, libcst.Tuple):
                self._dont.append(target.target)

        return self._visit_outside(node)

    def visit_Attribute(self, node: libcst.Attribute) -> bool:
        _v_ = (_precedence := self.get_precedence(node.value)) is not None
        _v_ = _v_ and t.cast(int, self.get_precedence(node)) < _precedence
        if _v_ or isinstance(node.value, libcst.Integer):
            self._do.append(node.value)

        return True

    def visit_Await(self, node: libcst.Await) -> bool:
        _v_ = (_precedence := self.get_precedence(node.expression)) is not None
        _v_ = _v_ and t.cast(int, self.get_precedence(node)) < _precedence
        if _v_ or isinstance(node.expression, libcst.Await):
            self._do.append(node.expression)

        return True

    def visit_BinaryOperation(self, node: libcst.BinaryOperation) -> bool:
        is_power = isinstance(node.operator, libcst.Power)
        if (
            (_precedence := self.get_precedence(node.left)) is not None
            and t.cast(int, self.get_precedence(node)) < _precedence
            or is_power
            and isinstance(_left := node.left, libcst.BinaryOperation)
            and isinstance(_left.operator, libcst.Power)
        ):
            self._do.append(node.left)

        _v_ = (_precedence := self.get_precedence(node.right)) is not None
        if _v_ and t.cast(int, self.get_precedence(node)) <= _precedence:
            self._do.append(node.right)

        if is_power and (
            isinstance(_right := node.right, libcst.UnaryOperation)
            and isinstance(
                _right.operator, (libcst.BitInvert, libcst.Minus, libcst.Plus)
            )
            or isinstance(_right := node.right, libcst.BinaryOperation)
            and isinstance(_right.operator, libcst.Power)
        ):
            self._dont.append(_right)

        return True

    def visit_BooleanOperation(self, node: libcst.BooleanOperation) -> bool:
        _v_ = (_precedence := self.get_precedence(node.left)) is not None
        if _v_ and t.cast(int, self.get_precedence(node)) < _precedence:
            self._do.append(node.left)

        _v_ = (_precedence := self.get_precedence(node.right)) is not None
        if _v_ and t.cast(int, self.get_precedence(node)) <= _precedence:
            self._do.append(node.right)

        return True

    def visit_Call(self, node: libcst.Call) -> bool:
        _v_ = (_precedence := self.get_precedence(node.func)) is not None
        if _v_ and t.cast(int, self.get_precedence(node)) < _precedence:
            self._do.append(node.func)

        if len(node.args) == 1:
            (arg,) = node.args

            _v_ = arg.keyword is None and arg.star == ""
            if _v_ and isinstance(arg.value, libcst.GeneratorExp):
                self._dont.append(arg.value)

        return True

    def visit_Comparison(self, node: libcst.Comparison) -> bool:
        nodes = [node.left]
        nodes.extend(comparison.comparator for comparison in node.comparisons)
        operators: t.List[t.Optional[libcst.BaseCompOp]] = [None]
        operators.extend(comparison.operator for comparison in node.comparisons)
        operators.append(None)

        _v_ = zip(nodes, operators, operators[1:])
        for sub_node, left_operator, right_operator in _v_:
            sub_precedence = self.get_precedence(sub_node)
            if sub_precedence is None:
                continue

            if (
                left_operator is not None
                and (_precedence := self.get_precedence(left_operator)) is not None
                and _precedence <= sub_precedence
            ) or (
                right_operator is not None
                and (_precedence := self.get_precedence(right_operator)) is not None
                and _precedence <= sub_precedence
            ):
                self._do.append(sub_node)

        return True

    def visit_CompFor(self, node: libcst.CompFor) -> bool:
        if isinstance(node.target, libcst.Tuple):
            self._dont.append(node.target)

        if isinstance(node.iter, (libcst.IfExp, libcst.Lambda)):
            self._do.append(node.iter)

        for comp_if in node.ifs:
            if isinstance(comp_if.test, (libcst.IfExp, libcst.Lambda)):
                self._do.append(comp_if.test)

        return True

    def visit_Decorator(self, node: libcst.Decorator) -> bool:
        if isinstance(node.decorator, libcst.NamedExpr):
            self._dont.append(node.decorator)

        return True

    visit_Expr = _visit_outside

    def visit_For(self, node: libcst.For) -> bool:
        if isinstance(node.target, libcst.Tuple):
            self._dont.append(node.target)

        if isinstance(node.iter, libcst.Tuple):
            self._dont.append(node.iter)

        return True

    def visit_FormattedStringExpression(
        self, node: libcst.FormattedStringExpression
    ) -> bool:
        _v_ = (libcst.Dict, libcst.DictComp, libcst.Lambda, libcst.Set, libcst.SetComp)
        if isinstance(node.expression, _v_):
            self._do.append(node.expression)

        elif isinstance(node.expression, (libcst.Tuple, libcst.Yield)):
            self._dont.append(node.expression)

        return True

    def visit_GeneratorExp(self, node: libcst.GeneratorExp) -> bool:
        self._do.append(node)
        return self._visit_comprehension(node)

    def _visit_test(self, node: t.Union[libcst.If, libcst.While]) -> bool:
        if isinstance(node.test, libcst.NamedExpr):
            self._dont.append(node.test)

        return True

    visit_If = _visit_test

    def visit_IfExp(self, node: libcst.IfExp) -> bool:
        _v_ = (_precedence := self.get_precedence(node.body)) is not None
        if _v_ and t.cast(int, self.get_precedence(node)) <= _precedence:
            self._do.append(node.body)

        _v_ = (_precedence := self.get_precedence(node.test)) is not None
        if _v_ and t.cast(int, self.get_precedence(node)) <= _precedence:
            self._do.append(node.test)

        return True

    def visit_Index(self, node: libcst.Index) -> bool:
        if node.star is None and isinstance(node.value, libcst.NamedExpr):
            self._dont.append(node.value)

        return True

    def _visit_collection(
        self, node: t.Union[libcst.Tuple, libcst.List, libcst.Set]
    ) -> bool:
        for element in node.elements:
            _v_ = isinstance(element, libcst.Element)
            _v_ = _v_ and isinstance(element.value, libcst.NamedExpr)
            if _v_ and node not in self._dont:
                self._dont.append(element.value)

        return True

    visit_List = _visit_collection

    def _visit_comprehension(self, node: libcst.BaseSimpleComp) -> bool:
        if isinstance(node.elt, libcst.NamedExpr):
            self._dont.append(node.elt)

        return True

    visit_ListComp = _visit_comprehension

    def visit_Match(self, node: libcst.Match) -> bool:
        if isinstance(node.subject, (libcst.NamedExpr, libcst.Tuple)):
            self._dont.append(node.subject)

        return True

    def visit_MatchAs(self, node: libcst.MatchAs) -> bool:
        _v_ = isinstance(_pattern := node.pattern, libcst.MatchAs)
        if _v_ and _pattern.pattern is not None:
            self._do.append(node.pattern)

        return True

    def visit_MatchCase(self, node: libcst.MatchCase) -> bool:
        if isinstance(node.guard, libcst.NamedExpr):
            self._dont.append(node.guard)

        return True

    def visit_MatchOr(self, node: libcst.MatchOr) -> bool:
        for element in node.patterns:
            _v_ = isinstance(_pattern := element.pattern, libcst.MatchAs)
            _v_ = _v_ and _pattern.pattern is not None
            if _v_ or isinstance(_pattern, libcst.MatchOr):
                self._do.append(_pattern)

        return True

    def visit_NamedExpr(self, node: libcst.NamedExpr) -> bool:
        self._do.append(node)
        return True

    def visit_Return(self, node: libcst.Return) -> bool:
        if isinstance(node.value, libcst.Tuple):
            self._dont.append(node.value)

        return True

    visit_Set = _visit_collection
    visit_SetComp = _visit_comprehension

    def visit_StarredDictElement(self, node: libcst.StarredDictElement) -> bool:
        _v_ = (libcst.BooleanOperation, libcst.Comparison, libcst.IfExp, libcst.Lambda)
        if (
            isinstance(node.value, _v_)
            or isinstance(_value := node.value, libcst.UnaryOperation)
            and isinstance(_value.operator, libcst.Not)
        ):
            self._do.append(node.value)

        return True

    def visit_StarredElement(self, node: libcst.StarredElement) -> bool:
        _v_ = (libcst.BooleanOperation, libcst.Comparison, libcst.IfExp, libcst.Lambda)
        if isinstance(node.value, _v_) or (
            isinstance(_value := node.value, libcst.UnaryOperation)
            and isinstance(_value.operator, libcst.Not)
        ):
            self._do.append(node.value)

        return True

    def visit_Subscript(self, node: libcst.Subscript) -> bool:
        _v_ = (_precedence := self.get_precedence(node.value)) is not None
        if _v_ and t.cast(int, self.get_precedence(node)) < _precedence:
            self._do.append(node.value)

        return True

    def visit_Tuple(self, node: libcst.Tuple) -> bool:
        self._do.append(node)
        return self._visit_collection(node)

    def visit_UnaryOperation(self, node: libcst.UnaryOperation) -> bool:
        _v_ = (_precedence := self.get_precedence(node.expression)) is not None
        if _v_ and t.cast(int, self.get_precedence(node)) < _precedence:
            self._do.append(node.expression)

        return True

    visit_While = _visit_test

    def visit_Yield(self, node: libcst.Yield) -> bool:
        if isinstance(node.value, libcst.Tuple):
            self._dont.append(node.value)

        self._do.append(node)
        return True


class NoParenthesisTransformer(libcst.CSTTransformer):
    def __init__(self):
        super().__init__()

        self._comment = False
        self._comment_stack = []

    def on_visit(self, node: libcst.CSTNode) -> bool:
        self._comment_stack.append(self._comment)
        self._comment = False
        return super().on_visit(node)

    def on_leave(
        self, original_node: libcst.CSTNode, updated_node: libcst.CSTNode
    ) -> libcst.CSTNode:
        _v_ = t.cast(libcst.CSTNode, super().on_leave(original_node, updated_node))
        updated_node = _v_

        self._comment = self._comment_stack.pop() or self._comment

        if (
            not self._comment
            and isinstance(updated_node, l__n_expression._BaseParenthesizedNode)
            and not isinstance(updated_node, (libcst.MatchValue, libcst.MatchSingleton))
        ):
            if isinstance(updated_node, libcst.MatchTuple):
                lpar = [libcst.LeftParen()]
                rpar = [libcst.RightParen()]

            else:
                lpar = []
                rpar = []

            updated_node = updated_node.with_changes(lpar=lpar, rpar=rpar)

        return updated_node

    def visit_Comment(self, node: libcst.Comment) -> bool:
        self._comment = True
        return True

    def leave_ParenthesizedWhitespace(
        self,
        original_node: libcst.ParenthesizedWhitespace,
        updated_node: libcst.ParenthesizedWhitespace,
    ) -> libcst.BaseParenthesizableWhitespace:
        if not self._comment:
            updated_node = libcst.SimpleWhitespace(value=" ")

        return updated_node
