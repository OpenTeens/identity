import random  # noqa: D104
import string


def random_str(length):  # noqa: D103
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))
