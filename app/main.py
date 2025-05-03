# --- START OF FILE main.py (Cleaned JPype Version) ---

from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends, Response
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import jpype
import jpype.imports
from jpype.types import JString

from app.gs1_parser import parse_gs1 # Utiliser le parser original
from app.models import (
    DecodeResponse, ErrorResponse, HealthResponse,
    GenerateRequest, BarcodeFormat, ImageFormat,
    DecoderInfo, BarcodeItem
)
# --- MODIFICATION: Importer barcode_detector pour ajustement ---
from app.barcode_detector import DecoderType, get_decoder_info, BarcodeFormat as DetectedBarcodeFormat
from app.barcode_generator import generate_barcode, BarcodeFormat as GenBarcodeFormat, ImageFormat as GenImageFormat
import shutil
from pylibdmtx.pylibdmtx import decode as dmtx_decode
from PIL import Image
import os
import io

# --- JPype Global Variables ---
jpype_started = False
NotFoundException = None
IOException = None
ImageIO = None
File_java = None
BufferedImageLuminanceSource = None
HybridBinarizer = None
BinaryBitmap = None
MultiFormatReader = None
DecodeHintType = None
Hints_java = None
ZXING_CLASSPATH = "/zxing/core.jar:/zxing/javase.jar"

# --- Lifespan Manager (inchangé mais essentiel) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global jpype_started, NotFoundException, IOException, ImageIO, File_java
    global BufferedImageLuminanceSource, HybridBinarizer, BinaryBitmap
    global MultiFormatReader, DecodeHintType, Hints_java

    print("Starting JPype JVM...")
    try:
        if not jpype.isJVMStarted():
             jpype.startJVM(
                 jpype.getDefaultJVMPath(),
                 "-ea",
                 f"-Djava.class.path={ZXING_CLASSPATH}",
                 convertStrings=False # Crucial pour \x1d
             )
             jpype_started = True
             print("JPype JVM Started Successfully.")

             print("Importing Java classes...")
             NotFoundException = jpype.JClass("com.google.zxing.NotFoundException")
             IOException = jpype.JClass("java.io.IOException")
             ImageIO = jpype.JClass("javax.imageio.ImageIO")
             File_java = jpype.JClass("java.io.File")
             BufferedImageLuminanceSource = jpype.JClass("com.google.zxing.client.j2se.BufferedImageLuminanceSource")
             HybridBinarizer = jpype.JClass("com.google.zxing.common.HybridBinarizer")
             BinaryBitmap = jpype.JClass("com.google.zxing.BinaryBitmap")
             MultiFormatReader = jpype.JClass("com.google.zxing.MultiFormatReader")
             DecodeHintType = jpype.JClass("com.google.zxing.DecodeHintType")
             Hints_java = jpype.JClass("java.util.Hashtable")
             print("Java classes imported.")

    except Exception as e:
        print(f"FATAL: Failed to start JPype JVM or import classes: {e}")
        jpype_started = False

    yield
    print("FastAPI shutting down (JPype JVM remains running).")

# --- Application FastAPI ---
app = FastAPI(
    title="GS1 Decoder API (JPype)",
    description="API pour décoder et générer des codes-barres GS1 via JPype/ZXing et pylibdmtx fallback",
    version="1.2.0", # Version stable
    lifespan=lifespan
)

@app.get("/health", response_model=HealthResponse)
async def health():
    zxing_ok = jpype_started and MultiFormatReader is not None and shutil.which("java") is not None
    capabilities = {
        "decoders": {
            "zxing_jpype": zxing_ok, # Préciser JPype
            "pylibdmtx": _check_pylibdmtx_available()
        },
        "supported_codes": ["DataMatrix", "QR Code", "GS1-128", "GS1 DataMatrix", "GS1 QR Code"],
        "api_version": app.version,
        "features": {"decode": True, "generate": True } # Réactiver generate
    }
    return {"status": "OK", "capabilities": capabilities}

