# --- START OF FILE main.py ---

from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends, Response
from fastapi.responses import StreamingResponse
# --- CORRECTION: Importer les bons modèles depuis app.models ---
from app.gs1_parser import parse_gs1
from app.models import (
    DecodeResponse, ErrorResponse, HealthResponse,
    GenerateRequest, BarcodeFormat, ImageFormat, # Retiré GenerateResponse qui n'est pas utilisé pour le retour d'image
    DecoderInfo, BarcodeItem # S'assurer que ces modèles sont utilisés
)
from app.barcode_detector import DecoderType, get_decoder_info
# --- CORRECTION: Importer les bons Enums depuis barcode_generator ---
from app.barcode_generator import generate_barcode, BarcodeFormat as GenBarcodeFormat, ImageFormat as GenImageFormat
import shutil
import subprocess
from pylibdmtx.pylibdmtx import decode as dmtx_decode
from PIL import Image
import os
import io

app = FastAPI(
    title="GS1 Decoder API",
    description="API pour décoder et générer des codes-barres au format GS1",
    version="1.1.0" # Vous pourriez incrémenter la version après les corrections
)

@app.get("/health", response_model=HealthResponse)
async def health():
    """
    Vérifie l'état du service et retourne des informations sur les capacités.

    Returns:
        dict: Statut et capacités du service
    """
    # Vérifier les dépendances
    capabilities = {
        "decoders": {
            "zxing": _check_zxing_available(),
            "pylibdmtx": _check_pylibdmtx_available()
        },
        "supported_codes": ["DataMatrix", "QR Code", "GS1-128", "GS1 DataMatrix", "GS1 QR Code"],
        "api_version": "1.1.0", # Correspond à la version de l'app
        "features": {
            "decode": True,
            "generate": True # Gardé même si moins prioritaire
        }
    }
    return {"status": "OK", "capabilities": capabilities}

