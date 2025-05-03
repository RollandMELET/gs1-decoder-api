"""
GS1 Barcode Detector Module

Ce module contient des fonctions pour:
1. Détecter le format du code-barres (QR Code, DataMatrix, etc.)
2. Identifier quelle bibliothèque a réussi à décoder le code-barres
3. Fournir des informations détaillées sur le résultat du décodage

Utilisé par le module principal pour enrichir la réponse de l'API.
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

def detect_gs1_format(raw_data):
    """
    Détecte le format GS1 d'un code-barres à partir des données brutes.
    
    Args:
        raw_data (str): Les données brutes décodées
        
    Returns:
        BarcodeFormat: Le format détecté
    """
    # Vérifier si les données commencent par un AI GS1 valide
    ai_pattern = r"^(00|01|02|10|11|13|15|17|20|21|30|31|32|33|34|35|36|37|90|91|92|93|94|95|96|97|98|99|240|241|242|250|251|253|254|255|3[0-9]{3}|4[0-9]{2}|7[0-9]{3}|8[0-9]{3})"
    
    if re.match(ai_pattern, raw_data):
        # Si les données commencent par ]d1, c'est un code 39
        if raw_data.startswith("]d1"):
            return BarcodeFormat.CODE128
        # Si les données commencent par ]d2, c'est un DataMatrix
        elif raw_data.startswith("]d2"):
            return BarcodeFormat.GS1_DATAMATRIX
        # Si les données commencent par ]Q3, c'est un QR Code
        elif raw_data.startswith("]Q3"):
            return BarcodeFormat.GS1_QRCODE
        # Par défaut pour les données GS1, c'est probablement un GS1-128
        else:
            return BarcodeFormat.GS1_128
    
    # Si le format n'est pas reconnu comme GS1, essayer de détecter le format générique
    return detect_generic_format(raw_data)

def detect_generic_format(raw_data):
    """
    Détecte le format générique d'un code-barres.
    
    Args:
        raw_data (str): Les données brutes décodées
        
    Returns:
        BarcodeFormat: Le format détecté
    """
    # Caractéristiques DataMatrix
    if (len(raw_data) > 0 and raw_data[0] == '^') or \
       (len(raw_data) > 5 and all(c.isalnum() or c in '+-/:.' for c in raw_data[:5])):
        return BarcodeFormat.DATAMATRIX
    
    # Caractéristiques QR Code (généralement plus long et peut contenir des URLs)
    if len(raw_data) > 20 and ('http' in raw_data.lower() or 'www.' in raw_data.lower()):
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
    barcode_format = detect_gs1_format(decoded_data)
    
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
    
    # Ajustements selon le format et la qualité des données
    if format != BarcodeFormat.UNKNOWN:
        base_score += 0.1
    
    # Vérifier la cohérence des données
    if format in [BarcodeFormat.GS1_128, BarcodeFormat.GS1_DATAMATRIX, BarcodeFormat.GS1_QRCODE]:
        # Vérifier si les données commencent par un AI valide
        if re.match(r"^(00|01|02|10|11|13|15|17|20|21|30)", data):
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
