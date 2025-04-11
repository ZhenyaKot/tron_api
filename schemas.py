from typing import List

from pydantic import BaseModel, ConfigDict


class STaskRequest(BaseModel):
    address: str


class STaskResponse(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )

    id: int
    address: str
    balance: float
    bandwidth: int
    energy: int


class STaskListResponse(BaseModel):
    items: List[STaskResponse]
    total: int
