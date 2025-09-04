from pydantic import BaseModel


class HandshakeResponseModel(BaseModel):
    anon_id: str