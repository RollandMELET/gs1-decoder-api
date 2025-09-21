# 📈 CHANGELOG - GS1 Decoder API

## 🎯 v2.1.0 - QUIET ZONE CONTROL (2025-01-21)

### ✨ NOUVELLES FONCTIONNALITÉS

#### 🎚️ **Contrôle Quiet Zone GS1 DataMatrix**
- **Paramètre `quiet_zone_modules`** : 0.0-10.0 (défaut: 1.0 = standard GS1)
- **Paramètre `no_quiet_zone`** : true/false pour design custom
- **Mode `client_mode`** : "optimized" (taille native) vs "compatible" (redimensionné)
- **Standards conformes** : ISO/IEC 16022 + GS1 General Specifications

#### 📊 **Résultats Variables selon Configuration**
| Configuration | Taille | Dimensions | Usage |
|---------------|--------|------------|-------|
| `no_quiet_zone: true` | 491 bytes | 80×80 px | Client gère design |
| `quiet_zone_modules: 1.0` | 526 bytes | 98×98 px | Standard GS1 |
| `quiet_zone_modules: 2.0` | 536 bytes | 116×116 px | Lisibilité accrue |

### 🔧 AMÉLIORATIONS TECHNIQUES

#### 🐍 **API Python (FastAPI)**
- Nouveaux paramètres dans `GenerateRequest` (app/models.py)
- Logique `client_mode="optimized"` préserve tailles natives
- Propagation paramètres API → bwip-js corrigée

#### 🟢 **Architecture Hybride Node.js**
- Script `generate_gs1_bwip.js` avec calcul proportionnel
- Formule : `quietZonePixels = Math.round(quietZoneModules * moduleSize)`
- Support padding asymétrique bwip-js

#### 🔄 **Propagation Paramètres**
```python
# Correction critique app/barcode_generator.py
cmd = [
    'node', '/app/generate_gs1_bwip.js',
    data, tmp.name,
    str(quiet_zone_modules)  # ← Paramètre propagé
]
```

### 🐛 CORRECTIONS CRITIQUES

#### 🚨 **Format API Critique**
- **Problème** : `"format": "datamatrix"` → Force redimensionnement 37KB
- **Solution** : `"format": "gs1-datamatrix"` → Taille optimisée 491-536 bytes
- **Impact** : Résolution problème client GAS-GenerateurEtiquette

#### ⚙️ **Mode Client Optimized**
- **Problème** : Redimensionnement forcé même en mode optimized
- **Solution** : Dimensions placeholder ignorées si `client_mode="optimized"`
- **Code** : `app/main.py` lignes 514-518

### 📚 DOCUMENTATION COMPLÈTE

#### 📖 **Nouvelles Documentations**
- `PROMPT_AGENT_GAS_GENERATEUR_ETIQUETTE.md` - Guide intégration AppScript
- `GS1_QUIET_ZONE_TECHNICAL_SPECS.md` - Spécifications techniques complètes
- README.md section "Contrôle Avancé Quiet Zone"
- CLAUDE.md mis à jour avec paramètres quiet zone

#### 🧠 **LLM-Optimized Updates**
- `llms.txt` section "Quiet Zone Control (NEW)"
- Patterns d'erreur quiet zone ajoutés
- Exemples de configuration par cas d'usage

### 🧪 VALIDATION & TESTS

#### ✅ **Tests Production Validés**
```bash
# Tests API format correct
curl -X POST "https://gs1-decoder-api.rorworld.eu/generate/" \
  -d '{"format":"gs1-datamatrix","quiet_zone_modules":1.0,"client_mode":"optimized"}'
# → 526 bytes, 98×98 pixels (SUCCÈS)
```

#### 🔍 **Cas de Test Critiques**
- Format `gs1-datamatrix` vs `datamatrix` validation
- Propagation paramètres API → bwip-js
- Mode `client_mode="optimized"` préservation taille native
- Standards GS1 conformité (1.0 module = standard)

### 🎯 CAS D'USAGE MÉTIER

#### 🏭 **Production Standard**
```json
{"quiet_zone_modules": 1.0, "client_mode": "optimized"}
```

#### 🎨 **Intégration Design Custom**
```json
{"no_quiet_zone": true, "client_mode": "optimized"}
```

#### 📱 **Haute Lisibilité Mobile**
```json
{"quiet_zone_modules": 2.0, "client_mode": "optimized"}
```

### 🔗 **COMPATIBILITÉ**

#### ✅ **Rétrocompatibilité**
- Paramètres quiet zone optionnels (défauts GS1 standard)
- Architecture hybride existante préservée
- APIs existantes inchangées

#### ⚠️ **Breaking Changes**
- Aucun (tous paramètres optionnels)

### 📋 **MIGRATION GUIDE**

#### 🔄 **Pour Clients Existants**
1. **Aucune action requise** - comportement par défaut conforme GS1
2. **Optimisation recommandée** - ajouter `"client_mode": "optimized"`
3. **Contrôle avancé** - utiliser `quiet_zone_modules` selon besoins

#### 🚨 **Format Critique**
- Utiliser `"format": "gs1-datamatrix"` (PAS `"datamatrix"`)
- Mode `"client_mode": "optimized"` pour tailles natives

---

## 📈 HISTORIQUE VERSIONS

### v2.0.x - Service Complet TDD
- Suite TDD exhaustive 6 formats
- Monitoring production granulaire
- Architecture hybride Python ↔ Node.js

### v1.9.0 - Service Industriel
- GS1 DataMatrix optimisation 96.8%
- 6 formats supportés
- Production-ready Docker

### v1.4.0 - TDD Complete
- Point de restauration stable
- GS1 DataMatrix core fonctionnel

---

**🏆 STATUT ACTUEL : PRODUCTION-READY**
*Architecture hybride avec contrôle quiet zone conforme standards internationaux*