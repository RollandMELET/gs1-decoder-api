#!/usr/bin/env python3
"""
Script de test pour le module gs1_parser
"""

from app.gs1_parser import parse_gs1, normalize_gs1_data, format_date, format_decimal_value, is_valid_gtin

def test_normalize_gs1_data():
    """Teste la fonction de normalisation des données GS1"""
    print("\n=== Test de normalize_gs1_data ===")
    
    test_cases = [
        # Format brut, résultat attendu
        ("]d201030123456789.103456", "01030123456789\x1d103456"),
        ("01030123456789|103456", "01030123456789\x1d103456"),
        ("01030123456789<GS>103456", "01030123456789\x1d103456"),
        ("01030123456789[FNC1]103456", "01030123456789\x1d103456"),
        ("01030123456789~103456", "01030123456789\x1d103456"),
    ]
    
    for input_data, expected in test_cases:
        result = normalize_gs1_data(input_data)
        # Afficher les bytes pour visualiser les caractères spéciaux
        print(f"Input: {repr(input_data)}")
        print(f"Output: {repr(result)}")
        print(f"Expected: {repr(expected)}")
        print(f"Test {'OK' if result == expected else 'ÉCHEC'}\n")

def test_format_date():
    """Teste la fonction de formatage des dates"""
    print("\n=== Test de format_date ===")
    
    test_cases = [
        # Date GS1, résultat attendu
        ("230503", "2023-05-03"),
        ("990101", "1999-01-01"),
        ("000229", "2000-02-29"),
        ("230532", "230532"),  # Date invalide (jour > 31)
        ("231345", "231345"),  # Date invalide (mois > 12)
        ("abcdef", "abcdef"),  # Non numérique
    ]
    
    for input_date, expected in test_cases:
        result = format_date(input_date)
        print(f"Input: {input_date}")
        print(f"Output: {result}")
        print(f"Expected: {expected}")
        print(f"Test {'OK' if result == expected else 'ÉCHEC'}\n")

def test_format_decimal_value():
    """Teste la fonction de formatage des valeurs décimales"""
    print("\n=== Test de format_decimal_value ===")
    
    test_cases = [
        # Valeur, position décimale, résultat attendu
        ("12345", 2, "123.45"),
        ("5", 2, "0.05"),
        ("50", 1, "5"),
        ("5000", 3, "5"),
        ("123456", 0, "123456"),
        ("abc", 2, "abc"),  # Non numérique
    ]
    
    for input_val, decimal_pos, expected in test_cases:
        result = format_decimal_value(input_val, decimal_pos)
        print(f"Input: {input_val}, pos: {decimal_pos}")
        print(f"Output: {result}")
        print(f"Expected: {expected}")
        print(f"Test {'OK' if result == expected else 'ÉCHEC'}\n")

def test_is_valid_gtin():
    """Teste la fonction de validation des GTIN"""
    print("\n=== Test de is_valid_gtin ===")
    
    test_cases = [
        # GTIN, valid?
        ("01234565", True),  # GTIN-8 valide
        ("590123412345", True),  # GTIN-12 valide
        ("5901234123457", True),  # GTIN-13 valide (EAN-13)
        ("00012345678905", True),  # GTIN-14 valide
        ("12345678901234", False),  # GTIN-14 invalide
        ("1234567", False),  # Trop court
        ("abcdefghijklmn", False),  # Non numérique
    ]
    
    for gtin, expected in test_cases:
        result = is_valid_gtin(gtin)
        print(f"GTIN: {gtin}")
        print(f"Valid: {result}")
        print(f"Expected: {expected}")
        print(f"Test {'OK' if result == expected else 'ÉCHEC'}\n")

def test_parse_gs1():
    """Teste la fonction parse_gs1 avec divers types d'entrées"""
    print("\n=== Test de parse_gs1 ===")
    
    test_cases = [
        # Entrée GS1, mode verbose, attente d'au moins X éléments
        ("01030123456789\x1d10ABC123\x1d21Serial123", False, 3),
        ("01030123456789\x1d10ABC123\x1d21Serial123", True, 3),
        ("01003024688761231035PK132100abcd", False, 3),
        ("]d2010030246887612310P3Q0VF21ABCD", False, 3),
        ("310012345", False, 1),  # Poids en kg sans décimale
        ("31012345", False, 1),   # Poids en kg avec 1 décimale
        ("3102987654", False, 1),  # Poids en kg avec 2 décimales
        ("17230503", False, 1),    # Date d'expiration
    ]
    
    for input_gs1, verbose, min_elements in test_cases:
        result = parse_gs1(input_gs1, verbose)
        print(f"Input: {repr(input_gs1)}")
        print(f"Verbose: {verbose}")
        print(f"Result: {result}")
        
        if verbose:
            success = len(result) >= min_elements
        else:
            success = len(result.keys()) >= min_elements
        
        print(f"Test {'OK' if success else 'ÉCHEC'}\n")

if __name__ == "__main__":
    print("=== Tests du module gs1_parser ===")
    test_normalize_gs1_data()
    test_format_date()
    test_format_decimal_value()
    test_is_valid_gtin()
    test_parse_gs1()
    print("=== Fin des tests ===")
