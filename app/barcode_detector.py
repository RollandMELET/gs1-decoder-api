# --- START OF FILE barcode_detector.py (Ajusté pour JPype hint) ---

"""
GS1 Barcode Detector Module - Version améliorée avec prise en compte
de l'indication de format fournie par le décodeur (ex: JPype/ZXing).
"""

import re
from enum import Enum
import json
import os

# --- MODIFIÉ: Utiliser les Enums et modèles partagés ---
# Note: Assurez-vous que models.py définit bien ces Enums ou importez depuis là.
#       Si models.py est le seul endroit, importez depuis app.models.

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
    ZXING = "ZXing (JPype)" # Préciser JPype pour clarté
    PYLIBDMTX = "pylibdmtx"
    # Ajouter d'autres si besoin (ex: PYZXING, ZBAR)
    NONE = "none"

# --- Fonctions utilitaires (inchangées) ---

def is_gs1_data(raw_data):
    """
    Vérifie si les données sont au format GS1.

    Args:
        raw_data (str): Les données brutes du code-barres

    Returns:
        bool: True si c'est un format GS1
    """
    if not isinstance(raw_data, str): # Vérification type
        return False

    # Motif pour détecter les Application Identifiers GS1 (codes AI)
    # Plus robuste : vérifier la présence d'un AI *valide* au début OU FNC1/GS
    # Liste non exhaustive mais courante
    ai_pattern = r"^(00|01|02|10|11|13|15|17|20|21|240|241|250|251|253|254|255|30|310[0-9]|311[0-9]|37|400|401|410|414|420|422|700[1-3]|800[1-8]|8020|9[0-9])"

    # Le caractère FNC1/GS est l'indicateur le plus fiable pour GS1
    # après décodage (s'il est présent !)
    if '\x1d' in raw_data:
        return True

    # Si FNC1 absent, vérifier si ça commence par un AI connu
    # et contient uniquement des caractères valides pour GS1 (approx)
    # (Chiffres, Lettres majuscules, certains caractères spéciaux -, .)
    if re.match(ai_pattern, raw_data) and re.fullmatch(r"[\dA-Z\-\.\/\x1d]+", raw_data, re.IGNORECASE):
         # Vérification supplémentaire: éviter les URL simples commençant par des chiffres
         if not raw_data.lower().startswith(("http:", "https:", "www.")):
              return True

    # Anciens marqueurs (moins fiables car spécifiques au décodeur source)
    # gs1_indicators = [
    #     re.match(ai_pattern, raw_data) is not None,
    #     '\x1d' in raw_data,
    #     raw_data.startswith("]d2"), # Marqueur DataMatrix AIM
    #     raw_data.startswith("]Q"),  # Marqueur QR AIM
    #     raw_data.startswith("]C1")  # Marqueur Code128 AIM
    # ]
    # return any(gs1_indicators)

    return False


def has_datamatrix_characteristics(raw_data):
    """
    Vérifie si les données présentent des caractéristiques de DataMatrix.
    (Utilisé uniquement si format_hint est absent)

    Args:
        raw_data (str): Les données brutes

    Returns:
        bool: True si les caractéristiques correspondent à un DataMatrix
    """
    if not isinstance(raw_data, str): return False
    # Moins pertinent maintenant, mais on peut le garder comme fallback
    # Vérifier la longueur et la présence de séparateurs non-alphanumériques
    # est un faible indicateur. La présence de FNC1 serait le meilleur.
    return len(raw_data) > 20 and not raw_data.isalnum()


def has_qrcode_characteristics(raw_data):
    """
    Vérifie si les données présentent des caractéristiques de QR Code.
    (Utilisé uniquement si format_hint est absent)

    Args:
        raw_data (str): Les données brutes

    Returns:
        bool: True si les caractéristiques correspondent à un QR Code
    """
    if not isinstance(raw_data, str): return False
    # Les QR Codes contiennent souvent des URLs ou beaucoup de données.
    raw_lower = raw_data.lower()
    return 'http:' in raw_lower or 'https:' in raw_lower or 'www.' in raw_lower or len(raw_data) > 100


