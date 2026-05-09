"""
Authentication helpers for B1 LMS
Password hashing and verification

Hashing Algorithm:
- Uses werkzeug.security (built on top of hashlib)
- Default method: pbkdf2:sha256
- PBKDF2 (Password-Based Key Derivation Function 2)
- SHA-256 hash function
- 260,000 iterations (werkzeug default for strong security)
- Includes salt automatically (random per password)
- Format: method$salt$hash

Security Features:
- Salted hashing (prevents rainbow table attacks)
- Slow hashing function (prevents brute force)
- Industry standard (NIST recommended)
"""

from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password):
    """
    Hash a password for storing

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return generate_password_hash(password)


def verify_password(password_hash, password):
    """
    Verify a password against its hash

    Args:
        password_hash: Hashed password from database
        password: Plain text password to verify

    Returns:
        True if password matches, False otherwise
    """
    return check_password_hash(password_hash, password)
