# CLAUDE.md - LLM Optimized

## Project Context
GS1 Decoder API: FastAPI service with 6 barcode formats. **CRITICAL**: GS1 DataMatrix 96.8% optimized (510-765 bytes vs 16k-23k) using bwip-js hybrid architecture.

## Commands Hierarchy

### Priority 1: Critical Operations
```bash
make test-critical    # 🔴 BLOCKING: Must pass before commit
make monitor         # 🔴 CRITICAL: GS1 DataMatrix surveillance
make setup          # 🚀 Complete setup (deps + TDD + hooks)
make restore-stable # 🔄 EMERGENCY: Rollback to stable
```

### Priority 2: Development Workflow
```bash
make dev            # Development server with reload
make test-fast      # Quick validation during development
make test-all       # Full test suite before PR
make lint          # Code quality validation
```

### Priority 3: Extended Operations
```bash
# Format-specific testing
make test-formats      # QR/Code128/DataMatrix/GS1 validation
make test-endpoints    # /generate/decode/parse/health testing

# Production monitoring
make monitor-all       # 6 formats + JSON metrics
make monitor-endpoints # 4 endpoints with details
make monitor-performance # Benchmarks with thresholds
```

## Architecture Map

### Critical Path (GS1 DataMatrix)
```
Request → main.py:240 → use_treepoem=False →
barcode_generator.py:generate_gs1_datamatrix_hybrid() →
bwip-js → treepoem → zint → dmtxwrite → 510-765 bytes
```

### Standard Formats Path
```
Request → main.py → use_treepoem=True →
prepare_gs1_content(unchanged) → treepoem/specific generators
```

## File Locations

### Core Components
- `app/main.py:240` - Routing logic + use_treepoem forcing
- `app/barcode_generator.py:520-580` - GS1 hybrid architecture
- `generate_gs1_bwip.js` - Node.js FNC1 solution
- `app/barcode_generator.py:prepare_gs1_content()` - Data isolation

### Test Protection
- `tests/unit/test_gs1_datamatrix_core.py` - 4 blocking tests
- `tests/formats/` - Extended format validation
- `tests/endpoints/` - API endpoint validation
- `.github/workflows/gs1-tests.yml` - CI/CD 7 jobs

### Monitoring
- `scripts/monitor-production.sh` - Critical GS1 DataMatrix
- `scripts/monitor-all-formats.sh` - 6 formats JSON metrics
- `scripts/performance-benchmark.sh` - Performance thresholds

## Testing Strategy

### Blocking Tests (MUST PASS)
1. `test_use_treepoem_false_for_gs1_datamatrix` - Architecture isolation
2. `test_bwipjs_priority_in_hybrid_architecture` - Fallback priority
3. `test_gs1_aim_identifier_validation` - ]d2 conformity
4. `test_file_size_optimization_simple` - 96.8% optimization

### Extended Coverage
- **Unit**: Core component isolation
- **Integration**: Python↔Node.js hybrid
- **Conformity**: GS1 standards ISO/IEC 16022
- **Performance**: Size optimization validation
- **Formats**: 6 format individual validation
- **Endpoints**: 4 API endpoint comprehensive

## Dependencies

### Docker Production
```
python:3.10-slim + nodejs:18 + ghostscript + libdmtx-dev + java21
setuptools>=60.0.0 (Python 3.13 compatibility)
```

### Critical Libraries
```
JPype1          # Python↔Java ZXing interface
bwip-js         # GS1 DataMatrix FNC1 solution (Node.js)
pylibdmtx       # DataMatrix fallback
treepoem        # Universal fallback generator
```

## Error Resolution

### GS1 DataMatrix Critical Errors
- **Bad checksum**: Use valid GTIN `(01)03760423190005`
- **Size >800 bytes**: Verify `use_treepoem=False` forced
- **]d1 identifier**: Check bwip-js priority in hybrid

### Standard Format Errors
- **500 Internal Error**: Check `prepare_gs1_content()` isolation
- **Import failures**: Verify `setuptools + system dependencies`

## Recovery Points
- `v1.9.0-tdd-complete-service` - Full service + TDD
- `v1.4.0-tdd-complete` - GS1 DataMatrix + TDD
- `v1.3.0-gs1-stable` - GS1 DataMatrix only

## Performance Targets
- **GS1 DataMatrix**: <2s, 500-800 bytes, ]d2 (**CRITICAL**)
- **Standard formats**: <5s response
- **Endpoints**: /health <1s, /generate <5s, /decode <10s

---
*Token-optimized for LLM context efficiency - Generated 2025*