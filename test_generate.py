#!/usr/bin/env python3
"""
Script de test pour l'endpoint de génération de codes-barres de l'API GS1-Decoder
"""

import requests
import sys
import json
import os
from PIL import Image
import io

# URL de l'API (par défaut locale, mais peut être passée en argument)
API_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

def save_image(image_data, filename):
    """Sauvegarde les données d'image dans un fichier"""
    with open(filename, "wb") as f:
        f.write(image_data)
    print(f"✅ Image sauvegardée: {filename}")

def test_generate_barcode(data, barcode_format, image_format="png", width=300, height=300):
    """
    Teste l'endpoint /generate/ avec différents paramètres
    
    Args:
        data (str): Données à encoder
        barcode_format (str): Format du code-barres
        image_format (str): Format de l'image (png, jpeg, svg)
        width (int): Largeur de l'image
        height (int): Hauteur de l'image
    """
    print(f"\n=== Test de génération de code-barres ===")
    print(f"Format: {barcode_format}")
    print(f"Données: {data}")
    print(f"Format d'image: {image_format}")
    print(f"Dimensions: {width}x{height}")
    
    # Préparation de la requête JSON
    payload = {
        "data": data,
        "format": barcode_format,
        "image_format": image_format,
        "width": width,
        "height": height
    }
    
    # Envoi de la requête
    response = requests.post(
        f"{API_URL}/generate/", 
        json=payload,
        headers={"Accept": f"image/{image_format}"}
    )
    
    # Analyse de la réponse
    if response.status_code == 200:
        print("✅ Génération réussie")
        
        # Créer le nom du fichier de sortie
        filename = f"test_barcode_{barcode_format}_{image_format}.{image_format}"
        
        # Sauvegarder l'image
        save_image(response.content, filename)
        
        # Si c'est une image PNG ou JPEG, essayer de l'ouvrir pour vérifier
        if image_format in ["png", "jpeg"]:
            try:
                img = Image.open(io.BytesIO(response.content))
                print(f"✅ Image valide: {img.format}, {img.size[0]}x{img.size[1]}")
            except Exception as e:
                print(f"❌ Erreur à l'ouverture de l'image: {e}")
    else:
        print(f"❌ Erreur: {response.status_code}")
        try:
            error_data = response.json()
            print(f"Détail: {error_data.get('detail', 'Pas de détail')}")
        except:
            print(f"Réponse: {response.text}")

if __name__ == "__main__":
    # Test avec différents formats de codes-barres et types de données
    test_cases = [
        # Test basique avec GS1 DataMatrix
        {
            "data": "01034531200000111719112510ABCD1234",
            "barcode_format": "gs1-datamatrix",
            "image_format": "png"
        },
        # Test avec QR Code
        {
            "data": "01030123456789103456",
            "barcode_format": "gs1-qrcode",
            "image_format": "png"
        },
        # Test avec Code 128
        {
            "data": "01030123456789",
            "barcode_format": "gs1-128",
            "image_format": "png"
        },
        # Test avec format JPEG
        {
            "data": "010301234567891721050110ABC123",
            "barcode_format": "datamatrix",
            "image_format": "jpeg"
        },
    ]
    
    for test_case in test_cases:
        test_generate_barcode(**test_case)
    
    print("\n=== Tests terminés ===")
