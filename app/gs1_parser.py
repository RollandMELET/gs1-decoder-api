"""
Module de parsing GS1 amélioré
Utilise les données complètes des AI depuis le fichier JSON
Version 1.1.0 avec support étendu des AI
"""

import os
import json
import re
from datetime import datetime

# Chemin vers le fichier JSON contenant les AI GS1
GS1_AI_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "gs1_application_identifiers.json")

def load_ai_table():
    """
    Charge la table des Application Identifiers depuis le fichier JSON.
    
    Returns:
        dict: Table des AI GS1
    """
    try:
        with open(GS1_AI_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement des AI GS1: {e}")
        # Table minimale par défaut en cas d'erreur
        return {
            "01": {"name": "GTIN", "length": 14, "fixed_length": True},
            "10": {"name": "BATCH", "length": 20, "fixed_length": False},
            "21": {"name": "SERIAL", "length": 20, "fixed_length": False},
            "90": {"name": "INTERNAL", "length": 30, "fixed_length": False},
        }

# Charger la table des AI
AI_TABLE = load_ai_table()

def normalize_gs1_data(data):
    """
    Normalise les données GS1 en remplaçant les séparateurs
    par des symboles standards et en nettoyant les préfixes spécifiques.
    
    Args:
        data (str): Les données GS1 brutes
        
    Returns:
        str: Les données normalisées
    """
    # Nettoyer les préfixes de format connus
    prefix_patterns = [
        r"^\]d2",     # Format ]d2 (DataMatrix)
        r"^\]Q\d",    # Format ]Qn (comme ]Q1)
        r"^\]C\d",    # Format ]Cn (comme ]C1)
    ]
    
    normalized = data
    for pattern in prefix_patterns:
        match = re.match(pattern, normalized)
        if match:
            normalized = normalized[match.end():]
            break
    
    # Dictionnaire des séparateurs connus et leur remplacement
    separators = {
        # ASCII GS (Group Separator)
        '\x1d': '\x1d',
        
        # Séparateurs courants dans différents systèmes
        '<GS>': '\x1d',
        '<gs>': '\x1d',
        '.': '\x1d',
        '|': '\x1d',
        '\\': '\x1d',
        '^': '\x1d',
        '~': '\x1d',
        
        # Certains décodeurs utilisent ces formats
        '[FNC1]': '\x1d',
        '(FNC1)': '\x1d',
        '{FNC1}': '\x1d',
        'FNC': '\x1d',
        'fnc': '\x1d'
    }
    
    # Remplacer tous les séparateurs connus
    for sep, replacement in separators.items():
        normalized = normalized.replace(sep, replacement)
    
    return normalized

def format_date(value):
    """
    Formate une date GS1 (YYMMDD) en format lisible.
    Version améliorée avec validation.
    
    Args:
        value (str): La date au format YYMMDD
        
    Returns:
        str: Date formatée (YYYY-MM-DD)
    """
    if not value or len(value) != 6 or not value.isdigit():
        return value
    
    # Extraire les composants de la date
    year = value[0:2]
    month = value[2:4]
    day = value[4:6]
    
    # Valider les composants (validation basique)
    if not (1 <= int(month) <= 12 and 1 <= int(day) <= 31):
        return value  # Date non valide, retourner la valeur d'origine
    
    # Formatter la date
    return f"20{year}-{month}-{day}" if int(year) < 50 else f"19{year}-{month}-{day}"

def format_decimal_value(value, decimal_position):
    """
    Formate une valeur numérique avec point décimal.
    Version améliorée avec gestion des cas limite.
    
    Args:
        value (str): La valeur numérique
        decimal_position (int): Position du point décimal
        
    Returns:
        str: Valeur formatée avec un point décimal
    """
    if not value or not value.isdigit():
        return value
    
    # Si la position décimale est 0, retourner tel quel
    if decimal_position == 0:
        return value
    
    # Ajouter des zéros en tête si nécessaire
    if len(value) <= decimal_position:
        value = '0' * (decimal_position - len(value) + 1) + value
    
    # Insérer le point décimal
    formatted = value[:-decimal_position] + '.' + value[-decimal_position:] if decimal_position > 0 else value
    
    # Supprimer les zéros en fin de nombre et le point si c'est un entier
    formatted = formatted.rstrip('0').rstrip('.') if '.' in formatted else formatted
    
    return formatted

def parse_gs1(data, verbose=False):
    """
    Parse un code GS1 et extrait les identifiants d'application.
    Version améliorée qui utilise la table complète des AI et gère mieux les formats spéciaux.
    
    Args:
        data (str): Le code GS1 brut
        verbose (bool): Si True, retourne les détails complets
        
    Returns:
        dict ou list: Les données parsées
    """
    # Validation des entrées
    if not data:
        return [] if verbose else {}
    
    # S'assurer que la donnée est une chaîne
    if not isinstance(data, str):
        try:
            data = str(data)
        except:
            return [] if verbose else {}
    
    # Normaliser les données.
    # Cas du format lisible parenthésé (AI)valeur(AI)valeur... : le découper
    # proprement en une forme concaténée séparée par le GS, que la boucle
    # standard parse ensuite (les valeurs variables sont coupées au bon endroit).
    # On bypasse normalize_gs1_data ici car son remplacement '.'->GS corromprait
    # les valeurs du format lisible.
    stripped = data.strip()
    if stripped.startswith("(") and re.fullmatch(r"(?:\(\d{2,4}\)[^(]*)+", stripped):
        segments = re.findall(r"\((\d{2,4})\)([^(]*)", stripped)
        data = "\x1d".join(ai + value for ai, value in segments)
    else:
        data = normalize_gs1_data(data)
    
    parsed = []
    simple_parsed = {}
    i = 0
    
    # Éviter les boucles infinies
    max_iterations = len(data) * 2
    iterations = 0
    
    while i < len(data) and iterations < max_iterations:
        iterations += 1
        
        # Si on est à la fin de la chaîne, sortir
        if i >= len(data):
            break
            
        # Si on trouve un séparateur Group Separator, passer au caractère suivant
        if data[i] == '\x1d':
            i += 1
            continue
            
        # Chercher l'AI le plus long possible
        ai = None
        ai_length = 0
        
        # Essayer d'abord les AIs de 4 chiffres
        if i + 4 <= len(data) and data[i:i+4].isdigit():
            candidate = data[i:i+4]
            if candidate in AI_TABLE:
                ai = candidate
                ai_length = 4
        
        # Gestion spéciale des AIs avec position décimale (310n-319n)
        if not ai and i + 4 <= len(data) and data[i:i+3].isdigit() and data[i+3:i+4].isdigit():
            prefix = data[i:i+3]
            digit = data[i+3:i+4]
            if prefix.startswith(('31', '32', '33', '34', '35', '36')):
                ai_template = prefix + "y"
                if ai_template in AI_TABLE or prefix in AI_TABLE:
                    ai = prefix + digit
                    ai_length = 4
        
        # Puis les AIs de 3 chiffres
        if not ai and i + 3 <= len(data) and data[i:i+3].isdigit():
            candidate = data[i:i+3]
            if candidate in AI_TABLE:
                ai = candidate
                ai_length = 3
        
        # Puis les AIs de 2 chiffres
        if not ai and i + 2 <= len(data) and data[i:i+2].isdigit():
            candidate = data[i:i+2]
            if candidate in AI_TABLE:
                ai = candidate
                ai_length = 2
        
        # Si aucun AI n'est trouvé, on avance d'un caractère
        if not ai:
            i += 1
            continue
        
        # Extraire les informations sur l'AI
        ai_info = AI_TABLE.get(ai, AI_TABLE.get(ai[:3] + "y", {}))
        ai_name = ai_info.get("name", "Unknown")
        ai_length_max = ai_info.get("length", 0)
        is_variable = not ai_info.get("fixed_length", True)
        decimal_position = ai_info.get("decimal_position", None)
        
        # Déterminer la position décimale pour les AIs de type 3XXy
        if ai.startswith('3') and len(ai) == 4 and decimal_position is None:
            # Le dernier chiffre de l'AI indique la position décimale
            decimal_position = int(ai[3])
        
        # Avancer au-delà de l'AI
        i += ai_length
        
        # Extraire la valeur selon que l'AI est à longueur fixe ou variable
        if is_variable:
            # Chercher le séparateur FNC1 (Group Separator)
            separator_pos = data.find('\x1d', i)
            if separator_pos == -1:
                value = data[i:]
                i = len(data)
            else:
                value = data[i:separator_pos]
                i = separator_pos + 1  # Avancer après le séparateur
        else:
            # Pour les AIs à longueur fixe
            value_length = min(ai_length_max, len(data) - i)
            value = data[i:i+value_length]
            i += value_length
        
        # Formater la valeur selon le type d'AI
        if ai.startswith(('11', '12', '13', '15', '16', '17')):
            # Dates
            value = format_date(value)
        elif decimal_position is not None:
            # Valeurs décimales
            value = format_decimal_value(value, decimal_position)
        
        # Vérifier la validité pour certains types d'AI
        is_valid = True
        if ai == "01" and value.isdigit() and len(value) in (8, 12, 13, 14):
            # GTIN : normaliser vers 14 chiffres puis vérifier le chiffre de contrôle
            value = pad_gtin14(value)
            is_valid = is_valid_gtin(value)
        
        # Enregistrer le résultat
        if verbose:
            # gtin14 : champ additif, renseigné pour l'AI 01 (GTIN normalisé sur 14
            # chiffres via pad_gtin14 plus haut), None pour les autres AI.
            parsed.append({
                "ai": ai,
                "name": ai_name,
                "value": value,
                "valid": is_valid,
                "gtin14": value if ai == "01" else None,
            })
        else:
            simple_parsed[ai_name] = value
    
    return parsed if verbose else simple_parsed

def is_valid_gtin(gtin):
    """
    Vérifie si un GTIN est valide en calculant son chiffre de contrôle (GS1 mod-10).

    L'algorithme GS1 est identique pour toutes les longueurs (8, 12, 13, 14) :
    parcourir le corps (tous les chiffres sauf le dernier) de droite à gauche,
    en appliquant le poids 3 sur le chiffre le plus à droite du corps, puis
    1, 3, 1... en alternance vers la gauche.

    Args:
        gtin (str): Le GTIN à vérifier

    Returns:
        bool: True si le GTIN est valide
    """
    if not gtin or not gtin.isdigit():
        return False

    # Longueurs valides pour un GTIN
    if len(gtin) not in (8, 12, 13, 14):
        return False

    # Corps = tous les chiffres sauf le chiffre de contrôle (dernier)
    digits = [int(d) for d in gtin[:-1]]

    # Parcours de droite à gauche - index 0 = chiffre le plus à droite du corps (poids 3)
    weighted_sum = sum(d * (3 if i % 2 == 0 else 1) for i, d in enumerate(reversed(digits)))

    # Calculer le chiffre de contrôle attendu
    calculated = (10 - (weighted_sum % 10)) % 10

    # Vérifier si le chiffre calculé correspond au dernier chiffre du GTIN
    return calculated == int(gtin[-1])


def pad_gtin14(value):
    """
    Normalise un GTIN court (8, 12, 13 chiffres) vers 14 chiffres par zéro-padding à gauche.
    Un GTIN-14 est renvoyé inchangé. L'AI (01) de GS1 impose toujours 14 positions.

    Args:
        value (str): un GTIN de longueur 8, 12, 13 ou 14, uniquement des chiffres.

    Returns:
        str: le GTIN normalisé sur 14 chiffres.

    Raises:
        ValueError: si value n'est pas numérique ou n'a pas une longueur GTIN légale.
    """
    if not value or not value.isdigit() or len(value) not in (8, 12, 13, 14):
        raise ValueError(f"GTIN invalide, longueur ou format illegal : {value!r}")
    return value.zfill(14)


def gtin_indicator(value):
    """
    Renvoie le chiffre indicateur d'un GTIN : le 1er chiffre du GTIN-14 normalisé.

    Args:
        value (str): un GTIN de longueur 8, 12, 13 ou 14.

    Returns:
        str: un seul caractère, le chiffre indicateur.

    Raises:
        ValueError: propagé depuis pad_gtin14 si value est illégal.
    """
    return pad_gtin14(value)[0]
