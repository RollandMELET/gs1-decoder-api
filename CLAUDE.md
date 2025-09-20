# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Setup
```bash
# Initial setup (installs dependencies, creates venv)
./setup_dev.sh

# Activate virtual environment
source venv/bin/activate  # Unix/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies manually if needed
pip install -r requirements.txt
```

### Running the Application
```bash
# Development server (with hot reload)
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Run API tests against local server
python test_api.py

# Test specific components
python test_barcode_detection.py <image_path>
python test_gs1_parser.py
python test_generate.py

# Test against production API
./test-gs1.sh

# Production API URL
# https://gs1-decoder-api.rorworld.eu/
```

### Docker
```bash
# Build image
docker build -t gs1-decoder-api .

# Run container
docker run -d -p 8000:8000 gs1-decoder-api

# Docker Compose
docker-compose up -d
```

## Architecture

### Core Components

**FastAPI Application** (`app/main.py`)
- Main application with 3 primary endpoints: `/health`, `/decode/`, `/parse/`, `/generate/`
- Uses JPype to interface with ZXing Java library for barcode decoding
- Startup/shutdown lifecycle management for JVM initialization
- Fallback to pylibdmtx for DataMatrix codes when ZXing fails

**Barcode Detection** (`app/barcode_detector.py`)
- Multi-decoder architecture: ZXing (JPype) → pylibdmtx fallback
- GS1 data format detection and classification
- Confidence scoring and barcode characteristic analysis
- Support for DataMatrix, QR Code, Code 128, and GS1 variants

**GS1 Parser** (`app/gs1_parser.py`)
- Application Identifier (AI) parsing using comprehensive JSON lookup table
- Handles both verbose (detailed AI breakdown) and simple (key-value) formats
- FNC1 character normalization and data validation
- Date/time formatting for temporal AI values

**Barcode Generator** (`app/barcode_generator.py`)
- Generates DataMatrix, QR Code, and Code 128 formats
- GS1-compliant encoding with proper FNC1 insertion
- Multiple output formats: PNG, JPEG, SVG
- Uses pylibdmtx, qrcode, and python-barcode libraries

**Data Models** (`app/models.py`)
- Pydantic models for request/response validation
- Supports both simplified and verbose parsing modes
- Comprehensive error handling models

### Key Dependencies

**Java Integration**
- Requires Java runtime for ZXing functionality
- ZXing JAR files: `/zxing/core.jar`, `/zxing/javase.jar`
- JPype1 for Python-Java bridge

**Native Libraries**
- libdmtx for DataMatrix decoding (system dependency)
- Pillow for image processing

**GS1 Data**
- Comprehensive AI definitions in `resources/gs1_application_identifiers.json`
- Supports 100+ GS1 Application Identifiers

### Data Flow

1. **Image Upload** → Temporary file storage
2. **ZXing Decode** → Java-based barcode detection (primary)
3. **pylibdmtx Fallback** → Native DataMatrix decoder (if ZXing fails)
4. **GS1 Parsing** → AI extraction and validation
5. **Response Assembly** → Structured JSON with metadata

### Environment Configuration

- Docker-ready with multi-stage build
- Handles both development (venv) and containerized deployments
- Environment variables: Java classpath, temporary directories
- Health check endpoint for monitoring
- **Production API:** https://gs1-decoder-api.rorworld.eu/

### Testing Strategy

- Unit tests for individual components (`test_*.py`)
- Integration tests against running API (`test_api.py`)
- Production smoke tests (`test-gs1.sh`)
- Manual testing with sample images in root directory