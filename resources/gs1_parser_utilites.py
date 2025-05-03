"""
GS1 Parser Utilities

Fonctions utilitaires pour le décodage et le parsing des codes-barres GS1.
Basé sur les spécifications officielles GS1:
https://www.gs1.org/standards/barcodes/application-identifiers

Ce module contient:
- Fonctions pour extraire et interpréter les Application Identifiers (AI)
- Fonctions pour formater les données selon leur type (dates, poids, etc.)
- Fonctions de normalisation des séparateurs GS1

"""

import json
import os
import re
from datetime import datetime

# Chemin vers le fichier JSON contenant les AI GS1
GS1_AI_PATH = os.path.join(os.path.dirname(__file__), "gs1_application_identifiers.json")

def load_ai_table():
    """
    Charge la table des Application Identifiers depuis le fichier JSON.
    
    Returns:
        dict: Table des AI GS1
    """
    try:
        with open(GS1_AI_PATH, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Erreur lors du chargement des AI GS1: {e}")
        return {}

# Table des AI
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

def find_ai_match(data, start_pos):
    """
    Recherche un AI correspondant dans la chaîne de données à partir d'une position.
    
    Args:
        data (str): Les données GS1
        start_pos (int): Position de départ pour la recherche
        
    Returns:
        tuple: (ai, name, length, is_variable, decimal_position)
    """
    # Essayer d'abord les AIs à 4 chiffres
    if start_pos + 4 <= len(data):
        ai_4 = data[start_pos:start_pos+4]
        if ai_4 in AI_TABLE:
            ai_info = AI_TABLE[ai_4]
            return (ai_4, ai_info["name"], ai_info["length"], 
                   not ai_info.get("fixed_length", True), 
                   ai_info.get("decimal_position", None))
    
    # Ensuite les AIs à 3 chiffres
    if start_pos + 3 <= len(data):
        ai_3 = data[start_pos:start_pos+3]
        if ai_3 in AI_TABLE:
            ai_info = AI_TABLE[ai_3]
            return (ai_3, ai_info["name"], ai_info["length"], 
                   not ai_info.get("fixed_length", True), 
                   ai_info.get("decimal_position", None))
    
    # Ensuite les AIs à 2 chiffres
    if start_pos + 2 <= len(data):
        ai_2 = data[start_pos:start_pos+2]
        if ai_2 in AI_TABLE:
            ai_info = AI_TABLE[ai_2]
            return (ai_2, ai_info["name"], ai_info["length"], 
                   not ai_info.get("fixed_length", True), 
                   ai_info.get("decimal_position", None))
    
    # Gestion des AIs spéciaux avec chiffre décimal (310y-319y)
    if start_pos + 4 <= len(data):
        prefix = data[start_pos:start_pos+3]
        if prefix in ["310", "311", "312", "313", "314", "315", "316", 
                      "320", "321", "322", "323", "324", "325", "326"]:
            digit = data[start_pos+3:start_pos+4]
            if digit.isdigit():
                ai = prefix + digit
                ai_template = prefix + "y"
                if ai_template in AI_TABLE:
                    ai_info = AI_TABLE[ai_template]
                    return (ai, ai_info["name"], ai_info["length"], 
                           not ai_info.get("fixed_length", True), 
                           int(digit))
    
    return (None, None, None, None, None)

def format_ai_value(ai, value):
    """
    Formate une valeur selon son AI.
    
    Args:
        ai (str): L'identifiant d'application
        value (str): La valeur brute
        
    Returns:
        str: La valeur formatée
    """
    # Dates (format YYMMDD)
    if ai in ["11", "12", "13", "15", "16", "17"]:
        return format_date(value)
    
    # Valeurs décimales (AIs 310y-316y, etc.)
    if ai.startswith("31") and len(ai) == 4 and ai[3].isdigit():
        return format_decimal_value(value, int(ai[3]))
    
    # Par défaut, retourner la valeur telle quelle
    return value

def detect_barcode_format(raw_data):
    """
    Tente de détecter le format du code-barres basé sur les données brutes.
    
    Args:
        raw_data (str): Les données brutes du code-barres
        
    Returns:
        str: Le format probable du code-barres
    """
    # GS1-128 commence généralement par un AI
    if re.match(r"^(00|01|02|10|11|13|15|17|20|21|240|241|250|30|310|320|400|401|402|410|411|412|413|414|420|421|422|423|424|425|426|700|710|711|712|713|720|723|730|740|750|760|7001|7002|7003|7004|7005|7006|7007|7008|7009|7010|7020|7021|7022|7023|7030|7031|7032|7033|7034|7035|7036|7037|7038|7039|7040|8001|8002|8003|8004|8005|8006|8007|8008|8010|8011|8012|8017|8018|8019|8020|8110|8111|8112|8200|90|91|92|93|94|95|96|97|98|99)", raw_data):
        return "GS1-128"
    
    # QR Code GS1
    if raw_data.startswith("]Q3") or raw_data.startswith("]d2"):
        return "GS1 QR Code"
    
    # DataMatrix GS1
    if raw_data.startswith("]d2") or (len(raw_data) > 2 and raw_data[0] == '\u001d'):
        return "GS1 DataMatrix"
    
    # Format inconnu
    return "Unknown"

def get_decoder_info():
    """
    Retourne des informations sur le décodeur GS1 actuel.
    
    Returns:
        dict: Informations sur le décodeur
    """
    return {
        "version": "1.0.0",
        "supported_ais": len(AI_TABLE),
        "supported_formats": ["GS1-128", "GS1 DataMatrix", "GS1 QR Code"]
    }
