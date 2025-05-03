# --- START OF FILE main.py (JPype Version) ---

from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends, Response
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager # Pour gérer le cycle de vie JPype/FastAPI
import jpype
import jpype.imports # Pour importer des packages Java comme s'ils étaient Python
from jpype.types import JString # Pour type hinting si nécessaire

from app.gs1_parser import parse_gs1 # Garder le parser original
from app.models import (
    DecodeResponse, ErrorResponse, HealthResponse,
    GenerateRequest, BarcodeFormat, ImageFormat,
    DecoderInfo, BarcodeItem
)
from app.barcode_detector import DecoderType, get_decoder_info
from app.barcode_generator import generate_barcode, BarcodeFormat as GenBarcodeFormat, ImageFormat as GenImageFormat
import shutil
from pylibdmtx.pylibdmtx import decode as dmtx_decode
from PIL import Image
import os
import io

# --- Variables Globales pour JPype et Classes Java ---
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

# --- Définir le Classpath ---
# Doit correspondre aux chemins dans le Dockerfile
ZXING_CLASSPATH = "/zxing/core.jar:/zxing/javase.jar"

# --- Gestion du cycle de vie FastAPI avec JPype ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global jpype_started, NotFoundException, IOException, ImageIO, File_java
    global BufferedImageLuminanceSource, HybridBinarizer, BinaryBitmap
    global MultiFormatReader, DecodeHintType, Hints_java

    print("Starting JPype JVM...")
    try:
        # Démarrer la JVM une seule fois au démarrage de l'application
        # convertStrings=False est CRUCIAL pour potentiellement préserver \x1d
        if not jpype.isJVMStarted():
             jpype.startJVM(
                 jpype.getDefaultJVMPath(),
                 "-ea", # Enable assertions (optionnel)
                 f"-Djava.class.path={ZXING_CLASSPATH}",
                 convertStrings=False # TRES IMPORTANT
             )
             jpype_started = True
             print("JPype JVM Started Successfully.")

             # Importer les classes Java nécessaires une fois
             print("Importing Java classes...")
             # Exceptions
             NotFoundException = jpype.JClass("com.google.zxing.NotFoundException")
             IOException = jpype.JClass("java.io.IOException")
             # Lecture Image
             ImageIO = jpype.JClass("javax.imageio.ImageIO")
             File_java = jpype.JClass("java.io.File")
             # Préparation ZXing
             BufferedImageLuminanceSource = jpype.JClass("com.google.zxing.client.j2se.BufferedImageLuminanceSource")
             HybridBinarizer = jpype.JClass("com.google.zxing.common.HybridBinarizer")
             BinaryBitmap = jpype.JClass("com.google.zxing.BinaryBitmap")
             # Lecteur
             MultiFormatReader = jpype.JClass("com.google.zxing.MultiFormatReader")
             # Hints (pour spécifier DATA_MATRIX et TRY_HARDER)
             DecodeHintType = jpype.JClass("com.google.zxing.DecodeHintType")
             Hints_java = jpype.JClass("java.util.Hashtable")
             print("Java classes imported.")

    except Exception as e:
        print(f"FATAL: Failed to start JPype JVM or import classes: {e}")
        jpype_started = False # Marquer comme échoué

    yield # L'application tourne ici

    # Code de nettoyage (pas de shutdown JVM dans les apps serveur généralement)
    print("FastAPI shutting down (JPype JVM remains running).")


# --- Initialiser l'application FastAPI avec le lifespan manager ---
app = FastAPI(
    title="GS1 Decoder API (JPype)",
    description="API pour décoder des codes-barres GS1 via JPype/ZXing",
    version="1.1.6-jpype",
    lifespan=lifespan # Gérer le démarrage/arrêt
)

