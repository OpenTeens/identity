"""Utility generating random datas."""

import random
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
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))
