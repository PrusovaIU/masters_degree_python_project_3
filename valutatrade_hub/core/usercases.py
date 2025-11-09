from .models import User


def register(username: str, password: str) -> User:
    if not username:
        raise ValueError("Параметр \"username\" не может быть пустым")
    if not password:
        raise ValueError("Параметр \"password\" не может быть пустым")
    if len(password) < 4:
        raise ValueError(
            "Параметр \"password\" не может быть короче 4 символов"
        )

