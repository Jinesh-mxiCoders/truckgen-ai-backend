from pydantic import BaseModel
from typing import Optional, Dict, Any

class TechnicalDocBase(BaseModel):
    product_type: str
    model: Optional[str]
    chunk: str
    metadata: Optional[Dict[str, Any]]

class TechnicalDocCreate(TechnicalDocBase):
    embedding: list[float]

class TechnicalDocRead(TechnicalDocBase):
    id: int

    class Config:
        orm_mode = True
