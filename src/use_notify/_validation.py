def is_int_like(value) -> bool:
    """Return True for int values, excluding bool."""
    return isinstance(value, int) and not isinstance(value, bool)


def is_number_like(value) -> bool:
    """Return True for int/float values, excluding bool."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)
