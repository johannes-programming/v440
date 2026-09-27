def magand(x: int, y: int, /) -> int:
    if x == y:
        return x
    if x + y <= 0:
        return max(x, y)
    raise ValueError
