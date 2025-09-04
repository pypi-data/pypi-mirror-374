from pydantic import BaseModel


class Register(BaseModel):
    page_content: str
    metadata: dict

class GroupsRouterRequest(BaseModel):
    query: str = "what is the symbol of pendle and cardano?"
    target_groups: list[str] = None

class SmartRouterRequest(BaseModel):
    query: str

