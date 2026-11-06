import random
import string


def generate_component_id() -> str:
    """Generate a unique component ID."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=10))  # noqa: S311  # nosec B311
