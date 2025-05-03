"""
GS1 Barcode Detector Module - Version améliorée
"""

import re
from enum import Enum
import json
import os

# Chemin vers les ressources
RESOURCES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources")

class BarcodeFormat(str, Enum):
    """Formats de codes-barres pris en charge."""
    DATAMATRIX = "DataMatrix"
    QRCODE = "QR Code"
    CODE128 = "Code 128"
    GS1_128 = "GS1-128"
    GS1_DATAMATRIX = "GS1 DataMatrix"
    GS1_QRCODE = "GS1 QR Code"
    UNKNOWN = "Unknown"

class DecoderType(str, Enum):
    """Types de décodeurs utilisés."""
    ZXING = "ZXing"
    PYLIBDMTX = "pylibdmtx"
    NONE = "none"

def detect_gs1_format(raw_data, decoder_used=None):
    """
    Détecte le format GS1 d'un code-barres à partir des données brutes.
    Version améliorée qui prend en compte le décodeur utilisé.
    
    Args:
        raw_data (str): Les données brutes décodées
        decoder_used (DecoderType): Le décodeur qui a réussi à lire le code
        
    Returns:
        BarcodeFormat: Le format détecté
    """
    # Prioriser l'information du décodeur (plus fiable)
    if decoder_used:
        if decoder_used == DecoderType.PYLIBDMTX:
            # Si pylibdmtx a décodé, c'est très probablement un DataMatrix
            # Vérifier en plus si c'est un GS1
            if is_gs1_data(raw_data):
                return BarcodeFormat.GS1_DATAMATRIX
            return BarcodeFormat.DATAMATRIX
        
        elif decoder_used == DecoderType.ZXING:
            # ZXing peut décoder plusieurs formats, analyse supplémentaire nécessaire
            if is_gs1_data(raw_data):
                # Déterminer quel type de code GS1 à partir des caractéristiques
                if has_datamatrix_characteristics(raw_data):
                    return BarcodeFormat.GS1_DATAMATRIX
                elif has_qrcode_characteristics(raw_data):
                    return BarcodeFormat.GS1_QRCODE
                else:
                    return BarcodeFormat.GS1_128
            else:
                # Format non-GS1, identifier selon les caractéristiques
                return detect_generic_format(raw_data)
    
    # Si pas d'info décodeur, utiliser l'analyse des données
    if is_gs1_data(raw_data):
        if has_datamatrix_characteristics(raw_data):
            return BarcodeFormat.GS1_DATAMATRIX
        elif has_qrcode_characteristics(raw_data):
            return BarcodeFormat.GS1_QRCODE
        else:
            return BarcodeFormat.GS1_128
    
    # Si pas identifié comme GS1, détecter le format générique
    return detect_generic_format(raw_data)

def is_gs1_data(raw_data):
    """
    Vérifie si les données sont au format GS1.
    
    Args:
        raw_data (str): Les données brutes du code-barres
        
    Returns:
        bool: True si c'est un format GS1
    """
    # Motif pour détecter les Application Identifiers GS1 (codes AI)
    ai_pattern = r"^(00|01|02|10|11|13|15|17|20|21|30|31|32|33|34|35|36|37|90|91|92|93|94|95|96|97|98|99|240|241|242|250|251|253|254|255|3[0-9]{3}|4[0-9]{2}|7[0-9]{3}|8[0-9]{3})"
    
    # Vérifier les marqueurs spécifiques GS1
    gs1_indicators = [
        re.match(ai_pattern, raw_data) is not None,  # Commence par un AI valide
        '\x1d' in raw_data,                         # Contient le séparateur FNC1
        raw_data.startswith("]d2"),                 # Marqueur de décodage DataMatrix
        raw_data.startswith("]Q1"),                 # Marqueur de décodage QR Code
        raw_data.startswith("]C1")                  # Marqueur de décodage Code 128
    ]
    
    return any(gs1_indicators)

def has_datamatrix_characteristics(raw_data):
    """
    Vérifie si les données présentent des caractéristiques de DataMatrix.
    
    Args:
        raw_data (str): Les données brutes
        
    Returns:
        bool: True si les caractéristiques correspondent à un DataMatrix
    """
    # Caractéristiques spécifiques des DataMatrix
    datamatrix_indicators = [
        raw_data.startswith("]d2"),      # Marqueur typique des DataMatrix
        '.' in raw_data,                 # Les DataMatrix utilisent souvent '.' comme séparateur
        len(raw_data) > 30 and raw_data.count('.') > 1  # DataMatrix GS1 ont souvent plusieurs séparateurs
    ]
    
    return any(datamatrix_indicators)

