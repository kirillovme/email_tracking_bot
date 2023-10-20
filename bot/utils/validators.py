import re

EMAIL_REGEX = r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'


def validate_email(email: str) -> bool:
    """Валидатор почтового ящика."""
    return bool(re.match(EMAIL_REGEX, email))
