"""
Module de génération de codes-barres GS1
Supporte la génération de DataMatrix, QR Code et Code 128
"""

import io
import os
import re
from PIL import Image
from enum import Enum
import qrcode
from barcode import Code128
from barcode.writer import ImageWriter
import pylibdmtx.pylibdmtx as dmtx

# Tenter d'importer treepoem si disponible (pour des formats supplémentaires)
try:
    import treepoem
    TREEPOEM_AVAILABLE = True
except ImportError:
    TREEPOEM_AVAILABLE = False

class BarcodeFormat(str, Enum):
    """Formats de codes-barres pris en charge pour la génération."""
    DATAMATRIX = "datamatrix"
    QRCODE = "qrcode"
    CODE128 = "code128"
    GS1_128 = "gs1-128"
    GS1_DATAMATRIX = "gs1-datamatrix"
    GS1_QRCODE = "gs1-qrcode"

class ImageFormat(str, Enum):
    """Formats d'image pris en charge pour l'export."""
    PNG = "png"
    JPEG = "jpeg"
    SVG = "svg"

def prepare_gs1_content(data, barcode_format):
    """
    Prépare les données GS1 pour la génération selon le format choisi.
    
    Args:
        data (str): Données brutes (ex: 01034531200000111719112510ABCD1234)
        barcode_format (BarcodeFormat): Format de code-barres cible
        
    Returns:
        str: Données formatées pour le générateur
    """
    # Pour DataMatrix GS1, insérer automatiquement les FNC1
    if barcode_format in [BarcodeFormat.GS1_DATAMATRIX, BarcodeFormat.GS1_QRCODE]:
        # Repérer les AI et insérer des séparateurs GS
        formatted = ""
        i = 0
        
        while i < len(data):
            # Identifier l'AI (2, 3 ou 4 chiffres)
            ai_length = 0
            ai = None
            
            # Tester des AIs de différentes longueurs
            for length in [4, 3, 2]:
                if i + length <= len(data) and data[i:i+length].isdigit():
                    ai = data[i:i+length]
                    ai_length = length
                    break
            
            if not ai:
                # Pas d'AI trouvé, avancer d'un caractère
                formatted += data[i]
                i += 1
                continue
            
            # Ajouter l'AI à la chaîne formatée
            formatted += ai
            i += ai_length
            
            # Chercher le prochain AI pour déterminer la fin de la valeur
            next_ai_pos = -1
            for j in range(i, len(data)):
                if j + 2 <= len(data) and data[j:j+2].isdigit():
                    # Vérifier si c'est le début d'un nouvel AI
                    if re.match(r'^(00|01|02|10|11|13|15|17|20|21|30|31|32|33|34|35|36|37|90|91|92)', data[j:j+2]):
                        next_ai_pos = j
                        break
            
            # Extraire la valeur
            if next_ai_pos != -1:
                value = data[i:next_ai_pos]
                formatted += value + "\u001d"  # Ajouter GS après la valeur
                i = next_ai_pos
            else:
                # Dernier AI, prendre le reste de la chaîne
                formatted += data[i:]
                i = len(data)
        
        return formatted
    
    # Pour GS1-128, ajouter le FNC1 au début
    elif barcode_format == BarcodeFormat.GS1_128:
        if TREEPOEM_AVAILABLE:
            # treepoem gère automatiquement le FNC1 pour GS1-128
            return data
        else:
            # Gestion manuelle avec bibliothèque de secours
            return f"~{data}"  # ~ est souvent utilisé pour représenter FNC1
    
    # Pour les formats non-GS1, utiliser les données telles quelles
    return data

def generate_datamatrix(data, size=(5, 5)):
    """
    Génère un code DataMatrix.
    
    Args:
        data (str): Données à encoder
        size (tuple): Taille en mm (largeur, hauteur)
        
    Returns:
        PIL.Image: Image du code DataMatrix
    """
    # Encoder en bytes pour pylibdmtx
    encoded_data = data.encode('utf-8')
    
    # Générer l'image
    img_data = dmtx.encode(encoded_data)
    
    # Convertir en image PIL
    img = Image.frombytes('RGB', (img_data.width, img_data.height), img_data.pixels)
    
    return img

