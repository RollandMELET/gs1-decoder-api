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

# --- NOUVEAU: Classe pour la structure parsée en mode verbose ---
class ParsedVerboseItem(BaseModel):
    """Structure d'un élément AI parsé en mode verbose."""
    ai: str
    name: str
    value: str
    valid: bool # Accepte explicitement un booléen

class BarcodeItem(BaseModel):
    """Représentation d'un code-barres décodé avec métadonnées."""
    raw: str
    # --- MODIFIÉ: Utilise ParsedVerboseItem dans l'Union ---
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
    capabilities: Dict[str, Any] # Gardé Any ici, car le contenu est variable

# Modèles pour la génération de codes-barres

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

# GenerateResponse n'existe pas dans le code original, mais serait utile
# Si vous voulez un retour structuré pour la génération au lieu de l'image directe
# class GenerateResponse(BaseModel):
#     """Réponse pour la génération réussie d'un code-barres."""
#     success: bool
#     format: BarcodeFormat
#     image_url: Optional[str] = None # Ou image_data: bytes
#     data: str

# --- FIN DU FICHIER models.py ---