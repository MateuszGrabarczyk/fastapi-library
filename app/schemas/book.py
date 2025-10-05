from datetime import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, Field, ConfigDict

SixDigits = Annotated[str, Field(pattern=r"^\d{6}$", description="Exactly 6 digits")]


class BookCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "serial_number": "123456",
                    "title": "Clean Architecture",
                    "author": "Robert C. Martin",
                }
            ]
        }
    )
    serial_number: SixDigits = Field(..., examples=["123456"])
    title: str = Field(..., max_length=255)
    author: str = Field(..., max_length=255)


class BookOut(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "a1b2c3d4",
                    "serial_number": "123456",
                    "title": "Clean Architecture",
                    "author": "Robert C. Martin",
                    "is_borrowed": True,
                    "borrowed_at": "2025-10-05T12:34:56Z",
                    "borrowed_by": "654321",
                }
            ]
        }
    )
    id: str
    serial_number: str
    title: str
    author: str
    is_borrowed: bool
    borrowed_at: Optional[datetime] = None
    borrowed_by: Optional[SixDigits] = None


class BorrowRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"borrower_card": "654321"},
            ]
        }
    )
    borrower_card: SixDigits = Field(..., examples=["654321"])


class SetStatusRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "is_borrowed": True,
                    "borrower_card": "654321",
                    "when": "2025-10-05T12:34:56Z",
                },
                {
                    "is_borrowed": False,
                    "when": "2025-10-05T12:34:56Z",
                },
            ]
        }
    )
    is_borrowed: bool
    borrower_card: Optional[SixDigits] = None
    when: Optional[datetime] = None
