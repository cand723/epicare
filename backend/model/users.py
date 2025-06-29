from pydantic import BaseModel, EmailStr, constr
from datetime import date
from enum import Enum


class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class UserRegisterRequest(BaseModel):
    name: constr(min_length=2)
    gender: GenderEnum
    date: date
    email: EmailStr
    password: constr(min_length=8)
