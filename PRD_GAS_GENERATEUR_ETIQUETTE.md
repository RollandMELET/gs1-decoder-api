# 📋 PRD - GAS-GenerateurEtiquette : Intégration SVG API GS1 Decoder

## **CONTEXT ET PROBLÈME**

### **Situation Actuelle**
- **Client** : GAS-GenerateurEtiquette utilise gs1-decoder-api
- **Problème** : API génère images optimisées (735-758 bytes) jugées "trop petites"
- **Fallback actuel** : bwip-js externe (3,500+ bytes) utilisé à la place
- **Impact** : Solution optimisée de l'API non utilisée

### **Logs Observés**
```
✅ gs1-decoder-api: 200 OK, 735-758 bytes
⚠️ Client: "Image trop petite ou vide"
🔄 Fallback: bwip-js externe, 3,500+ bytes
✅ Client: "Acceptable"
```

## **OBJECTIF**

Modifier GAS-GenerateurEtiquette pour utiliser **SVG vectoriel** de gs1-decoder-api, éliminant le besoin de fallback tout en conservant qualité optimale.

---

## **REQUIREMENTS FONCTIONNELS**

### **REQ-GAS-001 : Appel API SVG**

**Modifier payload d'appel API :**
```javascript
// AVANT (PNG actuel)
const payload = {
    "data": gs1Message,
    "format": "gs1-datamatrix",
    "image_format": "png",
    "width": 300,
    "height": 300
};

// APRÈS (SVG nouveau)
const payload = {
    "data": gs1Message,
    "format": "gs1-datamatrix",
    "image_format": "svg",           // ← CHANGEMENT
    "client_mode": "compatible",     // ← NOUVEAU
    "svg_viewbox_size": 300,        // ← NOUVEAU
    "target_file_size_kb": 2        // ← NOUVEAU (optionnel)
};
```

**Acceptance Criteria :**
- ✅ Payload modifié pour demander SVG
- ✅ Paramètres client_mode pour éviter fallback
- ✅ Gestion erreurs si SVG non disponible
- ✅ Backward compatibility maintenue

### **REQ-GAS-002 : Gestion Réponse SVG**

**Modifier traitement réponse API :**
```javascript
// Fonction de génération DataMatrix
function genererDataMatrixGS1(gs1Message, slide, position) {
    const response = UrlFetchApp.fetch(API_URL, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        payload: JSON.stringify(payload)
    });

    const contentType = response.getHeaders()['Content-Type'];

    if (contentType === 'image/svg+xml') {
        // ← NOUVEAU: Gestion SVG
        const svgContent = response.getContentText();
        return insererSVGDansSlide(slide, svgContent, position);
    } else if (contentType === 'image/png') {
        // ← EXISTANT: Gestion PNG (fallback)
        const blob = response.getBlob();
        return insererImageDansSlide(slide, blob, position);
    } else {
        throw new Error(`Format non supporté: ${contentType}`);
    }
}
```

**Acceptance Criteria :**
- ✅ Détection automatique SVG vs PNG
- ✅ Traitement approprié selon format
- ✅ Gestion erreurs formats non supportés
- ✅ Logging pour debugging

### **REQ-GAS-003 : Insertion SVG dans Google Slides**

**Nouvelle fonction insertion SVG :**
```javascript
function insererSVGDansSlide(slide, svgContent, position) {
    try {
        // Méthode 1: Conversion SVG → Image
        const blob = convertirSVGVersBlob(svgContent);
        const image = slide.insertImage(blob);

        // Positionnement
        image.setLeft(position.x);
        image.setTop(position.y);

        // Métadonnées pour tracking
        image.setDescription(`GS1 DataMatrix SVG - ${new Date()}`);

        console.log(`✅ SVG inséré: ${svgContent.length} caractères`);
        return image;

    } catch (error) {
        console.log(`❌ Erreur insertion SVG: ${error}`);
        throw error;
    }
}

function convertirSVGVersBlob(svgContent) {
    // Encoder SVG en base64 pour Google Slides
    const svgBase64 = Utilities.base64Encode(svgContent);
    return Utilities.newBlob(
        Utilities.base64Decode(svgBase64),
        'image/svg+xml',
        'datamatrix.svg'
    );
}
```

