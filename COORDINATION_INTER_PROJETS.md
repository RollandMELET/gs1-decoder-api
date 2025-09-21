# 🔄 COORDINATION INTER-PROJETS - GAS ↔ API SVG

## 🚨 **VIGILANCE ULTRA : Dépendances Critiques**

### **2 Projets Coordonnés**
```
📋 GAS-GenerateurEtiquette (CLIENT)
    ├── Current: Appelle gs1-decoder-api en priorité 1
    ├── Problem: Rejette 735-758 bytes comme "trop petites"
    ├── Fallback: bwip-js externe (3,500+ bytes)
    └── BESOIN: SVG vectoriel pour éviter fallback

📊 gs1-decoder-api (SERVER - CE PROJET)
    ├── Current: PNG optimisé 735-758 bytes (96.8% réduction)
    ├── Success: Architecture hybride bwip-js opérationnelle
    ├── Protection: Suite TDD + tests critiques
    └── EXTENSION: Support SVG + modes adaptatifs
```

## ⚠️ **SÉQUENCE COORDINATION OBLIGATOIRE**

### **PHASE 1 : API d'abord (CE PROJET)**
```
🎯 gs1-decoder-api DOIT être étendu EN PREMIER

ORDRE TÂCHES ARCHON (STRICT):
├── 120. Support SVG natif API
├── 125. Protection architecture hybride
├── 130. Modes adaptatifs
├── 135. Extension architecture hybride SVG
├── 140. Tests SVG + validation client
├── 150. Tests end-to-end coordination
├── 160. Documentation API v2.0
└── 170. Validation coordination finale

CRITICAL: Chaque tâche DOIT préserver optimisation PNG existante
```

### **PHASE 2 : Client ensuite (AUTRE PROJET)**
```
📋 GAS-GenerateurEtiquette implémente APRÈS API ready

MODIFICATIONS GAS (PRD livré):
├── Payload: "image_format": "svg"
├── Handler: image/svg+xml responses
├── Insertion: SVG dans Google Slides
└── Validation: Critères adaptés SVG

DÉPENDANCE: GAS ne peut commencer qu'après API v2.0 deployed
```

## 🎯 **COORDINATION TECHNIQUE CRITIQUE**

### **Payload Coordination**

**GAS va envoyer (après modifications) :**
```json
{
    "data": "(01)03760423190005(11)251001(3100)012000(21)000001B0(90)7391023(93)DHA(94)UP(95)ENVELOPPE_NUE_4UF",
    "format": "gs1-datamatrix",
    "image_format": "svg",           // ← NOUVEAU
    "client_mode": "compatible",     // ← NOUVEAU
    "width": 300,
    "height": 300
}
```

**API doit répondre :**
```
Status: 200 OK
Content-Type: image/svg+xml
Size: 1200-2000 bytes (satisfait critères client)
Content: SVG avec metadata GS1 + ]d2 identifier
```

### **Validation Criteria Coordination**

**Client GAS observe actuellement :**
```javascript
// Critères rejet observés dans logs
if (responseSize < 1000 && contentType === "image/png") {
    console.log("⚠️ Image trop petite ou vide");
    return false; // → Fallback bwip-js externe
}
```

**API v2.0 doit satisfaire :**
```python
# Nouveaux critères SVG
if content_type == "image/svg+xml":
    return content_length > 800  # SVG minimum pour client
elif content_type == "image/png" and client_mode == "compatible":
    return content_length > 2000  # PNG plus gros si demandé
else:
    return content_length > 500  # PNG optimisé (mode actuel)
```

## 🛡️ **PROTECTION ANTI-RÉGRESSION**

### **Architecture Critique Préservée**
```
🔴 PENDANT extension SVG, architecture PNG DOIT rester intacte:

✅ PNG optimisé: 735-758 bytes preserved
✅ Architecture hybride: bwip-js → fallbacks unchanged
✅ ]d2 identifier: Maintained in PNG
✅ Performance: < 2s PNG unchanged
✅ Tests critiques: MUST pass throughout development
```

### **Points de Contrôle**
```
CHECKPOINT 1 (après tâche 120): SVG support basic
├── make test-critical MUST pass
├── PNG generation unchanged
└── No regression in existing functionality

CHECKPOINT 2 (après tâche 130): Modes adaptatifs
├── client_mode="optimized" = comportement actuel
├── client_mode="compatible" = tailles client-friendly
└── Backward compatibility 100%

CHECKPOINT 3 (après tâche 150): Tests coordination
├── Simulation payload GAS successful
├── Client criteria satisfied
└── Fallback elimination demonstrated

CHECKPOINT FINAL (tâche 170): Production ready
├── API v2.0 deployed and stable
├── Documentation GAS coordination complete
└── Ready for GAS implementation
```

## 📋 **DELIVERABLES COORDINATION**

### **Pour Équipe API (CE PROJET)**
✅ **PRD_GAS_GENERATEUR_ETIQUETTE.md** - Specs pour codeur GAS
✅ **Tâches ARCHON** - 6 tâches API extension (120-170)
✅ **Tests coordination** - Validation inter-projets
✅ **Documentation v2.0** - API usage guides

### **Pour Équipe GAS (AUTRE PROJET)**
📋 **PRD complet** avec:
- Modifications payload requises
- Handling SVG responses
- Insertion Google Slides
- Validation criteria adaptation

## ⚠️ **RISQUES COORDINATION**

### **RISQUE 1 : Implémentation simultanée**
```
❌ DANGER: GAS commence avant API v2.0 ready
✅ SOLUTION: Séquence stricte API → GAS
```

### **RISQUE 2 : Régression architecture critique**
```
❌ DANGER: Extension SVG casse optimisation PNG
✅ SOLUTION: Tests critiques + checkpoints
```

### **RISQUE 3 : Critères client incompris**
```
❌ DANGER: SVG ne satisfait pas critères GAS
✅ SOLUTION: Reproduction exacte logs + simulation
```

## 🎯 **SUCCESS CRITERIA GLOBAL**

### **Objectif Final**
```
GAS-GenerateurEtiquette → gs1-decoder-API v2.0 → SVG → ✅ Accepté
                                                      (plus de fallback)

METRICS SUCCESS:
├── GAS payload → API SVG → 1200-2000 bytes
├── Client acceptance: "Image acceptable"
├── Fallback eliminated: Pas d'appel bwip-js externe
├── Performance: < 2s pour SVG
└── PNG optimization: Preserved (735-758 bytes)
```

### **Validation Finale**
```bash
# API côté
make test-critical     # Tests critiques passent
make monitor-svg       # Monitoring SVG production

# GAS côté (après implémentation PRD)
Test payload SVG → Response acceptable → Insertion Google Slides successful
```

---

## 📞 **COMMUNICATION COORDINATION**

### **Timeline Implémentation**
```
SEMAINE 1: gs1-decoder-API extension SVG (tâches ARCHON 120-170)
SEMAINE 2: Tests coordination + documentation v2.0
SEMAINE 3: GAS-GenerateurEtiquette implementation (PRD)
SEMAINE 4: Validation end-to-end + production
```

### **Points de Synchronisation**
- **Checkpoint API ready** : Notification équipe GAS
- **Tests coordination** : Validation inter-équipes
- **Deployment coordination** : API v2.0 → GAS modifications
- **Production validation** : Monitoring conjoint

---

**⚠️ CRITICAL SUCCESS FACTOR: Séquence rigoureuse + protection architecture + validation critères client**

*Document de coordination maître - ULTRA VIGILANCE appliquée*