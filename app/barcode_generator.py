"""
Module de génération de codes-barres GS1
Supporte la génération de DataMatrix, QR Code et Code 128
"""

import io
import os
import re
import json
from PIL import Image
from enum import Enum
import qrcode
from barcode import Code128
from barcode.writer import ImageWriter
import pylibdmtx.pylibdmtx as dmtx
from fastapi import HTTPException

# Tenter d'importer treepoem si disponible (pour des formats supplémentaires)
try:
    import treepoem
    TREEPOEM_AVAILABLE = True
except ImportError:
    TREEPOEM_AVAILABLE = False

# Tenter d'importer zint pour GS1 DataMatrix spécialisé
try:
    import zint
    ZINT_AVAILABLE = True
    print("[DEBUG] zint-bindings disponible")
except ImportError as e:
    ZINT_AVAILABLE = False
    print(f"[DEBUG] zint-bindings non disponible: {e}")

# Vérifier disponibilité dmtxwrite système
import shutil
DMTXWRITE_AVAILABLE = shutil.which('dmtxwrite') is not None

# Vérifier disponibilité bwip-js via Node.js (module local)
BWIPJS_AVAILABLE = (
    shutil.which('node') is not None and
    os.path.exists('/app/generate_gs1_bwip.js') and
    os.path.exists('/app/node_modules/bwip-js')
)

if BWIPJS_AVAILABLE:
    print("[DEBUG] bwip-js disponible via Node.js")
else:
    print("[DEBUG] bwip-js non disponible - node ou script manquant")

# Charger les définitions des Application Identifiers GS1
GS1_AI_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "gs1_application_identifiers.json")

def load_ai_definitions():
    """Charge les définitions des AI GS1 depuis le fichier JSON."""
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
        }

# Charger les définitions des AI au démarrage du module
AI_DEFINITIONS = load_ai_definitions()

def parse_parentheses_format(data):
    """
    Parse les données GS1 au format avec parenthèses.

    Args:
        data (str): Données au format (01)12345...(10)LOT123...

    Returns:
        list: Liste de tuples (ai, value) où ai est l'Application Identifier et value la valeur

    Example:
        "(01)12345678901234(10)LOT123" -> [("01", "12345678901234"), ("10", "LOT123")]
    """
    # Pattern pour capturer (AI)Value
    pattern = r'\((\d{2,4})\)([^()]*?)(?=\(\d|$)'
    matches = re.findall(pattern, data)

    result = []
    for ai, value in matches:
        # Nettoyer la valeur (enlever les espaces en fin)
        value = value.rstrip()
        result.append((ai, value))

    return result

