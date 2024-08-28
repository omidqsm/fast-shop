from pydantic import BaseModel, model_validator, field_validator, EmailStr, SecretStr, ConfigDict


class Token(BaseModel):
    access_token: str


class PhoneLogin(BaseModel):
    phone: str
    password: str
