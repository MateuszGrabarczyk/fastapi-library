import uuid
from typing import List

from sqlalchemy import String, CheckConstraint, CHAR
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    card_number: Mapped[str] = mapped_column(
        CHAR(6), unique=True, nullable=False, index=True
    )

    borrowed_books: Mapped[List["Book"]] = relationship(  # type: ignore
        "Book",
        back_populates="borrower",
        primaryjoin="User.card_number == Book.borrowed_by",
        foreign_keys="Book.borrowed_by",
    )

    __table_args__ = (
        CheckConstraint("card_number ~ '^[0-9]{6}$'", name="ck_users_card_six_digits"),
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} card={self.card_number} name={self.first_name} {self.last_name}>"
