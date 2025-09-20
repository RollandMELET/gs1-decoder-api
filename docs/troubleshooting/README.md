# 🔧 Guide Dépannage par Format

## 🚨 Problèmes Critiques

### ❌ **GS1 DataMatrix Défaillant**

**Symptômes :**
- API retourne 500 Internal Server Error
- Taille fichier > 800 bytes ou < 500 bytes
- Tests critiques échouent : `make test-critical`

**Diagnostic :**
```bash
# Vérifier architecture hybride
make test-nodejs

# Vérifier API production
curl https://gs1-decoder-api.rorworld.eu/health

# Monitoring critique
make monitor
```

**Solutions :**
1. **Restauration immédiate** : `make restore-stable`
2. **Vérifier GTIN valide** : Checksum correct
3. **Redéploiement** : Si problème Docker
4. **Rollback** : `git checkout v1.4.0-tdd-complete`

---

## 🟡 **Formats Standard Défaillants**

### ❌ **QR Code Échoue**

**Symptômes :**
- 500 Internal Server Error pour `barcode_format: "qr_code"`
- Logs : "Erreur interne du serveur lors de la génération"

**Diagnostic :**
```bash
# Test local
source venv/bin/activate
python3 -c "
from app.barcode_generator import generate_qrcode
result = generate_qrcode('Test QR')
print(f'Local QR: {len(result)} bytes')
"

# Test préparation données
python3 -c "
from app.barcode_generator import prepare_gs1_content, BarcodeFormat
result = prepare_gs1_content('Test QR', BarcodeFormat.QRCODE)
print(f'Données QR: {result}')
"
```

**Solutions :**
1. **Vérifier dépendances** : `pip install qrcode pillow`
2. **Tester routing** : Données QR ne doivent pas aller vers GS1
3. **Vérifier treepoem** : `pip install treepoem && brew install ghostscript`

### ❌ **DataMatrix Standard Échoue**

**Diagnostic :**
```bash
# Test pylibdmtx
python3 -c "import pylibdmtx; print('✅ pylibdmtx OK')"

# Test libdmtx système
brew install libdmtx
```

**Solutions :**
1. **Fix dépendances système** : `libdmtx-dev` (Linux) ou `libdmtx` (macOS)
2. **Python 3.13 compatibility** : `pip install setuptools`
3. **Test isolation** : Vérifier routing vs GS1 DataMatrix

### ❌ **Code 128 Échoue**

**Diagnostic :**
```bash
# Test python-barcode
python3 -c "
from barcode import Code128
from barcode.writer import ImageWriter
result = Code128('TEST', writer=ImageWriter())
print('✅ Code128 OK')
"
```

**Solutions :**
1. **Réinstaller** : `pip install python-barcode[images]`
2. **Vérifier Pillow** : `pip install --upgrade Pillow`

---

## 🛠️ **Debugging Environnement**

### 🐛 **Environnement Local vs Production**

**Différences communes :**
| Aspect | Local | Production (Docker) |
|--------|--------|-------------------|
| **Python** | 3.13 | 3.10 |
| **Dépendances** | Système (brew) | apt packages |
| **Ghostscript** | `/opt/homebrew/bin/gs` | `/usr/bin/gs` |
| **libdmtx** | Homebrew path | `/usr/lib/` |

**Validation environnement :**
```bash
# Local
make debug-python
make debug-nodejs

# Production (via logs)
curl https://gs1-decoder-api.rorworld.eu/health | jq .capabilities
```

### 🔍 **Logs et Diagnostics**

**Activer logs debug :**
```python
# Dans app/barcode_generator.py - temporaire
print(f"[DEBUG] Format: {barcode_format}, Data: {data[:50]}")
print(f"[DEBUG] use_treepoem: {use_treepoem}, TREEPOEM_AVAILABLE: {TREEPOEM_AVAILABLE}")
```

**Analyser erreurs :**
```bash
# Logs production
make monitor-all > diagnosis.log 2>&1

# Logs détaillés
./scripts/monitor-endpoints.sh
cat endpoints-metrics.json | jq .
```

---

## 📋 **Checklist Dépannage**

### ✅ **Avant de Déboguer**
- [ ] `make test-critical` passe ✅
- [ ] `make info` montre environnement correct
- [ ] API health : `curl https://gs1-decoder-api.rorworld.eu/health`
- [ ] Tests locaux : Formats fonctionnent individuellement

### ✅ **Diagnostic Étape par Étape**
1. **Isoler le problème** : Quel format/endpoint exact ?
2. **Test local** : Même erreur en local ?
3. **Vérifier routing** : Données vont au bon générateur ?
4. **Dépendances** : Librairies installées correctement ?
5. **Environnement** : Docker vs local différences ?

### ✅ **Solutions par Priorité**
1. **GS1 DataMatrix** : 🔴 **Restauration immédiate** si cassé
2. **Formats standard** : 🟡 **Investigation** puis fix progressif
3. **Performance** : 🔵 **Optimisation** si dégradation

---

## 🆘 **Escalade Support**

### 🔴 **Critique (GS1 DataMatrix)**
- **Restauration** : `make restore-stable`
- **Rollback** : `git checkout v1.4.0-tdd-complete`
- **Monitoring** : `make monitor` toutes les 5 minutes

### 🟡 **Standard (Autres Formats)**
- **Investigation** : Logs + tests locaux
- **Fix progressif** : Tests avant commit
- **Non-bloquant** : Service reste utilisable

### 📞 **Contact Support**
- **Issues GitHub** : https://github.com/RollandMELET/gs1-decoder-api/issues
- **Documentation** : `docs/` complet
- **Points restauration** : Tags git disponibles

---

> 🛡️ **Rappel** : Suite TDD protège automatiquement contre les régressions. En cas de doute, `make test-critical` est votre ami !