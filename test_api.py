#!/usr/bin/env python3
"""
Script de test pour l'API GS1-Decoder
Teste l'endpoint /decode/ avec une image d'un code DataMatrix
"""

import requests
import sys
import json
from pprint import pprint
import os

# URL de l'API (par défaut locale, mais peut être passée en argument)
API_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

def test_health():
    """Teste l'endpoint /health"""
    print("\n=== Test de l'endpoint /health ===")
    response = requests.get(f"{API_URL}/health")
    
    if response.status_code == 200:
        print("✅ L'API est en ligne")
        print("Réponse:")
        pprint(response.json())
    else:
        print(f"❌ Erreur: {response.status_code}")
        print(response.text)

def test_decode(image_path, verbose=False):
    """Teste l'endpoint /decode/ avec une image"""
    print(f"\n=== Test de /decode/ avec {os.path.basename(image_path)} (verbose={verbose}) ===")
    
    if not os.path.exists(image_path):
        print(f"❌ Erreur: Le fichier {image_path} n'existe pas")
        return
    
    # Préparation de la requête
    with open(image_path, "rb") as image_file:
        files = {"file": (os.path.basename(image_path), image_file, "image/jpeg")}
        data = {"verbose": str(verbose).lower()}
        
        # Envoi de la requête
        response = requests.post(f"{API_URL}/decode/", files=files, data=data)
    
    # Analyse de la réponse
    if response.status_code == 200:
        print("✅ Décodage réussi")
        result = response.json()
        print(f"Nombre de codes-barres détectés: {len(result['barcodes'])}")
        
        for i, barcode in enumerate(result['barcodes']):
            print(f"\n--- Code-barres #{i+1} ---")
            print(f"Format: {barcode['decoder_info']['format']}")
            print(f"Décodeur: {barcode['decoder_info']['decoder']}")
            print("\nDonnées brutes:")
            print(barcode['raw'])
            
            print("\nDonnées parsées:")
            if verbose:
                for ai in barcode['parsed']:
                    print(f"{ai['ai']} ({ai['name']}): {ai['value']}")
            else:
                for name, value in barcode['parsed'].items():
                    print(f"{name}: {value}")
    else:
        print(f"❌ Erreur: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # Test de l'endpoint /health
    test_health()
    
    # Test de l'endpoint /decode/ avec différentes images
    test_images = [
        "testDatamatrix-1.jpg",  # Image de test fournie avec le projet
        "imagetest.jpg",         # Autre image de test du projet
    ]
    
    for image_path in test_images:
        test_decode(image_path, verbose=False)
        test_decode(image_path, verbose=True)
    
    print("\n=== Tests terminés ===")
