from app.schemas.common import ErrorResponse

R400_INVALID_SERIAL = {
    "description": "Invalid serial number format",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "invalid_serial": {
                    "summary": "Serial must be 6 digits",
                    "value": {
                        "detail": "Invalid serial number: must be exactly 6 digits"
                    },
                }
            }
        }
    },
}

R400_INVALID_CARD = {
    "description": "Invalid card number format",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "invalid_card": {
                    "summary": "Card must be 6 digits",
                    "value": {
                        "detail": "Invalid card number: must be exactly 6 digits"
                    },
                }
            }
        }
    },
}

R400_INVALID_CARD_OR_SERIAL = {
    "description": "Invalid card or serial number format",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "invalid_serial": {
                    "summary": "Serial must be 6 digits",
                    "value": {
                        "detail": "Invalid serial number: must be exactly 6 digits"
                    },
                },
                "invalid_card": {
                    "summary": "Card must be 6 digits",
                    "value": {
                        "detail": "Invalid card number: must be exactly 6 digits"
                    },
                },
            }
        }
    },
}

R404_BOOK = {
    "description": "Book not found",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "book": {
                    "summary": "Book not found",
                    "value": {"detail": "Book with serial 123456 not found"},
                }
            }
        }
    },
}

R404_USER = {
    "description": "User not found",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "user": {
                    "summary": "User not found",
                    "value": {"detail": "User with card number 654321 not found"},
                }
            }
        }
    },
}

R404_BOOK_OR_USER = {
    "description": "Book or user not found",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "book": {
                    "summary": "Book not found",
                    "value": {"detail": "Book with serial 123456 not found"},
                },
                "user": {
                    "summary": "User not found",
                    "value": {"detail": "User with card number 654321 not found"},
                },
            }
        }
    },
}

R409_DUPLICATE_SERIAL = {
    "description": "Duplicate serial number",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "duplicate_serial": {
                    "summary": "Duplicate serial",
                    "value": {"detail": "Book with serial 123456 already exists"},
                }
            }
        }
    },
}

R409_ALREADY_BORROWED = {
    "description": "Book is already borrowed",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "already_borrowed": {
                    "summary": "Already borrowed",
                    "value": {"detail": "Book 123456 already borrowed by 654321"},
                }
            }
        }
    },
}

R409_NOT_BORROWED = {
    "description": "Book is not borrowed",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "not_borrowed": {
                    "summary": "Not borrowed",
                    "value": {"detail": "Book 123456 is not currently borrowed"},
                }
            }
        }
    },
}
