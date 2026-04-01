from pydantic import BaseModel, Field

class VaxCreate(BaseModel):
    name: str = Field(None, validate_default=True)
    target: str = Field(None, validate_default=True)
    illness: str = Field(None, validate_default=True)
    quantity: int = Field(None, validate_default=True)
    id_manufac: int = Field(None, validate_default=True)

class VaxUpdate(BaseModel):
    name: str = Field(None, validate_default=True)
    target: str = Field(None, validate_default=True)
    illness: str = Field(None, validate_default=True)
    quantity: int = Field(None, validate_default=True)
    id_manufac: int = Field(None, validate_default=True)

class VaxOut(VaxCreate):
    vax_id: int = Field(None, validate_default=True)
    
