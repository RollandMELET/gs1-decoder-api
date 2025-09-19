#!/usr/bin/env node
/**
 * Script Node.js wrapper pour générer des GS1 DataMatrix via bwip-js
 * Usage: node generate_gs1_bwip.js "données_gs1" "fichier_sortie.png"
 *
 * Basé sur les recommandations de la note technique :
 * - bwip-js = traduction directe du moteur PostScript BWIPP
 * - Support natif gs1datamatrix avec parsefnc
 * - Plus simple que treepoem (pas de dépendance Ghostscript)
 */

const bwipjs = require('bwip-js');
const fs = require('fs');
const path = require('path');

// Vérifier les arguments
if (process.argv.length < 4) {
    console.error('ERROR: Usage: node generate_gs1_bwip.js "données_gs1" "fichier_sortie.png"');
    console.error('ERROR: Exemple: node generate_gs1_bwip.js "(01)12345678901234" "output.png"');
    process.exit(1);
}

const data = process.argv[2];
const outputPath = process.argv[3];

console.log(`[DEBUG] bwip-js: Génération GS1 DataMatrix`);
console.log(`[DEBUG] Données: ${data}`);
console.log(`[DEBUG] Sortie: ${outputPath}`);

// Configuration bwip-js pour GS1 DataMatrix conforme
const options = {
    bcid: 'gs1datamatrix',      // Type GS1 DataMatrix (CRITIQUE)
    text: data,                 // Données à encoder
    parsefnc: true,             // Parse AI et gère FNC1 (CRITIQUE selon note)
    scale: 5,                   // Facteur d'échelle pour qualité
    includetext: false,         // Pas de texte sous le code
    textsize: 10                // Taille texte si activé
};

// Génération du code-barres
bwipjs.toBuffer(options, (err, pngBuffer) => {
    if (err) {
        console.error(`[ERROR] bwip-js génération échouée: ${err.message}`);
        console.error(`[ERROR] Données problématiques: ${data}`);
        process.exit(1);
    }

    try {
        // Sauvegarder le buffer PNG
        fs.writeFileSync(outputPath, pngBuffer);

        console.log(`[SUCCESS] GS1 DataMatrix généré avec bwip-js`);
        console.log(`[SUCCESS] Fichier: ${outputPath} (${pngBuffer.length} bytes)`);
        console.log(`[SUCCESS] Identifiant AIM attendu: ]d2 (GS1 DataMatrix)`);

        // Code de sortie 0 = succès
        process.exit(0);

    } catch (writeErr) {
        console.error(`[ERROR] Erreur écriture fichier: ${writeErr.message}`);
        process.exit(1);
    }
});

// Timeout de sécurité (10 secondes)
setTimeout(() => {
    console.error('[ERROR] Timeout bwip-js - génération trop longue');
    process.exit(1);
}, 10000);