@app.post(
    "/decode/",
    response_model=DecodeResponse, # Utilise le modèle corrigé via BarcodeItem
    responses={422: {"model": ErrorResponse}},
    summary="Décode des codes-barres à partir d'une image",
    description="Analyse une image et détecte/décode les codes-barres présents, supportant différents formats GS1"
)
async def decode_image(
    file: UploadFile = File(...),
    verbose: bool = Form(False),
    debug: bool = Form(False),
    log_file: str = Form(None) # Renommé pour correspondre à l'usage réel (str ou None)
):
    """
    Decode GS1 barcodes from an image.
    Params:
      - file: image file
      - verbose: whether to return verbose parse
      - debug: enable debug logging
      - log_file: path to write debug logs (server-side)
    """
    # Utiliser un nom de fichier temporaire plus robuste (évite collisions potentielles)
    # Bien que pour /tmp/ simple, le nom original soit souvent suffisant
    temp_file_path = f"/tmp/uploaded_{file.filename}" # Utiliser un chemin complet
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        # Si l'écriture échoue, lever une exception
        raise HTTPException(status_code=500, detail=f"Erreur lors de la sauvegarde du fichier temporaire: {e}")

    # Setup debug logging if requested
    logf = None
    if debug and log_file: # Vérifier que log_file n'est pas None ou vide
        try:
            # Utiliser 'a' (append) peut être utile si plusieurs requêtes debug arrivent vite
            logf = open(log_file, "a")
            logf.write(f"--- New Request ---\n")
            logf.write(f"[DEBUG] Saved upload to {temp_file_path}\n")
        except Exception as e:
            # Ne pas bloquer si le log échoue, mais peut-être logger l'erreur dans la console standard
            print(f"Warning: Impossible d'ouvrir le fichier de log {log_file}: {e}")
            logf = None # Assurer que logf est None si l'ouverture échoue

    decoded = []
    decoder_used = DecoderType.NONE
    zxing_stderr = "" # Pour stocker l'erreur zxing si besoin

    # 1) ZXing attempt
    try:
        # --- CORRECTION: Modification de la commande Java pour inclure jcommander.jar ---
        cmd = [
            "java",
            "-cp", "/zxing/javase.jar:/zxing/jcommander.jar", # Classpath corrigé
            "com.google.zxing.client.j2se.CommandLineRunner",
            temp_file_path # Utiliser le chemin complet
        ]
        if logf:
            logf.write(f"[DEBUG] Running ZXing command: {' '.join(cmd)}\n")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False # Ne pas lever d'exception si ZXing échoue, on le gère après
        )
        zxing_stderr = result.stderr.strip() # Garder l'erreur stderr

        # Traiter la sortie seulement si ZXing n'a pas retourné d'erreur majeure
        if result.returncode == 0 and result.stdout:
            decoded = [line for line in result.stdout.strip().splitlines() if line.strip() and not line.startswith("Raw result:")]
            if decoded:
                 # Retirer le préfixe "Parsed result:" si présent
                decoded = [line.replace("Parsed result:", "").strip() for line in decoded]
                decoder_used = DecoderType.ZXING

        if logf:
            logf.write(f"[DEBUG] ZXing return code: {result.returncode}\n")
            logf.write(f"[DEBUG] ZXing stdout: {result.stdout.strip()}\n")
            logf.write(f"[DEBUG] ZXing stderr: {zxing_stderr}\n")
            logf.write(f"[DEBUG] ZXing decoded after parsing stdout: {decoded}\n")

    except FileNotFoundError:
        # Java n'est probablement pas installé ou pas dans le PATH
        if logf: logf.write("[ERROR] ZXing command failed: 'java' command not found.\n")
        zxing_stderr = "'java' command not found."
    except Exception as e:
        # Autre erreur lors de l'exécution de subprocess
        if logf: logf.write(f"[ERROR] ZXing subprocess failed: {e}\n")
        zxing_stderr = f"Subprocess error: {e}"


    # 2) Fallback to pylibdmtx if ZXing failed or found nothing
    if not decoded:
        if logf:
            logf.write(f"[DEBUG] ZXing found nothing or failed (stderr: {zxing_stderr}). Trying pylibdmtx...\n")
        try:
            img = Image.open(temp_file_path)
            # Forcer la conversion en niveaux de gris peut parfois aider pylibdmtx
            dmtx_results = dmtx_decode(img.convert('L'))
            if dmtx_results:
                decoded = [res.data.decode("utf-8") for res in dmtx_results]
                decoder_used = DecoderType.PYLIBDMTX
                if logf:
                    logf.write(f"[DEBUG] pylibdmtx found {len(decoded)} codes: {decoded}\n")
            else:
                 if logf: logf.write("[DEBUG] pylibdmtx found no codes.\n")

        except Exception as e:
            if logf:
                logf.write(f"[ERROR] pylibdmtx error: {e}\n")
            # Ne pas écraser 'decoded' s'il contenait des résultats zxing
            # S'assurer que decoded est une liste vide si pylibdmtx échoue ET zxing a échoué
            if decoder_used != DecoderType.ZXING:
                 decoded = []

    # Finalize logs
    if logf:
        logf.write(f"[DEBUG] Final decoder used: {decoder_used}\n")
        logf.write(f"[DEBUG] Final decoded data: {decoded}\n")
        logf.close() # Fermer le fichier log

    # Supprimer le fichier temporaire
    try:
        os.remove(temp_file_path)
    except OSError as e:
        print(f"Warning: Could not remove temporary file {temp_file_path}: {e}")


    # Gérer le cas où aucun code n'est trouvé
    if not decoded:
        # Inclure l'erreur ZXing si elle existe et pertinente
        detail_msg = "Aucun code-barres détecté dans l'image."
        if zxing_stderr and decoder_used == DecoderType.NONE:
             detail_msg += f" (ZXing stderr: {zxing_stderr})"
        elif decoder_used == DecoderType.NONE:
             detail_msg += " (pylibdmtx a aussi échoué ou n'a rien trouvé)."

        raise HTTPException(
            status_code=422,
            detail=detail_msg
        )

    # Parse GS1 et construire la réponse
    barcodes_response = []
    for raw in decoded:
        try:
            # Utiliser le modèle corrigé, parse_gs1 retourne la bonne structure
            parsed_data = parse_gs1(raw, verbose=verbose)

            # Obtenir les informations de détection du format
            # Passer le raw data qui est une string
            decoder_info_dict = get_decoder_info(raw, decoder_used, verbose=verbose)

            # Créer l'instance du modèle DecoderInfo
            # Note: Assurez-vous que les clés retournées par get_decoder_info correspondent aux champs de DecoderInfo
            decoder_info_model = DecoderInfo(**decoder_info_dict)

            # Créer l'instance du modèle BarcodeItem
            barcode_item = BarcodeItem(
                raw=raw,
                parsed=parsed_data, # Doit correspondre à l'Union[Dict, List[ParsedVerboseItem]]
                decoder_info=decoder_info_model
            )
            barcodes_response.append(barcode_item)

        except Exception as e:
            # Gérer une erreur pendant le parsing ou la création du modèle pour UN code-barres
            # Permet de retourner les autres codes s'ils sont valides
            print(f"Error processing barcode data '{raw}': {e}")
            # Optionnel: ajouter une entrée d'erreur dans la réponse?
            # Pour l'instant, on l'ignore pour ne pas faire échouer toute la requête
            # Vous pourriez vouloir logger cette erreur spécifiquement
            if logf: logf.write(f"[ERROR] Failed to process/parse raw data '{raw}': {e}\n")


    # Si après traitement, aucun code-barres n'a pu être ajouté à la réponse
    if not barcodes_response:
         raise HTTPException(
            status_code=500, # Ou 422? Erreur interne car le parsing a échoué après décodage.
            detail="Erreur lors du traitement des données des codes-barres décodés."
        )

    # Retourner la réponse valide selon le modèle DecodeResponse
    return DecodeResponse(success=True, barcodes=barcodes_response)


