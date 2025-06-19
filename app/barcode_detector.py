# --- START OF FILE barcode_detector.py ---

"""
GS1 Barcode Detector Module - Version améliorée avec prise en compte
de l'indication de format fournie par le décodeur (ex: JPype/ZXing).
"""

import re
from enum import Enum
import json
import os

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
    ZXING = "ZXing (JPype)"
    PYLIBDMTX = "pylibdmtx"
    TEXT_INPUT = "text_input" # <--- AJOUT
    NONE = "none"

# --- Fonctions utilitaires (inchangées) ---

def is_gs1_data(raw_data):
    if not isinstance(raw_data, str):
        return False
    ai_pattern = r"^(00|01|02|10|11|13|15|17|20|21|240|241|250|251|253|254|255|30|310[0-9]|311[0-9]|37|400|401|410|414|420|422|700[1-3]|800[1-8]|8020|9[0-9])"
    if '\x1d' in raw_data:
        return True
    if re.match(ai_pattern, raw_data) and re.fullmatch(r"[\dA-Z\-\.\/\x1d]+", raw_data, re.IGNORECASE):
         if not raw_data.lower().startswith(("http:", "https:", "www.")):
              return True
    return False

def has_datamatrix_characteristics(raw_data):
    if not isinstance(raw_data, str): return False
    return len(raw_data) > 20 and not raw_data.isalnum()

def has_qrcode_characteristics(raw_data):
    if not isinstance(raw_data, str): return False
    raw_lower = raw_data.lower()
    return 'http:' in raw_lower or 'https:' in raw_lower or 'www.' in raw_lower or len(raw_data) > 100

def detect_generic_format(raw_data):
    if not isinstance(raw_data, str): return BarcodeFormat.UNKNOWN
    if has_datamatrix_characteristics(raw_data):
        return BarcodeFormat.DATAMATRIX
    if has_qrcode_characteristics(raw_data):
        return BarcodeFormat.QRCODE
    if re.fullmatch(r"[\w\s!\"#$%&'()*+,-./:;<=>?@\[\\\]^_`{|}~]+", raw_data):
         if not has_datamatrix_characteristics(raw_data) and not has_qrcode_characteristics(raw_data):
               return BarcodeFormat.CODE128
    return BarcodeFormat.UNKNOWN

# <--- MODIFICATION: Mise à jour de calculate_confidence --- >
def calculate_confidence(data, decoder, format_enum):
    """
    Calcule un score de confiance pour la détection.
    Adapté pour tenir compte de la fiabilité de JPype/ZXing et de l'entrée texte.
    """
    base_score = 0.0
    if decoder == DecoderType.ZXING:
        base_score = 0.9
    elif decoder == DecoderType.PYLIBDMTX:
        base_score = 0.7
    elif decoder == DecoderType.TEXT_INPUT: # <--- AJOUT
        base_score = 0.95 # Très haute confiance car l'utilisateur fournit les données
    else:
        base_score = 0.5

    if format_enum in [BarcodeFormat.GS1_128, BarcodeFormat.GS1_DATAMATRIX, BarcodeFormat.GS1_QRCODE]:
        if '\x1d' in data:
            base_score = min(base_score + 0.2, 1.0)
        elif re.match(r"^(01|02|10|11|17|21|30|37|4\d{2})", data):
             base_score = min(base_score + 0.05, 1.0)

    if format_enum != BarcodeFormat.UNKNOWN:
         base_score = min(base_score + 0.1, 1.0)

    return round(base_score, 2)

def get_barcode_characteristics(data, format_enum):
    # ... (fonction inchangée) ...
    if not isinstance(data, str):
         return {"length": 0, "content_type": "unknown", "contains_special_chars": False}
    contains_alpha = any(c.isalpha() for c in data)
    contains_digit = any(c.isdigit() for c in data)
    contains_special = any(not c.isalnum() and not c.isspace() for c in data)
    contains_fnc1 = '\x1d' in data
    content_type = "unknown"
    if contains_alpha and contains_digit: content_type = "alphanumeric"
    elif contains_digit and not contains_alpha: content_type = "numeric"
    elif contains_alpha and not contains_digit: content_type = "alpha"
    elif contains_special: content_type = "special"
    characteristics = {
        "length": len(data), "content_type": content_type,
        "contains_special_chars": contains_special, "contains_fnc1": contains_fnc1
    }
    if format_enum in [BarcodeFormat.GS1_128, BarcodeFormat.GS1_DATAMATRIX, BarcodeFormat.GS1_QRCODE]:
        ai_candidates = re.findall(r"\b(0[012]|1[01357]|21|30|310\d|37|9\d)\d*\b", data)
        characteristics["potential_leading_ais"] = list(set(ai_candidates))
    return characteristics

def get_decoder_info(raw_data, decoder_used, format_hint=None, verbose=False):
    # ... (fonction inchangée) ...
    detected_format = BarcodeFormat.UNKNOWN
    is_gs1 = is_gs1_data(raw_data)
    if format_hint:
        format_hint_upper = format_hint.upper().replace("_", "").replace(" ", "")
        if format_hint_upper == "DATAMATRIX" or format_hint_upper == "GS1DATAMATRIX":
            detected_format = BarcodeFormat.GS1_DATAMATRIX if is_gs1 else BarcodeFormat.DATAMATRIX
        elif format_hint_upper == "QRCODE" or format_hint_upper == "GS1QRCODE":
            detected_format = BarcodeFormat.GS1_QRCODE if is_gs1 else BarcodeFormat.QRCODE
        elif format_hint_upper == "CODE128" or format_hint_upper == "GS1128":
            detected_format = BarcodeFormat.GS1_128 if is_gs1 else BarcodeFormat.CODE128
    if detected_format == BarcodeFormat.UNKNOWN:
        if is_gs1:
            if has_datamatrix_characteristics(raw_data): detected_format = BarcodeFormat.GS1_DATAMATRIX
            elif has_qrcode_characteristics(raw_data): detected_format = BarcodeFormat.GS1_QRCODE
            else: detected_format = BarcodeFormat.GS1_128
        else:
            detected_format = detect_generic_format(raw_data)
    info = {
        "decoder": decoder_used.value,
        "format": detected_format.value,
        "is_gs1": detected_format in [BarcodeFormat.GS1_128, BarcodeFormat.GS1_DATAMATRIX, BarcodeFormat.GS1_QRCODE]
    }
    if verbose:
        info["confidence"] = calculate_confidence(raw_data, decoder_used, detected_format)
        info["characteristics"] = get_barcode_characteristics(raw_data, detected_format)
    return info

# --- END OF FILE barcode_detector.py ---