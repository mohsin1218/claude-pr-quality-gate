def add(a: int, b: int) -> int:
    """Return the sum of two integers."""
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("Both arguments must be integers")
    return a + b
