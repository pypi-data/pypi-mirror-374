from wcmatch import fnmatch as wcmatch


def fnmatch(string, pattern) -> bool:
    return wcmatch.fnmatch(string, pattern, flags=wcmatch.B| wcmatch.N| wcmatch.S)
