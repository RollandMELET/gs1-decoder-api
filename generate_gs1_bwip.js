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
    console.error('ERROR: Usage: node generate_gs1_bwip.js "données_gs1" "fichier_sortie.png" [quiet_zone_modules]');
    console.error('ERROR: Exemple: node generate_gs1_bwip.js "(01)12345678901234" "output.png" 1.0');
    console.error('ERROR: quiet_zone_modules: 1.0=standard GS1, 0.0=aucune, 2.0=double');
    process.exit(1);
}

const data = process.argv[2];
const outputPath = process.argv[3];
const quietZoneModules = process.argv[4] !== undefined ? parseFloat(process.argv[4]) : 1.0;  // Défaut 1.0 module (standard GS1)

console.log(`[DEBUG] bwip-js: Génération GS1 DataMatrix SIMPLIFIÉE`);
console.log(`[DEBUG] Données brutes: ${data}`);
console.log(`[DEBUG] Sortie: ${outputPath}`);

// CONFIGURATION CONFORME STANDARD GS1 - Quiet zone proportionnelle
console.log(`[DEBUG] Quiet zone: ${quietZoneModules} modules (standard GS1 = 1.0)`);

// Calculer quiet zone proportionnelle au module
// En bwip-js, scale=3 signifie 1 module = 3 pixels
const moduleSize = 3;  // scale factor
const quietZonePixels = Math.round(quietZoneModules * moduleSize);
console.log(`[DEBUG] Calcul: ${quietZoneModules} modules × ${moduleSize} pixels = ${quietZonePixels} pixels`);

const options = {
    bcid: 'gs1datamatrix',      // Type GS1 DataMatrix
    text: data,                 // Données brutes (avec parenthèses) - AUCUNE transformation
    scale: 3,                   // Même valeur que le projet de référence
    height: 10,                 // Valeurs standard du projet de référence
    width: 10,
    paddingleft: quietZonePixels,   // CONFORME: Quiet zone proportionnelle (modules × scale)
    paddingright: quietZonePixels,  // CONFORME: Quiet zone proportionnelle (modules × scale)
    paddingtop: quietZonePixels,    // CONFORME: Quiet zone proportionnelle (modules × scale)
    paddingbottom: quietZonePixels, // CONFORME: Quiet zone proportionnelle (modules × scale)
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