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

console.log(`[DEBUG] bwip-js: Tentative génération avec données: ${data}`);

// TENTATIVE 1: gs1datamatrix avec parsefnc (configuration note technique)
let options = {
    bcid: 'gs1datamatrix',      // Type GS1 DataMatrix selon documentation
    text: data,                 // Données au format (01)123...
    parsefnc: true,             // Parse FNC1 et AI automatiquement
    scale: 5,                   // Qualité
    includetext: false
};

console.log(`[DEBUG] bwip-js: Tentative 1 - gs1datamatrix + parsefnc`);
console.log(`[DEBUG] bwip-js: Options:`, JSON.stringify(options, null, 2));

// Fonction pour tester une configuration
function tryGeneration(opts, description) {
    return new Promise((resolve, reject) => {
        console.log(`[DEBUG] bwip-js: ${description}`);

        bwipjs.toBuffer(opts, (err, pngBuffer) => {
            if (err) {
                console.log(`[DEBUG] bwip-js: ${description} échoué: ${err.message}`);
                reject(err);
            } else {
                console.log(`[DEBUG] bwip-js: ${description} SUCCÈS (${pngBuffer.length} bytes)`);
                resolve(pngBuffer);
            }
        });
    });
}

// TENTATIVES MULTIPLES pour trouver la bonne configuration
async function generateGS1DataMatrix() {
    try {
        let pngBuffer;

        // TENTATIVE 1: gs1datamatrix + parsefnc (notre configuration actuelle)
        try {
            pngBuffer = await tryGeneration(options, "gs1datamatrix + parsefnc");
        } catch (e) {
            // TENTATIVE 2: datamatrix avec options GS1
            try {
                const options2 = {
                    bcid: 'datamatrix',
                    text: data,
                    parse: true,
                    parsefnc: true,
                    scale: 5
                };
                console.log(`[DEBUG] bwip-js: Tentative 2 - datamatrix + parse + parsefnc`);
                pngBuffer = await tryGeneration(options2, "datamatrix + parse + parsefnc");
            } catch (e2) {
                // TENTATIVE 3: datamatrix avec préfixe FNC1 manuel
                try {
                    const options3 = {
                        bcid: 'datamatrix',
                        text: `^FNC1${data}`,  // Préfixe FNC1 manuel
                        scale: 5
                    };
                    console.log(`[DEBUG] bwip-js: Tentative 3 - datamatrix + préfixe ^FNC1`);
                    pngBuffer = await tryGeneration(options3, "datamatrix + préfixe ^FNC1");
                } catch (e3) {
                    // TENTATIVE 4: format des données sans parenthèses
                    const dataNoParens = data.replace(/[\(\)]/g, ''); // Enlever ()
                    const options4 = {
                        bcid: 'gs1datamatrix',
                        text: dataNoParens,
                        parsefnc: true,
                        scale: 5
                    };
                    console.log(`[DEBUG] bwip-js: Tentative 4 - données sans parenthèses`);
                    console.log(`[DEBUG] bwip-js: Données transformées: ${dataNoParens}`);
                    pngBuffer = await tryGeneration(options4, "gs1datamatrix sans parenthèses");
                }
            }
        }

        // Sauvegarder le résultat
        fs.writeFileSync(outputPath, pngBuffer);

        console.log(`[SUCCESS] GS1 DataMatrix généré avec bwip-js`);
        console.log(`[SUCCESS] Fichier: ${outputPath} (${pngBuffer.length} bytes)`);
        console.log(`[SUCCESS] Identifiant AIM attendu: ]d2 (GS1 DataMatrix)`);

        process.exit(0);

    } catch (finalError) {
        console.error(`[ERROR] Toutes les tentatives bwip-js ont échoué`);
        console.error(`[ERROR] Dernière erreur: ${finalError.message}`);
        console.error(`[ERROR] Données: ${data}`);
        process.exit(1);
    }
}

// Lancer la génération
generateGS1DataMatrix();

// Timeout de sécurité (10 secondes)
setTimeout(() => {
    console.error('[ERROR] Timeout bwip-js - génération trop longue');
    process.exit(1);
}, 10000);