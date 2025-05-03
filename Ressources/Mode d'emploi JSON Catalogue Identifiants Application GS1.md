Catalogue JSON Identifiants Applications GS1

"Mode d'emploi JSON Catalogue Identifiants Application GS1" incluant le schéma JSON et un extrait commenté, conformément à votre demande.

````
# Mode d'emploi JSON Catalogue Identifiants Application GS1

Ce document décrit la structure attendue pour un catalogue numérique des Identifiants d'Application (AI) GS1, représenté sous la forme d'un tableau d'objets JSON. L'objectif est de fournir une référence structurée et détaillée pour chaque AI, basée sur les standards officiels GS1 [1, 2].

## Schéma JSON du Catalogue

Le catalogue complet est un tableau (Array) d'objets. Chaque objet représente un Identifiant d'Application unique et suit le schéma ci-dessous :

```json
[
  {
    "identifiant_ai": "string", // Code numérique de l'AI (2, 3 ou 4 chiffres)
    "designation": "string", // Nom officiel de l'AI
    "format_donnees": "string", // Format et longueur des données associées (notation GS1)
    "fnc1_requis": "boolean", // Indique si FNC1 est requis après les données si variable ET non dernier
    "titre_donnees": "string", // Titre court pour l'interprétation humaine (HRI)
    "description": "string", // Description détaillée de l'AI et de son usage
    "cle_gs1_associee": "string", // Clé GS1 principale typiquement associée (ex: GTIN, SSCC)
    "contextes_usage": [
      "string" // Liste des domaines ou industries d'utilisation
    ],
    "supports_donnees_autorises": [
      "string" // Liste des supports de données GS1 autorisés (ex: GS1-128, DataMatrix)
    ],
    "regles_et_contraintes": [
      "string" // Règles ou contraintes spécifiques d'utilisation
    ],
    "association_mandatoire": [
      "string" // AIs ou identifiants avec lesquels une association est obligatoire
    ]
  }
  // ... autres objets AI
]

````

Description Détaillée des Champs JSON

Chaque objet dans le tableau JSON décrit un Identifiant d'Application GS1 spécifique [1] :

1.

identifiant_ai

◦

Type : string

◦

Description : Le code numérique de l'Identifiant d'Application. C'est un préfixe numérique qui définit la signification et le format des données qui le suivent [1, 3]. Les AI peuvent avoir 2, 3 ou 4 chiffres [1, 4].

◦

Exemples : "00", "01", "10", "8200" [1].

2.

designation

◦

Type : string

◦

Description : Le nom officiel de l'AI selon les standards GS1 [1, 5-8]. Il décrit le type d'information identifié [1].

◦

Exemples : "Identification of a logistic unit (SSCC)" (pour AI 00) [1, 5], "Batch or lot number" (pour AI 10) [1, 5, 9, 10].

3.

format_donnees

◦

Type : string

◦

Description : Indique le format et la longueur des données associées à cet AI [1, 8]. La notation utilise des conventions spécifiques [1, 8]: * N : Chiffre numérique [1, 8, 11]. * X : Tout caractère de l'ensemble 82 de GS1 (alphanumérique) [1, 8, 12-14]. * Y : Tout caractère de l'ensemble 39 de GS1 [1, 8]. * Z : Tout caractère de l'ensemble 64 de GS1 (base64 file-safe / URI-safe) [1, 8]. * n après N, X, Y, Z : Longueur fixe de n caractères (ex: N6 pour 6 chiffres numériques) [1, 8, 14-16]. * ..n après N, X, Y, Z : Longueur variable, jusqu'à n caractères (ex: X..20 pour jusqu'à 20 caractères alphanumériques) [1, 8, 11, 14, 16]. * (FNC1) : Indique qu'un caractère FNC1 est requis après les données si l'AI est suivi d'un autre AI dans le même support de données et que la longueur des données est variable [1, 8, 14]. Le FNC1 sert aussi de séparateur entre éléments de données variables dans un même symbole [1, 14, 17-21]. Il peut aussi être le premier caractère dans les symboles GS1 DataMatrix ou QR Code encodant des chaînes GS1 [16-18, 22]. * [ ] : Indique un composant optionnel [1, 8, 23]. * Peut aussi indiquer une position décimale implicite (ex: 310n où 'n' est l'indicateur décimal) [1, 8, 14, 24-26].

◦

Exemples : "N2+N18" (AI 00) [1, 5, 9], "N2+X..20 (FNC1)" (AI 10) [1, 5, 9, 10], "N4+X..70 (FNC1)" (AI 8112) [1, 8, 14], "N4+N4" (AI 8111) [1, 27].

4.

fnc1_requis

◦

Type : boolean

◦

Description : Indique si un caractère FNC1 (true) est obligatoire après les données de cet AI si la longueur des données est variable ET que l'AI n'est pas le dernier dans l'élément de chaîne encodé [1, 8, 14]. Le FNC1 est également le premier caractère des symboles GS1 DataMatrix ou QR Code encodant des chaînes d'éléments GS1 [1, 16-18, 22].

◦

Valeurs : true ou false.

5.

titre_donnees

◦

Type : string

◦

Description : Le titre court ou l'abréviation normalisée associée aux données, utilisée dans l'interprétation lisible par l'homme (HRI - Human Readable Interpretation) sous le symbole [1, 2, 4-8, 28-30]. Les parenthèses autour de l'AI ne font pas partie des données encodées [1, 2, 4, 17, 30]. Parfois, seul le titre des données est affiché en HRI [1, 17, 31].

◦

Exemples : "SSCC" (pour AI 00) [1, 5], "BATCH/LOT" (pour AI 10) [1, 5, 9], "PRODUCT URL" (pour AI 8200) [1, 8, 14, 32].

6.

description

◦

Type : string

◦

Description : Une description plus complète de la signification et de l'usage de l'AI [1]. Inclut des détails sur le type d'information, l'entité qui l'attribue, et son rôle dans les processus [1].

◦

Exemples : AI (8200) identifie une URL autorisée par le propriétaire de la marque, à utiliser en association avec un GTIN [1, 32-34].

7.

cle_gs1_associee

◦

Type : string

◦

Description : Indique la clé d'identification GS1 principale (GTIN, SSCC, etc.) avec laquelle cet AI est typiquement utilisé ou associé [1]. Certains AI sont des attributs d'autres clés GS1 [1].

◦

Exemples : "GTIN" (pour AI 01, 8200, etc.) [1, 5, 9, 32, 33, 35, 36], "SSCC" (pour AI 00, 4300, etc.) [1, 5, 9, 37, 38].

8.

contextes_usage

◦

Type : Array of string

◦

Description : Liste des domaines, industries ou applications spécifiques où cet AI est couramment utilisé [1].

◦

Exemples : "Point de vente détail" [1, 39-46], "Logistique" [1, 37-39, 47-56], "Santé réglementée" [1, 9, 37, 57-65], "Emballage étendu (QR Code augmenté)" [1, 32, 33, 35, 39, 42, 66-68].

9.

supports_donnees_autorises

◦

Type : Array of string

◦

Description : Liste des supports de données GS1 (codes-barres 1D, 2D, RFID) dans lesquels cet AI peut être encodé [1]. La liste peut dépendre du contexte d'application [1, 3, 49, 59, 62, 69-72].

◦

Exemples : "GS1-128" [1, 3, 49, 59, 62, 69, 71-74], "GS1 DataMatrix" [1, 49, 59, 62, 69-72, 74-81].

10.

regles_et_contraintes

•

Type : Array of string

•

Description : Règles spécifiques, limitations ou contraintes d'utilisation définies dans les standards [1]. Peut inclure des restrictions sectorielles ou des règles de combinaison [1, 12].

•

Exemples : "Ne doit pas être utilisé en chaîne d'approvisionnement ouverte" (pour AI 8010) [1, 72], "Ne doit pas remplacer le GTIN, et le GTIN ne doit pas remplacer le GMN" (pour AI 8013) [1, 57].

11.

association_mandatoire

•

Type : Array of string

•

Description : Indique si cet AI doit obligatoirement être utilisé avec d'autres AIs ou identifiants dans certains contextes [1].

•

Exemples : "AI (01)" (pour AI 8200) [1, 32, 33], "GTIN" (pour AIs 710-715, etc.) [1, 34, 36, 59, 72, 82-85].

Dérivation de la Longueur et des Séparateurs pour le Parsing

Les informations sur la longueur des données et la règle du séparateur FNC1, cruciales pour un parsing correct, sont dérivées des champs format_donnees et fnc1_requis [1, 8, 9, 14].

Type de Longueur des Données

•

Comment dériver : Analyser la notation dans le champ format_donnees [1, 8, 14].

•

Interprétation :

◦

Si le format utilise Nn, Xn, Yn, ou Zn (longueur numérique spécifique n), la longueur est Fixe [1, 8, 14-16].

◦

Si le format utilise N..n, X..n, Y..n, ou Z..n (avec ..n), la longueur est Variable, jusqu'à la longueur maximale n [1, 8, 11, 14, 16].

◦

Les formats composés (ex: N2+N14 [1, 9, 86]) ont une longueur totale qui est la somme des longueurs fixes spécifiées. Les parties optionnelles [ ] [1, 8, 23] n'affectent pas le type de longueur du reste du format, mais rendent la longueur totale variable si l'option est utilisée.

◦

Notez la distinction entre "fixed length element strings" et "pre-defined length element strings" dans certains standards [87, 88]. Seuls ceux listés dans une table spécifique des standards (figure 7.8.5-2 des GS1 General Specifications [89] ou Table 2-3 du Guide DataMatrix [88]) n'ont pas besoin de séparateur si suivis d'un autre AI, car leur longueur est connue et fixe pour le parser [20, 87, 88].

Règle du Séparateur FNC1

•

Comment dériver : Analyser la présence de (FNC1) dans format_donnees et la valeur de fnc1_requis [1, 8, 14].

•

Interprétation :

◦

Si fnc1_requis est true (et le format inclut (FNC1)), un caractère FNC1 est requis après les données de cet AI si ces données sont de longueur variable ET que cet AI n'est PAS le dernier dans la chaîne d'éléments encodée [1, 8, 14, 20, 21, 87].

◦

Si fnc1_requis est false, aucun séparateur FNC1 n'est requis après les données de cet AI pour séparer le prochain AI [9, 87, 88]. C'est généralement le cas pour les AIs à longueur fixe dont la longueur est "pre-defined" [20, 87, 88].

◦

Le FNC1 est également utilisé comme premier caractère dans les symboles GS1 DataMatrix ou QR Code pour indiquer qu'ils contiennent des données GS1 [16-18, 21, 22, 74, 90-93].

Le caractère FNC1 est un caractère de contrôle spécifique aux symboles GS1 DataMatrix et QR Code (identifié par "]d2" ou "]Q3" dans la transmission [74, 93]) et GS1-128 (identifié par "]C1" [74, 94]). Dans la transmission de données scannées, il peut être représenté par le caractère ASCII

Extrait Commenté du Catalogue JSON (Exemples)

Voici un extrait JSON présentant deux objets, l'un pour un AI à longueur fixe et l'autre pour un AI à longueur variable, avec des commentaires explicatifs pour le parsing.

```
[
  {
    // AI 01 : Identification of a trade item (GTIN)
    "identifiant_ai": "01",
    "designation": "Identification of a trade item (GTIN)",
    "format_donnees": "N2+N14", // Format: 2 chiffres pour l'AI, 14 chiffres pour les données
    "fnc1_requis": false, // FNC1 n'est pas requis après les données (car longueur fixe "pre-defined")
    "titre_donnees": "GTIN",
    "description": "Identifie un article commercial à mesure fixe ou variable. C'est la clé principale pour l'identification des produits dans le système GS1.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Point de vente détail",
      "Logistique",
      "E-commerce",
      "Santé réglementée"
    ],
    "supports_donnees_autorises": [
      "EAN/UPC (implicite)",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar"
    ],
    "regles_et_contraintes": [
      "Doit être encodé en 14 chiffres avec des zéros non significatifs si nécessaire [35, 86].",
      "GTIN à usage réglementé en santé peut avoir 14 chiffres [60]."
    ],
    "association_mandatoire": [
      "AI (8200) en 'Extended Packaging' [32, 33]",
      "AIs 710-715 (NHRN) dans certains contextes santé [72]"
    ],
    // Précision pour le parsing :
    // La longueur des données pour l'AI 01 est TOUJOURS fixe à 14 chiffres [1, 9, 86].
    // En raison de sa longueur fixe "pre-defined" [88, 89], aucun séparateur FNC1 n'est requis après les 14 chiffres pour délimiter le prochain AI [20, 87].
    "notes_parsing": {
      "longueur": "Fixe",
      "valeur_longueur": "14 chiffres",
      "separateur_requis_apres_donnees": "Non (longueur fixe 'pre-defined' [88]). Le prochain AI commence immédiatement après les 14 chiffres."
    }
  },
  {
    // AI 10 : Batch or lot number
    "identifiant_ai": "10",
    "designation": "Batch or lot number",
    "format_donnees": "N2+X..20 (FNC1)", // Format: 2 chiffres pour l'AI, jusqu'à 20 caractères alphanumériques pour les données. (FNC1) indique un séparateur potentiel.
    "fnc1_requis": true, // FNC1 est requis après les données si elles sont de longueur variable ET si l'AI 10 n'est pas le dernier encodé.
    "titre_donnees": "BATCH/LOT",
    "description": "Identifie le numéro de lot ou de lot de production de l'article, essentiel pour la traçabilité.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Santé réglementée",
      "Traçabilité alimentaire",
      "Point de vente (moins fréquent)"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "Peut contenir des caractères alphanumériques de l'ensemble 82 [14]."
    ],
    "association_mandatoire": [
      "GTIN (dans la plupart des cas pour la traçabilité)"
    ],
     // Précision pour le parsing :
    // La longueur des données pour l'AI 10 est VARIABLE, jusqu'à 20 caractères [1, 9, 10].
    // Pour déterminer la fin des données de l'AI 10 lors du parsing d'une chaîne encodée :
    // 1. Si l'AI 10 est le dernier AI dans la chaîne, les données vont jusqu'à la fin du symbole.
    // 2. Si l'AI 10 n'est PAS le dernier AI dans la chaîne, les données se terminent par le caractère séparateur FNC1 (<GS> ASCII 29) [1, 8, 14, 20, 21, 87]. Le prochain AI commence immédiatement après le FNC1.
    "notes_parsing": {
      "longueur": "Variable",
      "valeur_longueur": "Jusqu'à 20 caractères alphanumériques",
      "separateur_requis_apres_donnees": "Oui, si suivi d'un autre AI. Chercher le caractère FNC1 (représenté par <GS> ASCII 29) pour marquer la fin des données de l'AI 10 [20, 21, 87]."
    }
  }
  // ... autres objets AI
]

```

Cet extrait commenté illustre comment le champ format_donnees (par sa notation Nn vs X..n) et le champ fnc1_requis (true/false) fournissent les informations nécessaires pour déterminer si la longueur est fixe ou variable et quelle est la règle de délimitation par le FNC1 pour un parsing correct [1, 8, 14]. Les notes de parsing dans l'exemple synthétisent cette interprétation pour chaque AI.