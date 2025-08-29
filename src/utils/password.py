from bcrypt import gensalt, hashpw


def hash_password(password: str) -> str:
    return hashpw(password.encode(), gensalt()).decode()
