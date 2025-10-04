import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.models import Book


@dataclass(frozen=True)
class BookDTO:
    id: uuid.UUID
    serial_number: str
    title: str
    author: str
    is_borrowed: bool
    borrowed_at: Optional[datetime]
    borrowed_by: Optional[str]

    @classmethod
    def from_model(cls, b: Book) -> "BookDTO":
        return cls(
            id=b.id,
            serial_number=b.serial_number,
            title=b.title,
            author=b.author,
            is_borrowed=b.is_borrowed,
            borrowed_at=b.borrowed_at,
            borrowed_by=b.borrowed_by,
        )
