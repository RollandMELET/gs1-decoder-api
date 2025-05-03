#!/usr/bin/env python3
"""
Script de test pour les nouvelles fonctionnalités de détection de codes-barres GS1.
Ce script peut être exécuté indépendamment pour tester les fonctionnalités
sans avoir à démarrer l'API complète.
"""

import os
import sys
import json
from PIL import Image
import subprocess
from pylibdmtx.pylibdmtx import decode as dmtx_decode

# Ajouter le répertoire parent au chemin de recherche pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importer les modules à tester
from app.barcode_detector_old import (
    detect_gs1_format, get_decoder_info, DecoderType, BarcodeFormat
)

def test_barcode_detection(image_path):
    """
    Teste la détection de codes-barres et le décodage sur une image donnée.
    
    Args:
        image_path (str): Chemin vers l'image à tester
    """
    print(f"Test de détection sur l'image: {image_path}")
    print("-" * 50)
    
    # Vérifier que l'image existe
    if not os.path.exists(image_path):
        print(f"Erreur: L'image {image_path} n'existe pas.")
        return
    
    # 1. Essayer de décoder avec ZXing
    print("Test de décodage avec ZXing...")
    cmd = [
        "java", "-cp", "/zxing/javase.jar",
        "com.google.zxing.client.j2se.CommandLineRunner", image_path
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        decoded_zxing = [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]
        
        if decoded_zxing:
            print(f"ZXing a détecté {len(decoded_zxing)} codes-barres:")
            for i, code in enumerate(decoded_zxing):
                print(f"  Code {i+1}: {code}")
                
                # Tester la détection de format
                format_detected = detect_gs1_format(code)
                print(f"  Format détecté: {format_detected}")
                
                # Tester les informations complètes
                decoder_info = get_decoder_info(code, DecoderType.ZXING, True)
                print(f"  Informations décodeur: {json.dumps(decoder_info, indent=2)}")
                print("")
        else:
            print("ZXing n'a détecté aucun code-barres.")
    except Exception as e:
        print(f"Erreur lors de l'exécution de ZXing: {e}")
    
    # 2. Essayer de décoder avec pylibdmtx
    print("\nTest de décodage avec pylibdmtx...")
    try:
        img = Image.open(image_path)
        dmtx_results = dmtx_decode(img)
        decoded_dmtx = [res.data.decode("utf-8") for res in dmtx_results]
        
        if decoded_dmtx:
            print(f"pylibdmtx a détecté {len(decoded_dmtx)} codes-barres:")
            for i, code in enumerate(decoded_dmtx):
                print(f"  Code {i+1}: {code}")
                
                # Tester la détection de format
                format_detected = detect_gs1_format(code)
                print(f"  Format détecté: {format_detected}")
                
                # Tester les informations complètes
                decoder_info = get_decoder_info(code, DecoderType.PYLIBDMTX, True)
                print(f"  Informations décodeur: {json.dumps(decoder_info, indent=2)}")
                print("")
        else:
            print("pylibdmtx n'a détecté aucun code-barres.")
    except Exception as e:
        print(f"Erreur lors de l'exécution de pylibdmtx: {e}")

def main():
    """Fonction principale."""
    # Vérifier les arguments
    if len(sys.argv) < 2:
        print("Usage: python test_barcode_detection.py <image_path>")
        sys.exit(1)
    
    # Tester la détection sur l'image spécifiée
    test_barcode_detection(sys.argv[1])

if __name__ == "__main__":
    main()
