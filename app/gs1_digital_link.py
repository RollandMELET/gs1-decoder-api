"""Parsing des URI GS1 Digital Link.

Convertit une URI Digital Link (ex. https://id.gs1.org/01/09521234543213/21/XYZ)
en une forme concaténée séparée par le GS, réutilisable par le parseur GS1 existant.
Supporte le chemin (path), la query string, les alias courts officiels GS1
(gtin, lot, ser...) et un préfixe de chemin sur domaine custom.
"""
import re
from urllib.parse import urlsplit, unquote, parse_qsl

from app.gs1_parser import pad_gtin14

# Garde anti-DoS : longueur maximale d'URI acceptée.
_MAX_URI_LEN = 4096

# Alias courts officiels GS1 Digital Link (source : GS1 DigitalLinkToolkit.js,
# champ shortcode de l'aitable). Sensibles à la casse, définis en minuscules.
_SHORT_CODES = {
    "sscc": "00", "gtin": "01", "lot": "10", "exp": "17", "ser": "21",
    "cpv": "22", "gdti": "253", "glnx": "254", "gcn": "255", "ginc": "401",
    "gsin": "402", "gln": "414", "payto": "415", "expdt": "7003",
    "grai": "8003", "giai": "8004", "itip": "8006", "cpid": "8010",
    "cpsn": "8011", "gsrnp": "8017", "gsrn": "8018", "srin": "8019",
}


def _resolve_ai(key):
    """Résout une clé de segment ou d'attribut Digital Link vers un AI numérique.

    Accepte un AI numérique de 2 à 4 chiffres tel quel, ou un alias court officiel
    (sensible à la casse). Renvoie None si la clé n'est pas un AI reconnu.
    """
    if key.isdigit() and 2 <= len(key) <= 4:
        return key
    return _SHORT_CODES.get(key)


def _path_pairs(path):
    """Extrait les paires (AI, valeur) du chemin d'une URI Digital Link.

    Ignore un éventuel préfixe : on démarre au premier segment qui résout en AI,
    puis on apparie (clé, valeur) deux par deux. S'arrête à la première clé non
    résolue (chemin malformé) ou sur un segment orphelin final.
    """
    segments = [seg for seg in path.split("/") if seg]
    start = next(
        (i for i, seg in enumerate(segments) if _resolve_ai(seg) is not None),
        None,
    )
    pairs = []
    if start is None:
        return pairs
    tokens = segments[start:]
    j = 0
    while j + 1 < len(tokens):
        ai = _resolve_ai(tokens[j])
        if ai is None:
            break
        pairs.append((ai, unquote(tokens[j + 1])))
        j += 2
    return pairs


def is_digital_link(s):
    """True si s ressemble à une URI GS1 Digital Link.

    Conditions : chaîne http(s), non vide, longueur bornée, et le chemin contient
    au moins une paire AI/valeur (AI numérique 2-4 chiffres ou alias court officiel).
    """
    if not isinstance(s, str) or not s or len(s) > _MAX_URI_LEN:
        return False
    if not re.match(r"https?://", s, re.IGNORECASE):
        return False
    return bool(_path_pairs(urlsplit(s).path))


def digital_link_to_gs1_string(uri):
    """Convertit une URI Digital Link en forme concaténée séparée par le GS (\\x1d).

    Traite le chemin puis la query string. Résout les alias courts officiels GS1.
    L'AI 01 (GTIN) est normalisé vers 14 chiffres via pad_gtin14. Les valeurs
    pourcent-encodées sont décodées.

    Raises:
        ValueError: si uri n'est pas une URI GS1 Digital Link.
    """
    if not is_digital_link(uri):
        raise ValueError(f"URI GS1 Digital Link invalide : {uri!r}")
    parts = urlsplit(uri)
    pairs = list(_path_pairs(parts.path))
    # Data attributes de la query string. parse_qsl décode déjà le pourcent-encodage.
    for key, value in parse_qsl(parts.query, keep_blank_values=False):
        ai = _resolve_ai(key)
        if ai is not None:
            pairs.append((ai, value))
    segments = []
    for ai, value in pairs:
        if ai == "01":
            value = pad_gtin14(value)
        segments.append(ai + value)
    return "\x1d".join(segments)
