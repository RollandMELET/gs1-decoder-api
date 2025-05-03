# --- START OF FILE main.py ---

from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends, Response
from fastapi.responses import StreamingResponse
from app.gs1_parser import parse_gs1
from app.models import (
    DecodeResponse, ErrorResponse, HealthResponse,
    GenerateRequest, BarcodeFormat, ImageFormat,
    DecoderInfo, BarcodeItem
)
from app.barcode_detector import DecoderType, get_decoder_info
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
    version="1.1.2" # Incrémenté pour cette étape de test
)

@app.get("/health", response_model=HealthResponse)
async def health():
    """
    Vérifie l'état du service et retourne des informations sur les capacités.

    Returns:
        dict: Statut et capacités du service
    """
    capabilities = {
        "decoders": {
            "zxing": _check_zxing_available(),
            "pylibdmtx": _check_pylibdmtx_available()
        },
        "supported_codes": ["DataMatrix", "QR Code", "GS1-128", "GS1 DataMatrix", "GS1 QR Code"],
        "api_version": app.version,
        "features": {
            "decode": True,
            "generate": True
        }
    }
    return {"status": "OK", "capabilities": capabilities}

@app.post(
    "/decode/",
    response_model=DecodeResponse,
    responses={422: {"model": ErrorResponse}},
    summary="Décode des codes-barres à partir d'une image",
    description="Analyse une image et détecte/décode les codes-barres présents, supportant différents formats GS1"
)
async def decode_image(
    file: UploadFile = File(...),
    verbose: bool = Form(False),
    debug: bool = Form(False),
    log_file: str = Form(None)
):
    """
    Decode GS1 barcodes from an image.
    Params:
      - file: image file
      - verbose: whether to return verbose parse
      - debug: enable debug logging
      - log_file: path to write debug logs (server-side)
    """
    temp_file_path = f"/tmp/uploaded_{file.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la sauvegarde du fichier temporaire: {e}")

    logf = None
    if debug and log_file:
        try:
            # Utiliser 'w' pour écraser le log à chaque test pour plus de clarté
            logf = open(log_file, "w")
            logf.write(f"--- New Request ---\n")
            logf.write(f"[DEBUG] Saved upload to {temp_file_path}\n")
        except Exception as e:
            print(f"Warning: Impossible d'ouvrir le fichier de log {log_file}: {e}")
            logf = None

    decoded = []
    decoder_used = DecoderType.NONE
    zxing_stderr = ""

    # 1) ZXing attempt
    if _check_zxing_available():
        try:
            cmd = [
                "java",
                "-cp", "/zxing/core.jar:/zxing/javase.jar:/zxing/jcommander.jar", # Classpath corrigé
                "com.google.zxing.client.j2se.CommandLineRunner",
                temp_file_path
            ]
            if logf:
                logf.write(f"[DEBUG] Running ZXing command: {' '.join(cmd)}\n")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            zxing_stderr = result.stderr.strip() # Garder l'erreur stderr

            # --- Logique d'extraction (peut nécessiter ajustement après observation) ---
            decoded_value = None
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().splitlines()
                try:
                    marker_line_index = -1
                    for idx, line in enumerate(lines):
                        if line.strip() == "Raw result:" or line.strip() == "Parsed result:":
                            marker_line_index = idx
                            break

                    if marker_line_index != -1 and marker_line_index + 1 < len(lines):
                        decoded_value = lines[marker_line_index + 1].strip()
                    elif marker_line_index == -1:
                        meaningful_lines = [line.strip() for line in lines if line.strip() and not line.startswith("Found") and not line.startswith("  Point") and not line.startswith("file:")]
                        if len(meaningful_lines) == 1:
                            decoded_value = meaningful_lines[0]

                except Exception as parse_ex:
                    if logf: logf.write(f"[ERROR] Failed to parse ZXing stdout: {parse_ex}\n")

            if decoded_value:
                decoded = [decoded_value]
                decoder_used = DecoderType.ZXING
            else:
                decoded = []
            # --- Fin de la logique d'extraction ---

            if logf:
                logf.write(f"[DEBUG] ZXing return code: {result.returncode}\n")
                logf.write(f"[DEBUG] ZXing stdout (full): {result.stdout.strip()}\n") # Log complet
                logf.write(f"[DEBUG] ZXing stderr: {zxing_stderr}\n")
                logf.write(f"[DEBUG] ZXing decoded after parsing stdout logic: {decoded}\n")

        except FileNotFoundError:
            if logf: logf.write("[ERROR] ZXing command failed: 'java' command not found.\n")
            zxing_stderr = "'java' command not found."
        except Exception as e:
            if logf: logf.write(f"[ERROR] ZXing subprocess failed: {e}\n")
            zxing_stderr = f"Subprocess error: {e}"
    else:
        if logf: logf.write("[DEBUG] Skipping ZXing attempt: prerequisites not met according to _check_zxing_available().\n")
        zxing_stderr = "ZXing prerequisites not met."

    # 2) Fallback to pylibdmtx if ZXing failed or found nothing
    if not decoded:
        if logf:
            logf.write(f"[DEBUG] ZXing found nothing or failed (stderr: {zxing_stderr}). Trying pylibdmtx...\n")
        if _check_pylibdmtx_available():
            try:
                img = Image.open(temp_file_path)
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
                if decoder_used != DecoderType.ZXING:
                    decoded = []
        else:
             if logf: logf.write("[DEBUG] Skipping pylibdmtx attempt: prerequisites not met.\n")

    # Finalize logs section
    if logf:
        logf.write(f"[DEBUG] Final decoder used: {decoder_used}\n")
        logf.write(f"[DEBUG] Final decoded data: {decoded}\n")
        # --- LA LIGNE CRUCIALE POUR CETTE ETAPE ---
        if decoded and logf:
             for i, raw_data in enumerate(decoded):
                 # Logger la représentation pour voir les caractères spéciaux
                 logf.write(f"[DEBUG] Raw data item {i} from decoder before parsing (repr): {repr(raw_data)}\n")
        # --- FIN DE LA LIGNE CRUCIALE ---
        logf.close()

    # Supprimer le fichier temporaire
    try:
        os.remove(temp_file_path)
    except OSError as e:
        print(f"Warning: Could not remove temporary file {temp_file_path}: {e}")

    if not decoded:
        detail_msg = "Aucun code-barres détecté dans l'image."
        if zxing_stderr and decoder_used == DecoderType.NONE:
             detail_msg += f" (ZXing stderr: {zxing_stderr})"
        elif decoder_used == DecoderType.NONE:
             detail_msg += " (pylibdmtx a aussi échoué ou n'a rien trouvé)."
        raise HTTPException(status_code=422, detail=detail_msg)

    barcodes_response = []
    for raw in decoded:
        try:
            # Important: Pour ce test, on utilise toujours le gs1_parser ORIGINAL
            # car on veut voir ce que le parser actuel fait avec la donnée brute réelle.
            parsed_data = parse_gs1(raw, verbose=verbose)

            decoder_info_dict = get_decoder_info(raw, decoder_used, verbose=verbose)
            decoder_info_model = DecoderInfo(**decoder_info_dict)
            barcode_item = BarcodeItem(
                raw=raw, # La donnée brute extraite par le décodeur
                parsed=parsed_data, # Le résultat du parser actuel
                decoder_info=decoder_info_model
            )
            barcodes_response.append(barcode_item)
        except Exception as e:
            print(f"Error processing barcode data '{raw}': {e}")
            # Essayer de logger l'erreur même si le fichier principal est fermé
            if debug and log_file:
                try:
                    with open(log_file, "a") as err_logf:
                         err_logf.write(f"[ERROR] Failed to process/parse raw data '{raw}': {e}\n")
                except: pass

    if not barcodes_response:
         raise HTTPException(
            status_code=500,
            detail="Erreur lors du traitement des données des codes-barres décodés."
        )

    return DecodeResponse(success=True, barcodes=barcodes_response)

