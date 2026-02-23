from fastapi import HTTPException, status


class UserAlreadyExistsException(HTTPException): ...


class UserNotExistsException(HTTPException): ...


class UserAlreadyBlockedException(HTTPException): ...


class UserAlreadyActiveException(HTTPException): ...


class BadRequestDataException(HTTPException): ...


class NegativeBalanceException(HTTPException):
    """Amount cannot be negative"""

    def __init__(self, detail: str = "Amount cannot be negative"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InvalidUserIdException(HTTPException):
    def __init__(self, detail: str = "user_id must be positive"):
        super().__init__(status_code=400, detail=detail)


class TransactionNotExistsException(HTTPException): ...


class TransactionDoesNotBelongToUserException(HTTPException): ...


class CreateTransactionForBlockedUserException(HTTPException): ...


class UpdateTransactionForBlockedUserException(HTTPException): ...


class TransactionAlreadyRollbackedException(HTTPException): ...
