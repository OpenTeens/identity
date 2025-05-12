"""Utility generating random datas."""

import secrets
import string


def random_str(length: int) -> str:
    """Generate a random string of specified length.

    This function generates a random string containing
    uppercase and lowercase letters as well as digits.

    Args:
        length (int): The length of the random string to be generated.

    Returns:
        str: A randomly generated string of the specified length.

    """
    return "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(length)
    )
