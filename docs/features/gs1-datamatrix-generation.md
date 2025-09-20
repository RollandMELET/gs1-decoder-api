# Feature: Génération de GS1 DataMatrix

## What This Feature Does
Cette fonctionnalité génère des codes GS1 DataMatrix conformes aux standards internationaux avec insertion automatique du caractère FNC1 pour garantir l'identification correcte comme codes ]d2 (GS1 DataMatrix) plutôt que ]d1 (DataMatrix standard).

## How It Works
L'utilisateur envoie des données GS1 formatées (ex: "(01)12345678901234") via l'API. Le système utilise une architecture hybride avec bwip-js comme générateur principal, optimise automatiquement la taille des fichiers, et retourne un code DataMatrix optimisé de 500-700 bytes au lieu des 16k-23k bytes traditionnels.

## Sequence Diagram
```
participant User
participant API
participant MainApp
participant BarcodeGenerator
participant NodeJS_bwipjs
participant ImageProcessor

User->API: POST /generate/ avec données GS1
API->MainApp: Validation et routage
MainApp->BarcodeGenerator: generate_barcode(gs1_datamatrix)
BarcodeGenerator->NodeJS_bwipjs: Subprocess avec données GS1
NodeJS_bwipjs->NodeJS_bwipjs: Configuration GS1 + FNC1
NodeJS_bwipjs->BarcodeGenerator: PNG optimisé (500-700 bytes)
BarcodeGenerator->ImageProcessor: Préservation taille native
ImageProcessor->BarcodeGenerator: Image finale
BarcodeGenerator->MainApp: Données binaires PNG
MainApp->API: Response avec métadonnées
API->User: Code GS1 DataMatrix optimisé
```

## Files Changed/Added
- `app/main.py` - Point d'entrée API avec forcing use_treepoem=False pour GS1 DataMatrix
- `app/barcode_generator.py` - Architecture hybride avec priorisation bwip-js et optimisation redimensionnement
- `generate_gs1_bwip.js` - Script Node.js simplifié pour génération GS1 DataMatrix conforme
- `package.json` - Dépendances Node.js pour bwip-js
- `CLAUDE.md` - Documentation avec URL API production

## Key Functions/Components

**generate_gs1_datamatrix_hybrid()**
- **What it does:** Génère GS1 DataMatrix via architecture hybride avec fallbacks (bwip-js → treepoem → zint → dmtxwrite)
- **Located in:** `app/barcode_generator.py:520-580`

**generate_barcode() - Endpoint principal**
- **What it does:** Force use_treepoem=False pour GS1 DataMatrix et gère l'optimisation des tailles
- **Located in:** `app/main.py:200-250`

**Script Node.js bwip-js**
- **What it does:** Configuration GS1 simplifiée basée sur projet de référence Terry Burton
- **Located in:** `generate_gs1_bwip.js`

## How to Test
1. **API Production:** `curl -X POST "https://gs1-decoder-api.rorworld.eu/generate/" -H "Content-Type: application/json" -d '{"data": "(01)12345678901234", "barcode_format": "gs1_datamatrix"}'`
2. **Vérifier taille:** Fichier doit faire 500-700 bytes (vs 16k-23k avant optimisation)
3. **Validation GS1:** Décoder avec ZXing doit retourner identifier AIM ]d2 (GS1 DataMatrix)

## Dependencies
- **bwip-js** (Node.js) - Générateur principal GS1 DataMatrix
- **Node.js runtime** - Exécution subprocess pour bwip-js
- **JPype1** - Interface ZXing pour validation
- **PIL/Pillow** - Traitement d'images

## Notes & TODOs
- **Optimisation majeure:** 96.8% de réduction de taille fichiers (22k → 730 bytes)
- **Architecture hybride:** Garantit génération même si bwip-js échoue
- **Conformité GS1:** Solution FNC1 validée par expert technique
- **Future:** Possibilité d'étendre à d'autres formats GS1 (QR Code, Code 128)
- **Performance:** Préservation tailles natives = réduction drastique bande passante