@app.post(
    "/decode/",
    response_model=DecodeResponse,
    responses={422: {"model": ErrorResponse}},
    summary="Décode des codes-barres à partir d'une image via JPype/ZXing",
    description="Tente de décoder via l'API Java ZXing, puis fallback pylibdmtx."
)
async def decode_image(
    file: UploadFile = File(...),
    verbose: bool = Form(False),
    debug: bool = Form(False),
    log_file: str = Form(None)
):
    global jpype_started, NotFoundException, IOException, ImageIO, File_java
    global BufferedImageLuminanceSource, HybridBinarizer, BinaryBitmap
    global MultiFormatReader, DecodeHintType, Hints_java

    temp_file_path = f"/tmp/uploaded_{file.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur sauvegarde fichier temp: {e}")

    logf = None
    if debug and log_file:
        try:
            logf = open(log_file, "w") # Ecraser log
            logf.write(f"--- New Decode Request ---\n")
            logf.write(f"[DEBUG] Saved upload to {temp_file_path}\n")
        except Exception as e:
            print(f"Warning: Impossible d'ouvrir le fichier de log {log_file}: {e}")
            logf = None

    decoded = []
    decoder_used = DecoderType.NONE
    zxing_error_msg = None
    barcode_format_hint = None # Pour aider get_decoder_info

    # 1) ZXing attempt (via JPype)
    if jpype_started and MultiFormatReader:
        try:
            if logf: logf.write(f"[DEBUG] Attempting decode with JPype/ZXing...\n")
            j_file = File_java(JString(temp_file_path))
            if not j_file.exists(): raise FileNotFoundError(f"Java file not found: {temp_file_path}")

            buffered_image = ImageIO.read(j_file)
            if buffered_image is None: raise ValueError("ImageIO could not read file")

            luminance_source = BufferedImageLuminanceSource(buffered_image)
            binarizer = HybridBinarizer(luminance_source)
            binary_bitmap = BinaryBitmap(binarizer)

            hints = Hints_java()
            possible_formats = jpype.java.util.Vector()
            # Essayer de détecter tous les formats supportés par ZXing que l'on gère
            possible_formats.add(jpype.JClass("com.google.zxing.BarcodeFormat").DATA_MATRIX)
            possible_formats.add(jpype.JClass("com.google.zxing.BarcodeFormat").QR_CODE)
            possible_formats.add(jpype.JClass("com.google.zxing.BarcodeFormat").CODE_128)
            hints.put(DecodeHintType.POSSIBLE_FORMATS, possible_formats)
            hints.put(DecodeHintType.TRY_HARDER, jpype.java.lang.Boolean.TRUE)

            reader = MultiFormatReader()
            java_result = reader.decode(binary_bitmap, hints)

            if java_result:
                raw_java_string = java_result.getText()
                raw_python_string = str(raw_java_string) # Conversion Python str
                detected_java_format = java_result.getBarcodeFormat()

                decoded = [raw_python_string]
                decoder_used = DecoderType.ZXING # On utilise le type ZXING standard
                barcode_format_hint = str(detected_java_format) # Ex: "DATA_MATRIX"

                if logf:
                    logf.write(f"[DEBUG] JPype/ZXing success. Format: {barcode_format_hint}\n")
                    logf.write(f"[DEBUG] Raw data (repr): {repr(raw_python_string)}\n") # Log du repr ici

            else: # Ne devrait pas arriver normalement
                zxing_error_msg = "decode returned null"
                if logf: logf.write(f"[WARN] JPype/ZXing {zxing_error_msg}\n")

        except jpype.JException(NotFoundException) as e:
            zxing_error_msg = "NotFoundException (no code found)"
            if logf: logf.write(f"[DEBUG] JPype/ZXing: {zxing_error_msg}\n")
        except jpype.JException(IOException) as e:
             zxing_error_msg = f"IOException reading image: {e}"
             if logf: logf.write(f"[ERROR] JPype/ZXing: {zxing_error_msg}\n")
        except Exception as e:
            zxing_error_msg = f"JPype/ZXing Error: {e}"
            if logf: logf.write(f"[ERROR] {zxing_error_msg}\n")
            if isinstance(e, jpype.JException):
                 print(f"Java Stack Trace:\n{e.stacktrace()}")
                 if logf: logf.write(f"Java Stack Trace:\n{e.stacktrace()}\n")
            decoded = [] # Echec -> liste vide
    else:
        if logf: logf.write("[DEBUG] Skipping JPype/ZXing: not available.\n")
        zxing_error_msg = "JPype/ZXing not available"

    # 2) Fallback to pylibdmtx if JPype/ZXing failed
    if not decoded:
        if logf:
            logf.write(f"[DEBUG] JPype/ZXing failed ({zxing_error_msg}). Trying pylibdmtx...\n")
        if _check_pylibdmtx_available():
            try:
                img = Image.open(temp_file_path)
                dmtx_results = dmtx_decode(img.convert('L'))
                if dmtx_results:
                    decoded = [res.data.decode("utf-8") for res in dmtx_results]
                    decoder_used = DecoderType.PYLIBDMTX
                    barcode_format_hint = "DATA_MATRIX" # pylibdmtx ne fait que ça
                    if logf: logf.write(f"[DEBUG] pylibdmtx found {len(decoded)} code(s).\n")
                    if logf: # Log repr ici aussi pour comparer si besoin
                         for i, raw_data in enumerate(decoded):
                            logf.write(f"[DEBUG] pylibdmtx raw data item {i} (repr): {repr(raw_data)}\n")
                else:
                     if logf: logf.write("[DEBUG] pylibdmtx found no codes.\n")
            except Exception as e:
                if logf: logf.write(f"[ERROR] pylibdmtx error: {e}\n")
                decoded = [] # Echec fallback
        else:
             if logf: logf.write("[DEBUG] pylibdmtx not available for fallback.\n")

    # Finalize logs section (juste fin du log)
    if logf:
        logf.write(f"[DEBUG] Final decoder selected: {decoder_used}\n")
        logf.write(f"[DEBUG] Final data count: {len(decoded)}\n")
        logf.close()

    # Supprimer le fichier temporaire
    try:
        os.remove(temp_file_path)
    except OSError as e:
        print(f"Warning: Could not remove temporary file {temp_file_path}: {e}")

    # Gérer l'échec final
    if not decoded:
        detail_msg = "Aucun code-barres détecté ou décodable dans l'image."
        if zxing_error_msg and decoder_used == DecoderType.NONE:
             detail_msg += f" (ZXing Error: {zxing_error_msg})"
        raise HTTPException(status_code=422, detail=detail_msg)

    # Parsing et construction réponse
    barcodes_response = []
    for raw in decoded:
        try:
            # Utiliser le parser GS1 original (qui fonctionne avec \x1d)
            parsed_data = parse_gs1(raw, verbose=verbose)

            # --- Utilisation de get_decoder_info (peut être ajusté plus tard) ---
            # On passe le nom Java brut du format si on l'a, sinon None
            decoder_name_for_info = "ZXing (JPype)" if decoder_used == DecoderType.ZXING else decoder_used.value
            # Utiliser le barcode_format_hint obtenu du décodeur
            decoder_info_dict = get_decoder_info_adjusted(raw, decoder_used, barcode_format_hint, verbose=verbose)
            # Surcharger le nom du décodeur
            decoder_info_dict["decoder"] = decoder_name_for_info

            decoder_info_model = DecoderInfo(**decoder_info_dict)
            barcode_item = BarcodeItem(raw=raw, parsed=parsed_data, decoder_info=decoder_info_model)
            barcodes_response.append(barcode_item)
        except Exception as e:
            print(f"Error processing barcode data '{raw}': {e}") # Log erreur parsing
            # Ne pas planter toute la requête si un seul code échoue au parsing

    if not barcodes_response: # Si le parsing a échoué pour tous les codes trouvés
         raise HTTPException(
            status_code=500,
            detail="Données décodées mais erreur lors du parsing GS1."
        )

    return DecodeResponse(success=True, barcodes=barcodes_response)

