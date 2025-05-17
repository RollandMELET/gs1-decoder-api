# --- START OF FILE main.py (Version 1.2.4 - Debug Log Endpoint Added) ---

__version__ = "1.2.4"  # Version de l'application
__author__ = "Rolland Melet"
__email__ = "rolland.melet@example.com" # Remplace par ton email
__description__ = "API pour décoder et générer des codes-barres GS1 via JPype/ZXing et pylibdmtx fallback"
__timestamp__ = "2024-05-18" # Date de la dernière modification significative

# --- Imports ---
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends, Response
from fastapi.responses import StreamingResponse, PlainTextResponse # Added PlainTextResponse
from contextlib import asynccontextmanager
import jpype
import jpype.imports
from jpype.types import JString
from typing import Optional, List, Union, Dict, Any
from enum import Enum

from app.gs1_parser import parse_gs1
from app.models import (
    DecodeResponse, ErrorResponse, HealthResponse,
    GenerateRequest, BarcodeFormat as ModelBarcodeFormat, ImageFormat as ModelImageFormat,
    DecoderInfo, BarcodeItem
)
from app.barcode_detector import DecoderType, BarcodeFormat as DetectedBarcodeFormatEnum
from app.barcode_generator import generate_barcode, BarcodeFormat as GenBarcodeFormat, ImageFormat as GenImageFormat
import shutil
from pylibdmtx.pylibdmtx import decode as dmtx_decode
from PIL import Image
import os
import io
from datetime import datetime
import traceback

# --- Enum for Scan Type Hinting (Ideally move to models.py for better organization) ---
class ScanBarcodeFormatHint(str, Enum):
    DATAMATRIX = "DATAMATRIX"
    QR_CODE = "QR_CODE"
    CODE_128 = "CODE_128"

# --- JPype Global Variables ---
# (Identique à la version précédente, non répété ici pour la brièveté)
jpype_started = False
NotFoundException_Java = None
IOException_Java = None
ImageIO_Java = None
File_Java = None
BufferedImageLuminanceSource_Java = None
HybridBinarizer_Java = None
BinaryBitmap_Java = None
MultiFormatReader_Java = None
DecodeHintType_Java = None
Hints_Java = None
BarcodeFormat_Java = None

ZXING_CLASSPATH = "/zxing/core.jar:/zxing/javase.jar"

# --- Lifespan Manager ---
# (Identique à la version précédente, non répété ici pour la brièveté)
@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    global jpype_started, NotFoundException_Java, IOException_Java, ImageIO_Java, File_Java
    global BufferedImageLuminanceSource_Java, HybridBinarizer_Java, BinaryBitmap_Java
    global MultiFormatReader_Java, DecodeHintType_Java, Hints_Java, BarcodeFormat_Java

    print("Starting JPype JVM...")
    try:
        if not jpype.isJVMStarted():
             jpype.startJVM(
                 jpype.getDefaultJVMPath(),
                 "-ea",
                 f"-Djava.class.path={ZXING_CLASSPATH}",
                 convertStrings=False
             )
             jpype_started = True
             print("JPype JVM Started Successfully.")

             print("Importing Java classes...")
             NotFoundException_Java = jpype.JClass("com.google.zxing.NotFoundException")
             IOException_Java = jpype.JClass("java.io.IOException")
             ImageIO_Java = jpype.JClass("javax.imageio.ImageIO")
             File_Java = jpype.JClass("java.io.File")
             BufferedImageLuminanceSource_Java = jpype.JClass("com.google.zxing.client.j2se.BufferedImageLuminanceSource")
             HybridBinarizer_Java = jpype.JClass("com.google.zxing.common.HybridBinarizer")
             BinaryBitmap_Java = jpype.JClass("com.google.zxing.BinaryBitmap")
             MultiFormatReader_Java = jpype.JClass("com.google.zxing.MultiFormatReader")
             DecodeHintType_Java = jpype.JClass("com.google.zxing.DecodeHintType")
             Hints_Java = jpype.JClass("java.util.Hashtable")
             BarcodeFormat_Java = jpype.JClass("com.google.zxing.BarcodeFormat")
             print("Java classes imported.")

    except Exception as e:
        print(f"FATAL: Failed to start JPype JVM or import classes: {e}")
        if isinstance(e, jpype.JException) and hasattr(e, 'stacktrace'):
            print(f"Java Stack Trace during startup:\n{e.stacktrace()}")
        jpype_started = False

    yield
    print("FastAPI shutting down. JPype JVM will shut down with the Python process if not manually stopped.")


