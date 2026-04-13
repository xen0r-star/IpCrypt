import re
from utils import auth_service

def validate_password_policy(
    password: str,
    *,
    min_lowercase: int = 1,
    min_uppercase: int = 2,
    min_digits: int = 1,
    min_special: int = 1,
    min_length: int = 12,
    special_pattern: str = r"[^a-zA-Z0-9]",
) -> tuple[bool, str]:
    """Validate a password against a configurable policy.

    Returns:
        (True, "OK") when the password is valid.
        (False, "...") with a readable reason when invalid.
    """
    errors: list[str] = []

    if min_length > 0 and len(password) < min_length:
        errors.append(f"Minimum {min_length} caracteres")

    lowercase_count = sum(1 for char in password if char.islower())
    if lowercase_count < min_lowercase:
        errors.append(f"Minimum {min_lowercase} minuscule(s)")

    uppercase_count = sum(1 for char in password if char.isupper())
    if uppercase_count < min_uppercase:
        errors.append(f"Minimum {min_uppercase} majuscules")

    digit_count = sum(1 for char in password if char.isdigit())
    if digit_count < min_digits:
        errors.append(f"Minimum {min_digits} chiffre(s)")

    special_count = len(re.findall(special_pattern, password))
    if special_count < min_special:
        errors.append(f"Minimum {min_special} caractere(s) special(aux)")

    if errors:
        return False, "; ".join(errors)

    return True, "OK"