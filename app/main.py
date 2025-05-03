from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from app.gs1_parser_old import parse_gs1
from app.models import DecodeResponse, ErrorResponse, HealthResponse
from app.barcode_detector_old import DecoderType, get_decoder_info
import shutil
import subprocess
from pylibdmtx.pylibdmtx import decode as dmtx_decode
from PIL import Image
import os

app = FastAPI()

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
        "supported_codes": ["DataMatrix", "QR Code", "GS1-128"],
        "api_version": "1.0.0"
    }
    return {"status": "OK", "capabilities": capabilities}

@app.post(
    "/decode/",
    response_model=DecodeResponse,
    responses={422: {"model": ErrorResponse}}
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
    temp_file = f"/tmp/{file.filename}"
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Setup debug logging if requested
    logf = None
    if debug and log_file:
        try:
            logf = open(log_file, "w")
            logf.write(f"[DEBUG] Saved upload to {temp_file}\n")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Impossible d'ouvrir le fichier de log: {e}")

    # 1) ZXing attempt
    cmd = [
        "java", "-cp", "/zxing/javase.jar",
        "com.google.zxing.client.j2se.CommandLineRunner", temp_file
    ]
    if logf:
        logf.write(f"[DEBUG] Running ZXing command: {' '.join(cmd)}\n")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    decoded = [line for line in result.stdout.strip().splitlines() if line.strip()]
    decoder_used = DecoderType.ZXING if decoded else DecoderType.NONE

    if logf:
        logf.write(f"[DEBUG] ZXing stdout: {result.stdout}\n")
        logf.write(f"[DEBUG] ZXing stderr: {result.stderr}\n")

    # 2) Fallback to pylibdmtx if ZXing failed
    if not decoded:
        if logf:
            logf.write("[DEBUG] ZXing found nothing, trying pylibdmtx...\n")
        try:
            img = Image.open(temp_file)
            dmtx_results = dmtx_decode(img)
            decoded = [res.data.decode("utf-8") for res in dmtx_results]
            decoder_used = DecoderType.PYLIBDMTX if decoded else DecoderType.NONE
            if logf:
                logf.write(f"[DEBUG] pylibdmtx found {len(decoded)} codes\n")
        except Exception as e:
            if logf:
                logf.write(f"[DEBUG] pylibdmtx error: {e}\n")
            decoded = []

    # Finalize logs
    if logf:
        logf.write(f"[DEBUG] Final decoded codes: {decoded}\n")
        logf.close()

    if not decoded:
        raise HTTPException(
            status_code=422,
            detail="Aucun code-barres détecté dans l'image (ZXing & pylibdmtx)."
        )

    # Parse GS1
    barcodes = []
    for raw in decoded:
        parsed = parse_gs1(raw, verbose)
        
        # Obtenir les informations de détection du format
        decoder_info = get_decoder_info(raw, decoder_used, verbose)
        
        barcode_data = {
            "raw": raw, 
            "parsed": parsed,
            "decoder_info": decoder_info if verbose else {"decoder": decoder_info["decoder"], "format": decoder_info["format"]}
        }
        barcodes.append(barcode_data)

    return {"success": True, "barcodes": barcodes}

def _check_zxing_available():
    """
    Vérifie si la bibliothèque ZXing est disponible.
    
    Returns:
        bool: True si ZXing est disponible
    """
    try:
        # Vérifier si le JAR ZXing existe
        return os.path.exists("/zxing/javase.jar")
    except:
        return False

def _check_pylibdmtx_available():
    """
    Vérifie si la bibliothèque pylibdmtx est disponible.
    
    Returns:
        bool: True si pylibdmtx est disponible
    """
    try:
        # Import simple pour vérifier si pylibdmtx fonctionne
        from pylibdmtx.pylibdmtx import decode as dmtx_decode
        return True
    except:
        return False
