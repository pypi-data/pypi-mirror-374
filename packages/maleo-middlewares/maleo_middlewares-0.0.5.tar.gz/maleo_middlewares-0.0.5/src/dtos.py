from pydantic import BaseModel, Field
from maleo.types.base.string import ListOfStrings


class InactiveKeys(BaseModel):
    keys: ListOfStrings = Field(..., min_length=1, description="Inactive keys")
