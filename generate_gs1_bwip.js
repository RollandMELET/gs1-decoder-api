#!/usr/bin/env node
/**
 * Script Node.js simplifié pour générer des GS1 DataMatrix via bwip-js
 * Usage: node generate_gs1_bwip.js "données_gs1" "fichier_sortie.png"
 *
 * NOUVELLE APPROCHE : Configuration ultra-simple basée sur le projet de référence fonctionnel
 * - Pas de tentatives multiples
 * - Pas de transformations des données
 * - Configuration identique au projet de référence qui fonctionne
 */

const bwipjs = require('bwip-js');
const fs = require('fs');

// Vérifier les arguments
if (process.argv.length < 4) {
    console.error('ERROR: Usage: node generate_gs1_bwip.js "données_gs1" "fichier_sortie.png"');
    console.error('ERROR: Exemple: node generate_gs1_bwip.js "(01)12345678901234" "output.png"');
    process.exit(1);
}

const data = process.argv[2];
const outputPath = process.argv[3];

console.log(`[DEBUG] bwip-js: Génération GS1 DataMatrix SIMPLIFIÉE`);
console.log(`[DEBUG] Données brutes: ${data}`);
console.log(`[DEBUG] Sortie: ${outputPath}`);

// CONFIGURATION OPTIMISÉE - Quiet zone minimale GS1 standard
const options = {
    bcid: 'gs1datamatrix',      // Type GS1 DataMatrix
    text: data,                 // Données brutes (avec parenthèses) - AUCUNE transformation
    scale: 3,                   // Même valeur que le projet de référence
    height: 10,                 // Valeurs standard du projet de référence
    width: 10,
    paddingleft: 2,             // OPTIMISÉ: Quiet zone minimale (était 10)
    paddingright: 2,            // OPTIMISÉ: Quiet zone minimale (était 10)
    paddingtop: 2,              // OPTIMISÉ: Quiet zone minimale (était 10)
    paddingbottom: 2,           // OPTIMISÉ: Quiet zone minimale (était 10)
    includetext: true,          // Comme dans le projet de référence
    textxalign: 'center',
    textcolor: '000000',
    textgaps: 2
};

console.log(`[DEBUG] bwip-js: Configuration simple du projet de référence`);
console.log(`[DEBUG] bwip-js: Options:`, JSON.stringify(options, null, 2));

// Génération directe avec une seule configuration
bwipjs.toBuffer(options, (err, pngBuffer) => {
    if (err) {
        console.error(`[ERROR] Génération bwip-js échouée: ${err.message}`);
        console.error(`[ERROR] Données: ${data}`);
        process.exit(1);
    }

    // Sauvegarder le résultat
    fs.writeFileSync(outputPath, pngBuffer);

    console.log(`[SUCCESS] GS1 DataMatrix généré avec configuration simple`);
    console.log(`[SUCCESS] Fichier: ${outputPath} (${pngBuffer.length} bytes)`);
    console.log(`[SUCCESS] Configuration identique au projet de référence fonctionnel`);
    console.log(`[SUCCESS] Identifiant AIM attendu: ]d2 (GS1 DataMatrix)`);

    process.exit(0);
});

// Timeout de sécurité (10 secondes)
setTimeout(() => {
    console.error('[ERROR] Timeout bwip-js - génération trop longue');
    process.exit(1);
}, 10000);