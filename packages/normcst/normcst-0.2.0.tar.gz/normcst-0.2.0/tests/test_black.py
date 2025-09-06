import black

import normcst.black as n_black


def test_format():
    for code, expected_code in [
        (  # trivial
            """
None
""",
            """
None
""",
        ),
        (  # pass if just comments
            """
 # comment 1
 # comment 2
""",
            """
 # comment 1
 # comment 2
""",
        ),
        (  # pass if unexpected indentation
            """
 remaining
""",
            """
 remaining
""",
        ),
        (  # one level of indentation
            """
    level+1
""",
            """
    level + 1
""",
        ),
        (  # two levels of indentation
            """
        level+2
""",
            """
        level + 2
""",
        ),
        (  # comment on higher level
            """
        # level 2 comment
    level+1
""",
            """
    # level 2 comment
    level + 1
""",
        ),
        (  # comment on lower level
            """
    # level 1 comment
        level+2
""",
            """
        # level 1 comment
        level + 2
""",
        ),
        (  # two different levels
            """
        level+2
    level+1
""",
            """
        level + 2
    level + 1
""",
        ),
        (  # simple string
            """
''
""",
            """
""
""",
        ),
        (  # indented simple string
            """
    ''
""",
            """
    ""
""",
        ),
    ]:
        code = code[1:-1]
        expected_code = expected_code[1:-1]
        assert n_black.format(code) == expected_code

    # mode
    assert n_black.format("''", mode=black.Mode(string_normalization=False)) == "''"
