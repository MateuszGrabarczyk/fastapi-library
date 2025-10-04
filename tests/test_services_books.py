import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.books import BookService
from app.exceptions import (
    BookAlreadyBorrowed,
    BookNotBorrowed,
    BookNotFound,
    DuplicateSerialNumber,
    InvalidCardNumber,
    InvalidSerialNumber,
)

async def add_sample_book(service: BookService, serial="123456", title="T", author="A"):
    return await service.add_book(serial_number=serial, title=title, author=author)

@pytest.mark.asyncio
async def test_add_and_get_book(session: AsyncSession):
    service = BookService(session)
    dto = await add_sample_book(service, "123456", "Clean Code", "Robert C. Martin")
    await session.commit()

    book = await service.get_by_serial("123456")
    assert book.serial_number == "123456"
    assert book.title == "Clean Code"
    assert book.author == "Robert C. Martin"
    assert book.is_borrowed is False
    assert dto.serial_number == "123456"

@pytest.mark.asyncio
async def test_add_book_duplicate_serial_raises(session: AsyncSession):
    service = BookService(session)
    await add_sample_book(service, "123456")
    await session.commit()

    with pytest.raises(DuplicateSerialNumber):
        await add_sample_book(service, "123456")

@pytest.mark.asyncio
async def test_get_by_serial_invalid_format_raises(session: AsyncSession):
    service = BookService(session)
    with pytest.raises(InvalidSerialNumber):
        await service.get_by_serial("12AB56")

@pytest.mark.asyncio
async def test_get_by_serial_not_found_raises(session: AsyncSession):
    service = BookService(session)
    with pytest.raises(BookNotFound):
        await service.get_by_serial("333333")

@pytest.mark.asyncio
async def test_list_books_filters(session: AsyncSession):
    service = BookService(session)
    await add_sample_book(service, "111111")
    await add_sample_book(service, "222222")
    await add_sample_book(service, "333333")
    await session.commit()

    await service.borrow_book(serial_number="222222", borrower_card="333333")
    await session.commit()

    all_rows = await service.list_books()
    assert len(all_rows) == 3

    only_borrowed = await service.list_books(is_borrowed=True)
    assert {b.serial_number for b in only_borrowed} == {"222222"}

    only_free = await service.list_books(is_borrowed=False)
    assert {b.serial_number for b in only_free} == {"111111", "333333"}

    by_card = await service.list_books(borrower_card="333333")
    assert len(by_card) == 1 and by_card[0].serial_number == "222222"

@pytest.mark.asyncio
async def test_borrow_and_return_happy_path(session: AsyncSession):
    service = BookService(session)
    await add_sample_book(service, "123456")
    await session.commit()

    dto_borrowed = await service.borrow_book(serial_number="123456", borrower_card="111111")
    await session.commit()

    assert dto_borrowed.is_borrowed is True
    assert dto_borrowed.borrowed_by == "111111"
    assert dto_borrowed.borrowed_at is not None

    dto_returned = await service.return_book(serial_number="123456")
    await session.commit()

    assert dto_returned.is_borrowed is False
    assert dto_returned.borrowed_by is None
    assert dto_returned.borrowed_at is None

@pytest.mark.asyncio
async def test_borrow_already_borrowed_raises(session: AsyncSession):
    service = BookService(session)
    await add_sample_book(service, "123456")
    await session.commit()

    await service.borrow_book(serial_number="123456", borrower_card="111111")
    await session.commit()

    with pytest.raises(BookAlreadyBorrowed):
        await service.borrow_book(serial_number="123456", borrower_card="222222")

@pytest.mark.asyncio
async def test_return_not_borrowed_raises(session: AsyncSession):
    service = BookService(session)
    await add_sample_book(service, "123456")
    await session.commit()

    with pytest.raises(BookNotBorrowed):
        await service.return_book(serial_number="123456")

@pytest.mark.asyncio
async def test_delete_borrowed_requires_flag(session: AsyncSession):
    service = BookService(session)
    await add_sample_book(service, "123456")
    await session.commit()

    await service.borrow_book(serial_number="123456", borrower_card="222222")
    await session.commit()

    with pytest.raises(BookAlreadyBorrowed):
        await service.delete_book(serial_number="123456", allow_if_borrowed=False)

    await service.delete_book(serial_number="123456", allow_if_borrowed=True)
    await session.commit()

    with pytest.raises(BookNotFound):
        await service.get_by_serial("123456")

@pytest.mark.asyncio
async def test_set_status_requires_card_when_borrowed(session: AsyncSession):
    service = BookService(session)
    await add_sample_book(service, "123456")
    await session.commit()

    with pytest.raises(InvalidCardNumber):
        await service.set_status(serial_number="123456", is_borrowed=True, borrower_card=None)

@pytest.mark.asyncio
async def test_set_status_borrowed_and_free(session: AsyncSession):
    service = BookService(session)
    await add_sample_book(service, "123456")
    await session.commit()

    dto1 = await service.set_status(serial_number="123456", is_borrowed=True, borrower_card="333333")
    await session.commit()
    assert dto1.is_borrowed is True
    assert dto1.borrowed_by == "333333"
    assert dto1.borrowed_at is not None

    dto2 = await service.set_status(serial_number="123456", is_borrowed=False)
    await session.commit()
    assert dto2.is_borrowed is False
    assert dto2.borrowed_by is None
    assert dto2.borrowed_at is None
