from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status
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
from app.api_docs.responses import (
    R400_INVALID_SERIAL,
    R400_INVALID_CARD,
    R400_INVALID_CARD_OR_SERIAL,
    R404_BOOK,
    R404_BOOK_OR_USER,
    R409_DUPLICATE_SERIAL,
    R409_ALREADY_BORROWED,
    R409_NOT_BORROWED,
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


@router.get(
    "",
    response_model=List[BookOut],
    summary="List books",
    description=(
        "Returns a paginated list of books. "
        "Optionally filter by **is_borrowed** and/or **borrower_card**. "
        "Results are ordered by `created_at` descending."
    ),
    responses={
        400: R400_INVALID_CARD,
    },
)
async def list_books(
    is_borrowed: Optional[bool] = Query(
        None,
        description="Filter by borrowing status",
        examples={"borrowed": {"value": True}, "available": {"value": False}},  # type: ignore
    ),
    borrower_card: Optional[str] = Query(
        None,
        description="Borrower card (6 digits) to filter by",
        examples={"by_user": {"value": "654321"}},  # type: ignore
    ),
    offset: int = Query(
        0, ge=0, le=1_000_000, description="Number of items to skip (pagination)"
    ),
    limit: int = Query(
        100, ge=1, le=500, description="Max number of items to return (1–500)"
    ),
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


@router.post(
    "",
    response_model=BookOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a book",
    description="Registers a new book by its **serial_number**, **title**, and **author**.",
    responses={
        400: R400_INVALID_SERIAL,
        409: R409_DUPLICATE_SERIAL,
    },
)
async def create_book(
    payload: BookCreate = Body(
        ...,
        description="Book data to create",
    ),
    db: AsyncSession = Depends(get_db),
):
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


@router.delete(
    "/{serial_number}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a book",
    description=(
        "Deletes the book by **serial_number**. "
        "If the book is currently borrowed, set **allow_if_borrowed=true** to force deletion."
    ),
    responses={
        400: R400_INVALID_SERIAL,
        404: R404_BOOK,
        409: R409_ALREADY_BORROWED,
    },
)
async def delete_book(
    serial_number: str = Path(
        ...,
        description="Book serial (6 digits)",
        examples={"ex": {"value": "123456"}},  # type: ignore
    ),
    allow_if_borrowed: bool = Query(
        False, description="Allow deletion even if the book is borrowed"
    ),
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
    except InvalidSerialNumber as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{serial_number}/borrow",
    response_model=BookOut,
    summary="Borrow a book",
    description="Marks the book as borrowed by the user with **borrower_card**.",
    responses={
        400: R400_INVALID_CARD_OR_SERIAL,
        404: R404_BOOK_OR_USER,
        409: R409_ALREADY_BORROWED,
    },
)
async def borrow_book(
    serial_number: str = Path(
        ...,
        description="Book serial (6 digits)",
        examples={"ex": {"value": "123456"}},  # type: ignore
    ),
    body: BorrowRequest = Body(
        ..., description="Borrower card of the user borrowing the book"
    ),
    db: AsyncSession = Depends(get_db),
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
    except InvalidSerialNumber as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{serial_number}/return",
    response_model=BookOut,
    summary="Return a book",
    description="Marks the book as returned (available).",
    responses={
        400: R400_INVALID_SERIAL,
        404: R404_BOOK,
        409: R409_NOT_BORROWED,
    },
)
async def return_book(
    serial_number: str = Path(
        ...,
        description="Book serial (6 digits)",
        examples={"ex": {"value": "123456"}},  # type: ignore
    ),
    db: AsyncSession = Depends(get_db),
):
    svc = BookService(db)
    try:
        dto = await svc.return_book(serial_number=serial_number)
        return dto_to_out(dto)
    except BookNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BookNotBorrowed as e:
        raise HTTPException(status_code=409, detail=str(e))
    except InvalidSerialNumber as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/{serial_number}/status",
    response_model=BookOut,
    summary="Set borrow status",
    description=(
        "Sets the borrow status directly. When setting `is_borrowed=true`, "
        "`borrower_card` is required. Optionally supply `when` to override the borrow timestamp."
    ),
    responses={
        400: R400_INVALID_CARD_OR_SERIAL,
        404: R404_BOOK_OR_USER,
    },
)
async def set_status(
    serial_number: str = Path(
        ...,
        description="Book serial (6 digits)",
        examples={"ex": {"value": "123456"}},  # type: ignore
    ),
    body: SetStatusRequest = Body(
        ...,
        description="Desired borrow status. For `is_borrowed=true`, include `borrower_card`.",
    ),
    db: AsyncSession = Depends(get_db),
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
    except InvalidSerialNumber as e:
        raise HTTPException(status_code=400, detail=str(e))
