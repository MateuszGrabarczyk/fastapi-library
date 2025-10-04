from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.dataclasses.book_dto import BookDTO
from app.schemas.book import BookCreate, BookOut, BorrowRequest, SetStatusRequest
from app.services.books import BookService
from app.exceptions import (
    BookAlreadyBorrowed,
    BookNotBorrowed,
    BookNotFound,
    DuplicateSerialNumber,
    InvalidCardNumber,
    InvalidSerialNumber,
    UserNotFound,
)

router = APIRouter(prefix="/books", tags=["books"])


def dto_to_out(dto: BookDTO) -> BookOut:
    return BookOut(
        id=str(dto.id),
        serial_number=dto.serial_number,
        title=dto.title,
        author=dto.author,
        is_borrowed=dto.is_borrowed,
        borrowed_at=dto.borrowed_at,
        borrowed_by=dto.borrowed_by,
    )


@router.get("", response_model=List[BookOut])
async def list_books(
    is_borrowed: Optional[bool] = None,
    borrower_card: Optional[str] = None,
    offset: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    svc = BookService(db)
    try:
        items = await svc.list_books(
            is_borrowed=is_borrowed,
            borrower_card=borrower_card,
            offset=offset,
            limit=limit,
        )
        return [dto_to_out(x) for x in items]
    except InvalidCardNumber as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("", response_model=BookOut, status_code=status.HTTP_201_CREATED)
async def create_book(payload: BookCreate, db: AsyncSession = Depends(get_db)):
    svc = BookService(db)
    try:
        dto = await svc.add_book(
            serial_number=payload.serial_number,
            title=payload.title,
            author=payload.author,
        )
        return dto_to_out(dto)
    except InvalidSerialNumber as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DuplicateSerialNumber as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/{serial_number}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    serial_number: str,
    allow_if_borrowed: bool = False,
    db: AsyncSession = Depends(get_db),
):
    svc = BookService(db)
    try:
        await svc.delete_book(
            serial_number=serial_number, allow_if_borrowed=allow_if_borrowed
        )
        return
    except BookNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BookAlreadyBorrowed as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/{serial_number}/borrow", response_model=BookOut)
async def borrow_book(
    serial_number: str, body: BorrowRequest, db: AsyncSession = Depends(get_db)
):
    svc = BookService(db)
    try:
        dto = await svc.borrow_book(
            serial_number=serial_number, borrower_card=body.borrower_card
        )
        return dto_to_out(dto)
    except BookNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidCardNumber as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BookAlreadyBorrowed as e:
        raise HTTPException(status_code=409, detail=str(e))
    except UserNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{serial_number}/return", response_model=BookOut)
async def return_book(serial_number: str, db: AsyncSession = Depends(get_db)):
    svc = BookService(db)
    try:
        dto = await svc.return_book(serial_number=serial_number)
        return dto_to_out(dto)
    except BookNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BookNotBorrowed as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.patch("/{serial_number}/status", response_model=BookOut)
async def set_status(
    serial_number: str, body: SetStatusRequest, db: AsyncSession = Depends(get_db)
):
    if body.is_borrowed and not body.borrower_card:
        raise HTTPException(
            status_code=400, detail="borrower_card is required when is_borrowed is true"
        )
    svc = BookService(db)
    try:
        dto = await svc.set_status(
            serial_number=serial_number,
            is_borrowed=body.is_borrowed,
            borrower_card=body.borrower_card,
            when=body.when,
        )
        return dto_to_out(dto)
    except BookNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidCardNumber as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
