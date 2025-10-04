from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field


SixDigits = Annotated[str, Field(pattern=r"^\d{6}$")]


class BookCreate(BaseModel):
    serial_number: SixDigits = Field(..., examples=["123456"])
    title: str = Field(..., max_length=255)
    author: str = Field(..., max_length=255)


class BookOut(BaseModel):
    id: str
    serial_number: str
    title: str
    author: str
    is_borrowed: bool
    borrowed_at: Optional[datetime] = None
    borrowed_by: Optional[SixDigits] = None


class BorrowRequest(BaseModel):
    borrower_card: SixDigits = Field(..., examples=["654321"])


class SetStatusRequest(BaseModel):
    is_borrowed: bool
    borrower_card: Optional[SixDigits] = None
    when: Optional[datetime] = None
