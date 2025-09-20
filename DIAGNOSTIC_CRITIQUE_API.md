# 🚨 DIAGNOSTIC CRITIQUE - Problème API GS1 DataMatrix

**Date :** 20 septembre 2025
**Statut :** CRITIQUE - Solution technique validée mais API non fonctionnelle
**Objectif :** Identifier pourquoi l'API Docker ne génère pas de vrais GS1 DataMatrix

---

## 📊 **SITUATION ACTUELLE**

### ✅ **SOLUTION LOCALE VALIDÉE**
| Méthode | Taille | Format Détecté | Status GS1 | Identifiant AIM |
|---------|--------|----------------|------------|-----------------|
| **Script Node.js local** | 563-696 bytes | "GS1 DataMatrix" | `is_gs1: true` | ]d2 ✅ |

**Configuration fonctionnelle :**
```javascript
// generate_gs1_bwip.js - FONCTIONNE
const options = {
    bcid: 'gs1datamatrix',
    text: data,              // Données brutes (01)123...
    scale: 3,
    height: 10, width: 10,
    paddingleft: 10, paddingright: 10,
    paddingtop: 10, paddingbottom: 10,
    includetext: true,
    textxalign: 'center',
    textcolor: '000000',
    textgaps: 2
};
```

### ❌ **PROBLÈME API DOCKER**
| Méthode | Taille | Format Détecté | Status GS1 | Identifiant AIM |
|---------|--------|----------------|------------|-----------------|
| **API Docker** | 34k-52k bytes | Non décodable | N/A | ❌ Échec |

---

## 🔍 **DIVERGENCE CRITIQUE IDENTIFIÉE**

### **ENVIRONNEMENT LOCAL vs DOCKER**

**Local (Fonctionne) :**
- Node.js 18.20.8
- bwip-js 4.7.0
- Script direct `generate_gs1_bwip.js`
- Configuration simple du projet de référence

**Docker (Échoue) :**
- Node.js 18.20.8 ✅ (identique)
- bwip-js 4.7.0 ✅ (identique)
- Script appelé via Python subprocess
- Architecture hybride avec fallbacks

---

## 🧩 **HYPOTHÈSES DIAGNOSTIQUES**

### **1. PROBLÈME DE DÉTECTION BWIPJS_AVAILABLE**
```python
# app/barcode_generator.py:39-43
BWIPJS_AVAILABLE = (
    shutil.which('node') is not None and
    os.path.exists('/app/generate_gs1_bwip.js') and
    os.path.exists('/app/node_modules/bwip-js')
)
```
**Problème possible :** Une de ces conditions échoue dans Docker

### **2. BYPASS DE L'ARCHITECTURE HYBRIDE**
L'API pourrait utiliser :
- Ancien code treepoem forcé
- Fallback direct sur pylibdmtx
- Cache application persistant
- Variable use_treepoem=True par défaut

### **3. ERREUR SUBPROCESS SILENCIEUSE**
```python
# app/barcode_generator.py:362-386
result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd='/app')
if result.returncode != 0:
    raise Exception(f"bwip-js échec: {result.stderr}")
```
**Problème possible :** Le subprocess échoue mais l'erreur est catchée et fallback activé

---

## 📈 **TIMELINE DES CORRECTIONS**

| Commit | Description | Résultat API |
|--------|-------------|--------------|
| `59a2c43` | Configuration simple script Node.js | 34k-52k ❌ |
| `037ecb3` | Synchronisation prepare_gs1_content() | 34k-52k ❌ |
| `a59ad76` | Force architecture hybride dans generate_barcode() | 34k-52k ❌ |

**Conclusion :** 3 corrections, 3 redéploiements, **AUCUN changement dans l'API**

---

## 🔧 **CORRECTIONS APPLIQUÉES SANS EFFET**

### **1. Script Node.js simplifié** ✅
- Suppression des 4 tentatives complexes
- Configuration identique au projet de référence
- Test local : SUCCÈS complet

### **2. Architecture Python corrigée** ✅
- prepare_gs1_content() passe données brutes
- generate_gs1_datamatrix_bwipjs() amélioré
- generate_barcode() utilise architecture hybride

### **3. Déploiements Docker confirmés** ✅
- Build sans erreur, commit correct détecté
- Container redémarré, Node.js 18.20.8 installé
- Health check : bwipjs=true, nodejs=true

---

## 🎯 **PROBLÈME CENTRAL**

**L'API Docker génère EXACTEMENT les mêmes fichiers** malgré :
- 3 corrections majeures
- 3 redéploiements complets
- 3 commits différents déployés

**Ceci indique :**
- Code non pris en compte dans Docker
- Cache persistant ou configuration figée
- Utilisation d'un autre chemin d'exécution
- Problème de variables d'environnement

---

## 🔬 **VALIDATION TECHNIQUE**

### **PREUVE QUE LA SOLUTION FONCTIONNE**
```bash
# LOCAL - SUCCÈS ✅
$ node generate_gs1_bwip.js "(01)03760423190005(11)250326" "test.png"
→ 563 bytes, décodable "GS1 DataMatrix", is_gs1: true

# API - ÉCHEC ❌
$ curl API → 34k bytes, non décodable
```

**CONCLUSION :** Le problème n'est PAS technique mais d'intégration Docker/Python.

---

## 🚀 **PROCHAINES INVESTIGATIONS REQUISES**

1. **Debug variables d'environnement** dans Docker
2. **Trace l'exécution** generate_barcode() → architecture hybride
3. **Vérifier chemins fichiers** /app/generate_gs1_bwip.js dans Docker
4. **Identifier fallback utilisé** (treepoem vs pylibdmtx vs autre)
5. **Solutions alternatives** contournement subprocess

La solution technique FNC1 est **COMPLÈTEMENT VALIDÉE**. Le problème est uniquement d'infrastructure ! 🎯