# --- Application FastAPI ---
app = FastAPI(
    title="GS1 Decoder API (JPype)",
    description=f"{__description__} (Version: {__version__})", # Utilise la description dundee
    version=__version__, # Utilise la version dunder
    lifespan=lifespan
)

#
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!! ATTENTION : ENDPOINT DE DÉBOGAGE CI-DESSOUS                         !!!
# !!! Cet endpoint est destiné UNIQUEMENT au débogage et NE DOIT PAS      !!!
# !!! être déployé en production, car il expose le contenu de fichiers   !!!
# !!! sur le serveur.                                                     !!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#
@app.get("/_debug_log_viewer/{log_filename:path}", response_class=PlainTextResponse, include_in_schema=False)
async def get_debug_log_viewer(log_filename: str):
    """
    *** ENDPOINT DE DÉBOGAGE UNIQUEMENT - À RETIRER AVANT PRODUCTION ***
    Lit et retourne le contenu d'un fichier log spécifié depuis /tmp/logs/.
    Exemple d'usage: /_debug_log_viewer/tipi_datamatrix_scan_log.txt
    """
    print(f"WARNING: Debug endpoint /_debug_log_viewer accessed for file: {log_filename}")
    # Par sécurité, on ne permet que de lire dans /tmp/logs/
    # et on s'assure que log_filename ne contient pas ".." pour éviter le path traversal.
    if ".." in log_filename:
        raise HTTPException(status_code=400, detail="Path traversal attempt detected.")
    
    # Le chemin est relatif à la racine du conteneur où l'API tourne
    # Si log_file dans cURL est /tmp/logs/X.txt, alors log_filename sera X.txt ici si on prend que le basename
    # Ou si on attend le chemin complet :
    # log_path = log_filename # si log_filename est déjà /tmp/logs/X.txt
    # Pour plus de sécurité, forçons le préfixe /tmp/logs/
    
    # Si log_filename est juste le nom du fichier (ex: "mon_log.txt")
    # log_path = os.path.join("/tmp/logs/", log_filename)
    
    # Si log_filename est le chemin complet DANS le conteneur (ex: "/tmp/logs/mon_log.txt")
    # On valide qu'il commence bien par le répertoire autorisé
    allowed_log_dir = "/tmp/logs/"
    if not log_filename.startswith(allowed_log_dir):
        # Si on veut être strict sur le nom de fichier passé via cURL
        # raise HTTPException(status_code=400, detail=f"Log file must be within {allowed_log_dir}")
        # Ou si on attend juste le nom et on préfixe :
        log_path = os.path.join(allowed_log_dir, os.path.basename(log_filename)) # Plus sûr, prend que le nom du fichier
    else: # Le chemin complet a été passé, on l'utilise (après check ".." ci-dessus)
         log_path = log_filename


    if not os.path.exists(log_path):
        raise HTTPException(status_code=404, detail=f"Log file not found at: {log_path}")
    
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
        return PlainTextResponse(content=content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading log file {log_path}: {str(e)}")
#
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!! FIN DE L'ENDPOINT DE DÉBOGAGE                                       !!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#

@app.get("/health", response_model=HealthResponse)
async def health():
    zxing_ok = jpype_started and MultiFormatReader_Java is not None and shutil.which("java") is not None
    capabilities = {
        "decoders": {
            "zxing_jpype": zxing_ok,
            "pylibdmtx": _check_pylibdmtx_available()
        },
        "supported_codes": [fmt.value for fmt in DetectedBarcodeFormatEnum if fmt != DetectedBarcodeFormatEnum.UNKNOWN],
        "api_version": app.version,
        "features": {"decode": True, "generate": True }
    }
    return {"status": "OK", "capabilities": capabilities}

@app.post(
    "/decode/",
    response_model=DecodeResponse,
    responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Décode des codes-barres à partir d'une image via JPype/ZXing",
    description="Tente de décoder via l'API Java ZXing, puis fallback pylibdmtx. Permet de spécifier les types de codes à rechercher."
)
async def decode_image(
    file: UploadFile = File(...),
    verbose: bool = Form(False),
    debug: bool = Form(False),
    log_file_name: Optional[str] = Form(None, alias="log_file"),
    scan_types: Optional[List[ScanBarcodeFormatHint]] = Form(None, alias="scan_types", description="Liste des types de codes-barres à rechercher (ex: DATAMATRIX, QR_CODE). Défaut: tous.")
):
    # ... (Contenu de la fonction decode_image identique à la version 1.2.3 que tu as déjà) ...
    # ... (Elle inclut déjà la création du répertoire de log os.makedirs) ...
    global jpype_started, NotFoundException_Java, IOException_Java, ImageIO_Java, File_Java
    global BufferedImageLuminanceSource_Java, HybridBinarizer_Java, BinaryBitmap_Java
    global MultiFormatReader_Java, DecodeHintType_Java, Hints_Java, BarcodeFormat_Java

    temp_file_path = f"/tmp/uploaded_{file.filename}"
    logf = None

    try:
        try:
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            print(f"Erreur sauvegarde fichier temp: {str(e)}") 
            raise HTTPException(status_code=500, detail=f"Erreur sauvegarde fichier temp: {str(e)}")

        if debug and log_file_name:
            try:
                log_dir = os.path.dirname(log_file_name)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir, exist_ok=True)
                logf = open(log_file_name, "a", encoding="utf-8")
                logf.write(f"\n--- New Decode Request ({datetime.now()}) ---\n")
                logf.write(f"[DEBUG] Uploaded file: {file.filename}, Saved to: {temp_file_path}\n")
                logf.write(f"[DEBUG] Verbose: {verbose}, Debug: {debug}, LogFile: {log_file_name}\n")
                logf.write(f"[DEBUG] Scan types requested: {scan_types if scan_types else 'Default (All)'}\n")
            except Exception as e:
                print(f"Warning: Impossible d'ouvrir le fichier de log {log_file_name}: {e}")
                logf = None

        decoded_data_list = []
        decoder_used = DecoderType.NONE
        zxing_error_msg = None
        barcode_format_hint_from_decoder = None

        if jpype_started and MultiFormatReader_Java and BarcodeFormat_Java:
            try:
                if logf: logf.write(f"[DEBUG] Attempting decode with JPype/ZXing...\n")
                
                j_file = File_Java(JString(temp_file_path))
                if not j_file.exists():
                    if logf: logf.write(f"[ERROR] Java File object reports not found: {temp_file_path}\n")
                    raise FileNotFoundError(f"Java File object reports not found: {temp_file_path}")

                buffered_image = ImageIO_Java.read(j_file)
                if buffered_image is None:
                    if logf: logf.write(f"[ERROR] ImageIO.read returned null for {temp_file_path}. Image format unsupported or file corrupt.\n")
                    raise ValueError("ImageIO.read returned null; image format might be unsupported by Java or file is corrupt.")

                luminance_source = BufferedImageLuminanceSource_Java(buffered_image)
                binarizer = HybridBinarizer_Java(luminance_source)
                binary_bitmap = BinaryBitmap_Java(binarizer)

                hints = Hints_Java()
                possible_formats_vector = jpype.java.util.Vector()
                
                format_map_to_zxing = {
                    ScanBarcodeFormatHint.DATAMATRIX: BarcodeFormat_Java.DATA_MATRIX,
                    ScanBarcodeFormatHint.QR_CODE: BarcodeFormat_Java.QR_CODE,
                    ScanBarcodeFormatHint.CODE_128: BarcodeFormat_Java.CODE_128,
                }

                apply_default_zxing_formats = True
                if scan_types:
                    user_requested_zxing_formats = False
                    for stype in scan_types:
                        if stype in format_map_to_zxing:
                            possible_formats_vector.add(format_map_to_zxing[stype])
                            if logf: logf.write(f"[DEBUG] Adding {stype.value} to ZXing hints.\n")
                            user_requested_zxing_formats = True
                    if user_requested_zxing_formats:
                        apply_default_zxing_formats = False
                    elif logf:
                         logf.write(f"[WARN] User specified scan_types {scan_types} but none mapped. Applying default ZXing formats.\n")
                
                if apply_default_zxing_formats:
                    if logf: logf.write(f"[DEBUG] Applying default ZXing formats: DATA_MATRIX, QR_CODE, CODE_128.\n")
                    possible_formats_vector.add(BarcodeFormat_Java.DATA_MATRIX)
                    possible_formats_vector.add(BarcodeFormat_Java.QR_CODE)
                    possible_formats_vector.add(BarcodeFormat_Java.CODE_128)
                
                if not possible_formats_vector.isEmpty():
                    hints.put(DecodeHintType_Java.POSSIBLE_FORMATS, possible_formats_vector)
                
                hints.put(DecodeHintType_Java.TRY_HARDER, jpype.java.lang.Boolean.TRUE)

                reader = MultiFormatReader_Java()
                java_result = reader.decode(binary_bitmap, hints)

                if java_result:
                    raw_java_string = java_result.getText()
                    raw_python_string = str(raw_java_string)
                    detected_java_format_obj = java_result.getBarcodeFormat()
                    
                    decoded_data_list = [raw_python_string]
                    decoder_used = DecoderType.ZXING
                    barcode_format_hint_from_decoder = str(detected_java_format_obj)

                    if logf:
                        logf.write(f"[DEBUG] JPype/ZXing success. Format hint: {barcode_format_hint_from_decoder}\n")
                        logf.write(f"[DEBUG] Raw data (repr): {repr(raw_python_string)}\n")
                else:
                    zxing_error_msg = "ZXing reader.decode() returned null (no barcode found, no exception)"
                    if logf: logf.write(f"[WARN] JPype/ZXing: {zxing_error_msg}\n")
            
            except NotFoundException_Java as e_nf:
                zxing_error_msg = "NotFoundException (no code found by ZXing)"
                if logf: logf.write(f"[DEBUG] JPype/ZXing: {zxing_error_msg}. Java Detail: {e_nf.getMessage() if hasattr(e_nf, 'getMessage') else e_nf}\n")
            except IOException_Java as e_io:
                zxing_error_msg = f"IOException during ZXing processing"
                if logf: logf.write(f"[ERROR] JPype/ZXing: {zxing_error_msg}. Java Detail: {e_io.getMessage() if hasattr(e_io, 'getMessage') else e_io}\n")
            except jpype.JException as e_j:
                zxing_error_msg = f"Generic JPype/ZXing Java Error: {e_j.getClass().getName()}"
                if logf: logf.write(f"[ERROR] {zxing_error_msg}\n")
                if hasattr(e_j, 'stacktrace'):
                    stack_trace = e_j.stacktrace()
                    if logf: logf.write(f"Java Stack Trace:\n{stack_trace}\n")
                elif logf: logf.write(f"Raw Java Exception (no stacktrace method): {e_j}\n")
            except Exception as e_py:
                zxing_error_msg = f"Python Error during JPype/ZXing attempt: {type(e_py).__name__} - {e_py}"
                if logf: logf.write(f"[ERROR] {zxing_error_msg}\n")
            
            if zxing_error_msg:
                decoded_data_list = []
        else:
            if logf: logf.write("[DEBUG] Skipping JPype/ZXing: JPype not started or core Java classes not available.\n")
            zxing_error_msg = "JPype/ZXing not available or not initialized"

        if not decoded_data_list:
            if logf:
                logf.write(f"[DEBUG] ZXing did not find codes (Reason: {zxing_error_msg if zxing_error_msg else 'skipped/not available'}).\n")
            
            should_try_pylibdmtx = True
            if scan_types and ScanBarcodeFormatHint.DATAMATRIX not in scan_types:
                should_try_pylibdmtx = False
                if logf: logf.write(f"[DEBUG] Skipping pylibdmtx fallback as DATAMATRIX not in scan_types: {scan_types}.\n")
            
            if should_try_pylibdmtx:
                if _check_pylibdmtx_available():
                    if logf: logf.write(f"[DEBUG] Trying pylibdmtx...\n")
                    try:
                        pil_image = Image.open(temp_file_path)
                        dmtx_results = dmtx_decode(pil_image.convert('L'), timeout=500, max_count=1)
                        if dmtx_results:
                            decoded_data_list = [res.data.decode("utf-8", errors="replace") for res in dmtx_results]
                            decoder_used = DecoderType.PYLIBDMTX
                            barcode_format_hint_from_decoder = "DATA_MATRIX"
                            if logf:
                                logf.write(f"[DEBUG] pylibdmtx found {len(decoded_data_list)} DataMatrix code(s).\n")
                                for i, raw_data in enumerate(decoded_data_list):
                                    logf.write(f"[DEBUG] pylibdmtx raw data {i} (repr): {repr(raw_data)}\n")
                        else:
                            if logf: logf.write("[DEBUG] pylibdmtx found no codes.\n")
                    except Exception as e:
                        if logf: logf.write(f"[ERROR] pylibdmtx error: {type(e).__name__} - {e}\n")
                        decoded_data_list = []
                elif logf:
                    logf.write("[DEBUG] pylibdmtx not available for fallback.\n")

        if logf:
            logf.write(f"[DEBUG] Final decoder: {decoder_used.value if decoder_used else 'None'}\n")
            logf.write(f"[DEBUG] Final decoded data count: {len(decoded_data_list)}\n")
            
        if not decoded_data_list:
            detail_msg = "Aucun code-barres n'a pu être détecté ou décodé dans l'image."
            if zxing_error_msg and decoder_used == DecoderType.NONE : 
                 detail_msg += f" (Info décodeur principal: {zxing_error_msg})"
            if logf: logf.write(f"[INFO] No barcodes decoded. Raising HTTPException: {detail_msg}\n")
            raise HTTPException(status_code=422, detail=detail_msg)

        barcodes_response_items = []
        for raw_data_str in decoded_data_list:
            try:
                parsed_gs1_data = parse_gs1(raw_data_str, verbose=verbose)
                
                actual_decoder_name_str = "Unknown"
                if decoder_used == DecoderType.ZXING:
                    actual_decoder_name_str = "ZXing (JPype)"
                elif decoder_used == DecoderType.PYLIBDMTX:
                    actual_decoder_name_str = "pylibdmtx"

                decoder_info_dict = get_decoder_info_adjusted(
                    raw_data_str, 
                    decoder_used,
                    barcode_format_hint_from_decoder, 
                    verbose=verbose
                )
                decoder_info_dict["decoder"] = actual_decoder_name_str 

                decoder_info_model = DecoderInfo(**decoder_info_dict)
                barcode_item = BarcodeItem(raw=raw_data_str, parsed=parsed_gs1_data, decoder_info=decoder_info_model)
                barcodes_response_items.append(barcode_item)
            except Exception as e_parse:
                error_msg = f"Erreur parsing GS1/construction item pour '{repr(raw_data_str)}': {type(e_parse).__name__} - {e_parse}"
                if logf: logf.write(f"[ERROR] {error_msg}\n")

        if not barcodes_response_items:
            msg = "Données décodées mais aucune n'a pu être parsée correctement."
            if logf: logf.write(f"[ERROR] {msg}. Raising HTTPException.\n")
            raise HTTPException(status_code=500, detail=msg)

        if logf: logf.write(f"[INFO] Processed {len(barcodes_response_items)} barcodes.\n")
        return DecodeResponse(success=True, barcodes=barcodes_response_items)

    finally:
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                if logf and not logf.closed : logf.write(f"[DEBUG] Temp file {temp_file_path} removed.\n")
            except OSError as e_remove:
                if logf and not logf.closed: logf.write(f"[WARN] Could not remove temp file {temp_file_path}: {e_remove}\n")
        
        if logf and not logf.closed:
            logf.write("--- End of Decode Request ---\n")
            logf.close()