def has_qrcode_characteristics(raw_data):
    """
    Vérifie si les données présentent des caractéristiques de QR Code.
    
    Args:
        raw_data (str): Les données brutes
        
    Returns:
        bool: True si les caractéristiques correspondent à un QR Code
    """
    # Caractéristiques spécifiques des QR Codes
    qrcode_indicators = [
        raw_data.startswith("]Q"),       # Marqueur typique des QR Codes
        'http' in raw_data.lower(),      # Les QR Codes contiennent souvent des URLs
        'www.' in raw_data.lower(),      # Les QR Codes contiennent souvent des URLs
        len(raw_data) > 100              # Les QR Codes peuvent stocker beaucoup de données
    ]
    
    return any(qrcode_indicators)

def detect_generic_format(raw_data):
    """
    Détecte le format générique d'un code-barres (non-GS1).
    
    Args:
        raw_data (str): Les données brutes décodées
        
    Returns:
        BarcodeFormat: Le format détecté
    """
    # Caractéristiques DataMatrix
    if has_datamatrix_characteristics(raw_data):
        return BarcodeFormat.DATAMATRIX
    
    # Caractéristiques QR Code
    if has_qrcode_characteristics(raw_data):
        return BarcodeFormat.QRCODE
    
    # Caractéristiques Code 128 (généralement numérique ou alphanumérique simple)
    if all(c.isalnum() or c in '+-/' for c in raw_data):
        return BarcodeFormat.CODE128
    
    # Format inconnu
    return BarcodeFormat.UNKNOWN

def get_decoder_info(decoded_data, decoder_used, verbose=False):
    """
    Génère des informations détaillées sur le décodage.
    
    Args:
        decoded_data (str): Les données décodées
        decoder_used (DecoderType): Le décodeur utilisé
        verbose (bool): Si True, inclut des informations supplémentaires
        
    Returns:
        dict: Informations sur le décodage
    """
    barcode_format = detect_gs1_format(decoded_data, decoder_used)
    
    # Informations de base
    info = {
        "decoder": decoder_used,
        "format": barcode_format,
        "is_gs1": barcode_format in [BarcodeFormat.GS1_128, BarcodeFormat.GS1_DATAMATRIX, BarcodeFormat.GS1_QRCODE]
    }
    
    # Informations supplémentaires en mode verbose
    if verbose:
        info["confidence"] = calculate_confidence(decoded_data, decoder_used, barcode_format)
        info["characteristics"] = get_barcode_characteristics(decoded_data, barcode_format)
    
    return info

def calculate_confidence(data, decoder, format):
    """
    Calcule un score de confiance pour la détection.
    
    Args:
        data (str): Les données décodées
        decoder (DecoderType): Le décodeur utilisé
        format (BarcodeFormat): Le format détecté
        
    Returns:
        float: Score de confiance (0-1)
    """
    # Score de base selon le décodeur
    base_score = 0.8 if decoder == DecoderType.ZXING else 0.7 if decoder == DecoderType.PYLIBDMTX else 0.5
    
    # Ajustements selon le format et les caractéristiques
    if format == BarcodeFormat.GS1_DATAMATRIX and decoder == DecoderType.PYLIBDMTX:
        # Haute confiance si pylibdmtx a décodé un DataMatrix
        base_score += 0.2
    elif format == BarcodeFormat.GS1_128 and decoder == DecoderType.ZXING:
        # Haute confiance si ZXing a décodé un Code 128
        base_score += 0.2
    elif format != BarcodeFormat.UNKNOWN:
        # Confiance légèrement accrue pour tout format reconnu
        base_score += 0.1
    
    # Vérifier la cohérence des données avec le format
    if format in [BarcodeFormat.GS1_128, BarcodeFormat.GS1_DATAMATRIX, BarcodeFormat.GS1_QRCODE]:
        if re.match(r"^(00|01|02|10|11|13|15|17|20|21|30)", data):
            base_score += 0.1
        
        # Points de confiance supplémentaires basés sur la présence de séparateurs typiques
        if format == BarcodeFormat.GS1_DATAMATRIX and ('.' in data or '\x1d' in data):
            base_score += 0.1
    
    # Limiter le score à 1.0
    return min(base_score, 1.0)

def get_barcode_characteristics(data, format):
    """
    Détermine les caractéristiques du code-barres.
    
    Args:
        data (str): Les données décodées
        format (BarcodeFormat): Le format détecté
        
    Returns:
        dict: Caractéristiques du code-barres
    """
    characteristics = {
        "length": len(data),
        "content_type": "alphanumeric" if any(c.isalpha() for c in data) else "numeric",
        "contains_special_chars": any(not c.isalnum() and not c.isspace() for c in data),
    }
    
    # Caractéristiques spécifiques aux formats GS1
    if format in [BarcodeFormat.GS1_128, BarcodeFormat.GS1_DATAMATRIX, BarcodeFormat.GS1_QRCODE]:
        # Identifier les AIs potentiels
        ai_candidates = re.findall(r"(00|01|02|10|11|13|15|17|20|21|30|31|32|33|34|35|36|37|90|91|92|93|94|95|96|97|98|99|240|241|242|250|251|253|254|255|3\d{3}|4\d{2}|7\d{3}|8\d{3})", data)
        characteristics["potential_ais"] = ai_candidates
    
    return characteristics