from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from app.gs1_parser import parse_gs1
from app.models import DecodeResponse, ErrorResponse
import shutil
import subprocess
from pylibdmtx.pylibdmtx import decode as dmtx_decode
from PIL import Image

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "OK"}

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
        "java", "-cp", "/zxing/javase/javase.jar",
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
        barcodes.append({"raw": raw, "parsed": parsed})

    return {"success": True, "barcodes": barcodes}
