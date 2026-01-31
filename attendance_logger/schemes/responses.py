from pydantic import BaseModel


class Ok(BaseModel):
    status: str = "OK"


class OkAccessToken(Ok):
    access_token: str


class OkWithMessage(Ok):
    message: str


class BadRequest(BaseModel):
    status: str = "Bad Request"


class BadRequestWithMessage(BadRequest):
    message: str


class BadRequestWithMessages(BadRequest):
    messages: dict = {}


class Forbidden(BaseModel):
    status: str = "Forbidden"
    message: str = "Insufficient Permissions."
