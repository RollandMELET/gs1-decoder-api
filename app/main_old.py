from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends, Response
from fastapi.responses import StreamingResponse
from app.gs1_parser import parse_gs1
from app.models import (
    DecodeResponse, ErrorResponse, HealthResponse, 
    GenerateRequest, GenerateResponse, BarcodeFormat, ImageFormat
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
    version="1.1.0"
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
        "api_version": "1.1.0",
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

@app.post(
    "/generate/",
    responses={
        200: {"content": {"image/png": {}, "image/jpeg": {}, "image/svg+xml": {}}},
        422: {"model": ErrorResponse}
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
        # Mapper les formats d'entrée aux formats internes
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
        
        # Générer le code-barres
        barcode_image = generate_barcode(
            data=request.data,
            barcode_format=barcode_format_map[request.format],
            image_format=image_format_map[request.image_format],
            width=request.width,
            height=request.height
        )
        
        # Déterminer le type MIME
        mime_types = {
            ImageFormat.PNG: "image/png",
            ImageFormat.JPEG: "image/jpeg",
            ImageFormat.SVG: "image/svg+xml",
        }
        media_type = mime_types[request.image_format]
        
        # Retourner l'image
        return StreamingResponse(
            io.BytesIO(barcode_image),
            media_type=media_type,
            headers={
                "Content-Disposition": f"inline; filename=barcode.{request.image_format.value}"
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ImportError as e:
        raise HTTPException(status_code=501, detail=f"Fonctionnalité non disponible: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération: {str(e)}")

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