@app.post("/generate/", 
          responses={ # ... (identique à la version précédente) ...
               200: {"content": {"image/png": {}, "image/jpeg": {}, "image/svg+xml": {}}}, 
              422: {"model": ErrorResponse}, 
              501: {"model": ErrorResponse}, 
              500: {"model": ErrorResponse} 
          },
          summary="Génère un code-barres GS1", 
          description="Crée une image de code-barres à partir des données GS1 fournies")
async def generate_barcode_image(request: GenerateRequest):
    # ... (Contenu de la fonction generate_barcode_image identique à la version 1.2.3) ...
    try:
        barcode_format_map = {
            ModelBarcodeFormat.DATAMATRIX: GenBarcodeFormat.DATAMATRIX,
            ModelBarcodeFormat.QRCODE: GenBarcodeFormat.QRCODE,
            ModelBarcodeFormat.CODE128: GenBarcodeFormat.CODE128,
            ModelBarcodeFormat.GS1_128: GenBarcodeFormat.GS1_128,
            ModelBarcodeFormat.GS1_DATAMATRIX: GenBarcodeFormat.GS1_DATAMATRIX,
            ModelBarcodeFormat.GS1_QRCODE: GenBarcodeFormat.GS1_QRCODE,
        }
        image_format_map = {
            ModelImageFormat.PNG: GenImageFormat.PNG,
            ModelImageFormat.JPEG: GenImageFormat.JPEG,
            ModelImageFormat.SVG: GenImageFormat.SVG,
        }

        internal_barcode_format = barcode_format_map.get(request.format)
        internal_image_format = image_format_map.get(request.image_format)

        if internal_barcode_format is None:
            raise ValueError(f"Format de code-barres non supporté pour la génération: {request.format.value}")
        if internal_image_format is None:
            raise ValueError(f"Format d'image non supporté pour la génération: {request.image_format.value}")

        barcode_image_bytes = generate_barcode(
            data=request.data,
            barcode_format=internal_barcode_format,
            image_format=internal_image_format,
            width=request.width,
            height=request.height
        )
        
        mime_types = {
            ModelImageFormat.PNG: "image/png",
            ModelImageFormat.JPEG: "image/jpeg",
            ModelImageFormat.SVG: "image/svg+xml"
        }
        media_type = mime_types.get(request.image_format)
        if media_type is None:
            raise ValueError(f"Type MIME inconnu pour le format d'image: {request.image_format.value}")

        return StreamingResponse(
            io.BytesIO(barcode_image_bytes),
            media_type=media_type,
            headers={"Content-Disposition": f"inline; filename=\"barcode_{request.format.value}.{request.image_format.value}\""}
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ImportError as e:
        raise HTTPException(status_code=501, detail=f"Fonctionnalité de génération non disponible (dépendance manquante): {str(e)}")
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=f"Fonctionnalité de génération non implémentée: {str(e)}")
    except Exception as e:
        print(f"Erreur inattendue lors de la génération du code-barres: {type(e).__name__} - {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Erreur interne du serveur lors de la génération du code-barres.")

