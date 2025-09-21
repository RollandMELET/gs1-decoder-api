# PROMPT AGENT APPSCRIPT - GAS-GenerateurEtiquette

## 🎯 OBJECTIF
Intégrer l'API GS1 Decoder (https://gs1-decoder-api.rorworld.eu/) dans votre système AppScript pour générer des codes GS1 DataMatrix optimisés avec contrôle précis des quiet zones.

## 📋 CONFIGURATION API OPTIMALE

### ✅ PARAMÈTRES OBLIGATOIRES
```javascript
const apiCall = {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  payload: JSON.stringify({
    // FORMAT CRITIQUE: Utilisez "gs1-datamatrix" (PAS "datamatrix")
    "format": "gs1-datamatrix",

    // VOS DONNÉES GS1 (format parenthèses supporté)
    "data": "(01)03453120000011(17)271031(10)BATCH123",

    // FORMAT DE SORTIE
    "output_format": "png",

    // CONTRÔLE QUIET ZONE (NOUVEAU)
    "quiet_zone_modules": 1.0,    // 1.0 = standard GS1, 0.0 = aucune, 2.0 = élargie
    "no_quiet_zone": false,       // true = client gère design

    // MODE CLIENT (CRITIQUE POUR TAILLE)
    "client_mode": "optimized"    // "optimized" = taille native (500-600 bytes)
                                 // "compatible" = grande taille (40KB+)
  })
};
```

### 📊 RÉSULTATS ATTENDUS SELON CONFIGURATION

| Configuration | Taille fichier | Dimensions | Usage recommandé |
|---------------|----------------|------------|------------------|
| `no_quiet_zone: true` | **491 bytes** | 80×80 px | Client gère design/padding |
| `quiet_zone_modules: 1.0` | **526 bytes** | 98×98 px | **Standard GS1 conforme** |
| `quiet_zone_modules: 2.0` | **536 bytes** | 116×116 px | Meilleure lisibilité |

### 🔧 CODE APPSCRIPT COMPLET

```javascript
function generateOptimizedGS1DataMatrix(gs1Data, quietZoneModules = 1.0) {
  const url = 'https://gs1-decoder-api.rorworld.eu/generate/';

  const payload = {
    "format": "gs1-datamatrix",           // CRITIQUE: gs1-datamatrix (pas datamatrix)
    "data": gs1Data,
    "output_format": "png",
    "quiet_zone_modules": quietZoneModules, // Standard GS1 = 1.0
    "no_quiet_zone": false,
    "client_mode": "optimized"            // CRITIQUE: optimized (pas compatible)
  };

  const options = {
    'method': 'POST',
    'headers': {
      'Content-Type': 'application/json'
    },
    'payload': JSON.stringify(payload)
  };

  try {
    const response = UrlFetchApp.fetch(url, options);

    if (response.getResponseCode() === 200) {
      const imageBlob = response.getBlob();

      // Vérifier la taille (doit être 500-600 bytes en mode optimized)
      const fileSize = imageBlob.getBytes().length;
      console.log(`Image générée: ${fileSize} bytes`);

      if (fileSize > 10000) {
        console.warn('⚠️ Image trop lourde! Vérifiez les paramètres API');
      }

      return imageBlob;
    } else {
      throw new Error(`API Error: ${response.getResponseCode()}`);
    }
  } catch (error) {
    console.error('Erreur génération GS1 DataMatrix:', error);
    return null;
  }
}

// EXEMPLES D'UTILISATION
function examples() {
  // Standard GS1 conforme (recommandé)
  const standard = generateOptimizedGS1DataMatrix("(01)03453120000011(17)271031(10)BATCH123", 1.0);

  // Sans quiet zone (vous gérez le padding)
  const minimal = generateOptimizedGS1DataMatrix("(01)03453120000011(17)271031(10)BATCH123", 0.0);

  // Quiet zone élargie (meilleure lisibilité)
  const extended = generateOptimizedGS1DataMatrix("(01)03453120000011(17)271031(10)BATCH123", 2.0);
}
```

### ⚠️ ERREURS À ÉVITER

❌ **NE PAS FAIRE:**
```javascript
// ERREUR 1: Mauvais format
"format": "datamatrix"  // → Force redimensionnement 37KB

// ERREUR 2: Mode compatible par défaut
"client_mode": "compatible"  // → Génère 40KB+ au lieu de 500 bytes

// ERREUR 3: Oublier quiet_zone
// Sans paramètres quiet zone → Pas de contrôle du padding
```

✅ **CONFIGURATION CORRECTE:**
```javascript
{
  "format": "gs1-datamatrix",     // Format GS1 correct
  "client_mode": "optimized",     // Taille native optimisée
  "quiet_zone_modules": 1.0       // Standard GS1 conforme
}
```

### 🎯 CAS D'USAGE SPÉCIFIQUES

#### 1. **Génération Standard (Recommandé)**
```javascript
// Pour usage général conforme GS1
const config = {
  "quiet_zone_modules": 1.0,
  "client_mode": "optimized"
};
// Résultat: ~526 bytes, 98×98 pixels
```

#### 2. **Intégration Design Custom**
```javascript
// Vous gérez le padding dans votre interface
const config = {
  "no_quiet_zone": true,
  "client_mode": "optimized"
};
// Résultat: ~491 bytes, 80×80 pixels (minimal)
```

#### 3. **Haute Lisibilité**
```javascript
// Pour impression ou affichage difficile
const config = {
  "quiet_zone_modules": 2.0,
  "client_mode": "optimized"
};
// Résultat: ~536 bytes, 116×116 pixels
```

### 🔍 DIAGNOSTIC PROBLÈMES

Si vous obtenez des fichiers **> 10KB** :
1. ✅ Vérifiez `"format": "gs1-datamatrix"`
2. ✅ Confirmez `"client_mode": "optimized"`
3. ✅ Testez avec les exemples ci-dessus

### 📚 DOCUMENTATION COMPLÈTE
- API Endpoint: https://gs1-decoder-api.rorworld.eu/
- Documentation: https://github.com/RollandMELET/gs1-decoder-api
- Support formats: GS1 DataMatrix, QR Code, Code128
- Standards: ISO/IEC 16022, GS1 General Specifications