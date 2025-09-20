# 📋 Guide Formats Supportés

## 🎯 Vue d'Ensemble Formats

L'API supporte **6 formats de codes-barres** avec optimisations spécifiques et différenciation GS1 vs Standard.

### 📊 Matrice Support Formats

| Format | Type | Taille Typique | Performance | Générateur Principal |
|--------|------|---------------|-------------|---------------------|
| **GS1 DataMatrix** | 🔴 GS1 | 500-800 bytes | < 2s | bwip-js (hybride) |
| **GS1 QR Code** | 🟡 GS1 | 1-20 KB | < 5s | qrcode + GS1 |
| **GS1-128** | 🟡 GS1 | 500-10 KB | < 3s | python-barcode + GS1 |
| **QR Code** | 🔵 Standard | 1-50 KB | < 5s | qrcode / treepoem |
| **DataMatrix** | 🔵 Standard | 2-30 KB | < 5s | pylibdmtx / treepoem |
| **Code 128** | 🔵 Standard | 500-20 KB | < 3s | python-barcode / treepoem |

## 🔴 **GS1 DataMatrix - Critique**

### Caractéristiques
- **Optimisation** : 96.8% réduction taille (500-800 bytes vs 16-23 KB)
- **Architecture** : Hybride bwip-js → fallbacks (treepoem → zint → dmtxwrite)
- **Conformité** : FNC1 position 1, identifier AIM ]d2
- **Performance** : < 2s génération (critique)

### Exemples
```bash
# Simple
curl -X POST "https://gs1-decoder-api.rorworld.eu/generate/" \
  -H "Content-Type: application/json" \
  -d '{"data": "(01)03760423190005", "barcode_format": "gs1_datamatrix"}'

# Expert
curl -X POST "https://gs1-decoder-api.rorworld.eu/generate/" \
  -H "Content-Type: application/json" \
  -d '{"data": "(01)03760423190005(11)250910(3100)012000(21)0000019C", "barcode_format": "gs1_datamatrix"}'
```

### Protection TDD
- **Tests critiques** : 4 tests bloquants obligatoires
- **Monitoring** : Surveillance temps réel optimisation
- **Point restauration** : `v1.4.0-tdd-complete`

## 🟡 **Formats GS1 Autres**

### GS1 QR Code
```bash
curl -X POST "https://gs1-decoder-api.rorworld.eu/generate/" \
  -H "Content-Type: application/json" \
  -d '{"data": "(01)03760423190005", "barcode_format": "gs1_qr_code"}'
```

### GS1-128
```bash
curl -X POST "https://gs1-decoder-api.rorworld.eu/generate/" \
  -H "Content-Type: application/json" \
  -d '{"data": "(01)03760423190005", "barcode_format": "gs1_128"}'
```

## 🔵 **Formats Standard**

### QR Code Standard
```bash
curl -X POST "https://gs1-decoder-api.rorworld.eu/generate/" \
  -H "Content-Type: application/json" \
  -d '{"data": "https://example.com/qr-test", "barcode_format": "qr_code"}'
```

### DataMatrix Standard
```bash
curl -X POST "https://gs1-decoder-api.rorworld.eu/generate/" \
  -H "Content-Type: application/json" \
  -d '{"data": "Standard DataMatrix Content", "barcode_format": "datamatrix"}'
```

### Code 128 Standard
```bash
curl -X POST "https://gs1-decoder-api.rorworld.eu/generate/" \
  -H "Content-Type: application/json" \
  -d '{"data": "CODE128CONTENT", "barcode_format": "code_128"}'
```

## 🔧 **Différenciation GS1 vs Standard**

### Traitement des Données

| Type | Format Données | Traitement | Résultat |
|------|---------------|------------|----------|
| **GS1** | `(01)12345678901234` | Formatage AI + FNC1 | Conforme standards |
| **Standard** | `"Text content"` | Aucune transformation | Données inchangées |

### Architecture Génération

```
GS1 DataMatrix:    use_treepoem=False → Architecture hybride bwip-js
Autres GS1:        use_treepoem=True  → treepoem avec options GS1
Formats Standard:  use_treepoem=True  → treepoem ou générateurs spécifiques
```

## 📊 **Monitoring et Debugging**

### Commandes Monitoring
```bash
# Monitoring tous formats
make monitor-all

# Performance benchmarks
make monitor-performance

# Tests concurrent
make monitor-performance-concurrent

# Monitoring endpoints
make monitor-endpoints
```

### Diagnostic Problèmes
```bash
# Vérifier capacités
curl https://gs1-decoder-api.rorworld.eu/health

# Debug format spécifique
make test-nodejs  # Test GS1 DataMatrix local

# Tests critiques
make test-critical

# Restauration d'urgence
make restore-stable
```

## 🎯 **Best Practices par Format**

### GS1 DataMatrix
- ✅ **Utiliser données avec parenthèses** : `(01)12345678901234`
- ✅ **GTIN valides** : Checksum correct obligatoire
- ✅ **Monitoring critique** : Alertes si dégradation
- ❌ **Pas de redimensionnement** : Tailles natives préservées

### QR Code Standard
- ✅ **Tout type de données** : Text, URLs, données binaires
- ✅ **Redimensionnement OK** : Dimensions ajustables
- ✅ **Performance < 5s** : Acceptable pour UX

### DataMatrix Standard
- ✅ **Données alphanumériques** : Optimisé pour densité
- ✅ **Différenciation vs GS1** : Pas de formatage AI
- ✅ **Fallbacks multiples** : pylibdmtx, treepoem

### Code 128
- ✅ **Données ASCII** : Caractères standard supportés
- ✅ **Largeur optimisée** : Format horizontal
- ✅ **Performance rapide** : < 3s génération

## 🚨 **Troubleshooting**

### Problèmes Courants

**❌ "Erreur interne du serveur"**
- **Cause** : Format/données incompatibles
- **Solution** : Vérifier format + données appropriées

**❌ "Bad checksum" (GS1)**
- **Cause** : GTIN invalide
- **Solution** : Utiliser GTIN avec checksum correct

**❌ "AIs must start with '('"**
- **Cause** : Données non-GS1 avec format GS1
- **Solution** : Utiliser format standard approprié

### Monitoring Dégradation
```bash
# Si GS1 DataMatrix < 500 bytes ou > 800 bytes
make restore-stable

# Si performance > seuils
make monitor-performance

# Si formats standard échouent
./scripts/monitor-all-formats.sh
```

## 🔄 **Migration Guide**

### Depuis Version Antérieure
1. **Backup** : `git tag backup-$(date +%Y%m%d)`
2. **Pull** : `git pull origin main`
3. **Setup** : `make setup`
4. **Validation** : `make test-critical`
5. **Test formats** : `make monitor-all`

### Nouveaux Utilisateurs
1. **Clone** : `git clone https://github.com/RollandMELET/gs1-decoder-api`
2. **Setup** : `make setup`
3. **Validation** : `make test-critical`
4. **Test API** : `make monitor`

---

> 💡 **Note importante** : GS1 DataMatrix est le format critique avec optimisation 96.8%. Les autres formats sont supportés mais secondaires.