from pydantic import BaseModel


class Register(BaseModel):
    username: str
    email: str
    password: str


class Login(BaseModel):
    email: str
    password: str


class Confirmation(BaseModel):
    username: str
    email: str