@app.post(
    "/generate/",
    responses={
        200: {"content": {"image/png": {}, "image/jpeg": {}, "image/svg+xml": {}}},
        422: {"model": ErrorResponse},
        501: {"model": ErrorResponse}, # Pour ImportError
        500: {"model": ErrorResponse}  # Pour autres erreurs serveur
    },
    summary="Génère un code-barres GS1",
    description="Crée une image de code-barres à partir des données GS1 fournies"
)
async def generate_barcode_image(request: GenerateRequest):
    """
    Génère un code-barres à partir des données fournies.

    Args:
        request: Paramètres de génération du code-barres

    Returns:
        StreamingResponse: Image du code-barres
    """
    try:
        # Mapper les formats d'entrée aux formats internes du générateur
        # S'assurer que les clés correspondent bien aux Enums de models.py
        barcode_format_map = {
            BarcodeFormat.DATAMATRIX: GenBarcodeFormat.DATAMATRIX,
            BarcodeFormat.QRCODE: GenBarcodeFormat.QRCODE,
            BarcodeFormat.CODE128: GenBarcodeFormat.CODE128,
            BarcodeFormat.GS1_128: GenBarcodeFormat.GS1_128,
            BarcodeFormat.GS1_DATAMATRIX: GenBarcodeFormat.GS1_DATAMATRIX,
            BarcodeFormat.GS1_QRCODE: GenBarcodeFormat.GS1_QRCODE,
        }

        image_format_map = {
            ImageFormat.PNG: GenImageFormat.PNG,
            ImageFormat.JPEG: GenImageFormat.JPEG,
            ImageFormat.SVG: GenImageFormat.SVG,
        }

        # Vérifier si le format demandé est supporté par le mapping
        internal_barcode_format = barcode_format_map.get(request.format)
        internal_image_format = image_format_map.get(request.image_format)

        if internal_barcode_format is None:
             raise ValueError(f"Format de code-barres non supporté: {request.format}")
        if internal_image_format is None:
             raise ValueError(f"Format d'image non supporté: {request.image_format}")


        # Générer le code-barres
        barcode_image_bytes = generate_barcode(
            data=request.data,
            barcode_format=internal_barcode_format,
            image_format=internal_image_format,
            width=request.width,
            height=request.height
            # Ajoutez use_treepoem=False si vous voulez forcer l'utilisation des libs spécifiques
            # use_treepoem=True # (Comportement par défaut si treepoem est dispo)
        )

        # Déterminer le type MIME
        mime_types = {
            ImageFormat.PNG: "image/png",
            ImageFormat.JPEG: "image/jpeg",
            ImageFormat.SVG: "image/svg+xml", # Note: La génération SVG peut nécessiter treepoem ou une autre lib
        }
        media_type = mime_types.get(request.image_format)
        if media_type is None:
             # Ne devrait pas arriver si la validation précédente est passée
             raise ValueError(f"Type MIME inconnu pour format: {request.image_format}")


        # Retourner l'image
        return StreamingResponse(
            io.BytesIO(barcode_image_bytes), # Créer un flux depuis les bytes
            media_type=media_type,
            headers={
                # Rendre le nom de fichier un peu plus descriptif
                "Content-Disposition": f"inline; filename=\"barcode_{request.format.value}.{request.image_format.value}\""
            }
        )

    except ValueError as e:
        # Erreur de valeur (ex: format non supporté, taille invalide)
        raise HTTPException(status_code=422, detail=str(e))
    except ImportError as e:
        # Dépendance manquante (ex: treepoem non installé pour SVG)
        raise HTTPException(status_code=501, detail=f"Fonctionnalité non disponible (dépendance manquante): {str(e)}")
    except NotImplementedError as e:
        # Fonctionnalité explicitement non implémentée (ex: SVG sans treepoem)
         raise HTTPException(status_code=501, detail=f"Fonctionnalité non implémentée: {str(e)}")
    except Exception as e:
        # Toute autre erreur pendant la génération
        # Logger l'erreur ici peut être utile pour le débogage serveur
        print(f"Erreur inattendue lors de la génération du code-barres: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne lors de la génération du code-barres.")


def _check_zxing_available():
    """
    Vérifie si les composants nécessaires pour ZXing sont disponibles.
    Retourne False si Java n'est pas trouvé ou si les JARs manquent.
    """
    if not shutil.which("java"): # Vérifie si 'java' est dans le PATH
        return False
    # Vérifie l'existence des DEUX jars maintenant
    if not os.path.exists("/zxing/javase.jar") or not os.path.exists("/zxing/jcommander.jar"):
        return False
    return True

def _check_pylibdmtx_available():
    """
    Vérifie si la bibliothèque pylibdmtx et sa dépendance C sont probablement disponibles.
    """
    try:
        from pylibdmtx.pylibdmtx import decode as dmtx_decode
        # Optionnel: Faire un mini-test de décodage si nécessaire,
        # mais l'import est généralement suffisant pour le health check.
        return True
    except ImportError:
        # Si l'import Python échoue
        return False
    except Exception:
        # Si l'import réussit mais libdmtx a un problème au chargement? (Moins courant)
        return False

# --- FIN DU FICHIER main.py ---