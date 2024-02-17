from pydantic import BaseModel

class InputImage(BaseModel):
    url: str
    width: int
    height: int
    
class OutputImage(BaseModel):
    url: str
    width: int
    height: int