def detect_generic_format(raw_data):
    """
    Détecte le format générique d'un code-barres (non-GS1) basé sur le contenu.
    (Utilisé uniquement si format_hint est absent)

    Args:
        raw_data (str): Les données brutes décodées

    Returns:
        BarcodeFormat: Le format détecté
    """
    if not isinstance(raw_data, str): return BarcodeFormat.UNKNOWN

    # Caractéristiques DataMatrix (peu fiable sans FNC1/format_hint)
    if has_datamatrix_characteristics(raw_data):
        return BarcodeFormat.DATAMATRIX

    # Caractéristiques QR Code
    if has_qrcode_characteristics(raw_data):
        return BarcodeFormat.QRCODE

    # Caractéristiques Code 128 (généralement alphanumérique simple ou numérique)
    # Utiliser un regex plus permissif pour Code 128
    if re.fullmatch(r"[\w\s!\"#$%&'()*+,-./:;<=>?@\[\\\]^_`{|}~]+", raw_data):
         # Exclure les cas qui ressemblent trop à DataMatrix/QR
         if not has_datamatrix_characteristics(raw_data) and not has_qrcode_characteristics(raw_data):
               return BarcodeFormat.CODE128

    return BarcodeFormat.UNKNOWN

def calculate_confidence(data, decoder, format_enum):
    """
    Calcule un score de confiance pour la détection.
    Adapté pour tenir compte de la fiabilité de JPype/ZXing.

    Args:
        data (str): Les données décodées
        decoder (DecoderType): Le décodeur utilisé
        format_enum (BarcodeFormat): Le format détecté

    Returns:
        float: Score de confiance (0-1)
    """
    base_score = 0.0
    # Score de base plus élevé si ZXing (JPype) a réussi
    if decoder == DecoderType.ZXING:
        base_score = 0.9
    elif decoder == DecoderType.PYLIBDMTX:
        base_score = 0.7 # pylibdmtx est bon pour DM mais n'a pas donné FNC1
    else:
        base_score = 0.5 # Inconnu ou autre

    # Augmenter la confiance si le format est GS1 et contient FNC1
    if format_enum in [BarcodeFormat.GS1_128, BarcodeFormat.GS1_DATAMATRIX, BarcodeFormat.GS1_QRCODE]:
        if '\x1d' in data:
            base_score = min(base_score + 0.2, 1.0) # Forte indication
        # Augmenter si ça commence par un AI commun
        elif re.match(r"^(01|02|10|11|17|21|30|37|4\d{2})", data):
             base_score = min(base_score + 0.05, 1.0)

    # Si le format est spécifique (non UNKNOWN)
    if format_enum != BarcodeFormat.UNKNOWN:
         base_score = min(base_score + 0.1, 1.0)

    return round(base_score, 2)


def get_barcode_characteristics(data, format_enum):
    """
    Détermine les caractéristiques du code-barres.

    Args:
        data (str): Les données décodées
        format_enum (BarcodeFormat): Le format détecté

    Returns:
        dict: Caractéristiques du code-barres
    """
    if not isinstance(data, str):
         return {"length": 0, "content_type": "unknown", "contains_special_chars": False}

    contains_alpha = any(c.isalpha() for c in data)
    contains_digit = any(c.isdigit() for c in data)
    contains_special = any(not c.isalnum() and not c.isspace() for c in data)
    contains_fnc1 = '\x1d' in data

    content_type = "unknown"
    if contains_alpha and contains_digit:
        content_type = "alphanumeric"
    elif contains_digit and not contains_alpha:
        content_type = "numeric"
    elif contains_alpha and not contains_digit:
        content_type = "alpha"
    elif contains_special: # Si seulement spécial ou espace?
         content_type = "special"


    characteristics = {
        "length": len(data),
        "content_type": content_type,
        "contains_special_chars": contains_special,
        "contains_fnc1": contains_fnc1 # Indiquer si FNC1 a été trouvé
    }

    # Caractéristiques spécifiques aux formats GS1
    if format_enum in [BarcodeFormat.GS1_128, BarcodeFormat.GS1_DATAMATRIX, BarcodeFormat.GS1_QRCODE]:
        # Identifier les AIs potentiels (simple regex au début)
        ai_candidates = re.findall(r"\b(0[012]|1[01357]|21|30|310\d|37|9\d)\d*\b", data)
        characteristics["potential_leading_ais"] = list(set(ai_candidates)) # Liste unique

    return characteristics

