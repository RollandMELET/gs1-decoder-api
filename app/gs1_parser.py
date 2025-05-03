"""
Module de parsing GS1 amélioré
Utilise les données complètes des AI depuis le fichier JSON
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
    par des symboles standards.
    
    Args:
        data (str): Les données GS1 brutes
        
    Returns:
        str: Les données normalisées
    """
    # Remplacer les séparateurs connus par le caractère GS standard
    separators = ['.', '|', '\\']
    normalized = data
    for sep in separators:
        normalized = normalized.replace(sep, '\x1d')
    
    return normalized

def format_date(value):
    """
    Formate une date GS1 (YYMMDD) en format lisible.
    
    Args:
        value (str): La date au format YYMMDD
        
    Returns:
        str: Date formatée (YY-MM-DD)
    """
    if len(value) == 6 and value.isdigit():
        return f"{value[0:2]}-{value[2:4]}-{value[4:6]}"
    return value

def format_decimal_value(value, decimal_position):
    """
    Formate une valeur numérique avec point décimal.
    
    Args:
        value (str): La valeur numérique
        decimal_position (int): Position du point décimal
        
    Returns:
        str: Valeur formatée avec un point décimal
    """
    if not value.isdigit():
        return value
    
    # Si la position décimale est 0, retourner tel quel
    if decimal_position == 0:
        return value
    
    # Ajouter des zéros en tête si nécessaire
    if len(value) <= decimal_position:
        value = '0' * (decimal_position - len(value) + 1) + value
    
    # Insérer le point décimal
    formatted = value[:-decimal_position] + '.' + value[-decimal_position:] if decimal_position > 0 else value
    return formatted

def parse_gs1(data, verbose=False):
    """
    Parse un code GS1 et extrait les identifiants d'application.
    Version améliorée qui utilise la table complète des AI.
    
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
    
    # Normaliser les données
    data = normalize_gs1_data(data)
    
    parsed = []
    simple_parsed = {}
    i = 0
    
    # Éviter les boucles infinies
    max_iterations = len(data) * 2
    iterations = 0
    
    while i < len(data) and iterations < max_iterations:
        iterations += 1
        
        # Chercher l'AI le plus long possible
        ai = None
        ai_length = 0
        
        # Essayer d'abord les AIs de 4 chiffres
        if i + 4 <= len(data):
            candidate = data[i:i+4]
            if candidate in AI_TABLE:
                ai = candidate
                ai_length = 4
        
        # Puis les AIs de 3 chiffres
        if not ai and i + 3 <= len(data):
            candidate = data[i:i+3]
            if candidate in AI_TABLE:
                ai = candidate
                ai_length = 3
        
        # Puis les AIs de 2 chiffres
        if not ai and i + 2 <= len(data):
            candidate = data[i:i+2]
            if candidate in AI_TABLE:
                ai = candidate
                ai_length = 2
        
        # Gestion spéciale des AIs avec position décimale (310n-319n)
        if not ai and i + 4 <= len(data):
            prefix = data[i:i+3]
            digit = data[i+3:i+4]
            if prefix.startswith('31') and digit.isdigit():
                ai_template = prefix + "y"
                if ai_template in AI_TABLE:
                    ai = prefix + digit
                    ai_length = 4
        
        # Si aucun AI n'est trouvé, on avance d'un caractère
        if not ai:
            i += 1
            continue
        
        # Extraire les informations sur l'AI
        ai_info = AI_TABLE[ai]
        ai_name = ai_info.get("name", "Unknown")
        ai_length_max = ai_info.get("length", 0)
        is_variable = not ai_info.get("fixed_length", True)
        decimal_position = ai_info.get("decimal_position", None)
        
        # Avancer au-delà de l'AI
        i += ai_length
        
        # Extraire la valeur selon que l'AI est à longueur fixe ou variable
        if is_variable:
            # Chercher le séparateur FNC1
            separator_pos = data.find('\x1d', i)
            if separator_pos == -1:
                value = data[i:]
                i = len(data)
            else:
                value = data[i:separator_pos]
                i = separator_pos + 1
        else:
            # Pour les AIs à longueur fixe
            value_length = min(ai_length_max, len(data) - i)
            value = data[i:i+value_length]
            i += value_length
        
        # Formater la valeur selon le type d'AI
        if ai.startswith('11') or ai.startswith('13') or ai.startswith('15') or ai.startswith('17'):
            # Dates
            value = format_date(value)
        elif decimal_position is not None:
            # Valeurs décimales
            value = format_decimal_value(value, decimal_position)
        
        # Enregistrer le résultat
        if verbose:
            parsed.append({"ai": ai, "name": ai_name, "value": value})
        else:
            simple_parsed[ai_name] = value
    
    return parsed if verbose else simple_parsed