from pydantic import BaseModel
from datetime import date as date_, datetime
from typing import Optional


class User(BaseModel):
    username: str
    email: Optional[str] = None
    disabled: bool


class UserIn(User):
    password: str


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    """
    返回给用户的token
    """
    access_token: str
    token_type: str


class Plate(BaseModel):
    plate_code: str
    plate_name: str
