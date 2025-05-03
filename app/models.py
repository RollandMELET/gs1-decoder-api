from pydantic import BaseModel
from typing import List, Union, Dict, Any, Optional

class DecoderInfo(BaseModel):
    """Informations sur le décodeur utilisé et le format détecté."""
    decoder: str
    format: str
    is_gs1: Optional[bool] = None
    confidence: Optional[float] = None
    characteristics: Optional[Dict[str, Any]] = None

class BarcodeItem(BaseModel):
    """Représentation d'un code-barres décodé avec métadonnées."""
    raw: str
    parsed: Union[Dict[str, str], List[Dict[str, str]]]
    decoder_info: DecoderInfo

class DecodeResponse(BaseModel):
    """Réponse de l'API pour l'endpoint de décodage."""
    success: bool
    barcodes: List[BarcodeItem]

class ErrorResponse(BaseModel):
    """Réponse en cas d'erreur."""
    success: bool = False
    error: str

class DecoderCapabilities(BaseModel):
    """Capacités des décodeurs disponibles."""
    zxing: bool
    pylibdmtx: bool

class HealthResponse(BaseModel):
    """Réponse de l'API pour l'endpoint de santé."""
    status: str
    capabilities: Dict[str, Any]
