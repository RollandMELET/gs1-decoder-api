# 📚 Ressources GS1 pour GS1-Decoder-API

Ce répertoire contient toutes les ressources nécessaires pour le développement et l'amélioration du GS1-Decoder-API, en particulier concernant les Application Identifiers (AI) de GS1.

## 📋 Fichiers inclus

### `gs1_application_identifiers.json`
Liste complète des Application Identifiers (AI) GS1 au format JSON, incluant:
- Code AI
- Nom normalisé
- Description
- Format (numérique, alphanumérique)
- Longueur et indication fixe/variable
- Position décimale pour les valeurs numériques avec point décimal

### `gs1_parser_utilities.py`
Bibliothèque d'utilitaires Python pour:
- Normalisation des données GS1
- Analyse et extraction des AI
- Formatage des valeurs spécifiques (dates, poids, etc.)
- Détection du format de code-barres

## 🔍 Documentation GS1 officielle

Les documents suivants ont été utilisés comme référence :

- [GS1 General Specifications](https://www.gs1.org/docs/barcodes/GS1_General_Specifications.pdf)
- [Liste officielle des AI](https://www.gs1.org/standards/barcodes/application-identifiers)
- [Référentiel d'AI](https://ref.gs1.org/ai/)

## 💡 Utilisation

Ces ressources sont destinées à être utilisées dans l'implémentation complète du parseur GS1 pour prendre en charge tous les AI disponibles, comme mentionné dans les "Idées d'améliorations futures" du README principal.

## 🧩 Support des formats de codes-barres

Formats de codes-barres GS1 pris en charge:
- GS1-128
- GS1 DataMatrix
- GS1 QR Code

## 📝 Notes d'implémentation

Lors de l'implémentation du support complet des AI, veuillez considérer:

1. Les AI à longueur variable nécessitent un séparateur (FNC1, représenté par \x1d, ou parfois par des séparateurs alternatifs ".", "|", etc.)
2. Les AI à longueur fixe ne nécessitent pas de séparateur
3. Certains codes nécessitent un traitement spécial:
   - Les dates (formats YYMMDD)
   - Les valeurs numériques avec position décimale (310y-319y)
   - Les identifiants composés (GTIN + numéro de série)

## 🔄 Stratégie de décodage

### Détection du décodeur utilisé
Pour identifier quelle bibliothèque a réussi à décoder le code-barres:
1. Essayer d'abord ZXing (plus robuste pour les codes GS1-128)
2. Si échec, essayer pylibdmtx (meilleur pour les DataMatrix)
3. Retourner l'information sur le décodeur utilisé dans la réponse

### Détection automatique du format
L'analyse du format se fait par:
1. Examen des caractères de début (symboles spéciaux, identifiants FNC)
2. Analyse du motif des données (présence d'AI valides)
3. Caractéristiques des données (longueur, type de caractères)

### Amélioration du parsing
1. Normalisation des séparateurs
2. Reconnaissance de tous les AI standards
3. Gestion des cas particuliers (décimaux, dates)
4. Support des concaténations d'AI

## 📊 Exemple de flux de traitement

1. Réception de l'image
2. Décodage avec ZXing puis pylibdmtx si nécessaire
3. Normalisation des données brutes
4. Détection du format de code-barres
5. Parsing et extraction des AI
6. Formatage des valeurs selon leur type
7. Construction de la réponse structurée

## 🔧 Tests et validation

Des tests unitaires seront ajoutés pour valider:
- La détection des AI
- Le parsing correct des données
- La gestion des cas particuliers
- La robustesse face aux codes malformés

## 📈 Plan d'évolution

1. Implémentation du support complet des AI
2. Amélioration de la détection des formats
3. Ajout de la génération de codes-barres
4. Interface utilisateur pour l'upload et la visualisation
