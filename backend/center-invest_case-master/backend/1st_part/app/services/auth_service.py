from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repos import user_repo


class AuthService:
    @staticmethod
    def register(db: Session, email: str, password: str) -> User:
        if user_repo.get_by_email(db, email):
            raise ValueError("User already exists")
        password_hash = hash_password(password)
        return user_repo.create(db, email, password_hash)

    @staticmethod
    def login(db: Session, email: str, password: str) -> str:
        user = user_repo.get_by_email(db, email)
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")
        return create_access_token(subject=user.email)
