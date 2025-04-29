from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from app.gs1_parser import parse_gs1
from app.models import DecodeResponse, ErrorResponse
import shutil
import subprocess

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "OK"}

@app.post("/decode/", response_model=DecodeResponse, responses={422: {"model": ErrorResponse}})
async def decode_image(file: UploadFile = File(...), verbose: bool = Form(False)):
    temp_file = f"/tmp/{file.filename}"
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = subprocess.run(
        ["java", "-cp", "/zxing/javase/javase.jar", "com.google.zxing.client.j2se.CommandLineRunner", temp_file],
        capture_output=True, text=True
    )

    decoded_outputs = result.stdout.strip().splitlines()

    if not decoded_outputs or all(not line.strip() for line in decoded_outputs):
        raise HTTPException(status_code=422, detail="Aucun code-barres détecté dans l'image.")

    barcodes = []
    for decoded_text in decoded_outputs:
        parsed = parse_gs1(decoded_text, verbose)
        barcodes.append({"raw": decoded_text, "parsed": parsed})

    return {"success": True, "barcodes": barcodes}