# --- Endpoint /generate/ (inchangé) ---
@app.post(
    "/generate/",
    responses={
        200: {"content": {"image/png": {}, "image/jpeg": {}, "image/svg+xml": {}}},
        422: {"model": ErrorResponse},
        501: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Génère un code-barres GS1",
    description="Crée une image de code-barres à partir des données GS1 fournies"
)
async def generate_barcode_image(request: GenerateRequest):
    try:
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
        internal_barcode_format = barcode_format_map.get(request.format)
        internal_image_format = image_format_map.get(request.image_format)
        if internal_barcode_format is None: raise ValueError(f"Format de code-barres non supporté: {request.format}")
        if internal_image_format is None: raise ValueError(f"Format d'image non supporté: {request.image_format}")
        barcode_image_bytes = generate_barcode(data=request.data, barcode_format=internal_barcode_format, image_format=internal_image_format, width=request.width, height=request.height)
        mime_types = { ImageFormat.PNG: "image/png", ImageFormat.JPEG: "image/jpeg", ImageFormat.SVG: "image/svg+xml" }
        media_type = mime_types.get(request.image_format)
        if media_type is None: raise ValueError(f"Type MIME inconnu pour format: {request.image_format}")
        return StreamingResponse(io.BytesIO(barcode_image_bytes), media_type=media_type, headers={"Content-Disposition": f"inline; filename=\"barcode_{request.format.value}.{request.image_format.value}\""})
    except ValueError as e: raise HTTPException(status_code=422, detail=str(e))
    except ImportError as e: raise HTTPException(status_code=501, detail=f"Fonctionnalité non disponible (dépendance manquante): {str(e)}")
    except NotImplementedError as e: raise HTTPException(status_code=501, detail=f"Fonctionnalité non implémentée: {str(e)}")
    except Exception as e: print(f"Erreur inattendue lors de la génération du code-barres: {e}"); raise HTTPException(status_code=500, detail=f"Erreur interne lors de la génération du code-barres.")

# --- Fonctions de vérification mises à jour ---
def _check_zxing_available():
    if not shutil.which("java"): return False
    # Vérifier les TROIS JARs
    if not os.path.exists("/zxing/core.jar") or \
       not os.path.exists("/zxing/javase.jar") or \
       not os.path.exists("/zxing/jcommander.jar"):
        return False
    return True

def _check_pylibdmtx_available():
    try:
        from pylibdmtx.pylibdmtx import decode as dmtx_decode
        return True
    except ImportError: return False
    except Exception: return False

# --- FIN DU FICHIER main.py ---