def build_gs1_string_from_ais(ai_value_pairs):
    """
    Construit une chaîne GS1 conforme à partir des paires AI/valeur.

    Args:
        ai_value_pairs (list): Liste de tuples (ai, value)

    Returns:
        str: Chaîne GS1 avec les séparateurs GS appropriés
    """
    result = ""

    for i, (ai, value) in enumerate(ai_value_pairs):
        # Ajouter l'AI et sa valeur
        result += ai + value

        # Ajouter un séparateur GS si l'AI a une longueur variable
        # et qu'il n'est pas le dernier élément
        ai_def = AI_DEFINITIONS.get(ai)
        if ai_def and not ai_def.get("fixed_length", True) and i < len(ai_value_pairs) - 1:
            result += "\u001d"  # Caractère GS (Group Separator)

    return result

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
        data (str): Données brutes - supporte maintenant les formats :
                   - Sans parenthèses : 01034531200000111719112510ABCD1234
                   - Avec parenthèses : (01)03453120000011(17)191125(10)ABCD1234
        barcode_format (BarcodeFormat): Format de code-barres cible

    Returns:
        str: Données formatées pour le générateur avec séparateurs GS appropriés
    """
    # NOUVELLE APPROCHE pour GS1 DataMatrix : passer les données brutes à bwip-js
    # basé sur le projet de référence fonctionnel qui utilise les données telles quelles
    if barcode_format == BarcodeFormat.GS1_DATAMATRIX:
        # FIXER: Passer les données brutes à bwip-js (comme le projet de référence)
        # bwip-js gère lui-même le parsing des AI et l'insertion du FNC1
        return data  # Données brutes, pas de transformation

    # Pour les autres formats GS1, garder l'ancien comportement
    elif barcode_format == BarcodeFormat.GS1_QRCODE:
        # Détecter le format d'entrée
        if '(' in data and ')' in data:
            # Format avec parenthèses - parser et reconstruire
            ai_value_pairs = parse_parentheses_format(data)
            formatted = build_gs1_string_from_ais(ai_value_pairs)
        else:
            # Format sans parenthèses - utiliser l'ancien algorithme amélioré
            formatted = _parse_raw_gs1_data(data)

        return formatted

    # Pour GS1-128, ajouter le FNC1 au début
    elif barcode_format == BarcodeFormat.GS1_128:
        # Si format avec parenthèses, convertir d'abord
        processed_data = data
        if '(' in data and ')' in data:
            ai_value_pairs = parse_parentheses_format(data)
            processed_data = build_gs1_string_from_ais(ai_value_pairs)

        if TREEPOEM_AVAILABLE:
            # treepoem gère automatiquement le FNC1 pour GS1-128
            return processed_data
        else:
            # Gestion manuelle avec bibliothèque de secours
            return f"~{processed_data}"  # ~ est souvent utilisé pour représenter FNC1

    # Pour les formats non-GS1, utiliser les données telles quelles
    return data

def _parse_raw_gs1_data(data):
    """
    Parse les données GS1 au format brut (sans parenthèses) - version améliorée.

    Args:
        data (str): Données brutes sans parenthèses

    Returns:
        str: Données formatées avec séparateurs GS appropriés
    """
    formatted = ""
    i = 0

    while i < len(data):
        # Identifier l'AI (2, 3 ou 4 chiffres)
        ai = None
        ai_length = 0

        # Tester des AIs de différentes longueurs en vérifiant s'ils existent
        for length in [4, 3, 2]:
            if i + length <= len(data):
                potential_ai = data[i:i+length]
                if potential_ai.isdigit() and potential_ai in AI_DEFINITIONS:
                    ai = potential_ai
                    ai_length = length
                    break

        if not ai:
            # Pas d'AI valide trouvé, avancer d'un caractère
            formatted += data[i]
            i += 1
            continue

        # Ajouter l'AI à la chaîne formatée
        formatted += ai
        i += ai_length

        # Déterminer la longueur de la valeur
        ai_def = AI_DEFINITIONS[ai]
        value_length = ai_def["length"]
        is_fixed_length = ai_def["fixed_length"]

        if is_fixed_length:
            # Longueur fixe - extraire exactement le nombre de caractères requis
            if i + value_length <= len(data):
                value = data[i:i+value_length]
                formatted += value
                i += value_length
            else:
                # Pas assez de caractères restants
                formatted += data[i:]
                break
        else:
            # Longueur variable - chercher le prochain AI ou prendre jusqu'à la fin
            next_ai_pos = len(data)  # Par défaut, jusqu'à la fin

            # Chercher le prochain AI valide
            for j in range(i, len(data)):
                for ai_len in [2, 3, 4]:
                    if j + ai_len <= len(data):
                        potential_ai = data[j:j+ai_len]
                        if potential_ai.isdigit() and potential_ai in AI_DEFINITIONS:
                            next_ai_pos = j
                            break
                if next_ai_pos < len(data):
                    break

            # Extraire la valeur
            value = data[i:next_ai_pos]
            formatted += value

            # Ajouter séparateur GS si ce n'est pas le dernier élément
            if next_ai_pos < len(data):
                formatted += "\u001d"

            i = next_ai_pos

    return formatted

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

# ========================================
# FONCTIONS SPÉCIALISÉES GS1 DATAMATRIX
# ========================================

def generate_gs1_datamatrix_bwipjs(data, **kwargs):
    """
    Génère un GS1 DataMatrix via bwip-js Node.js (SOLUTION CORRIGÉE).

    Args:
        data (str): Données GS1 formatées (avec parenthèses supportées)
        **kwargs: Arguments supplémentaires

    Returns:
        PIL.Image: Image du GS1 DataMatrix

    Raises:
        Exception: Si bwip-js n'est pas disponible ou échoue
    """
    if not BWIPJS_AVAILABLE:
        raise ImportError("bwip-js non disponible - Node.js ou script manquant")

    print(f"[DEBUG] bwip-js CORRIGÉ: Génération GS1 DataMatrix avec données: {repr(data[:50])}...")

    import subprocess
    import tempfile

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        try:
            # Commande Node.js SIMPLIFIÉE pour générer le GS1 DataMatrix
            cmd = [
                'node',
                '/app/generate_gs1_bwip.js',
                data,  # Données brutes (pas de transformation)
                tmp.name
            ]

            print(f"[DEBUG] bwip-js CORRIGÉ: Exécution commande: {' '.join(cmd)}")

            # Exécution avec timeout et capture des erreurs
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,  # Timeout 30 secondes
                cwd='/app'
            )

            print(f"[DEBUG] bwip-js CORRIGÉ: Code retour: {result.returncode}")
            print(f"[DEBUG] bwip-js CORRIGÉ: Stdout: {result.stdout.strip()}")

            if result.stderr:
                print(f"[DEBUG] bwip-js CORRIGÉ: Stderr: {result.stderr.strip()}")

            if result.returncode != 0:
                # En cas d'échec, lever une exception pour passer au fallback
                print(f"[DEBUG] bwip-js CORRIGÉ: Échec - passera au fallback")
                raise Exception(f"bwip-js échec (code {result.returncode}): {result.stderr}")

            # Vérifier que le fichier a été créé
            if not os.path.exists(tmp.name) or os.path.getsize(tmp.name) == 0:
                raise Exception("bwip-js n'a pas généré de fichier PNG valide")

            # Charger l'image générée
            img = Image.open(tmp.name)
            print(f"[DEBUG] bwip-js CORRIGÉ: SUCCÈS - Image chargée {img.size}")

            return img

        except subprocess.TimeoutExpired:
            raise Exception("bwip-js timeout - génération trop longue")
        except Exception as e:
            print(f"[DEBUG] bwip-js CORRIGÉ: Erreur subprocess: {e}")
            raise e
        finally:
            # Nettoyage du fichier temporaire
            try:
                if os.path.exists(tmp.name):
                    os.unlink(tmp.name)
            except:
                pass

def generate_gs1_datamatrix_treepoem(data, **kwargs):
    """
    Génère un GS1 DataMatrix via treepoem (recommandé).

    Args:
        data (str): Données GS1 formatées
        **kwargs: Arguments supplémentaires

    Returns:
        PIL.Image: Image du GS1 DataMatrix

    Raises:
        Exception: Si treepoem n'est pas disponible ou échoue
    """
    if not TREEPOEM_AVAILABLE:
        raise ImportError("treepoem n'est pas disponible")

    print(f"[DEBUG] treepoem: Génération GS1 DataMatrix avec données: {repr(data[:50])}...")

    # CORRECTION: Utiliser gs1datamatrix avec parsefnc (CRITIQUE selon la note)
    try:
        # Cette approche utilise EXACTEMENT ce que recommande la note technique
        img = treepoem.generate_barcode(
            barcode_type='gs1datamatrix',
            data=data,
            options={
                'parsefnc': True,      # CRITIQUE: Parse les AI et gère FNC1 automatiquement
                'version': 'auto'      # Taille automatique
            }
        )
        print("[DEBUG] treepoem: Succès GS1 DataMatrix avec parsefnc=True")
        return img.convert('RGB')
    except Exception as e:
        print(f"[DEBUG] treepoem: gs1datamatrix+parsefnc échoué: {e}")
        raise e  # Ne pas faire de fallback - on veut du vrai GS1

def generate_gs1_datamatrix_zint(data, **kwargs):
    """
    Génère un GS1 DataMatrix via zint-python.

    Args:
        data (str): Données GS1 formatées
        **kwargs: Arguments supplémentaires

    Returns:
        PIL.Image: Image du GS1 DataMatrix

    Raises:
        Exception: Si zint n'est pas disponible ou échoue
    """
    if not ZINT_AVAILABLE:
        raise ImportError("zint-python n'est pas disponible")

    print(f"[DEBUG] zint: Génération GS1 DataMatrix avec données: {repr(data[:50])}...")

    # Utilisation correcte de zint-bindings
    barcode = zint.Barcode(zint.BarcodeType.DATAMATRIX)
    barcode.set_option_2(1)     # Active le mode GS1

    # Génération PNG
    png_data = barcode.encode_and_render(data, file_format='PNG')

    # Conversion PIL
    return Image.open(io.BytesIO(png_data))

def generate_gs1_datamatrix_dmtxwrite(data, **kwargs):
    """
    Génère un GS1 DataMatrix via dmtxwrite système.

    Args:
        data (str): Données GS1 formatées
        **kwargs: Arguments supplémentaires

    Returns:
        PIL.Image: Image du GS1 DataMatrix

    Raises:
        Exception: Si dmtxwrite n'est pas disponible ou échoue
    """
    if not DMTXWRITE_AVAILABLE:
        raise ImportError("dmtxwrite n'est pas disponible sur le système")

    print(f"[DEBUG] dmtxwrite: Génération GS1 DataMatrix avec données: {repr(data[:50])}...")

    import tempfile
    import subprocess

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        # Commande dmtxwrite avec options GS1
        cmd = [
            'dmtxwrite',
            '-f', 'PNG',           # Format PNG
            '-e', 'gs1',           # Encodage GS1 (si supporté)
            '-o', tmp.name,        # Fichier sortie
            data                   # Données
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return Image.open(tmp.name)
        except subprocess.CalledProcessError as e:
            # Fallback sans option -e gs1
            cmd_fallback = ['dmtxwrite', '-f', 'PNG', '-o', tmp.name, data]
            subprocess.run(cmd_fallback, check=True, capture_output=True)
            return Image.open(tmp.name)

def generate_gs1_datamatrix_hybrid(data, **kwargs):
    """
    Générateur hybride GS1 DataMatrix avec fallbacks automatiques.
    ORDRE DE PRIORITÉ basé sur note technique :
    1. bwip-js (MEILLEUR - backend BWIPP natif, pas de Ghostscript)
    2. treepoem (BON - backend BWIPP, mais dépendance Ghostscript)
    3. zint (ALTERNATIF)

    Args:
        data (str): Données GS1 formatées
        **kwargs: Arguments supplémentaires

    Returns:
        PIL.Image: Image du GS1 DataMatrix

    Raises:
        Exception: Si tous les générateurs échouent
    """
    errors = []

    print(f"[DEBUG] GS1 DataMatrix hybride: Tentative génération pour {repr(data[:30])}...")

    # PRIORITÉ 1: bwip-js (NOUVEAU - recommandé note technique)
    if BWIPJS_AVAILABLE:
        try:
            print("[DEBUG] Tentative bwip-js (priorité 1)")
            return generate_gs1_datamatrix_bwipjs(data, **kwargs)
        except Exception as e:
            errors.append(f"bwip-js: {e}")
            print(f"[DEBUG] bwip-js échoué: {e}")

    # PRIORITÉ 2: treepoem (existant)
    if TREEPOEM_AVAILABLE:
        try:
            print("[DEBUG] Tentative treepoem (priorité 2)")
            return generate_gs1_datamatrix_treepoem(data, **kwargs)
        except Exception as e:
            errors.append(f"treepoem: {e}")
            print(f"[DEBUG] treepoem échoué: {e}")

    # PRIORITÉ 3: zint-python (existant)
    if ZINT_AVAILABLE:
        try:
            print("[DEBUG] Tentative zint (priorité 3)")
            return generate_gs1_datamatrix_zint(data, **kwargs)
        except Exception as e:
            errors.append(f"zint: {e}")
            print(f"[DEBUG] zint échoué: {e}")

    # PRIORITÉ 4: dmtxwrite système (dernier recours)
    if DMTXWRITE_AVAILABLE:
        try:
            print("[DEBUG] Tentative dmtxwrite (priorité 4)")
            return generate_gs1_datamatrix_dmtxwrite(data, **kwargs)
        except Exception as e:
            errors.append(f"dmtxwrite: {e}")
            print(f"[DEBUG] dmtxwrite échoué: {e}")

    # PAS de fallback pylibdmtx pour GS1 - il ne peut pas générer de vrai GS1 DataMatrix
    raise Exception(f"Tous les générateurs GS1 DataMatrix spécialisés ont échoué: {errors}. pylibdmtx ne peut pas générer de vrai GS1 DataMatrix (pas de FNC1).")

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
        BarcodeFormat.GS1_DATAMATRIX: "datamatrix",  # DataMatrix avec données GS1
        BarcodeFormat.GS1_QRCODE: "qrcode",
    }

    treepoem_type = format_map.get(barcode_format, "code128")

    # Options spécifiques pour certains formats
    options = {}
    if barcode_format == BarcodeFormat.GS1_DATAMATRIX:
        # Pour GS1 DataMatrix avec treepoem, essayer différentes approches
        print(f"[DEBUG] Treepoem: GS1 DataMatrix avec données: {repr(data[:30])}...")
        # Treepoem pourrait gérer automatiquement le GS1
    elif barcode_format in [BarcodeFormat.GS1_QRCODE, BarcodeFormat.GS1_128]:
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

    # Debug: afficher la chaîne formatée pour GS1 DataMatrix
    if barcode_format == BarcodeFormat.GS1_DATAMATRIX:
        print(f"[DEBUG] Input data: {repr(data)}")
        print(f"[DEBUG] Formatted for GS1 DataMatrix: {repr(formatted_data)}")
    
    # Utiliser treepoem si disponible et demandé
    if use_treepoem and TREEPOEM_AVAILABLE:
        try:
            img = generate_barcode_with_treepoem(formatted_data, barcode_format)
        except Exception as e:
            # Fallback aux méthodes spécifiques en cas d'erreur
            print(f"Treepoem error: {e}, using specific generators")
            use_treepoem = False
    
    # Utiliser les générateurs spécifiques avec architecture hybride
    if not use_treepoem or not TREEPOEM_AVAILABLE:
        if barcode_format == BarcodeFormat.GS1_DATAMATRIX:
            # FORCE treepoem pour GS1 DataMatrix avec parsefnc
            if TREEPOEM_AVAILABLE:
                print("[DEBUG] Force treepoem pour GS1 DataMatrix")
                try:
                    img = treepoem.generate_barcode(
                        barcode_type='gs1datamatrix',
                        data=formatted_data,
                        options={
                            'parsefnc': True,      # CRITIQUE pour FNC1
                            'version': 'auto'
                        }
                    )
                    print("[DEBUG] SUCCESS: treepoem GS1 DataMatrix avec parsefnc")
                    img = img.convert('RGB')
                except Exception as e:
                    print(f"[DEBUG] ERREUR treepoem: {e}")
                    raise HTTPException(status_code=500, detail=f"Impossible de générer GS1 DataMatrix conforme: {e}")
            else:
                raise HTTPException(status_code=501, detail="treepoem requis pour GS1 DataMatrix conforme - bibliothèque non disponible")
        elif barcode_format == BarcodeFormat.DATAMATRIX:
            # EXISTANT: DataMatrix standard (INCHANGÉ pour éviter régressions)
            img = generate_datamatrix(formatted_data)
        elif barcode_format in [BarcodeFormat.QRCODE, BarcodeFormat.GS1_QRCODE]:
            # EXISTANT: QR Code (INCHANGÉ)
            img = generate_qrcode(formatted_data)
        elif barcode_format in [BarcodeFormat.CODE128, BarcodeFormat.GS1_128]:
            # EXISTANT: Code 128 (INCHANGÉ)
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
