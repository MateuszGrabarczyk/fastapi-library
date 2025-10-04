from typing import List, Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Book
from app.dataclasses.book_dto import BookDTO
from app.exceptions import (
    BookAlreadyBorrowed,
    BookNotBorrowed,
    BookNotFound,
    DuplicateSerialNumber,
    InvalidCardNumber,
    InvalidSerialNumber,
)
from app.utils import validate_card, validate_serial, utcnow


class BookService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_serial(
        self, serial_number: str, *, for_update: bool = False
    ) -> Book:
        try:
            serial = validate_serial(serial_number)
        except ValueError as e:
            raise InvalidSerialNumber(str(e)) from e
        stmt = select(Book).where(Book.serial_number == serial)
        if for_update:
            stmt = stmt.with_for_update()
        result = await self.session.execute(stmt)
        book = result.scalar_one_or_none()
        if not book:
            raise BookNotFound(f"Book with serial {serial} not found")
        return book

    async def list_books(
        self,
        *,
        is_borrowed: Optional[bool] = None,
        borrower_card: Optional[str] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> List[BookDTO]:
        stmt = select(Book)
        if is_borrowed is not None:
            stmt = stmt.where(Book.is_borrowed == is_borrowed)
        if borrower_card is not None:
            try:
                card = validate_card(borrower_card)
            except ValueError as e:
                raise InvalidCardNumber(str(e)) from e
            stmt = stmt.where(Book.borrowed_by == card)
        stmt = stmt.offset(max(offset, 0)).limit(max(1, min(limit, 500)))
        result = await self.session.execute(stmt)
        rows = result.scalars().all()
        return [BookDTO.from_model(b) for b in rows]

    async def add_book(self, *, serial_number: str, title: str, author: str) -> BookDTO:
        try:
            serial = validate_serial(serial_number)
        except ValueError as e:
            raise InvalidSerialNumber(str(e)) from e
        book = Book(serial_number=serial, title=title.strip(), author=author.strip())
        self.session.add(book)
        try:
            await self.session.flush()
        except IntegrityError as e:
            raise DuplicateSerialNumber(
                f"Book with serial {serial} already exists"
            ) from e
        return BookDTO.from_model(book)

    async def delete_book(
        self, *, serial_number: str, allow_if_borrowed: bool = False
    ) -> None:
        book = await self.get_by_serial(serial_number, for_update=True)
        if book.is_borrowed and not allow_if_borrowed:
            raise BookAlreadyBorrowed(
                f"Book {book.serial_number} is currently borrowed by {book.borrowed_by}"
            )
        await self.session.delete(book)

    async def borrow_book(self, *, serial_number: str, borrower_card: str) -> BookDTO:
        try:
            card = validate_card(borrower_card)
        except ValueError as e:
            raise InvalidCardNumber(str(e)) from e
        book = await self.get_by_serial(serial_number, for_update=True)
        if book.is_borrowed:
            raise BookAlreadyBorrowed(
                f"Book {book.serial_number} already borrowed by {book.borrowed_by}"
            )
        book.is_borrowed = True
        book.borrowed_by = card
        book.borrowed_at = utcnow()
        self.session.add(book)
        return BookDTO.from_model(book)

    async def return_book(self, *, serial_number: str) -> BookDTO:
        book = await self.get_by_serial(serial_number, for_update=True)
        if not book.is_borrowed:
            raise BookNotBorrowed(
                f"Book {book.serial_number} is not currently borrowed"
            )
        book.is_borrowed = False
        book.borrowed_by = None
        book.borrowed_at = None
        self.session.add(book)
        return BookDTO.from_model(book)

    async def set_status(
        self,
        *,
        serial_number: str,
        is_borrowed: bool,
        borrower_card: Optional[str] = None,
        when: Optional[datetime] = None,
    ) -> BookDTO:
        book = await self.get_by_serial(serial_number, for_update=True)
        if is_borrowed:
            try:
                card = validate_card(borrower_card or "")
            except ValueError as e:
                raise InvalidCardNumber(str(e)) from e
            book.is_borrowed = True
            book.borrowed_by = card
            book.borrowed_at = when or utcnow()
        else:
            book.is_borrowed = False
            book.borrowed_by = None
            book.borrowed_at = None
        self.session.add(book)
        return BookDTO.from_model(book)
