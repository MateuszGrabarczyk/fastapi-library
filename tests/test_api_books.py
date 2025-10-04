import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from app.api.books import router

@pytest.fixture(scope="session")
def app():
    app = FastAPI()
    app.include_router(router)
    return app

@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

async def _create_book(client, serial="123456", title="T", author="A"):
    return await client.post("/books", json={"serial_number": serial, "title": title, "author": author})

@pytest.mark.anyio
async def test_create_and_list_books(client):
    response = await _create_book(client, "123456", "Clean Code", "Robert C. Martin")
    assert response.status_code == 201
    body = response.json()
    assert body["serial_number"] == "123456"
    assert body["title"] == "Clean Code"
    assert body["author"] == "Robert C. Martin"
    assert body["is_borrowed"] is False
    response = await client.get("/books")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert {key for key in ["id", "serial_number", "title", "author", "is_borrowed"]}.issubset(data[0].keys())

@pytest.mark.anyio
async def test_create_book_duplicate_serial(client):
    assert (await _create_book(client, "222222")).status_code == 201
    response = await _create_book(client, "222222")
    assert response.status_code == 409

@pytest.mark.anyio
async def test_create_book_invalid_serial(client):
    response = await _create_book(client, "12AB56")
    assert response.status_code == 422

@pytest.mark.anyio
async def test_list_filters_and_pagination(client):
    for serial_number in ("111111", "222222", "333333"):
        assert (await _create_book(client, serial_number)).status_code == 201
    response = await client.post("/books/222222/borrow", json={"borrower_card": "333333"})
    assert response.status_code == 200
    response = await client.get("/books")
    assert response.status_code == 200 and len(response.json()) == 3
    response = await client.get("/books", params={"is_borrowed": True})
    items = response.json()
    assert {book["serial_number"] for book in items} == {"222222"}
    response = await client.get("/books", params={"is_borrowed": False})
    items = response.json()
    assert {book["serial_number"] for book in items} == {"111111", "333333"}
    response = await client.get("/books", params={"borrower_card": "333333"})
    items = response.json()
    assert len(items) == 1 and items[0]["serial_number"] == "222222"

@pytest.mark.anyio
async def test_borrow_and_return_happy_path(client):
    assert (await _create_book(client, "123457")).status_code == 201
    response = await client.post("/books/123457/borrow", json={"borrower_card": "111111"})
    assert response.status_code == 200
    book_data = response.json()
    assert book_data["is_borrowed"] is True and book_data["borrowed_by"] == "111111" and book_data["borrowed_at"] is not None
    response = await client.post("/books/123457/return")
    assert response.status_code == 200
    book_data = response.json()
    assert book_data["is_borrowed"] is False and book_data["borrowed_by"] is None and book_data["borrowed_at"] is None

@pytest.mark.anyio
async def test_borrow_already_borrowed(client):
    assert (await _create_book(client, "123458")).status_code == 201
    assert (await client.post("/books/123458/borrow", json={"borrower_card": "111111"})).status_code == 200
    response = await client.post("/books/123458/borrow", json={"borrower_card": "222222"})
    assert response.status_code == 409

@pytest.mark.anyio
async def test_return_not_borrowed(client):
    assert (await _create_book(client, "123459")).status_code == 201
    response = await client.post("/books/123459/return")
    assert response.status_code == 409

@pytest.mark.anyio
async def test_delete_borrowed_requires_flag(client):
    assert (await _create_book(client, "123460")).status_code == 201
    assert (await client.post("/books/123460/borrow", json={"borrower_card": "222222"})).status_code == 200
    response = await client.delete("/books/123460")
    assert response.status_code == 409
    response = await client.delete("/books/123460", params={"allow_if_borrowed": True})
    assert response.status_code == 204
    response = await client.get("/books")
    serials = {book["serial_number"] for book in response.json()}
    assert "123460" not in serials

@pytest.mark.anyio
async def test_set_status_requires_card_when_true(client):
    assert (await _create_book(client, "123461")).status_code == 201
    response = await client.patch("/books/123461/status", json={"is_borrowed": True})
    assert response.status_code == 400

@pytest.mark.anyio
async def test_set_status_borrow_and_free(client):
    assert (await _create_book(client, "123462")).status_code == 201
    response = await client.patch("/books/123462/status", json={"is_borrowed": True, "borrower_card": "333333"})
    assert response.status_code == 200
    book_data = response.json()
    assert book_data["is_borrowed"] is True and book_data["borrowed_by"] == "333333" and book_data["borrowed_at"] is not None
    response = await client.patch("/books/123462/status", json={"is_borrowed": False})
    assert response.status_code == 200
    book_data = response.json()
    assert book_data["is_borrowed"] is False and book_data["borrowed_by"] is None and book_data["borrowed_at"] is None
