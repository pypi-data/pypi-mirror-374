import re
import typing as t

import black


def format(code: str, mode: t.Optional[black.Mode] = None) -> str:
    if mode is None:
        mode = black.Mode()

    match = re.search(r"^(?P<space>[ ]*)[^\s#]", code, flags=re.MULTILINE)
    if match is None:
        return code

    levels, remaining = divmod(len(match.group("space")), 4)
    if remaining != 0:
        return code

    parts = ["pass\n"]
    for level in range(levels):
        _indentation = " " * (level * 4)
        parts.append(f"{_indentation}if _:\n{_indentation}    pass\n")

    parts.append(code)
    code = black.format_str("".join(parts), mode=mode).rstrip()
    return "\n".join(code.split("\n")[1 + levels * 2 :])
