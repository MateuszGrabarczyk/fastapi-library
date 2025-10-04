import uuid
from sqlalchemy import Column, String, CheckConstraint, CHAR
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    card_number = Column(CHAR(6), unique=True, nullable=False, index=True)

    borrowed_books = relationship("Book", back_populates="borrower")

    __table_args__ = (
        CheckConstraint("card_number ~ '^[0-9]{6}$'", name="ck_users_card_six_digits"),
    )

    def __repr__(self) -> str:
        return (
            f"<User id={self.id} card={self.card_number} "
            f"name={self.first_name} {self.last_name}>"
        )