# --- Endpoint /generate/ (peut être réactivé si besoin) ---
@app.post("/generate/", responses={ 200: {"content": {"image/png": {}, "image/jpeg": {}, "image/svg+xml": {}}}, 422: {"model": ErrorResponse}, 501: {"model": ErrorResponse}, 500: {"model": ErrorResponse} }, summary="Génère un code-barres GS1", description="Crée une image de code-barres à partir des données GS1 fournies")
async def generate_barcode_image(request: GenerateRequest):
    # ... (code generate inchangé) ...
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

# --- Fonctions de vérification (inchangées) ---
def _check_zxing_available():
    return jpype_started and MultiFormatReader is not None and shutil.which("java") is not None

def _check_pylibdmtx_available():
    try:
        from pylibdmtx.pylibdmtx import decode as dmtx_decode
        return True
    except ImportError: return False
    except Exception: return False

# --- Fonction Ajustée pour obtenir DecoderInfo ---
# Ceci est une copie de get_decoder_info de barcode_detector.py
# avec un ajustement pour utiliser le format hint de JPype/ZXing si disponible
# Idéalement, cette logique devrait être DANS barcode_detector.py
from app.barcode_detector import is_gs1_data, detect_generic_format, calculate_confidence, get_barcode_characteristics

def get_decoder_info_adjusted(raw_data, decoder_used, format_hint=None, verbose=False):
    """
    Génère des informations détaillées sur le décodage,
    en utilisant une indication de format si fournie par le décodeur.
    """
    detected_format = None
    is_gs1 = is_gs1_data(raw_data)

    # Utiliser l'indice de format si disponible (plus fiable)
    if format_hint:
        if format_hint == "DATA_MATRIX":
            detected_format = DetectedBarcodeFormat.GS1_DATAMATRIX if is_gs1 else DetectedBarcodeFormat.DATAMATRIX
        elif format_hint == "QR_CODE":
             detected_format = DetectedBarcodeFormat.GS1_QRCODE if is_gs1 else DetectedBarcodeFormat.QRCODE
        elif format_hint == "CODE_128":
             detected_format = DetectedBarcodeFormat.GS1_128 if is_gs1 else DetectedBarcodeFormat.CODE128
        # Ajouter d'autres formats si nécessaire
        else: # Fallback si format_hint non géré
             detected_format = detect_generic_format(raw_data)
             if is_gs1 and detected_format in [DetectedBarcodeFormat.CODE128, DetectedBarcodeFormat.UNKNOWN]:
                   detected_format = DetectedBarcodeFormat.GS1_128 # Supposer GS1-128 si GS1 et format linéaire/inconnu

    # Si pas d'indice, utiliser la détection basée sur les données
    if detected_format is None:
        if is_gs1:
            # On pourrait essayer d'affiner ici, mais sans info décodeur c'est dur
            # Par défaut, on pourrait supposer DataMatrix si contient '.' ou est long?
            # Ou rester générique si impossible de deviner
            from app.barcode_detector import has_datamatrix_characteristics, has_qrcode_characteristics
            if has_datamatrix_characteristics(raw_data):
                 detected_format = DetectedBarcodeFormat.GS1_DATAMATRIX
            elif has_qrcode_characteristics(raw_data):
                 detected_format = DetectedBarcodeFormat.GS1_QRCODE
            else: # Probablement linéaire
                 detected_format = DetectedBarcodeFormat.GS1_128
        else:
            detected_format = detect_generic_format(raw_data)


    # Informations de base
    info = {
        "decoder": decoder_used.value, # Utiliser .value pour obtenir la string de l'Enum
        "format": detected_format.value,
        "is_gs1": detected_format in [DetectedBarcodeFormat.GS1_128, DetectedBarcodeFormat.GS1_DATAMATRIX, DetectedBarcodeFormat.GS1_QRCODE]
    }

    if verbose:
        info["confidence"] = calculate_confidence(raw_data, decoder_used, detected_format)
        info["characteristics"] = get_barcode_characteristics(raw_data, detected_format)

    return info


# --- FIN DU FICHIER main.py ---