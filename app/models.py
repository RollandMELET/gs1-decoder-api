# --- START OF FILE models.py ---

from pydantic import BaseModel, Field
from typing import List, Union, Dict, Any, Optional
from enum import Enum

class DecoderInfo(BaseModel):
    """Informations sur le décodeur utilisé et le format détecté."""
    decoder: str
    format: str
    is_gs1: Optional[bool] = None
    confidence: Optional[float] = None
    characteristics: Optional[Dict[str, Any]] = None

class ParsedVerboseItem(BaseModel):
    """Structure d'un élément AI parsé en mode verbose."""
    ai: str
    name: str
    value: str
    valid: bool

class BarcodeItem(BaseModel):
    """Représentation d'un code-barres décodé avec métadonnées."""
    raw: str
    parsed: Union[Dict[str, str], List[ParsedVerboseItem]]
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

# --- Modèles pour la génération de codes-barres ---

class BarcodeFormat(str, Enum):
    """Formats de codes-barres pris en charge pour la génération."""
    DATAMATRIX = "datamatrix"
    QRCODE = "qrcode"
    CODE128 = "code128"
    GS1_128 = "gs1-128"
    GS1_DATAMATRIX = "gs1-datamatrix"
    GS1_QRCODE = "gs1-qrcode"

class ImageFormat(str, Enum):
    """Formats d'image pris en charge pour l'export."""
    PNG = "png"
    JPEG = "jpeg"
    SVG = "svg"

class GenerateRequest(BaseModel):
    """Paramètres pour la génération d'un code-barres."""
    data: str = Field(..., description="Données à encoder (ex: 01034531200000111719112510ABCD1234)")
    format: BarcodeFormat = Field(default=BarcodeFormat.GS1_DATAMATRIX, description="Format du code-barres")
    image_format: ImageFormat = Field(default=ImageFormat.PNG, description="Format de l'image générée")
    width: int = Field(default=300, ge=50, le=1000, description="Largeur de l'image en pixels")
    height: int = Field(default=300, ge=50, le=1000, description="Hauteur de l'image en pixels")


# <--- AJOUT: Nouveaux modèles pour l'endpoint /parse/ --- >
class ParseRequest(BaseModel):
    """Requête pour l'endpoint de parsing de données brutes."""
    raw_data: str = Field(..., description="La chaîne de caractères brute issue du décodage du code-barres, incluant les potentiels caractères FNC1/GS.")
    barcode_format: Optional[str] = Field(None, description="Format optionnel du code-barres d'origine (ex: 'GS1 DataMatrix', 'QR_CODE'). Aide à la classification.")

class ParseResponse(BaseModel):
    """Réponse pour l'endpoint de parsing."""
    success: bool
    barcodes: List[BarcodeItem]


# --- END OF FILE models.py ---