from fastapi import HTTPException, status


class UserAlreadyExistsException(HTTPException):
    def __init__(self, detail: str = "User with this email already exists"):
        super().__init__(status_code=409, detail=detail)


class UserNotExistsException(HTTPException):
    def __init__(self, detail: str = "User with this id does not exist"):
        super().__init__(status_code=404, detail=detail)


class UserAlreadyBlockedException(HTTPException):
    def __init__(self, detail: str = "User is already blocked"):
        super().__init__(status_code=400, detail=detail)


class UserAlreadyActiveException(HTTPException):
    def __init__(self, detail: str = "User is already active"):
        super().__init__(status_code=400, detail=detail)


class BadRequestDataException(HTTPException):
    def __init__(self, detail: str = "Bad Request"):
        super().__init__(status_code=400, detail=detail)


class NegativeBalanceException(HTTPException):
    """Amount cannot be negative"""

    def __init__(self, detail: str = "Amount cannot be negative"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InvalidUserIdException(HTTPException):
    def __init__(self, detail: str = "User_id must be positive"):
        super().__init__(status_code=400, detail=detail)


class TransactionNotExistsException(HTTPException):
    def __init__(self, detail: str = "Transaction with this id does not exist"):
        super().__init__(status_code=404, detail=detail)


class TransactionDoesNotBelongToUserException(HTTPException):
    def __init__(self, transaction_id: int, user_id: int):
        detail: str = f"Transaction with id=`{transaction_id}` does not belong to user with id=`{user_id}`"
        super().__init__(status_code=404, detail=detail)


class CreateTransactionForBlockedUserException(HTTPException):
    def __init__(self, detail: str = "User with this id is blocked"):
        super().__init__(status_code=404, detail=detail)


class UpdateTransactionForBlockedUserException(HTTPException):
    def __init__(self, user_id: int):
        detail: str = f"User with id=`{user_id}` is blocked"
        super().__init__(status_code=400, detail=detail)


class TransactionAlreadyRollbackedException(HTTPException):
    def __init__(self, transaction_id: int):
        detail: str = f"Transaction with id=`{transaction_id}` is already rollbacked"
        super().__init__(status_code=400, detail=detail)
