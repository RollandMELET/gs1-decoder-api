from pydantic import BaseModel
from typing import List, Union

class BarcodeItem(BaseModel):
    raw: str
    parsed: Union[dict, List[dict]]

class DecodeResponse(BaseModel):
    success: bool
    barcodes: List[BarcodeItem]

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
