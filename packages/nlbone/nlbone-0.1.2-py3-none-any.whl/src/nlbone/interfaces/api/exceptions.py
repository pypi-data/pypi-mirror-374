from fastapi import HTTPException, status

class UnprocessableEntityException(HTTPException):
    def __init__(self, detail: str, loc: list[str] | None = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"msg": detail, "loc": loc or []},
        )
