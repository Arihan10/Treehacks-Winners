from pydantic import BaseModel

class DoRequest(BaseModel):
    type: str  
    identifier: str
    natural_language_task: str