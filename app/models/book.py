import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, CheckConstraint, CHAR, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    serial_number = Column(CHAR(6), nullable=False, unique=True, index=True)

    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)

    is_borrowed = Column(Boolean, nullable=False, default=False)
    borrowed_at = Column(DateTime(timezone=True), nullable=True)

    borrowed_by = Column(
        CHAR(6),
        ForeignKey("users.card_number", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    borrower = relationship("User", back_populates="borrowed_books")

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        CheckConstraint(
            "serial_number ~ '^[0-9]{6}$'", name="ck_books_serial_six_digits"
        ),
        CheckConstraint(
            "(is_borrowed AND borrowed_at IS NOT NULL AND borrowed_by IS NOT NULL) "
            "OR (NOT is_borrowed AND borrowed_at IS NULL AND borrowed_by IS NULL)",
            name="ck_books_borrow_state_consistent",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Book id={self.id} serial={self.serial_number} "
            f"title={self.title!r} author={self.author!r} borrowed={self.is_borrowed}>"
        )
