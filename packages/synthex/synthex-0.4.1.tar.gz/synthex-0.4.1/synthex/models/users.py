from pydantic import BaseModel


class UserResponseModel(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    is_verified: bool