def generate_qrcode(data, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=4):
    """
    Génère un QR Code.
    
    Args:
        data (str): Données à encoder
        error_correction: Niveau de correction d'erreur
        box_size (int): Taille de chaque "boîte" du QR code en pixels
        border (int): Taille de la bordure en nombre de boîtes
        
    Returns:
        PIL.Image: Image du QR Code
    """
    qr = qrcode.QRCode(
        version=None,  # Auto-détermination de la version
        error_correction=error_correction,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def generate_code128(data):
    """
    Génère un Code 128.
    
    Args:
        data (str): Données à encoder
        
    Returns:
        PIL.Image: Image du Code 128
    """
    # Utiliser python-barcode pour générer un Code 128
    output = io.BytesIO()
    Code128(data, writer=ImageWriter()).write(output)
    
    # Convertir le résultat en image PIL
    output.seek(0)
    img = Image.open(output)
    return img

def generate_barcode_with_treepoem(data, barcode_format):
    """
    Génère un code-barres en utilisant la bibliothèque treepoem.
    
    Args:
        data (str): Données à encoder
        barcode_format (BarcodeFormat): Format de code-barres
        
    Returns:
        PIL.Image: Image du code-barres
    """
    if not TREEPOEM_AVAILABLE:
        raise ImportError("La bibliothèque treepoem n'est pas disponible")
    
    # Mapper le format au type treepoem
    format_map = {
        BarcodeFormat.DATAMATRIX: "datamatrix",
        BarcodeFormat.QRCODE: "qrcode",
        BarcodeFormat.CODE128: "code128",
        BarcodeFormat.GS1_128: "gs1-128",
        BarcodeFormat.GS1_DATAMATRIX: "datamatrix",
        BarcodeFormat.GS1_QRCODE: "qrcode",
    }
    
    treepoem_type = format_map.get(barcode_format, "code128")
    
    # Options spécifiques pour certains formats
    options = {}
    if barcode_format in [BarcodeFormat.GS1_DATAMATRIX, BarcodeFormat.GS1_QRCODE, BarcodeFormat.GS1_128]:
        options["includetext"] = "true"
        options["includecheckintext"] = "true"
    
    # Générer l'image
    img = treepoem.generate_barcode(
        barcode_type=treepoem_type,
        data=data,
        options=options
    )
    
    # Convertir en mode RGB pour assurer la compatibilité avec tous les formats
    return img.convert("RGB")

def generate_barcode(data, barcode_format=BarcodeFormat.DATAMATRIX, image_format=ImageFormat.PNG, 
                    width=300, height=300, use_treepoem=True):
    """
    Génère un code-barres du format spécifié.
    
    Args:
        data (str): Données à encoder
        barcode_format (BarcodeFormat): Format du code-barres
        image_format (ImageFormat): Format de l'image de sortie
        width (int): Largeur souhaitée (en pixels)
        height (int): Hauteur souhaitée (en pixels)
        use_treepoem (bool): Utiliser treepoem si disponible
        
    Returns:
        bytes: Image encodée au format spécifié
        
    Raises:
        ValueError: Si le format de code-barres n'est pas pris en charge
        ImportError: Si une bibliothèque requise n'est pas disponible
    """
    # Préparer les données selon le format GS1
    formatted_data = prepare_gs1_content(data, barcode_format)
    
    # Utiliser treepoem si disponible et demandé
    if use_treepoem and TREEPOEM_AVAILABLE:
        try:
            img = generate_barcode_with_treepoem(formatted_data, barcode_format)
        except Exception as e:
            # Fallback aux méthodes spécifiques en cas d'erreur
            print(f"Treepoem error: {e}, using specific generators")
            use_treepoem = False
    
    # Utiliser les générateurs spécifiques
    if not use_treepoem or not TREEPOEM_AVAILABLE:
        if barcode_format in [BarcodeFormat.DATAMATRIX, BarcodeFormat.GS1_DATAMATRIX]:
            img = generate_datamatrix(formatted_data)
        elif barcode_format in [BarcodeFormat.QRCODE, BarcodeFormat.GS1_QRCODE]:
            img = generate_qrcode(formatted_data)
        elif barcode_format in [BarcodeFormat.CODE128, BarcodeFormat.GS1_128]:
            img = generate_code128(formatted_data)
        else:
            raise ValueError(f"Format de code-barres non pris en charge: {barcode_format}")
    
    # Redimensionner l'image
    img = img.resize((width, height), Image.LANCZOS)
    
    # Encoder l'image au format demandé
    output = io.BytesIO()
    
    if image_format == ImageFormat.SVG:
        # Pour le SVG, utiliser une bibliothèque spécifique ou convertir depuis PNG
        raise NotImplementedError("Le format SVG n'est pas encore implémenté")
    else:
        # PNG ou JPEG
        img.save(output, format=image_format.upper())
    
    return output.getvalue()
