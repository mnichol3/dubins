from functools import wraps


def round_return(decimals=2):
    """Decorator to round the return value of a function.

    Parameters
    ----------
    ndigits: int, optional
        Number of digits to round to. Default is 2.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            def round_value(val):
                if isinstance(val, float):
                    return round(val, decimals)
                elif isinstance(val, int):
                    return val
                elif isinstance(val, tuple):
                    return tuple(round_value(x) for x in val)
                elif isinstance(val, list):
                    # Check if this is a list of tuples
                    if all(isinstance(item, tuple) for item in val):
                        return [round_value(item) for item in val]
                return val

            return round_value(result)
        return wrapper
    return decorator
