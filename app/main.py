# --- START OF FILE main.py ---

from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends, Response
from fastapi.responses import StreamingResponse
from app.gs1_parser import parse_gs1 # Garder le parser original
from app.models import (
    DecodeResponse, ErrorResponse, HealthResponse,
    GenerateRequest, BarcodeFormat, ImageFormat,
    DecoderInfo, BarcodeItem
)
from app.barcode_detector import DecoderType, get_decoder_info
from app.barcode_generator import generate_barcode, BarcodeFormat as GenBarcodeFormat, ImageFormat as GenImageFormat
import shutil
# Suppression de subprocess
from pylibdmtx.pylibdmtx import decode as dmtx_decode
from PIL import Image
import os
import io
# --- AJOUT: Import de la bibliothèque pyzxing ---
from pyzxing import BarCodeReader

app = FastAPI(
    title="GS1 Decoder API",
    description="API pour décoder et générer des codes-barres au format GS1",
    version="1.1.5" # Incrémenté pour l'étape pyzxing
)

# --- AJOUT: Initialiser le lecteur pyzxing ---
try:
    # pyzxing trouve les JARs automatiquement s'ils sont dans des chemins standards
    # ou on peut spécifier le répertoire ZXING_LIBRARY mais essayons sans d'abord
    # S'assurer que JAVA_HOME est peut-être nécessaire dans l'env Docker si non standard
    zxing_reader = BarCodeReader()
    PYZXING_AVAILABLE = True
except Exception as e:
    # La détection de pyzxing est plus complexe, on pourrait juste supposer True
    # si l'import a réussi et que Java est là.
    print(f"Avertissement initialisation pyzxing (peut être normal): {e}")
    # On suppose qu'il est dispo si l'import a marché et java existe
    if shutil.which("java"):
         PYZXING_AVAILABLE = True
         zxing_reader = BarCodeReader() # Recréer au cas où
    else:
         print("Java non trouvé, pyzxing ne sera pas disponible.")
         PYZXING_AVAILABLE = False
         zxing_reader = None


@app.get("/health", response_model=HealthResponse)
async def health():
    capabilities = {
        # --- MODIFIÉ: Vérifier pyzxing ---
        "decoders": {
            "zxing": PYZXING_AVAILABLE, # Utiliser notre flag
            "pylibdmtx": _check_pylibdmtx_available()
        },
        "supported_codes": ["DataMatrix", "QR Code", "GS1-128", "GS1 DataMatrix", "GS1 QR Code"],
        "api_version": app.version,
        "features": {"decode": True, "generate": True }
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
    temp_file_path = f"/tmp/uploaded_{file.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la sauvegarde du fichier temporaire: {e}")

    logf = None
    if debug and log_file:
        try:
            logf = open(log_file, "w")
            logf.write(f"--- New Request (Test pyzxing) ---\n")
            logf.write(f"[DEBUG] Saved upload to {temp_file_path}\n")
        except Exception as e:
            print(f"Warning: Impossible d'ouvrir le fichier de log {log_file}: {e}")
            logf = None

    decoded = []
    decoder_used = DecoderType.NONE
    zxing_error_msg = None

    # 1) ZXing attempt (via pyzxing)
    if PYZXING_AVAILABLE and zxing_reader:
        try:
            if logf: logf.write(f"[DEBUG] Attempting decode with pyzxing...\n")
            # --- MODIFICATION: Utilisation de pyzxing ---
            # pyzxing.decode retourne une liste de dictionnaires ou None
            results = zxing_reader.decode(temp_file_path, try_harder=True, possible_formats="DATA_MATRIX")

            if results:
                # Extraire les données brutes (bytes) de chaque résultat
                raw_byte_list = [r.get('raw') for r in results if r.get('raw')]
                if raw_byte_list:
                    # Décoder les bytes en utf-8
                    decoded = [b.decode('utf-8') for b in raw_byte_list]
                    decoder_used = DecoderType.ZXING # Marquer comme ZXing
                    if logf: logf.write(f"[DEBUG] pyzxing success. Raw data extracted: {decoded}\n")
                else:
                    if logf: logf.write(f"[DEBUG] pyzxing found barcode(s) but no 'raw' field in results: {results}\n")
                    decoded = [] # Pas de donnée brute extraite
            else:
                if logf: logf.write(f"[DEBUG] pyzxing found no barcode.\n")
                decoded = []

        except Exception as e:
            zxing_error_msg = f"pyzxing error: {e}"
            if logf: logf.write(f"[ERROR] {zxing_error_msg}\n")
            decoded = []

    else:
        if logf: logf.write("[DEBUG] Skipping pyzxing attempt: not available.\n")
        zxing_error_msg = "pyzxing not available."

    # 2) Fallback to pylibdmtx if pyzxing failed or found nothing
    if not decoded:
        if logf:
            logf.write(f"[DEBUG] pyzxing found nothing or failed ({zxing_error_msg}). Trying pylibdmtx...\n")
        if _check_pylibdmtx_available():
            try:
                img = Image.open(temp_file_path)
                dmtx_results = dmtx_decode(img.convert('L'))
                if dmtx_results:
                    decoded = [res.data.decode("utf-8") for res in dmtx_results]
                    decoder_used = DecoderType.PYLIBDMTX
                    if logf: logf.write(f"[DEBUG] pylibdmtx found {len(decoded)} codes: {decoded}\n")
                else:
                     if logf: logf.write("[DEBUG] pylibdmtx found no codes.\n")
            except Exception as e:
                if logf: logf.write(f"[ERROR] pylibdmtx error: {e}\n")
                if decoder_used != DecoderType.ZXING: decoded = []
        else:
            if logf: logf.write("[DEBUG] Skipping pylibdmtx attempt: not available.\n")

    # Finalize logs section
    if logf:
        logf.write(f"[DEBUG] Final decoder used: {decoder_used}\n")
        logf.write(f"[DEBUG] Final decoded data: {decoded}\n")
        if decoded and logf:
             for i, raw_data in enumerate(decoded):
                 # --- Log repr() pour voir si pyzxing inclut \x1d ---
                 logf.write(f"[DEBUG] Raw data item {i} from final decoder (repr): {repr(raw_data)}\n")
        logf.close()

    # Supprimer le fichier temporaire
    try:
        os.remove(temp_file_path)
    except OSError as e:
        print(f"Warning: Could not remove temporary file {temp_file_path}: {e}")

    if not decoded:
        detail_msg = "Aucun code-barres détecté dans l'image."
        if zxing_error_msg and decoder_used == DecoderType.NONE:
             detail_msg += f" (ZXing/pyzxing error: {zxing_error_msg})"
        elif decoder_used == DecoderType.NONE:
             detail_msg += " (pylibdmtx a aussi échoué ou n'a rien trouvé)."
        raise HTTPException(status_code=422, detail=detail_msg)

    barcodes_response = []
    for raw in decoded:
        try:
            # --- Toujours parser avec le gs1_parser original ---
            parsed_data = parse_gs1(raw, verbose=verbose)
            # Utiliser le nom de décodeur correct dans l'info
            decoder_name_for_info = "pyzxing" if decoder_used == DecoderType.ZXING else decoder_used.value
            decoder_info_dict = get_decoder_info(raw, decoder_used, verbose=verbose)
            # Surcharger le nom si nécessaire
            decoder_info_dict["decoder"] = decoder_name_for_info

            decoder_info_model = DecoderInfo(**decoder_info_dict)
            barcode_item = BarcodeItem(raw=raw, parsed=parsed_data, decoder_info=decoder_info_model)
            barcodes_response.append(barcode_item)
        except Exception as e:
            print(f"Error processing barcode data '{raw}': {e}")
            if debug and log_file:
                try:
                    with open(log_file, "a") as err_logf:
                        err_logf.write(f"[ERROR] Failed to process/parse raw data '{raw}': {e}\n")
                except: pass

    if not barcodes_response:
         raise HTTPException(status_code=500, detail="Erreur lors du traitement des données des codes-barres décodés.")

    return DecodeResponse(success=True, barcodes=barcodes_response)

