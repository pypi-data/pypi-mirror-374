from pydantic import BaseModel


class CreditResponseModel(BaseModel):
    amount: int
    currency: str