def _check_pylibdmtx_available():
    # ... (identique à la version précédente) ...
    try:
        return True
    except ImportError:
        return False
    except Exception:
        return False

# --- Helper function for Decoder Info ---
# (Identique à la version précédente, non répété ici pour la brièveté)
from app.barcode_detector import is_gs1_data, detect_generic_format, calculate_confidence, get_barcode_characteristics

def get_decoder_info_adjusted(raw_data: str, decoder_used_enum: DecoderType, format_hint_str: Optional[str] = None, verbose: bool = False) -> dict:
    detected_format_enum = DetectedBarcodeFormatEnum.UNKNOWN
    is_gs1 = is_gs1_data(raw_data)

    if format_hint_str:
        hint_upper = format_hint_str.upper().replace("_", "")
        if hint_upper == "DATAMATRIX":
            detected_format_enum = DetectedBarcodeFormatEnum.GS1_DATAMATRIX if is_gs1 else DetectedBarcodeFormatEnum.DATAMATRIX
        elif hint_upper == "QRCODE":
            detected_format_enum = DetectedBarcodeFormatEnum.GS1_QRCODE if is_gs1 else DetectedBarcodeFormatEnum.QRCODE
        elif hint_upper == "CODE128":
            detected_format_enum = DetectedBarcodeFormatEnum.GS1_128 if is_gs1 else DetectedBarcodeFormatEnum.CODE128

    if detected_format_enum == DetectedBarcodeFormatEnum.UNKNOWN:
        if is_gs1:
            from app.barcode_detector import has_datamatrix_characteristics, has_qrcode_characteristics
            if decoder_used_enum == DecoderType.PYLIBDMTX :
                detected_format_enum = DetectedBarcodeFormatEnum.GS1_DATAMATRIX
            elif has_datamatrix_characteristics(raw_data):
                 detected_format_enum = DetectedBarcodeFormatEnum.GS1_DATAMATRIX
            elif has_qrcode_characteristics(raw_data):
                 detected_format_enum = DetectedBarcodeFormatEnum.GS1_QRCODE
            else:
                 detected_format_enum = DetectedBarcodeFormatEnum.GS1_128
        else:
            detected_format_enum = detect_generic_format(raw_data)

    if detected_format_enum == DetectedBarcodeFormatEnum.UNKNOWN:
        if is_gs1 : # If it's GS1 data but no specific format matched, default to GS1_128
            detected_format_enum = DetectedBarcodeFormatEnum.GS1_128
    
    info = {
        "decoder": decoder_used_enum.value, # Will be overwritten by user-friendly string
        "format": detected_format_enum.value,
        "is_gs1": detected_format_enum in [
            DetectedBarcodeFormatEnum.GS1_DATAMATRIX,
            DetectedBarcodeFormatEnum.GS1_QRCODE,
            DetectedBarcodeFormatEnum.GS1_128
        ]
    }

    if verbose:
        info["confidence"] = calculate_confidence(raw_data, decoder_used_enum, detected_format_enum)
        info["characteristics"] = get_barcode_characteristics(raw_data, detected_format_enum)

    return info

# --- END OF FILE main.py ---