# --- Endpoint /generate/ (inchangé) ---
@app.post("/generate/", responses={ 200: {"content": {"image/png": {}, "image/jpeg": {}, "image/svg+xml": {}}}, 422: {"model": ErrorResponse}, 501: {"model": ErrorResponse}, 500: {"model": ErrorResponse} }, summary="Génère un code-barres GS1", description="Crée une image de code-barres à partir des données GS1 fournies")
async def generate_barcode_image(request: GenerateRequest):
    # ... (code de generate_barcode_image reste identique) ...
    try:
        barcode_format_map = { BarcodeFormat.DATAMATRIX: GenBarcodeFormat.DATAMATRIX, BarcodeFormat.QRCODE: GenBarcodeFormat.QRCODE, BarcodeFormat.CODE128: GenBarcodeFormat.CODE128, BarcodeFormat.GS1_128: GenBarcodeFormat.GS1_128, BarcodeFormat.GS1_DATAMATRIX: GenBarcodeFormat.GS1_DATAMATRIX, BarcodeFormat.GS1_QRCODE: GenBarcodeFormat.GS1_QRCODE, }
        image_format_map = { ImageFormat.PNG: GenImageFormat.PNG, ImageFormat.JPEG: GenImageFormat.JPEG, ImageFormat.SVG: GenImageFormat.SVG, }
        internal_barcode_format = barcode_format_map.get(request.format); internal_image_format = image_format_map.get(request.image_format)
        if internal_barcode_format is None: raise ValueError(f"Format de code-barres non supporté: {request.format}")
        if internal_image_format is None: raise ValueError(f"Format d'image non supporté: {request.image_format}")
        barcode_image_bytes = generate_barcode(data=request.data, barcode_format=internal_barcode_format, image_format=internal_image_format, width=request.width, height=request.height)
        mime_types = { ImageFormat.PNG: "image/png", ImageFormat.JPEG: "image/jpeg", ImageFormat.SVG: "image/svg+xml" }; media_type = mime_types.get(request.image_format)
        if media_type is None: raise ValueError(f"Type MIME inconnu pour format: {request.image_format}")
        return StreamingResponse(io.BytesIO(barcode_image_bytes), media_type=media_type, headers={"Content-Disposition": f"inline; filename=\"barcode_{request.format.value}.{request.image_format.value}\""})
    except ValueError as e: raise HTTPException(status_code=422, detail=str(e))
    except ImportError as e: raise HTTPException(status_code=501, detail=f"Fonctionnalité non disponible (dépendance manquante): {str(e)}")
    except NotImplementedError as e: raise HTTPException(status_code=501, detail=f"Fonctionnalité non implémentée: {str(e)}")
    except Exception as e: print(f"Erreur inattendue lors de la génération du code-barres: {e}"); raise HTTPException(status_code=500, detail=f"Erreur interne lors de la génération du code-barres.")


# --- Fonctions de vérification (MODIFIÉES) ---
def _check_zxing_available():
    # Utilise maintenant le flag PYZXING_AVAILABLE
    return PYZXING_AVAILABLE

def _check_pylibdmtx_available():
    try:
        from pylibdmtx.pylibdmtx import decode as dmtx_decode
        return True
    except ImportError: return False
    except Exception: return False

# --- FIN DU FICHIER main.py ---