class BookError(Exception):
    pass


class BookNotFound(BookError):
    pass


class DuplicateSerialNumber(BookError):
    pass


class InvalidSerialNumber(BookError):
    pass


class InvalidCardNumber(BookError):
    pass


class BookAlreadyBorrowed(BookError):
    pass


class BookNotBorrowed(BookError):
    pass
