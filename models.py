from pydantic import BaseModel

class UserQuery(BaseModel):
    query: str

class ChatHistory(BaseModel):
    role: str
    content: str