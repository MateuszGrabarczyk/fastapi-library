# FastAPI Library Management System

A simple REST API for managing library books built with FastAPI and PostgreSQL. This system allows library to track and update the status of books in their collection.

## Features

- **Book Management**: Add, remove, and list books
- **Borrowing System**: Update book status (borrowed/available) and track borrowers
- **PostgreSQL Database**: Persistent data storage with migrations
- **Docker Support**: Easy deployment with docker-compose
- **API Documentation**: Interactive Swagger/OpenAPI docs

## Book Information

Each book contains the following information:

- **Serial Number**: 6-digit unique identifier (entered by staff)
- **Title**: Book title
- **Author**: Book author
- **Borrowing Status**: Currently borrowed or available
- **Borrower Information**: 6-digit library card number and borrowing date (when applicable)

## API Endpoints

- `POST /books/` - Add a new book
- `GET /books/` - Get list of all books
- `DELETE /books/{serial_number}` - Remove a book
- `PUT /books/{serial_number}/borrow` - Borrow a book
- `PUT /books/{serial_number}/return` - Return a book

## Tech Stack

- **FastAPI**
- **PostgreSQL**
- **SQLAlchemy**
- **Alembic**
- **Pydantic**
- **Docker**
- **pytest**

## Quick Start

### Prerequisites

- Docker
- Docker Compose

### Running the Application

1. **Clone the repository:**

   ```bash
   git clone https://github.com/MateuszGrabarczyk/fastapi-library.git
   cd fastapi-library
   ```

2. **Create .env file based on .env.example**

3. **Start the application:**

   ```bash
   docker compose up -d
   ```

   This command will:

   - Start PostgreSQL database
   - Build and run the FastAPI application
   - Run database migrations automatically
   - Seed the database with test users:
     - Jan Kowalski — card_number: 111111
     - Anna Nowak — card_number: 222222
     - Piotr Wiśniewski — card_number: 333333
     - **Note**: books are not seeded by this migration — add books manually via the API (POST /books/) or directly in the database.

4. **Access the application:**
   - API: http://localhost:8000
   - Interactive API Documentation: http://localhost:8000/docs

### Stopping the Application

```bash
docker compose down
```

To also remove the database volume:

```bash
docker compose down -v
```

### Running Tests

It can be done directly in the container:

```bash
pytest
```

### Project Structure

```

├── app/
│ ├── api/ # API route handlers
│ ├── dataclasses/ # Data transfer objects
│ ├── models/ # SQLAlchemy models
│ ├── schemas/ # Pydantic schemas
│ ├── services/ # Business logic
│ ├── config.py # Configuration settings
│ ├── db.py # Database connection
│ └── main.py # FastAPI application
├── alembic/ # Database migrations
├── tests/ # Tests
├── docker-compose.yml # Docker configuration
├── Dockerfile # Container definition
└── requirements.txt # Python dependencies

```

```

```
