# _NormCST_

is a Python package providing tools for [_LibCST_](https://github.com/Instagram/LibCST) related to normalization.
The main contributions are `normcst.ParenthesisTransformer`, a `libcst.CSTTransformer` which adds necessary parentheses, and `normcst.NoParenthesisTransformer`, a `libcst.CSTTransformer` which removes all parenthesis.
Secondary contributions are found in `normcst.black` and `normcst.utils` like `roundtrips` which verifies whether or not the given node survives a roundtrip (`to_string` -> `parse` -> `deep_equals`).

## Quickstart

- Install using `pip`
  - e.g. `pipenv run python -m pip install normcst[all]`
- Import and use
  - e.g. `import normcst` and `node.visit(normcst.ParenthesisTransformer())`
- Optionally run tests
  - e.g. `pipenv run python -m pytest /path/to/normcst/tests`

## Personal remarks

**2025-09-05**

Almost 6 months ago I published this side project and mentioned it in [Issue 341](https://github.com/Instagram/LibCST/pull/458).
Nothing really changed except that time provides confidence; it didn't fail me ever since.
There hasn't been much interest in it either, or reason to complain.
Anyways, it's on PyPI now.
