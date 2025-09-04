from pydantic import BaseModel
from typing import Optional
from typing import TypeVar, Generic


T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    status_code: int = 200
    status: str = "success"
    message: Optional[str] = None
    data: Optional[T] = None
    
    
class ActionResult(BaseModel):
    success: bool
    message: Optional[str] = None