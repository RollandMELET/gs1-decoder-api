# PLAN TDD, corrections gs1-decoder-api : GTIN-13 + Digital Link

> Statut : BROUILLON DE CADRAGE v2 (post-passe adversariale, findings vérifiés sur pièces). En attente de validation par Rolland. Aucun code avant accord explicite.
> Rédigé le 2026-07-05. Orchestration multi-agents TDD (orchestrateur Opus).

## 1. Contexte

Service FastAPI de décodage GS1 (`app/main.py`, endpoint `POST /parse/`), déployé sur `gs1-decoder-api.rorworld.eu`. Coeur de parsing unique : `app/gs1_parser.py::parse_gs1`. Consommé par le client TS `@360sc/gs1-client` (repo traca-engine), qui garde des fixtures oracles.

Deux corrections issues du backlog §13 du PLAN traca-engine :
- **(A) GTIN-13 dans le flux de parse** : validation + normalisation vers GTIN-14 des GTIN courts (8/12/13).
- **(B) Parsing Digital Link** : reconnaître une URI GS1 Digital Link (aujourd'hui rejetée en 422, exclue de `is_gs1_data`).

## 2. Décisions Rolland (2026-07-05)

| Sujet | Décision |
|-------|----------|
| Périmètre + ordre | **(A) puis (B)**, chantier complet. (A) fournit le helper de normalisation GTIN réutilisé par (B). |
| Contrat API sortie GTIN | **Champ additif optionnel** `gtin14` sur `ParsedVerboseItem`, non cassant. Synchroniser les fixtures oracles côté traca-engine. |
| Périmètre Digital Link | **Complet** : id.gs1.org ET domaine custom, path AIs numériques, query string, alias courts/longs. |
| Version | Aligner `__version__` (`main.py:3` = 1.3.0) sur le CHANGELOG (2.1.0), bump mineur additif à la livraison. À trancher avant le commit final. |

## 3. Findings de la passe adversariale (VÉRIFIÉS SUR PIÈCES par l'orchestrateur)

Ces constats REDÉFINISSENT le plan. Chacun rejoué à la main, pas cru sur rapport.

- **F1, BUG RÉEL EN PROD : `is_valid_gtin` est FAUX pour GTIN-12 et GTIN-13.** Les branches de parité `len%2` (`gs1_parser.py:320-323`) sont inversées. Rejeu orchestrateur : `4006381333931` (EAN-13 valide) -> False ; `036000291452` (UPC-12 valide) -> False. Certains 13 (`5901234123457`) passent par coïncidence mod-10, pas par justesse. Le service déployé mis-valide donc des GTIN valides. -> **Créer une issue GitHub `fix` sur ce repo** (règle de traçabilité). A1 n'est pas « confirmer », c'est « corriger un bug prouvé ».
- **F2, parenthèses non gérées.** `normalize_gs1_data` (`:38-89`) ne retire pas `()`. Le format lisible `(01)03760423190005` fuite le `)` dans la valeur (`value=')0376042319000'`, un chiffre perdu, `valid=False`). Toutes les fixtures `(nn)...` sont mal parsées pour l'AI 01 aujourd'hui.
- **F3, un strip naïf des `()` est LOSSY.** Retirer `(` et `)` sans réinsérer de GS casse les AIs à longueur variable : `(10)ABC(21)XYZ` -> `10ABC21XYZ` -> BATCH avale tout. Il faut un parcours DÉDIÉ du format parenthésé (AI entre parens, valeur jusqu'à la prochaine `(`).
- **F4, GTIN-8 se pad bien en 14.** Rejeu : `96385074` -> `00000096385074` reste valide. Donc `pad_gtin14 = zfill(14)` UNIFORME pour 8/12/13, PAS de garde spéciale GTIN-8.
- **F5, `normalize_gs1_data` remplace `.` par GS (`:71`).** Une URL DL passée après normalisation devient `https://id\x1dgs1\x1dorg/...`. La détection DL DOIT tourner AVANT `normalize`, sur l'input brut.
- **F6, B6 vise la mauvaise branche.** Pour une vraie URL, `detect_generic_format` renvoie DataMatrix (via `has_datamatrix_characteristics`, `barcode_detector.py:43`, `len>20 and not isalnum`), pas QR. Corriger la branche DataMatrix + rouvrir l'exclusion http de `is_gs1_data` (`:38`) de façon CIBLÉE (seulement pour un DL reconnu, pas toute URL).
- **F7, GATE INOPÉRANTE : venv cassé.** `venv/bin/*` pointe vers un ancien chemin `/Users/rollandmelet/Développement/...` (shebangs morts, `pytest` inexécutable). La GATE SUR PIÈCES (rejeu pytest) est impossible tant que l'env n'est pas reconstruit. **Préalable P0 obligatoire.**
- **F8, baseline non établi.** `test_parse_complete.py` asserte `format=="GS1"` pour `(01)...` alors que `is_gs1_data` renvoie False sur l'entrée parenthésée -> ce test est probablement DÉJÀ rouge, avant tout chantier. Établir la matrice réelle pass/fail sur un env réparé AVANT de parler de non-régression.
- **F9, alias `exp` inventé.** Figer la table d'alias DL sur la liste OFFICIELLE GS1 (gtin=01, cpv=22, lot=10, ser=21, cpid...), vérifier chaque alias, décider la sensibilité à la casse. `exp` n'est pas un short-name officiel.

## 4. Préalables (avant toute tâche A/B)

- **P0, réparer le venv** (recréer : `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt -r requirements-test.txt`). MODIFICATION D'ENVIRONNEMENT -> à TRACER dans `RoR_Install_Maison/logs/journal.md`. Sans ça, aucune gate pytest ne mord.
- **P1, établir le baseline** : `make test-all` (ou pytest ciblé) sur env réparé, capturer la matrice pass/fail RÉELLE. Marquer les tests déjà rouges (dont F8) comme dette préexistante, pas régression du chantier.
- **P2, ouvrir l'issue GitHub `fix`** pour F1 (is_valid_gtin faux), avec repro et leçon.

## 5. Protocole d'orchestration (rappel, non négociable)

- Briefs à périmètre exclusif + chemins absolus. TDD deux temps : RED gaté AVANT GREEN.
- **GATE SUR PIÈCES** : `git status` + rejeu pytest + relecture du diff + mutation qui mord. Jamais sur le rapport de l'agent.
- Fichiers réservés orchestrateur : `models.py` (contrat), `pytest.ini`, `requirements*.txt`, `Makefile`, `CHANGELOG.md`, version.
- **NE PAS TOUCHER** : `app/*_old*.py`, `resources/gs1_parser_utilites.py` (doublon mort). Vrai coeur : `app/gs1_parser.py`.
- Sous-agent d'analyse retourne du texte, n'écrit jamais sur disque. Jamais de commit/push sans accord explicite de Rolland. Français accentué, pas de tirets longs.

## 6. DoD transverse

- `make test-critical` vert + suite ciblée verte, sur venv réparé.
- Couverture `--cov-fail-under=85` (pytest.ini). Le nouveau module DL (`app/gs1_digital_link.py`) est compté dans `--cov=app` : CHAQUE tâche DL livre ses tests d'erreur (URI malformée, alias inconnu, path vide, host+port, slash final, scheme majuscule) sinon la couverture GLOBALE tombe et rougit toute la suite.
- Mutation de gate : chaque GREEN validé par une mutation orchestrateur qui fait rougir au moins un test ciblé.
- Non-régression mesurée CONTRE le baseline P1 (pas contre un état supposé vert).

## 7. Phase A, GTIN-13 (fondation)

| ID | Tâche | Modèle | RED (test d'abord) | GREEN (code) |
|----|-------|--------|--------------------|--------------|
| A1 | **Corriger** `is_valid_gtin` (bug F1) | **sonnet** (« le code est FAUX, corrige-le », pas confirmer) | `tests/unit/test_gtin.py` : `4006381333931` (13, aujourd'hui False->attendu True), `036000291452` (12, False->True), un 12 invalide, un 13 invalide, `96385074` (8), un 14 valide + un 14 invalide. | Réécrire en algo UNIQUE à poids inversés (parcours du corps de droite à gauche, poids 3,1,3,1...), supprimer la branche `len%2` (`:317-323`). |
| A2 | Helpers `pad_gtin14` + `gtin_indicator` | haiku | `96385074 -> 00000096385074` (indicateur 0), 13->14, 12->14, tous restent valides via A1. | `pad_gtin14 = value.zfill(14)` UNIFORME 8/12/13 (pas de garde GTIN-8). `gtin_indicator` = 1er chiffre du 14. |
| A4 | Parcours dédié format parenthésé `(nn)...` | sonnet | `(10)ABC(21)XYZ -> BATCH=ABC, SERIAL=XYZ` (pas ABC21XYZ) ; `(01)03760423190005 -> GTIN 14 chiffres propres`. | Parcours dédié (AI entre parens, valeur jusqu'à la prochaine `(`) en amont, ou extraction propre. NE PAS strip bêtement (F3). Non-régression concaténés. |
| A3 | Brancher normalisation GTIN dans le flux | sonnet | `parse_gs1(verbose=True)` : AI 01 avec GTIN-13 -> `valid=True` + normalisé en 14 ; invalide -> `valid=False`. | Remplacer la garde `len==14` (`:273-277`) par `validate(pad_gtin14(value))` sans exiger 14 a priori. **Après A4** (le format `(01)...` doit déjà donner une value propre). |
| A5 | Champ additif `gtin14` (contrat) | orchestrateur (sonnet) | `ParsedVerboseItem.gtin14` optionnel présent POUR AI 01 uniquement, absent/None sinon. Mode simple (dict) INCHANGÉ. `/decode/` non impacté. Non-régression baseline. | `models.py:15-20` (`Optional[str]=None`), peuplé dans `parse_gs1`. MAJ fixtures oracles `@360sc/gs1-client` (traca-engine) actée séparément. |

Ordre strict : A1 -> A2 -> **A4 -> A3** -> A5.

## 8. Phase B, Digital Link complet (après A close)

| ID | Tâche | Modèle | RED | GREEN |
|----|-------|--------|-----|-------|
| B1 | Parser DL, cas standard | sonnet | `tests/unit/test_digital_link.py` : `parse_digital_link("https://id.gs1.org/01/09521234543213/21/XYZ")` -> AIs `01`, `21` via `AI_TABLE` + tests d'erreur (path vide, segment orphelin). | Nouveau `app/gs1_digital_link.py`, path segments -> AIs, réutilise la table AI. |
| B2 | Domaine custom + query + pourcent-encodage | sonnet | `https://example.com/01/.../10/LOT`, query `?17=261231&10=LOT`, valeurs pourcent-encodées `/10/LOT%2FA` et `?10=LOT%2FA`. | `urllib.parse` + `unquote` sur valeurs path ET query. |
| B3 | Alias courts/longs (liste OFFICIELLE) | sonnet | Alias GS1 vérifiés (gtin, cpv, lot, ser, cpid...) mappés vers AIs ; alias inconnu -> erreur testée ; casse gérée. | Table d'alias figée sur la liste GS1 publiée (retirer `exp` sauf preuve). |
| B4 | GTIN-14 dans DL réutilise A2 | haiku | `/01/<gtin-13>` en DL sort normalisé en 14 comme phase A. | Brancher `pad_gtin14` (A2), pas de duplication. |
| B5 | Détection + routage AVANT `normalize` | sonnet | `parse_gs1(uri_dl)` renvoie les mêmes `ParsedVerboseItem` ; une URL n'est PAS mutilée par le remplacement `.`->GS. | Détection DL sur l'input BRUT, AVANT la ligne d'appel de `normalize_gs1_data` (`:160-172`). Regex SANS backtracking + cap de longueur (DoS). |
| B6 | Détection format GS1 cohérente | sonnet | `is_gs1_data(uri_dl)` -> True CIBLÉ ; `detect_generic_format(uri_dl)` -> format DL, pas DataMatrix ni Code128 ; `POST /parse/` URI DL -> 200 + AIs (au lieu de 422). | Corriger `has_datamatrix_characteristics` (`:43`, intercepte avant QR) ; rouvrir l'exclusion http de `is_gs1_data` (`:38`) SEULEMENT pour un DL reconnu. |

Grammaire DL visée (ambition « complet ») : une primary key (01), qualifiers ordonnés dans le path (22/10/21), data attributes dans la query. À défaut de couvrir toute la grammaire, documenter le parser comme permissif.

Ordre strict B1 -> B6, après A close.

## 9. Points de vigilance

- **Contrat additif** : `gtin14` optionnel = non cassant API, mais fixtures oracles `@360sc/gs1-client` à regénérer et re-valider (action séparée, tracée, hors ce repo).
- **`ParseRequest` sans `verbose`** : le champ envoyé par les tests est ignoré (pas de `extra=forbid`), l'endpoint force `verbose=True`. Ne pas s'appuyer dessus.
- **Test verbose/simple** (`test_parse_complete.py:76-117`) déjà en désaccord avec le code : dette préexistante à trancher (corriger le test ou l'ignorer), pas une régression du chantier.
- **Couverture 85% globale** : le module DL neuf doit livrer ses branches d'erreur, sinon toute la suite rougit.

## 10. Hors périmètre / dormant

- Nettoyage des `_old` + refonte double table AI (dette, backlog).
- Version bump définitif : décision à la livraison, avec Rolland.
- Grammaire DL stricte complète si le parser permissif suffit à l'usage.
