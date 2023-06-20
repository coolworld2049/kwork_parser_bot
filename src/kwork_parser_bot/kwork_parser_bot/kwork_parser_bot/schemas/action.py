from typing import Optional

from pydantic import BaseModel


class Action(BaseModel):
    text: str
    description: Optional[str]
    user_id: int
    category_id: Optional[int]
    subcategory_id: Optional[int]
    action: str
