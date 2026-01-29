from pydantic import BaseModel


class Ok(BaseModel):
    status: str = "OK"


class OkWithMessage(Ok):
    message: str


class BadRequest(BaseModel):
    status: str = "Bad Request"


class BadRequestWithMessage(BadRequest):
    message: str


class BadRequestWithMessages(BadRequest):
    messages: dict = {}
