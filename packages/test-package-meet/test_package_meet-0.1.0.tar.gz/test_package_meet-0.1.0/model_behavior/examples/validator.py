from typing import Dict

from pydantic import BaseModel, field_validator, model_validator, computed_field


class User(BaseModel):
    name: str

    @field_validator("name")
    def validate_name(self, value) -> str:
        if len(value) < 3:
            raise ValueError("name must be at least 3 characters long")
        return value


class SignupData(BaseModel):
    email: str
    password: str
    confirm_password: str

    @model_validator(mode="after")
    def password_match(self, values) -> Dict[str, str]:
        if values["password"] != values["confirm_password"]:
            raise ValueError("password and confirmation password do not match")
        return values


class LoginAttempt(BaseModel):
    attempts: int
    max_attempts: int = 5

    @computed_field
    @property
    def attempt_number(self) -> bool:
        if self.attempts == self.max_attempts:
            raise ValueError("attempt number exceeds max attempt number")
        return True
