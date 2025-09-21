# Project Knowledge Graph - GS1 Decoder API

## Component Relationship Map

### Core Flow
```
User Request → FastAPI → Format Router → Generator → Response
    ↓
[Health/Generate/Decode/Parse] → [GS1/Standard Logic] → [Optimized Output]
```

### Critical Dependencies Chain
```
GS1 DataMatrix Success Requires:
main.py:240 → use_treepoem=False → generate_gs1_datamatrix_hybrid() →
bwip-js (Node.js) → 510-765 bytes → ]d2 identifier
```

## Component Graph

### API Layer
```
FastAPI App (app/main.py)
├── /health → HealthResponse (capabilities check)
├── /generate/ → GenerateRequest → BarcodeGenerator
├── /decode/ → UploadFile → BarcodeDetector → GS1Parser
└── /parse/ → ParseRequest → GS1Parser → StructuredResponse
```

### Generator Layer
```
BarcodeGenerator (app/barcode_generator.py)
├── GS1_DATAMATRIX → generate_gs1_datamatrix_hybrid()
│   ├── Priority 1: bwip-js (Node.js) → 500-800 bytes
│   ├── Priority 2: treepoem → standard size
│   ├── Priority 3: zint → fallback
│   └── Priority 4: dmtxwrite → last resort
├── GS1_QRCODE → prepare_gs1_content() → generate_qrcode()
├── GS1_128 → prepare_gs1_content() → generate_code128()
├── QRCODE → prepare_gs1_content(unchanged) → generate_qrcode()
├── DATAMATRIX → prepare_gs1_content(unchanged) → generate_datamatrix()
└── CODE128 → prepare_gs1_content(unchanged) → generate_code128()
```

### Data Processing Layer
```
prepare_gs1_content() - Data Router
├── BarcodeFormat.QRCODE → data (unchanged)
├── BarcodeFormat.DATAMATRIX → data (unchanged)
├── BarcodeFormat.CODE128 → data (unchanged)
├── BarcodeFormat.GS1_DATAMATRIX → data (raw for bwip-js)
├── BarcodeFormat.GS1_QRCODE → GS1 formatting
└── BarcodeFormat.GS1_128 → GS1 formatting + FNC1
```

### Protection Layer
```
TDD Protection System
├── Pre-commit Hooks → test_critical (4 blocking tests)
├── GitHub Actions → 7 jobs (critical → standard → performance)
├── Monitoring Scripts → 6 surveillance tools
└── Recovery Points → 3 stable tags
```

## Dependency Graph

### System Dependencies
```
Docker Container
├── python:3.10-slim
├── nodejs:18 → bwip-js → GS1 DataMatrix FNC1
├── ghostscript → treepoem → fallback generation
├── libdmtx-dev → pylibdmtx → DataMatrix support
├── default-jre → ZXing → decoding
└── setuptools>=60.0.0 → Python 3.13 compatibility
```

### Python Libraries
```
FastAPI Stack
├── fastapi + uvicorn → API framework
├── pydantic → request/response validation
├── python-multipart → file upload support
└── pillow → image processing

Barcode Libraries
├── JPype1 → Java ZXing interface
├── pylibdmtx → DataMatrix decode/generate
├── qrcode → QR Code generation
├── python-barcode → Code 128 generation
├── treepoem → universal fallback
└── zint-bindings → alternative generator
```

## Critical State Validation

### GS1 DataMatrix Health Check
```
✅ Health endpoint → bwipjs: true + nodejs: true
✅ Generate test → 500-800 bytes response
✅ Performance → <2s response time
✅ Identifier → ]d2 AIM code
```

### System State Indicators
```
Healthy System:
✓ make test-critical → All 4 tests pass
✓ make monitor → GS1 metrics within thresholds
✓ API health → bwipjs + nodejs available
✓ File sizes → 500-800 bytes range

Degraded System:
✗ test_critical fails → Immediate restore-stable
✗ GS1 size >800b → Architecture compromise
✗ bwipjs: false → Critical capability missing
```

## File Priority Map

### Must-Know Files (Priority 1)
1. `app/main.py:240` - use_treepoem routing logic
2. `app/barcode_generator.py:generate_gs1_datamatrix_hybrid()` - Critical optimization
3. `tests/unit/test_gs1_datamatrix_core.py` - Protection tests
4. `generate_gs1_bwip.js` - FNC1 solution

### Important Files (Priority 2)
5. `app/barcode_generator.py:prepare_gs1_content()` - Data isolation
6. `scripts/monitor-production.sh` - Production surveillance
7. `.github/workflows/gs1-tests.yml` - CI/CD protection
8. `Makefile` - Development commands

### Supporting Files (Priority 3)
9. `tests/formats/` - Extended format validation
10. `docs/` - Technical documentation
11. `scripts/monitor-*.sh` - Extended monitoring
12. Recovery points (`*_POINT*.md`)

## Quick Reference Tables

### Commands by Use Case
| Need | Command | Time | Critical |
|------|---------|------|----------|
| Validate setup | `make test-critical` | 30s | YES |
| Start development | `make dev` | 5s | No |
| Check production | `make monitor` | 10s | YES |
| Emergency restore | `make restore-stable` | 30s | YES |
| Full validation | `make test-all` | 5m | No |

### Error → Solution Map
| Error Pattern | Quick Fix |
|---------------|-----------|
| "Bad checksum" | Use `(01)03760423190005` |
| "Size >800 bytes" | Check `use_treepoem=False` |
| "]d1 identifier" | Verify bwip-js priority |
| "500 Internal Error" | Check data isolation |
| "Import failed" | Verify dependencies |

### Format Selection Guide
| Data Type | Recommended Format |
|-----------|-------------------|
| `(01)12345...` | `gs1_datamatrix` |
| `"Text content"` | `qr_code` |
| `"ALPHANUMERIC"` | `code_128` |
| `"DM content"` | `datamatrix` |

---

**Context-optimized documentation** - Essential information preserved, verbosity eliminated for LLM efficiency.