@app.get("/health", response_model=HealthResponse)
async def health():
    # Health check basé sur si la JVM a démarré et les classes chargées
    zxing_ok = jpype_started and MultiFormatReader is not None
    capabilities = {
        "decoders": {
            "zxing": zxing_ok, # Basé sur l'état JPype
            "pylibdmtx": _check_pylibdmtx_available()
        },
        "supported_codes": ["DataMatrix", "QR Code", "GS1-128", "GS1 DataMatrix", "GS1 QR Code"],
        "api_version": app.version,
        "features": {"decode": True, "generate": False } # Désactiver generate pour simplifier
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
            logf = open(log_file, "w")
            logf.write(f"--- New Request (Test JPype/ZXing) ---\n")
            logf.write(f"[DEBUG] Saved upload to {temp_file_path}\n")
        except Exception as e:
            print(f"Warning: Impossible d'ouvrir le fichier de log {log_file}: {e}")
            logf = None

    decoded = []
    decoder_used = DecoderType.NONE
    zxing_error_msg = None

    # 1) ZXing attempt (via JPype)
    if jpype_started and MultiFormatReader: # Vérifier si JPype est prêt
        try:
            if logf: logf.write(f"[DEBUG] Attempting decode with JPype/ZXing...\n")

            # Créer un objet File Java
            j_file = File_java(JString(temp_file_path))
            if not j_file.exists():
                 raise FileNotFoundError(f"Java ne peut pas trouver le fichier: {temp_file_path}")

            # Lire l'image en Java BufferedImage
            buffered_image = ImageIO.read(j_file)
            if buffered_image is None:
                 raise ValueError(f"ImageIO n'a pas pu lire le fichier (format non supporté?): {temp_file_path}")

            # Préparer pour ZXing
            luminance_source = BufferedImageLuminanceSource(buffered_image)
            binarizer = HybridBinarizer(luminance_source)
            binary_bitmap = BinaryBitmap(binarizer)

            # Configurer les hints pour aider le décodage
            hints = Hints_java()
            # Spécifier le format DataMatrix
            possible_formats = jpype.java.util.Vector()
            possible_formats.add(jpype.JClass("com.google.zxing.BarcodeFormat").DATA_MATRIX)
            hints.put(DecodeHintType.POSSIBLE_FORMATS, possible_formats)
            # Essayer plus fort
            hints.put(DecodeHintType.TRY_HARDER, jpype.java.lang.Boolean.TRUE)

            # Créer le lecteur et décoder
            reader = MultiFormatReader()
            if logf: logf.write(f"[DEBUG] Calling reader.decode() with hints...\n")
            java_result = reader.decode(binary_bitmap, hints) # Appel Java

            if java_result:
                # Obtenir le texte brut (Java String)
                raw_java_string = java_result.getText()
                # Convertir en chaîne Python (JPype le fait souvent implicitement, mais soyons explicites)
                # Crucial de voir si cette conversion préserve \x1d avec convertStrings=False
                raw_python_string = str(raw_java_string)

                decoded = [raw_python_string]
                decoder_used = DecoderType.ZXING
                if logf: logf.write(f"[DEBUG] JPype/ZXing success. Raw data extracted: {decoded}\n")
            else:
                # Ne devrait pas arriver si decode lance NotFoundException
                if logf: logf.write(f"[DEBUG] JPype/ZXing decode returned None (inattendu).\n")
                zxing_error_msg = "decode returned None"

        # Gérer les exceptions Java spécifiques
        except jpype.JException(NotFoundException) as e:
            zxing_error_msg = "NotFoundException (pas de code trouvé)"
            if logf: logf.write(f"[DEBUG] JPype/ZXing: {zxing_error_msg} - {e}\n")
            decoded = []
        except jpype.JException(IOException) as e:
             zxing_error_msg = f"IOException lors de la lecture image: {e}"
             if logf: logf.write(f"[ERROR] JPype/ZXing: {zxing_error_msg}\n")
             decoded = []
        except Exception as e: # Attraper les autres erreurs (Python ou Java non gérées)
            zxing_error_msg = f"Erreur JPype/ZXing: {e}"
            if logf: logf.write(f"[ERROR] {zxing_error_msg}\n")
            # Imprimer la stack trace Java si c'est une exception Java
            if isinstance(e, jpype.JException):
                 print(f"Java Stack Trace:\n{e.stacktrace()}")
                 if logf: logf.write(f"Java Stack Trace:\n{e.stacktrace()}\n")
            decoded = []

    else:
        if logf: logf.write("[DEBUG] Skipping JPype/ZXing attempt: not available.\n")
        zxing_error_msg = "JPype/ZXing not available."

    # 2) Fallback to pylibdmtx if ZXing via JPype failed or found nothing
    if not decoded:
        if logf:
            logf.write(f"[DEBUG] JPype/ZXing found nothing or failed ({zxing_error_msg}). Trying pylibdmtx...\n")
        if _check_pylibdmtx_available():
            try:
                # Utiliser le chemin Python pour Pillow
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
                 # --- TOUJOURS logger repr() pour voir si on a \x1d ---
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
             detail_msg += f" (ZXing/JPype error: {zxing_error_msg})"
        elif decoder_used == DecoderType.NONE:
             detail_msg += " (pylibdmtx a aussi échoué ou n'a rien trouvé)."
        raise HTTPException(status_code=422, detail=detail_msg)

    barcodes_response = []
    for raw in decoded:
        try:
            # --- Utiliser le parser GS1 ORIGINAL ---
            parsed_data = parse_gs1(raw, verbose=verbose)
            decoder_name_for_info = "ZXing (JPype)" if decoder_used == DecoderType.ZXING else decoder_used.value
            decoder_info_dict = get_decoder_info(raw, decoder_used, verbose=verbose)
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
         raise HTTPException(status_code=500, detail="Erreur lors du traitement des données.")

    return DecodeResponse(success=True, barcodes=barcodes_response)

# --- Endpoint /generate/ (laissé tel quel mais commenté pour simplicité) ---
# @app.post("/generate/", ...)
# async def generate_barcode_image(request: GenerateRequest):
#     # ... (code inchangé mais non prioritaire) ...
#     pass

# --- Fonctions de vérification mises à jour ---
def _check_zxing_available():
    # Vérifie si JPype a démarré correctement et si Java est dans le path
    return jpype_started and MultiFormatReader is not None and shutil.which("java") is not None

def _check_pylibdmtx_available():
    try:
        from pylibdmtx.pylibdmtx import decode as dmtx_decode
        return True
    except ImportError: return False
    except Exception: return False

# --- FIN DU FICHIER main.py (JPype Version) ---