# 📦 GS1 Decoder API - LLM Optimized

> **Critical Success**: GS1 DataMatrix 96.8% size optimization (510-765 bytes vs 16k-23k) with comprehensive TDD protection.

## Quick Overview

**Service**: FastAPI barcode generation/decoding 6 formats
**API**: https://gs1-decoder-api.rorworld.eu/
**Critical Feature**: GS1 DataMatrix optimized with FNC1 compliance
**Protection**: 30-file TDD suite with auto-blocking regression tests

## Instant Setup
```bash
git clone https://github.com/RollandMELET/gs1-decoder-api
cd gs1-decoder-api
make setup && make test-critical  # Complete setup + validation
```

## Core API Usage

### Generate Barcodes
```bash
# Critical: GS1 DataMatrix (optimized)
curl -X POST "https://gs1-decoder-api.rorworld.eu/generate/" \
  -H "Content-Type: application/json" \
  -d '{"data": "(01)03760423190005", "barcode_format": "gs1_datamatrix"}'
# → 510 bytes PNG, ]d2 identifier

# Standard: QR Code
curl -X POST "https://gs1-decoder-api.rorworld.eu/generate/" \
  -H "Content-Type: application/json" \
  -d '{"data": "QR Content", "barcode_format": "qr_code"}'
```

### Decode Images
```bash
curl -X POST "https://gs1-decoder-api.rorworld.eu/decode/" \
  -F "file=@image.png" -F "verbose=false"
# → {"found": true, "data": "(01)...", "aim_identifier": "]d2"}
```

### Parse GS1 Data
```bash
curl -X POST "https://gs1-decoder-api.rorworld.eu/parse/" \
  -H "Content-Type: application/json" \
  -d '{"raw_data": "(01)03760423190005(17)250910", "verbose": true}'
# → [{"ai": "01", "name": "GTIN", "value": "03760423190005"}]
```

## Supported Formats Matrix

| Format | Input Example | Output Size | Performance |
|--------|---------------|-------------|-------------|
| `gs1_datamatrix` | `(01)03760423190005` | 500-800 bytes | <2s 🔴 |
| `gs1_qr_code` | `(01)03760423190005` | 1-20 KB | <5s |
| `gs1_128` | `(01)03760423190005` | 500-10 KB | <3s |
| `qr_code` | `"QR Content"` | 1-50 KB | <5s |
| `datamatrix` | `"DM Content"` | 2-30 KB | <5s |
| `code_128` | `"CODE128"` | 500-20 KB | <3s |

## Development Workflow

### Critical Workflow (Before Commits)
```bash
make test-critical  # 🔴 MUST PASS - Blocks dangerous commits
make lint          # Code quality
git commit         # Pre-commit hooks auto-run
```

### Development Loop
```bash
make dev           # Terminal 1: Development server
make test-fast     # Terminal 2: Quick validation during dev
```

### Extended Testing
```bash
make test-formats   # Format-specific validation
make test-endpoints # API endpoint testing
make test-all      # Complete suite before PR
```

## Production Monitoring

### Critical Surveillance
```bash
make monitor               # GS1 DataMatrix critical metrics
make monitor-all          # 6 formats + JSON metrics
make monitor-performance  # Benchmarks with thresholds
```

### Health Validation
```bash
curl https://gs1-decoder-api.rorworld.eu/health
# → {"status": "OK", "capabilities": {"generators": {"bwipjs": true}}}
```

## Error Resolution

### GS1 DataMatrix Critical Issues
```bash
# Symptom: Size >800 bytes or <500 bytes
make restore-stable  # Emergency rollback

# Symptom: ]d1 instead of ]d2 identifier
# Check: bwip-js priority in hybrid architecture

# Symptom: Bad checksum errors
# Fix: Use valid GTIN (01)03760423190005
```

### Standard Format Issues
```bash
# Symptom: 500 Internal Server Error
# Check: prepare_gs1_content() data isolation
# Verify: Docker dependencies (setuptools, ghostscript, libdmtx)
```

## Protection Systems

### Automated Protection
- **Pre-commit hooks**: Critical tests auto-run
- **GitHub Actions**: 7-job CI/CD validation
- **TDD blocking**: 4 tests prevent GS1 DataMatrix regression
- **Monitoring alerts**: Production surveillance with escalation

### Recovery Points
- `v1.9.0-tdd-complete-service` - Full service + TDD
- `v1.4.0-tdd-complete` - GS1 DataMatrix + TDD
- `v1.3.0-gs1-stable` - GS1 DataMatrix only

## Documentation Structure

### Technical References
- `llms.txt` - **This file** - LLM-optimized reference
- `docs/features/service-complet-tdd.md` - Complete architecture
- `docs/troubleshooting/README.md` - Format-specific debugging
- `docs/formats/README.md` - Format usage guides

### API Documentation
- **Interactive**: https://gs1-decoder-api.rorworld.eu/docs (Swagger)
- **Reference**: https://gs1-decoder-api.rorworld.eu/redoc (ReDoc)

---

## Context-Efficient Summary

**Project**: Production-ready barcode API with critical GS1 DataMatrix optimization
**Key Achievement**: 96.8% size reduction + TDD protection + monitoring
**Commands**: `make test-critical` (blocking) + `make monitor` (surveillance)
**Recovery**: `make restore-stable` (emergency)
**Status**: Industrial-grade service with anti-regression protection

*Optimized for LLM context efficiency - 60% token reduction vs original*