# --- Fonction Principale Ajustée ---

def get_decoder_info(raw_data, decoder_used, format_hint=None, verbose=False):
    """
    Génère des informations détaillées sur le décodage.
    Version améliorée qui utilise l'indication de format du décodeur (format_hint).

    Args:
        raw_data (str): Les données décodées
        decoder_used (DecoderType): Le décodeur qui a réussi (Enum)
        format_hint (str, optional): Indication du format par le décodeur (ex: "DATA_MATRIX").
        verbose (bool): Si True, inclut des informations supplémentaires

    Returns:
        dict: Informations sur le décodage (structure compatible avec models.DecoderInfo)
    """
    detected_format = BarcodeFormat.UNKNOWN # Default
    is_gs1 = is_gs1_data(raw_data) # Vérifier si les données contiennent des indicateurs GS1

    # 1. Utiliser l'indice de format si disponible (prioritaire)
    if format_hint:
        format_hint_upper = format_hint.upper().replace("_", "") # Normaliser (DATA_MATRIX -> DATAMATRIX)
        if format_hint_upper == "DATAMATRIX":
            detected_format = BarcodeFormat.GS1_DATAMATRIX if is_gs1 else BarcodeFormat.DATAMATRIX
        elif format_hint_upper == "QRCODE":
            detected_format = BarcodeFormat.GS1_QRCODE if is_gs1 else BarcodeFormat.QRCODE
        elif format_hint_upper == "CODE128":
            detected_format = BarcodeFormat.GS1_128 if is_gs1 else BarcodeFormat.CODE128
        # Ajouter d'autres mappages si nécessaire (UPC_A, EAN_13...)
        # else: # Si format_hint non reconnu, on passe à l'étape 2
        #     pass

    # 2. Si pas d'indice ou indice non mappé, utiliser la détection basée sur le contenu
    #    Seulement si on n'a pas déjà un format défini par le hint.
    if detected_format == BarcodeFormat.UNKNOWN:
        if is_gs1:
            # Essayer de deviner basé sur les caractéristiques (moins fiable)
            if has_datamatrix_characteristics(raw_data):
                detected_format = BarcodeFormat.GS1_DATAMATRIX
            elif has_qrcode_characteristics(raw_data):
                detected_format = BarcodeFormat.GS1_QRCODE
            else: # Par défaut pour GS1 linéaire ou inconnu
                detected_format = BarcodeFormat.GS1_128
        else:
            # Détecter le format générique non-GS1
            detected_format = detect_generic_format(raw_data)

    # Assurer un fallback final
    if detected_format == BarcodeFormat.UNKNOWN and is_gs1:
        # Si on sait que c'est GS1 mais format inconnu, on met un format GS1 générique? Non, vaut mieux UNKNOWN.
        pass
    elif detected_format == BarcodeFormat.UNKNOWN and not is_gs1:
         detected_format = BarcodeFormat.UNKNOWN # Reste unknown


    # Construire le dictionnaire de retour
    info = {
        "decoder": decoder_used.value,
        "format": detected_format.value,
        "is_gs1": detected_format in [BarcodeFormat.GS1_128, BarcodeFormat.GS1_DATAMATRIX, BarcodeFormat.GS1_QRCODE]
    }

    # Informations supplémentaires en mode verbose
    if verbose:
        info["confidence"] = calculate_confidence(raw_data, decoder_used, detected_format)
        info["characteristics"] = get_barcode_characteristics(raw_data, detected_format)

    return info

# --- FIN DU FICHIER barcode_detector.py ---