**Acceptance Criteria :**
- ✅ SVG s'affiche correctement dans Google Slides
- ✅ Qualité vectorielle préservée
- ✅ Positionnement précis maintenu
- ✅ Gestion erreurs robuste

### **REQ-GAS-004 : Validation et Fallback**

**Logique de validation améliorée :**
```javascript
function validerReponseAPI(response, source) {
    const contentType = response.getHeaders()['Content-Type'];
    const contentLength = response.getBlob().getBytes().length;

    // Critères validation adaptés au format
    if (contentType === 'image/svg+xml') {
        // SVG: Valider contenu + métadonnées
        const svgContent = response.getContentText();
        const isValidSVG = svgContent.includes('<svg') &&
                          svgContent.includes('data-format="gs1-datamatrix"');

        if (isValidSVG && contentLength > 400) {  // SVG minimum
            console.log(`✅ ${source} - SVG valide: ${contentLength} bytes`);
            return true;
        }
    } else if (contentType === 'image/png') {
        // PNG: Critères existants ajustés
        if (contentLength > 700) {  // Critère PNG ajusté
            console.log(`✅ ${source} - PNG valide: ${contentLength} bytes`);
            return true;
        }
    }

    console.log(`⚠️ ${source} - Critères non satisfaits`);
    return false;
}
```

**Acceptance Criteria :**
- ✅ Validation adaptée au format (SVG vs PNG)
- ✅ Critères appropriés par type contenu
- ✅ Fallback intelligent si validation échoue
- ✅ Logging détaillé pour debugging

---

## **COORDINATION IMPLÉMENTATION**

### **ÉTAPE 1 : API GS1 Decoder (PRIORITÉ 1)**
```
gs1-decoder-api DOIT être étendu AVANT modifications GAS
│
├── Ajouter support SVG
├── Implémenter modes adaptatifs
├── Tests SVG + backward compatibility
└── Déployement production
```

### **ÉTAPE 2 : GAS-GenerateurEtiquette (APRÈS API)**
```
GAS PEUT être modifié APRÈS que API supporte SVG
│
├── Modifier payload appels API
├── Implémenter gestion SVG
├── Tests insertion Google Slides
└── Validation qualité + performance
```

### **VALIDATION CROISÉE**
```
Tests end-to-end OBLIGATOIRES:
│
├── GAS appelle API avec "image_format": "svg"
├── API répond SVG valide + métadonnées
├── GAS insère SVG dans Google Slides
├── Validation visuelle + fonctionnelle
└── Performance mesurée vs solution actuelle
```

---

## **RISQUES ET MITIGATION**

### **RISQUE 1 : Google Slides ne supporte pas SVG directement**
**Mitigation :** Conversion SVG → PNG côté GAS si nécessaire

### **RISQUE 2 : Performance SVG dégradée**
**Mitigation :** Benchmarks + fallback PNG automatique

### **RISQUE 3 : Régression API optimisation GS1**
**Mitigation :** Tests critiques obligatoires + points restauration

---

## **DELIVERABLES GAS-GenerateurEtiquette**

### **Code Changes Required**
1. **Payload modification** : Demander SVG + modes
2. **Response handling** : Gérer image/svg+xml
3. **Insertion function** : SVG dans Google Slides
4. **Validation logic** : Critères adaptés SVG
5. **Error handling** : Fallback intelligent

### **Testing Required**
1. **API integration** : SVG requests + responses
2. **Google Slides** : SVG display quality
3. **Performance** : SVG vs PNG comparison
4. **Edge cases** : Error scenarios + fallbacks

### **Documentation Updates**
1. **Usage guide** : How to call API for SVG
2. **Troubleshooting** : SVG-specific issues
3. **Performance notes** : Expected improvements

---

**⚠️ DEPENDENCY CRITICAL :** GAS modifications can only begin AFTER gs1-decoder-API supports SVG output. Coordination essential for success.

---

*PRD destiné au codeur GAS-GenerateurEtiquette pour intégration SVG de gs1-decoder-API*