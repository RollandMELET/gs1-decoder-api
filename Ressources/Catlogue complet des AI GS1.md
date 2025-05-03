Absolument ! Voici le catalogue complet des Identifiants d'Application (AI) GS1 au format JSON, basé sur les informations extraites de la source "GS1-General-Specifications R25.pdf" et structuré selon la description fournie dans la source "Catalogue JSON Identifiants Applications GS1".

Chaque objet dans le tableau JSON ci-dessous décrit un Identifiant d'Application GS1 spécifique.

```
[
  {
    "identifiant_ai": "00",
    "designation": "Identification of a logistic unit (SSCC)",
    "format_donnees": "N2+N18",
    "fnc1_requis": false,
    "titre_donnees": "SSCC",
    "description": "Identifie une unité logistique (Serial Shipping Container Code - SSCC). Le SSCC est la seule clé GS1 qui DOIT être utilisée comme identifiant d'une unité logistique. Il assure une identification unique dans le monde entier.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Gestion d'entrepôt",
      "Traçabilité"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "Mandatory data carrier is GS1-128. GS1 DataMatrix or GS1 QR Code MAY be included in addition.",
      "The SSCC is used with EDI communications to enable identification and traceability.",
      "GS1-128 should be used, at a minimum, where the trade item grouping will encounter open supply chains."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "01",
    "designation": "Identification of a trade item (GTIN)",
    "format_donnees": "N2+N14",
    "fnc1_requis": false,
    "titre_donnees": "GTIN",
    "description": "Identifie un article de commerce (Global Trade Item Number - GTIN). C'est une clé d'identification fondamentale utilisée dans le système GS1. Le GTIN est la clé GS1 principale utilisée pour accéder aux standards et services de données B2C de GS1.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Point de vente détail",
      "Distribution générale",
      "Santé réglementée",
      "Commerce électronique"
    ],
    "supports_donnees_autorises": [
      "EAN/UPC",
      "ITF-14",
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "Different formats exist (GTIN-8, GTIN-12, GTIN-13, GTIN-14) depending on the application.",
      "For variable measure items, GTIN with indicator digit 9 is used.",
      "SHALL NOT be used to identify packaging components for production control.",
      "AI (01) SHALL be the first element string encoded when using GS1 DataBar Expanded."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "02",
    "designation": "Identification of trade items contained in a logistic unit",
    "format_donnees": "N2+N14",
    "fnc1_requis": false,
    "titre_donnees": "CONTENT",
    "description": "Identifie les articles de commerce spécifiques (par leur GTIN) contenus dans une unité logistique.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Gestion d'entrepôt"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Its use together with AI (37) and SSCC is common in some sectors."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "03",
    "designation": "Identification of a Made-to-Order (MtO) trade item (GTIN)",
    "format_donnees": "N2+N14",
    "fnc1_requis": false,
    "titre_donnees": "MTO GTIN",
    "description": "Identifie un article de commerce fabriqué sur commande (Made-to-Order - MtO) par son GTIN.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Articles fabriqués sur commande",
      "Production",
      "Logistique"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "10",
    "designation": "Batch or lot number",
    "format_donnees": "N2+X..20 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "BATCH/LOT",
    "description": "Identifie le numéro de lot ou de lot de production. Utilisé pour la traçabilité des produits.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Santé réglementée",
      "Alimentaire",
      "Production"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length."
    ],
    "association_mandatoire": []
  },
   {
    "identifiant_ai": "11",
    "designation": "Production date (YYMMDD)",
    "format_donnees": "N2+N6",
    "fnc1_requis": false,
    "titre_donnees": "PROD DATE",
    "description": "Indique la date de production d'un article au format AAMMJJ (Année Année Mois Mois Jour Jour).",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Gestion des stocks",
      "Traçabilité",
      "Périssables"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "12",
    "designation": "Due date (YYMMDD)",
    "format_donnees": "N2+N6",
    "fnc1_requis": false,
    "titre_donnees": "DUE DATE",
    "description": "Indique une date d'échéance au format AAMMJJ.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Gestion des stocks"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [],
    "association_mandatoire": []
  },
   {
    "identifiant_ai": "13",
    "designation": "Packaging date (YYMMDD)",
    "format_donnees": "N2+N6",
    "fnc1_requis": false,
    "titre_donnees": "PACK DATE",
    "description": "Indique la date d'emballage d'un article au format AAMMJJ.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Gestion des stocks",
      "Traçabilité"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "15",
    "designation": "Best before date (YYMMDD)",
    "format_donnees": "N2+N6",
    "fnc1_requis": false,
    "titre_donnees": "BEST BEFORE or BEST BY",
    "description": "Indique la date de durabilité minimale (à consommer de préférence avant) au format AAMMJJ.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Point de vente détail",
      "Logistique",
      "Gestion des stocks",
      "Périssables"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "If only year and month are available, DD must be filled with two zeroes, except where noted.",
       "HRI may vary (BEST BEFORE or BEST BY)."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "16",
    "designation": "Sell by date (YYMMDD)",
    "format_donnees": "N2+N6",
    "fnc1_requis": false,
    "titre_donnees": "SELL BY",
    "description": "Indique la date limite de vente au format AAMMJJ.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Point de vente détail",
      "Logistique",
      "Gestion des stocks",
      "Périssables"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "If only year and month are available, DD must be filled with two zeroes, except where noted."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "17",
    "designation": "Expiration date (YYMMDD)",
    "format_donnees": "N2+N6",
    "fnc1_requis": false,
    "titre_donnees": "EXPIRY or EXP",
    "description": "Indique la date de péremption (à utiliser avant) au format AAMMJJ. Utilisé couramment dans le secteur de la santé réglementée.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Point de vente détail",
      "Logistique",
      "Gestion des stocks",
      "Santé réglementée",
      "Périssables"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "If only year and month are available, DD must be filled with two zeroes, except where noted.",
       "HRI may vary (EXPIRY or EXP).",
       "Can be used as an optional attribute with GCN (AI 255)."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "20",
    "designation": "Internal product variant",
    "format_donnees": "N2+N..8",
    "fnc1_requis": false,
    "titre_donnees": "VARIANT",
    "description": "Identifie une variante de produit interne qui n'est pertinente que pour le propriétaire de la marque et les tiers agissant en son nom. Diffère de la variante de produit consommateur (AI 22).",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Gestion de production interne",
      "Gestion des stocks interne"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Data field length is up to 8 numeric digits."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "21",
    "designation": "Serial number",
    "format_donnees": "N2+X..20 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "SERIAL or SER",
    "description": "Identifie de manière unique une instance individuelle d'un article de commerce. Utilisé couramment dans le secteur de la santé réglementée.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Santé réglementée",
      "Traçabilité",
      "Fabrication",
      "Logistique"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "HRI may vary (SERIAL or SER)."
    ],
    "association_mandatoire": [
      "AI (01) or GTIN."
    ]
  },
  {
    "identifiant_ai": "22",
    "designation": "Consumer product variant",
    "format_donnees": "N2+X..20 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "CONSUMER VARIANT",
    "description": "Identifie une variante de produit destinée au consommateur. Les données transmises DOIVENT être traitées avec le GTIN de l'article de commerce associé.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Point de vente détail",
      "Gestion des stocks"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Differs from internal product variant (AI 20)."
    ],
    "association_mandatoire": [
       "GTIN."
    ]
  },
  {
    "identifiant_ai": "235",
    "designation": "Third Party Controlled, Serialised Extension of Global TradeItem Number (GTIN) (TPX)",
    "format_donnees": "N3+X..28 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "TPX",
    "description": "Fournit une extension sérialisée du GTIN contrôlée par une tierce partie (TPX). Lié à la traçabilité des produits, notamment du tabac dans le cadre de la réglementation européenne.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Traçabilité du tabac (Réglementation européenne 2018/574)"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Used within the framework of EU Regulation 2018/574."
    ],
    "association_mandatoire": [
       "GTIN."
    ]
  },
  {
    "identifiant_ai": "240",
    "designation": "Additional product identification assigned by the manufacturer",
    "format_donnees": "N3+X..30 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "ADDITIONAL ID",
    "description": "Fournit une identification produit supplémentaire attribuée par le fabricant.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Fabrication",
      "Gestion des stocks"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "241",
    "designation": "Customer part number",
    "format_donnees": "N3+X..30 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "CUSTOMER PART NO.",
    "description": "Identifie le numéro de pièce client.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Relations commerciales B2B",
      "Gestion des stocks"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "242",
    "designation": "Made-to-Order variation number",
    "format_donnees": "N3+N..6",
    "fnc1_requis": false,
    "titre_donnees": "MTO VARIANT",
    "description": "Identifie le numéro de variation pour les articles fabriqués sur commande.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Articles fabriqués sur commande",
      "Production"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
        "Data field length is up to 6 numeric digits.",
       "Used with AI (01) for GTIN-14 (indicator digit 9) when the item is a trade item.",
       "Used with AI (02) and AI (37) in conjunction with SSCC for logistic units of custom trade items."
    ],
    "association_mandatoire": [
        "AI (01) or AI (02) and AI (37) depending on context."
    ]
  },
   {
    "identifiant_ai": "243",
    "designation": "Packaging component number",
    "format_donnees": "N3+X..30 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "PACK COMPONENT NUMBER",
    "description": "Identifie un composant d'emballage.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Production",
      "Emballage"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "250",
    "designation": "Secondary serial number",
    "format_donnees": "N3+X..30 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "SECONDARY SERIAL",
    "description": "Identifie un numéro de série secondaire.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Fabrication",
      "Traçabilité"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "251",
    "designation": "Reference to source entity",
    "format_donnees": "N3+X..30 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "SOURCE ENTITY",
    "description": "Fournit une référence à l'entité source. Les données transmises DOIVENT être traitées avec le GTIN de l'article de commerce associé.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Traçabilité",
      "Fabrication"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length."
    ],
    "association_mandatoire": [
       "GTIN."
    ]
  },
  {
    "identifiant_ai": "253",
    "designation": "Global Document Type Identifier (GDTI)",
    "format_donnees": "N3+N13[+X..17] (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "GDTI",
    "description": "Identifie un type de document global (GDTI). Permet d'identifier de manière unique divers documents tels que les documents de transport, les factures, etc..",
    "cle_gs1_associee": "GDTI",
    "contextes_usage": [
      "Gestion de documents",
      "Logistique",
      "Administratif"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "The serial component (optional part X..17) uses characters from the GS1 AI encodable character set 82."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "254",
    "designation": "Global Location Number (GLN) extension component",
    "format_donnees": "N3+X..20 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "GLN EXTENSION COMPONENT",
    "description": "Fournit un composant d'extension pour un Global Location Number (GLN).",
    "cle_gs1_associee": "GLN",
    "contextes_usage": [
      "Gestion des lieux",
      "Logistique"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "255",
    "designation": "Global Coupon Number (GCN)",
    "format_donnees": "N3+N13[+N..12] (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "GCN",
    "description": "Identifie un numéro de coupon global (GCN). Utilisé pour l'identification unique des coupons physiques ou numériques.",
    "cle_gs1_associee": "GCN",
    "contextes_usage": [
      "Point de vente détail",
      "Promotions",
      "Marketing",
      "Coupons numériques"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Can be supplemented by other AIs like (17), (390N), (394n), (8111).",
       "Data carrier specifications for digital coupons were out of scope when standard was developed; local implementations may use GS1 DataBar.",
       "Serial component is optional."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "30",
    "designation": "Variable count of items",
    "format_donnees": "N2+N..8 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "VAR. COUNT",
    "description": "Indique un nombre variable d'articles.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Gestion des stocks"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "310n",
    "designation": "Net weight, kilograms (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "NET WEIGHT (kg)",
    "description": "Indique le poids net en kilogrammes pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Point de vente détail (produits à poids variable)",
      "Logistique",
      "Alimentaire"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "311n",
    "designation": "Length or first dimension, metres (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "LENGTH (m)",
    "description": "Indique la longueur ou première dimension en mètres pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "312n",
    "designation": "Width, diameter, or second dimension, metres (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "WIDTH (m)",
    "description": "Indique la largeur, le diamètre ou la deuxième dimension en mètres pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "313n",
    "designation": "Depth, thickness, height, or third dimension, metres (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "HEIGHT (m)",
    "description": "Indique la profondeur, l'épaisseur, la hauteur ou la troisième dimension en mètres pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
   {
    "identifiant_ai": "314n",
    "designation": "Area, square metres (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "AREA (m2)",
    "description": "Indique la surface en mètres carrés pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
   {
    "identifiant_ai": "315n",
    "designation": "Volume, cubic metres (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "VOLUME (m3)",
    "description": "Indique le volume en mètres cubes pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
   {
    "identifiant_ai": "316n",
    "designation": "Net volume, litres (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "NET VOLUME (l)",
    "description": "Indique le volume net en litres pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Point de vente détail (produits à poids variable)",
      "Logistique"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "320n",
    "designation": "Net weight, pounds (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "NET WEIGHT (lb)",
    "description": "Indique le poids net en livres pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Point de vente détail (produits à poids variable)",
      "Logistique",
      "Alimentaire"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places.",
      "AI (3202) and AI (3203) can be used in a compressed sequence with AI (01) for weight up to specific limits."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "321n",
    "designation": "Length or first dimension, inches (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "LENGTH (in)",
    "description": "Indique la longueur ou première dimension en pouces pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "322n",
    "designation": "Length or first dimension, feet (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "LENGTH (ft)",
    "description": "Indique la longueur ou première dimension en pieds pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "323n",
    "designation": "Length or first dimension, yards (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "LENGTH (yd)",
    "description": "Indique la longueur ou première dimension en yards pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "324n",
    "designation": "Width, diameter, or second dimension, inches (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "WIDTH (in)",
    "description": "Indique la largeur, le diamètre ou la deuxième dimension en pouces pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "325n",
    "designation": "Width, diameter, or second dimension, feet (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "WIDTH (ft)",
    "description": "Indique la largeur, le diamètre ou la deuxième dimension en pieds pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "326n",
    "designation": "Width, diameter, or second dimension, yards (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "WIDTH (yd)",
    "description": "Indique la largeur, le diamètre ou la deuxième dimension en yards pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "327n",
    "designation": "Depth, thickness, height, or third dimension, inches (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "HEIGHT (in)",
    "description": "Indique la profondeur, l'épaisseur, la hauteur ou la troisième dimension en pouces pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
   {
    "identifiant_ai": "328n",
    "designation": "Depth, thickness, height, or third dimension, feet (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "HEIGHT (ft)",
    "description": "Indique la profondeur, l'épaisseur, la hauteur ou la troisième dimension en pieds pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "329n",
    "designation": "Depth, thickness, height, or third dimension, yards (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "HEIGHT (yd)",
    "description": "Indique la profondeur, l'épaisseur, la hauteur ou la troisième dimension en yards pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "330n",
    "designation": "Net weight, pounds (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "NET WEIGHT (lb), log",
    "description": "Indique le poids net en livres pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "331n",
    "designation": "Length or first dimension, inches (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "LENGTH (in), log",
    "description": "Indique la longueur ou première dimension en pouces pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "332n",
    "designation": "Length or first dimension, feet (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "LENGTH (ft), log",
    "description": "Indique la longueur ou première dimension en pieds pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "333n",
    "designation": "Length or first dimension, yards (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "LENGTH (yd), log",
    "description": "Indique la longueur ou première dimension en yards pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "334n",
    "designation": "Width, diameter, or second dimension, inches (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "WIDTH (in), log",
    "description": "Indique la largeur, le diamètre ou la deuxième dimension en pouces pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "335n",
    "designation": "Width, diameter, or second dimension, feet (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "WIDTH (ft), log",
    "description": "Indique la largeur, le diamètre ou la deuxième dimension en pieds pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "336n",
    "designation": "Width, diameter, or second dimension, yards (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "WIDTH (yd), log",
    "description": "Indique la largeur, le diamètre ou la deuxième dimension en yards pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "337n",
    "designation": "Depth, thickness, height, or third dimension, inches (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "HEIGHT (in), log",
    "description": "Indique la profondeur, l'épaisseur, la hauteur ou la troisième dimension en pouces pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "338n",
    "designation": "Depth, thickness, height, or third dimension, feet (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "HEIGHT (ft), log",
    "description": "Indique la profondeur, l'épaisseur, la hauteur ou la troisième dimension en pieds pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "339n",
    "designation": "Depth, thickness, height, or third dimension, yards (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "HEIGHT (yd), log",
    "description": "Indique la profondeur, l'épaisseur, la hauteur ou la troisième dimension en yards pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "340n",
    "designation": "Net volume, gallons (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "NET VOLUME (gal), log",
    "description": "Indique le volume net en gallons pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "341n",
    "designation": "Net volume, quarts (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "NET VOLUME (qt), log",
    "description": "Indique le volume net en quarts pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "342n",
    "designation": "Net volume, fluid ounces (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "NET VOLUME (floz), log",
    "description": "Indique le volume net en onces liquides pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "343n",
    "designation": "Net weight, kilograms (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "NET WEIGHT (kg), log",
    "description": "Indique le poids net en kilogrammes pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "344n",
    "designation": "Width, diameter, or second dimension, inches (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "WIDTH (in), log",
    "description": "Indique la largeur, le diamètre ou la deuxième dimension en pouces pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "345n",
    "designation": "Width, diameter, or second dimension, feet (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "WIDTH (ft), log",
    "description": "Indique la largeur, le diamètre ou la deuxième dimension en pieds pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "346n",
    "designation": "Width, diameter, or second dimension, yard (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "WIDTH (yd), log",
    "description": "Indique la largeur, le diamètre ou la deuxième dimension en yards pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "347n",
    "designation": "Depth, thickness, height, or third dimension, inches (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "HEIGHT (in), log",
    "description": "Indique la profondeur, l'épaisseur, la hauteur ou la troisième dimension en pouces pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "348n",
    "designation": "Depth, thickness, height, or third dimension, feet (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "HEIGHT (ft), log",
    "description": "Indique la profondeur, l'épaisseur, la hauteur ou la troisième dimension en pieds pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "349n",
    "designation": "Depth, thickness, height, or third dimension, yards (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "HEIGHT (yd), log",
    "description": "Indique la profondeur, l'épaisseur, la hauteur ou la troisième dimension en yards pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
   {
    "identifiant_ai": "350n",
    "designation": "Area, square inches (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "AREA (in2)",
    "description": "Indique la surface en pouces carrés pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "351n",
    "designation": "Area, square feet (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "AREA (ft2)",
    "description": "Indique la surface en pieds carrés pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
   {
    "identifiant_ai": "352n",
    "designation": "Area, square yards (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "AREA (yd2)",
    "description": "Indique la surface en yards carrés pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "353n",
    "designation": "Area, square inches (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "AREA (in2), log",
    "description": "Indique la surface en pouces carrés pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "354n",
    "designation": "Area, square feet (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "AREA (ft2), log",
    "description": "Indique la surface en pieds carrés pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "355n",
    "designation": "Area, square yards (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "AREA (yd2), log",
    "description": "Indique la surface en yards carrés pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "356n",
    "designation": "Net weight, troy ounces (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "NET WEIGHT (troy ounces)",
    "description": "Indique le poids net en onces troy pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Produits précieux",
      "Logistique"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "357n",
    "designation": "Net weight, ounces (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "NET WEIGHT (oz)",
    "description": "Indique le poids net en onces pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Point de vente détail (produits à poids variable)",
      "Logistique"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "360n",
    "designation": "Net volume, quarts (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "NET VOLUME (qt)",
    "description": "Indique le volume net en quarts pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Point de vente détail (produits à poids variable)",
      "Logistique"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "361n",
    "designation": "Net volume, gallons (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "NET VOLUME (gal)",
    "description": "Indique le volume net en gallons pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Point de vente détail (produits à poids variable)",
      "Logistique"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "362n",
    "designation": "Volume, cubic inches (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "VOLUME (in3)",
    "description": "Indique le volume en pouces cubes pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "363n",
    "designation": "Volume, cubic feet (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "VOLUME (ft3)",
    "description": "Indique le volume en pieds cubes pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "364n",
    "designation": "Volume, cubic yards (variable measure trade item)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "VOLUME (yd3)",
    "description": "Indique le volume en yards cubes pour un article de commerce à mesure variable. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "365n",
    "designation": "Volume, cubic inches (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "VOLUME (in3), log",
    "description": "Indique le volume en pouces cubes pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "366n",
    "designation": "Volume, cubic feet (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "VOLUME (ft3), log",
    "description": "Indique le volume en pieds cubes pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "367n",
    "designation": "Volume, cubic yards (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "VOLUME (yd3), log",
    "description": "Indique le volume en yards cubes pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "368n",
    "designation": "Volume, litres (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "VOLUME (l), log",
    "description": "Indique le volume en litres pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "369n",
    "designation": "Volume, cubic metres (logistics unit)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "VOLUME (m3), log",
    "description": "Indique le volume en mètres cubes pour une unité logistique. Le quatrième chiffre de l'AI ('n') indique la position décimale implicite.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Gestion des dimensions"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
      "The fourth digit 'n' specifies the number of decimal places."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "37",
    "designation": "Count of trade items or trade item pieces contained in a logistic unit",
    "format_donnees": "N2+N..8 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "COUNT",
    "description": "Indique le nombre d'articles de commerce ou de pièces d'articles de commerce contenus dans une unité logistique.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Gestion des stocks",
      "Préparation de commandes"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Its use together with AI (02) and SSCC is common in some sectors.",
       "Used with AI (02) and AI (242) in conjunction with SSCC for logistic units of custom trade items."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "400",
    "designation": "Purchase order number",
    "format_donnees": "N3+X..30 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "PO NUMBER",
    "description": "Identifie le numéro du bon de commande.",
    "cle_gs1_associee": null,
    "contextes_usage": [
      "Logistique",
      "Achats",
      "Relations commerciales B2B"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "401",
    "designation": "Global Identification Number for Consignment (GINC)",
    "format_donnees": "N3+X..30 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "GINC",
    "description": "Identifie un numéro d'identification global pour une expédition (Global Identification Number for Consignment - GINC). C'est un numéro unique attribué par un expéditeur pour identifier un groupement logique d'unités logistiques.",
    "cle_gs1_associee": "GINC",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Douane",
      "EDI"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "May be processed as stand-alone information or with other identification data.",
       "Fulfils the requirements of the WCO's UCR."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "402",
    "designation": "Global Shipment Identification Number (GSIN)",
    "format_donnees": "N3+N17",
    "fnc1_requis": false,
    "titre_donnees": "GSIN",
    "description": "Identifie un numéro d'identification global pour une expédition (Global Shipment Identification Number - GSIN). Utilisé dans le transport et la logistique.",
    "cle_gs1_associee": "GSIN",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "EDI"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [],
    "association_mandatoire": []
  },
   {
    "identifiant_ai": "403",
    "designation": "Routing number",
    "format_donnees": "N3+X..30 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "ROUTING NUMBER",
    "description": "Indique le numéro de routage.",
    "cle_gs1_associee": null,
    "contextes_usage": [
      "Logistique",
      "Transport"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "410",
    "designation": "Ship to - Deliver to Global Location Number (GLN)",
    "format_donnees": "N3+N13",
    "fnc1_requis": false,
    "titre_donnees": "SHIP TO LOC",
    "description": "Identifie le lieu de livraison (Global Location Number - GLN).",
    "cle_gs1_associee": "GLN",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Relations commerciales B2B"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "411",
    "designation": "Bill to - Invoice to Global Location Number (GLN)",
    "format_donnees": "N3+N13",
    "fnc1_requis": false,
    "titre_donnees": "BILL TO LOC",
    "description": "Identifie le lieu de facturation (Global Location Number - GLN). Réfère au nom et à l'adresse du partenaire commercial à facturer.",
    "cle_gs1_associee": "GLN",
    "contextes_usage": [
      "Relations commerciales B2B",
      "Facturation",
      "Administratif"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "412",
    "designation": "Purchase from Global Location Number (GLN)",
    "format_donnees": "N3+N13",
    "fnc1_requis": false,
    "titre_donnees": "PURCHASE FROM LOC",
    "description": "Identifie le lieu d'achat (Global Location Number - GLN).",
    "cle_gs1_associee": "GLN",
    "contextes_usage": [
      "Relations commerciales B2B",
      "Achats"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "413",
    "designation": "Ship for - Consignee Global Location Number (GLN)",
    "format_donnees": "N3+N13",
    "fnc1_requis": false,
    "titre_donnees": "SHIP FOR LOC",
    "description": "Identifie le lieu de destination/consignataire (Global Location Number - GLN).",
    "cle_gs1_associee": "GLN",
    "contextes_usage": [
      "Logistique",
      "Transport",
      "Relations commerciales B2B"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "414",
    "designation": "Identification of a physical location - Global Location Number (GLN)",
    "format_donnees": "N3+N13",
    "fnc1_requis": false,
    "titre_donnees": "LOCATION No.",
    "description": "Identifie une localisation physique (Global Location Number - GLN). Le GLN est validé par GS1 dans le cadre de la réglementation européenne sur la traçabilité du tabac.",
    "cle_gs1_associee": "GLN",
    "contextes_usage": [
      "Logistique",
      "Gestion des lieux",
      "Traçabilité du tabac (Réglementation européenne 2018/574)"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Within a GS1 based implementation for Facility ID under EU 2018/574, the ID Issuer UIC, GS1 UIC Extension 1 and Importer index are concatenated before the GLN."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "415",
    "designation": "Invoicing Party Global Location Number (GLN)",
    "format_donnees": "N3+N13",
    "fnc1_requis": false,
    "titre_donnees": "INVOICING PARTY",
    "description": "Identifie la partie qui émet la facture (Global Location Number - GLN).",
    "cle_gs1_associee": "GLN",
    "contextes_usage": [
      "Relations commerciales B2B",
      "Facturation",
      "Administratif"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "420",
    "designation": "Ship to - Deliver to postal code",
    "format_donnees": "N3+X..20 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "SHIP TO POST",
    "description": "Indique le code postal du lieu de livraison.",
    "cle_gs1_associee": "GLN",
    "contextes_usage": [
      "Logistique",
      "Transport"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "421",
    "designation": "Ship to - Deliver to postal code, country (variable measure trade item)",
    "format_donnees": "N3+N3+X..9 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "SHIP TO POST",
    "description": "Indique le code postal et le code pays (ISO 3166 numérique à 3 chiffres) du lieu de livraison.",
    "cle_gs1_associee": "GLN",
    "contextes_usage": [
      "Logistique",
      "Transport international"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Uses 3-digit ISO 3166 country code."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "422",
    "designation": "Country of origin of trade item",
    "format_donnees": "N3+N3",
    "fnc1_requis": false,
    "titre_donnees": "ORIGIN",
    "description": "Indique le pays d'origine de l'article de commerce en utilisant le code pays numérique à 3 chiffres de la norme internationale ISO 3166.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Logistique",
      "Douane",
      "Traçabilité"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Uses 3-digit ISO 3166 country code."
    ],
    "association_mandatoire": []
  },
   {
    "identifiant_ai": "423",
    "designation": "Country of initial processing",
    "format_donnees": "N3+N3+N6 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "INIT. PROCESS",
    "description": "Indique le pays et la date de traitement initial. Utilise le code pays numérique à 3 chiffres de la norme internationale ISO 3166.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Traçabilité",
      "Industrie (ex: produits de la mer)",
      "Logistique"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Uses 3-digit ISO 3166 country code and YYMMDD date format."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "424",
    "designation": "Country of processing",
    "format_donnees": "N3+N3",
    "fnc1_requis": false,
    "titre_donnees": "PROCESS",
    "description": "Indique le pays où le traitement a eu lieu en utilisant le code pays numérique à 3 chiffres de la norme internationale ISO 3166.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Traçabilité",
      "Industrie",
      "Logistique"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Uses 3-digit ISO 3166 country code."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "425",
    "designation": "Country of disassembly",
    "format_donnees": "N3+N3",
    "fnc1_requis": false,
    "titre_donnees": "DISASSEMBLY",
    "description": "Indique le pays où le démontage a eu lieu en utilisant le code pays numérique à 3 chiffres de la norme internationale ISO 3166.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Traçabilité",
      "Gestion des déchets",
      "Recyclage"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Uses 3-digit ISO 3166 country code."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "426",
    "designation": "Country covering full process chain",
    "format_donnees": "N3+N3",
    "fnc1_requis": false,
    "titre_donnees": "FULL PROCESS",
    "description": "Indique le pays où toute la chaîne de traitement de l'article de commerce a eu lieu en utilisant le code pays numérique à 3 chiffres de la norme internationale ISO 3166. Ne doit être utilisé que si le traitement complet a eu lieu dans un seul pays.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Traçabilité",
      "Logistique",
      "Production"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Uses 3-digit ISO 3166 country code.",
       "Must only be used if the full processing took place in a single country."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7001",
    "designation": "Catch area (fisheries)",
    "format_donnees": "N4+N..6 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "CATCH AREA",
    "description": "Indique la zone de capture (pour les produits de la pêche).",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Industrie de la pêche",
      "Traçabilité alimentaire"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Data field length is up to 6 numeric digits."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7002",
    "designation": "Start of catch date (YYMMDD) (fisheries)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "CATCH DATE START",
    "description": "Indique la date de début de capture (pour les produits de la pêche) au format AAMMJJ.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Industrie de la pêche",
      "Traçabilité alimentaire"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7003",
    "designation": "End of catch date (YYMMDD) (fisheries)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "CATCH DATE END",
    "description": "Indique la date de fin de capture (pour les produits de la pêche) au format AAMMJJ.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Industrie de la pêche",
      "Traçabilité alimentaire"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7004",
    "designation": "Active potency (healthcare trade item)",
    "format_donnees": "N4+N..4 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "ACTIVE POTENCY",
    "description": "Indique la puissance active pour certains produits de santé (par exemple, produits d'hémophilie). La puissance peut varier selon le lot.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Santé réglementée",
      "Pharmacie",
      "Traçabilité"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Measured in International Units (IUs).",
       "HRI is not required on the item."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7005",
    "designation": "Catch subdivision (fisheries)",
    "format_donnees": "N4+X..10 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "CATCH SUBDIV",
    "description": "Indique la subdivision de capture (pour les produits de la pêche).",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Industrie de la pêche",
      "Traçabilité alimentaire"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7006",
    "designation": "First freezing date (YYMMDD) (fisheries)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "FRZ DATE",
    "description": "Indique la première date de congélation (pour les produits de la pêche) au format AAMMJJ.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Industrie de la pêche",
      "Traçabilité alimentaire"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7007",
    "designation": "First sales date (YYMMDD) (fisheries)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "SELL DATE",
    "description": "Indique la première date de vente (pour les produits de la pêche) au format AAMMJJ.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Industrie de la pêche",
      "Traçabilité alimentaire"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7008",
    "designation": "Catching vessel identification (fisheries)",
    "format_donnees": "N4+X..10 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "CATCH VESSEL",
    "description": "Identifie le navire de pêche (pour les produits de la pêche).",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Industrie de la pêche",
      "Traçabilité alimentaire"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7009",
    "designation": "Fishing gear type (fisheries)",
    "format_donnees": "N4+X..10 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "FISHING GEAR",
    "description": "Indique le type d'engin de pêche (pour les produits de la pêche). Lié à la traçabilité alimentaire.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Industrie de la pêche",
      "Traçabilité alimentaire"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Uses UN/CEFACT codes; GS1 maintains a list."
    ],
    "association_mandatoire": [
       "Must be processed together with the GTIN."
    ]
  },
   {
    "identifiant_ai": "7010",
    "designation": "Production method",
    "format_donnees": "N4+X..2 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "PROD METHOD",
    "description": "Indique la méthode de production.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Production",
      "Traçabilité"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7011",
    "designation": "Test by date (YYMMDD)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "TEST BY DATE",
    "description": "Indique la date limite de test au format AAMMJJ.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Contrôle qualité",
      "Logistique",
      "Périssables"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7020",
    "designation": "Refurbishment lot ID",
    "format_donnees": "N4+X..20 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "REFURB LOT",
    "description": "Identifie le numéro de lot de remise à neuf.",
    "cle_gs1_associee": "GIAI",
    "contextes_usage": [
      "Gestion d'actifs",
      "Maintenance",
      "Remise à neuf"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length."
    ],
    "association_mandatoire": []
  },
   {
    "identifiant_ai": "7021",
    "designation": "Functional status",
    "format_donnees": "N4+X..20 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "FUNC STATUS",
    "description": "Indique le statut fonctionnel de l'article de commerce. Peut être requis par la réglementation ou des exigences commerciales.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Santé réglementée",
      "Qualité",
      "Production"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7022",
    "designation": "Revision status",
    "format_donnees": "N4+X..20 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "REV STATUS",
    "description": "Indique le statut de révision.",
    "cle_gs1_associee": "GIAI",
    "contextes_usage": [
      "Gestion d'actifs",
      "Maintenance",
      "Production"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7023",
    "designation": "Global Individual Asset Identifier of an assembly",
    "format_donnees": "N4+X..30 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "ASSY GIAI",
    "description": "Identifie le Global Individual Asset Identifier (GIAI) d'un assemblage ou d'un composant composite. Peut être marqué sur une partie de l'assemblage s'il n'y a pas d'espace dédié sur l'assemblage lui-même.",
    "cle_gs1_associee": "GIAI",
    "contextes_usage": [
      "Gestion d'actifs",
      "Fabrication",
      "Maintenance"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "SHALL be used to indicate the GIAI of the assembly when marked on a component."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "703s",
    "designation": "Number of processor with three-digit ISO country code",
    "format_donnees": "N4+N3+X..27 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "PROCESSOR NO.",
    "description": "Indique le numéro de processeur avec un code pays ISO à trois chiffres. Permet d'identifier une partie relative à son rôle dans un processus commercial.",
    "cle_gs1_associee": "GLN",
    "contextes_usage": [
      "Traitement",
      "Traçabilité"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Uses 3-digit ISO 3166 country code, where 's' is the country code."
    ],
    "association_mandatoire": []
  },
   {
    "identifiant_ai": "7040",
    "designation": "GS1 UIC with Extension 1 and Importer index",
    "format_donnees": "N4+X..30 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "GS1 UIC EXT.",
    "description": "Indique le Code d'Identification Unique (UIC) d'un émetteur d'ID selon la réglementation européenne 2018/574, son Extension 1 et l'index de l'importateur, si applicable. Autorisé pour l'identification de l'autorisation au niveau national des clés GS1 dans les systèmes de surveillance du commerce illicite, dans le cadre de la traçabilité des produits du tabac.",
    "cle_gs1_associee": null,
    "contextes_usage": [
      "Traçabilité du tabac (Réglementation européenne 2018/574)"
    ],
    "supports_donnees_autorises": [
      "GS1 DataMatrix",
      "GS1 QR Code"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Limited to application standard 2.1.14 (traceability of tobacco products).",
       "SHALL be used solely exclusively to facilitate identification of country level authorisation for GS1 identification keys within illicit trade surveillance systems.",
       "SHALL NOT be used with GS1 identification keys for open, supply chain systems.",
       "Required attribute for Machine Identification per EU 2018/574."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7041",
    "designation": "UN/CEFACT freight unit type",
    "format_donnees": "N4+X..4 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "FREIGHT TYPE",
    "description": "Indique le type d'unité de fret selon les codes alphanumériques UN/CEFACT. GS1 maintient une liste basée sur la Recommandation 21 de l'UN/ECE.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Transport"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Uses UN/CEFACT codes."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "710-716",
    "designation": "National Healthcare Reimbursement Number (NHRN)",
    "format_donnees": "N3+X..20 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "NHRN",
    "description": "Identifie un numéro de remboursement national de santé (NHRN). Plusieurs AIs sont dédiés à cet usage. Ils doivent être traités avec le GTIN.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Santé réglementée",
      "Pharmacie",
      "Remboursement"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Specific sections describe the structure and rules of use."
    ],
    "association_mandatoire": [
       "GTIN."
    ]
  },
  {
    "identifiant_ai": "723s",
    "designation": "Certification reference",
    "format_donnees": "N4+X..30 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "CERT. REFERENCE",
    "description": "Indique une référence de certification, par exemple pour la Marine Equipment Directive européenne. L'AI inclut le schéma de certification (2 caractères) et la référence de certification (28 caractères).",
    "cle_gs1_associee": "GTIN / GIAI",
    "contextes_usage": [
      "Certification",
      "Industrie maritime"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "'s' indicates the certification scheme.",
       "Must be processed together with the GTIN of the trade item or the GIAI of the asset."
    ],
    "association_mandatoire": [
       "GTIN or GIAI."
    ]
  },
  {
    "identifiant_ai": "7240",
    "designation": "Protocol ID",
    "format_donnees": "N4+X..20 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "PROTOCOL ID",
    "description": "Identifie un ID de protocole.",
    "cle_gs1_associee": null,
    "contextes_usage": [
      "Systèmes informatiques",
      "Communication de données"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7241",
    "designation": "AIDC media type",
    "format_donnees": "N4+N..4 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "AIDC MEDIA TYPE",
    "description": "Indique le type de support d'identification automatique et de capture de données (AIDC media type). Peut être utilisé comme attribut optionnel avec GSRN (AI 8017, 8018).",
    "cle_gs1_associee": "GSRN",
    "contextes_usage": [
      "AIDC",
      "Gestion des identifiants"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Data field length is up to 4 numeric digits."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7242",
    "designation": "Version Control Number (VCN)",
    "format_donnees": "N4+N..4 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "VCN",
    "description": "Indique le numéro de contrôle de version (VCN). Peut être utilisé comme attribut optionnel avec GSRN (AI 8017, 8018).",
    "cle_gs1_associee": "GSRN",
    "contextes_usage": [
      "Gestion de versions",
      "Gestion des identifiants"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Data field length is up to 4 numeric digits."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7250",
    "designation": "Date of birth (YYMMDD)",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "DOB",
    "description": "Indique la date de naissance au format AAMMJJ. Utilisé pour les données démographiques du patient dans les codes-barres GS1 pour les dossiers de santé électroniques.",
    "cle_gs1_associee": null,
    "contextes_usage": [
      "Santé",
      "Identification de personne"
    ],
    "supports_donnees_autorises": [
      "GS1 DataMatrix",
      "GS1 QR Code"
    ],
    "regles_et_contraintes": [],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7251",
    "designation": "Date and time of birth (YYMMDDHHMM)",
    "format_donnees": "N4+N10",
    "fnc1_requis": false,
    "titre_donnees": "DOB AND TIME",
    "description": "Indique la date et l'heure de naissance au format AAMMJJHHMM (Année Année Mois Mois Jour Jour Heure Heure Minute Minute). Utilisé pour les données démographiques du patient.",
    "cle_gs1_associee": null,
    "contextes_usage": [
      "Santé",
      "Identification de personne"
    ],
    "supports_donnees_autorises": [
      "GS1 DataMatrix",
      "GS1 QR Code"
    ],
    "regles_et_contraintes": [],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7252",
    "designation": "Biological sex",
    "format_donnees": "N4+N..1 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "SEX",
    "description": "Indique le sexe biologique. Utilisé pour les données démographiques du patient.",
    "cle_gs1_associee": null,
    "contextes_usage": [
      "Santé",
      "Identification de personne"
    ],
    "supports_donnees_autorises": [
      "GS1 DataMatrix",
      "GS1 QR Code"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Data field length is up to 1 numeric digit."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7253",
    "designation": "Family name of person",
    "format_donnees": "N4+X..35 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "FAMILY NAME",
    "description": "Indique le nom de famille de la personne. Utilisé pour les données démographiques du patient.",
    "cle_gs1_associee": null,
    "contextes_usage": [
      "Santé",
      "Identification de personne"
    ],
    "supports_donnees_autorises": [
      "GS1 DataMatrix",
      "GS1 QR Code"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Uses characters from the GS1 AI encodable character set 82."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7254",
    "designation": "Given name of person",
    "format_donnees": "N4+X..35 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "GIVEN NAME",
    "description": "Indique le prénom de la personne. Utilisé pour les données démographiques du patient.",
    "cle_gs1_associee": null,
    "contextes_usage": [
      "Santé",
      "Identification de personne"
    ],
    "supports_donnees_autorises": [
      "GS1 DataMatrix",
      "GS1 QR Code"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Uses characters from the GS1 AI encodable character set 82."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7255",
    "designation": "Name suffix of person",
    "format_donnees": "N4+X..8 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "NAME SUFFIX",
    "description": "Indique le suffixe du nom de la personne (par exemple, Jr., Sr., III). Utilisé pour les données démographiques du patient.",
    "cle_gs1_associee": null,
    "contextes_usage": [
      "Santé",
      "Identification de personne"
    ],
    "supports_donnees_autorises": [
      "GS1 DataMatrix",
      "GS1 QR Code"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Uses characters from the GS1 AI encodable character set 82.",
       "Data field length is up to 8 characters."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7256",
    "designation": "Full name of person",
    "format_donnees": "N4+X..70 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "FULL NAME",
    "description": "Indique le nom complet de la personne. Utilisé pour les données démographiques du patient.",
    "cle_gs1_associee": null,
    "contextes_usage": [
      "Santé",
      "Identification de personne"
    ],
    "supports_donnees_autorises": [
      "GS1 DataMatrix",
      "GS1 QR Code"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Uses characters from the GS1 AI encodable character set 82."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7257",
    "designation": "Address of person",
    "format_donnees": "N4+X..70 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "ADDRESS",
    "description": "Indique l'adresse de la personne. Utilisé pour les données démographiques du patient.",
    "cle_gs1_associee": null,
    "contextes_usage": [
      "Santé",
      "Identification de personne"
    ],
    "supports_donnees_autorises": [
      "GS1 DataMatrix",
      "GS1 QR Code"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Uses characters from the GS1 AI encodable character set 82."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7258",
    "designation": "Baby birth sequence indicator",
    "format_donnees": "N4+X..1 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "BABY SEQUENCE",
    "description": "Indique l'indicateur de séquence de naissance du bébé (par exemple, pour les naissances multiples). Utilisé pour les données démographiques du patient.",
    "cle_gs1_associee": null,
    "contextes_usage": [
      "Santé",
      "Identification de personne (nouveau-nés)"
    ],
    "supports_donnees_autorises": [
      "GS1 DataMatrix",
      "GS1 QR Code"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Uses characters from the GS1 AI encodable character set 82.",
       "Data field length is up to 1 character."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "7259",
    "designation": "Baby of family name",
    "format_donnees": "N4+X..35 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "BABY FAMILY NAME",
    "description": "Indique le nom de famille du bébé. Utilisé pour les données démographiques du patient.",
    "cle_gs1_associee": null,
    "contextes_usage": [
      "Santé",
      "Identification de personne (nouveau-nés)"
    ],
    "supports_donnees_autorises": [
      "GS1 DataMatrix",
      "GS1 QR Code"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Uses characters from the GS1 AI encodable character set 82."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "8001",
    "designation": "Roll products - width, length, core diameter, direction, splices",
    "format_donnees": "N4+N14+N..[..] (FNC1) for variable data field length",
    "fnc1_requis": true,
    "titre_donnees": "ROLL PROD",
    "description": "Fournit des informations sur les produits en rouleau : largeur, longueur, diamètre du noyau, direction et épissures.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Industrie (ex: papier, film)",
      "Logistique"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Format includes a fixed part (N14) and a variable part."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "8002",
    "designation": "Cellular mobile telephone identifier",
    "format_donnees": "N4+X..20 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "CMT No.",
    "description": "Identifie un téléphone mobile cellulaire (par exemple, IMEI). Ces données sont normalement traitées comme des informations autonomes.",
    "cle_gs1_associee": null,
    "contextes_usage": [
      "Télécommunications",
      "Logistique",
      "Gestion d'actifs"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Uses characters from the GS1 AI encodable character set 82."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "8003",
    "designation": "Global Returnable Asset Identifier (GRAI)",
    "format_donnees": "N4+N14[+X..16] (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "GRAI",
    "description": "Identifie un actif réutilisable ou équipement de transport (par exemple, fût de bière, palette plastique). Le GRAI permet le suivi et l'enregistrement des données pertinentes. Il est composé du préfixe d'entreprise GS1 et du type d'actif, avec un composant sériel optionnel.",
    "cle_gs1_associee": "GRAI",
    "contextes_usage": [
      "Gestion d'actifs retournables",
      "Logistique (conteneurs, palettes, etc.)",
      "Santé (micro-logistique des dispositifs médicaux)"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Serial component is optional.",
       "MUST NEVER be used to identify the transported or contained trade item."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "8004",
    "designation": "Global Individual Asset Identifier (GIAI)",
    "format_donnees": "N4+X..30 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "GIAI",
    "description": "Identifie un actif individuel (par exemple, équipement médical, machine). Utilisé dans le cadre de la réglementation européenne sur la traçabilité du tabac pour identifier les machines.",
    "cle_gs1_associee": "GIAI",
    "contextes_usage": [
      "Gestion d'actifs individuels",
      "Santé (micro-logistique des dispositifs médicaux)",
      "Traçabilité du tabac (Réglementation européenne 2018/574)"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Within a GS1 based implementation for Machine ID under EU 2018/574, the ID Issuer UIC, GS1 UIC Extension 1 and Importer index are concatenated before the GIAI."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "8005",
    "designation": "Price per unit of measure",
    "format_donnees": "N4+N6",
    "fnc1_requis": false,
    "titre_donnees": "PRICE PER UNIT",
    "description": "Indique le prix par unité de mesure.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Point de vente détail (produits à poids/mesure variable)",
      "Facturation"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [],
    "association_mandatoire": []
  },
   {
    "identifiant_ai": "8006",
    "designation": "Identification of an individual trade item piece (ITIP)",
    "format_donnees": "N4+N14+N..18 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "ITIP",
    "description": "Identifie une pièce individuelle d'un article de commerce (Item of a Trade Item Piece - ITIP). Utilisé lorsque l'article de commerce est composé de plusieurs parties physiques.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Fabrication",
      "Logistique (pour les articles multi-pièces)",
      "Gestion des stocks"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Carrier choices for marking using AI (8006) are GS1-128, GS1 DataMatrix, GS1 QR Code and EPC/RFID.",
       "Format includes a fixed part (N14) and a variable part up to 18 numeric digits."
    ],
    "association_mandatoire": []
  },
   {
    "identifiant_ai": "8007",
    "designation": "International Bank Account Number (IBAN)",
    "format_donnees": "N4+X..34 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "IBAN",
    "description": "Indique un numéro de compte bancaire international (IBAN).",
    "cle_gs1_associee": null,
    "contextes_usage": [
      "Finance",
      "Facturation",
      "Paiements"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Uses characters from the GS1 AI encodable character set 82."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "8008",
    "designation": "Date and time of production (YYMMDDHHMM)",
    "format_donnees": "N4+N12 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "PROD DATE/TIME",
    "description": "Indique la date et l'heure de production au format AAMMJJHHMM (Année Année Mois Mois Jour Jour Heure Heure Minute Minute).",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Production",
      "Traçabilité",
      "Logistique"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "8009",
    "designation": "Optically readable sensor indicator",
    "format_donnees": "N4+X..50 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "SENSOR INDICATOR",
    "description": "Indique les paramètres d'instruction d'un capteur lisible optiquement définis par AIM. Les données transmises DOIVENT être traitées avec le GTIN de l'article de commerce ou le SSCC de l'unité logistique associé.",
    "cle_gs1_associee": "GTIN / SSCC",
    "contextes_usage": [
      "Capteurs",
      "Surveillance de l'état",
      "Logistique",
      "Gestion d'actifs"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Uses characters from the GS1 AI encodable character set 82.",
       "Intended to be carrier agnostic, but payload limitations apply (e.g., GS1-128 max 48 characters)."
    ],
    "association_mandatoire": [
       "GTIN or SSCC."
    ]
  },
  {
    "identifiant_ai": "8010",
    "designation": "Component/Part Identifier (CPID)",
    "format_donnees": "N4+X..30 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "CPID",
    "description": "Identifie un composant ou une pièce (CPID). Classifié comme une 'clé GS1', mais NE DOIT PAS être utilisé dans les chaînes d'approvisionnement ouvertes.",
    "cle_gs1_associee": "CPID",
    "contextes_usage": [
      "Fabrication (gestion des composants)",
      "Gestion des stocks interne"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Uses characters from the GS1 AI encodable character set 39.",
       "Must NOT be used in open supply chains."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "8011",
    "designation": "Component/Part Identifier serial number",
    "format_donnees": "N4+N..12 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "CPID SERIAL",
    "description": "Fournit un numéro de série optionnel pour le Component/Part Identifier (AI 8010). Le format est numérique uniquement, maximum 12 chiffres.",
    "cle_gs1_associee": "CPID",
    "contextes_usage": [
      "Fabrication (gestion des composants)",
      "Gestion des stocks interne"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Data field length is up to 12 numeric digits."
    ],
    "association_mandatoire": [
       "AI (8010) Component/Part Identifier."
    ]
  },
  {
    "identifiant_ai": "8012",
    "designation": "Software version",
    "format_donnees": "N4+X..20 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "SW VERSION",
    "description": "Indique la version du logiciel.",
    "cle_gs1_associee": null,
    "contextes_usage": [
      "Gestion des actifs",
      "Logiciels",
      "Maintenance"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Uses characters from the GS1 AI encodable character set 82."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "8013",
    "designation": "Global Model Number (GMN)",
    "format_donnees": "N4+X..30 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "GMN",
    "description": "Identifie un numéro de modèle global (GMN) pour un modèle de produit (par exemple, famille de dispositifs médicaux, modèle d'électronique grand public). Le GMN est la base à partir de laquelle les articles de commerce associés sont dérivés. Le GMN comprend le préfixe d'entreprise GS1, une référence de modèle et une paire de caractères de contrôle.",
    "cle_gs1_associee": "GMN",
    "contextes_usage": [
      "Santé réglementée (dispositifs médicaux)",
      "Électronique grand public",
      "Habillement",
      "Gestion de modèles"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Uses characters from the GS1 AI encodable character set 82.",
       "SHALL NOT be used to identify the entity as a trade item.",
       "GTIN MUST NOT replace GMN, and GMN MUST NOT replace GTIN."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "8014",
    "designation": "Highly Individualised Device Registration Identifier (HIDRI)",
    "format_donnees": "N4+X..30 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "HIDRI",
    "description": "Identifie un identifiant d'enregistrement de dispositif hautement individualisé (HIDRI).",
    "cle_gs1_associee": null,
    "contextes_usage": [
      "Santé réglementée",
      "Dispositifs médicaux"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Uses characters from the GS1 AI encodable character set 82."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "8017",
    "designation": "Global Service Relation Number – Provider",
    "format_donnees": "N4+N18",
    "fnc1_requis": false,
    "titre_donnees": "GSRN - PROVIDER",
    "description": "Représente le Global Service Relation Number (GSRN) d'une relation entre l'organisation offrant le service et le prestataire du service. Utilisé par exemple dans le secteur de la santé pour identifier un prestataire médical par rôle.",
    "cle_gs1_associee": "GSRN",
    "contextes_usage": [
      "Santé",
      "Services",
      "Identification de personne/rôle"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar Expanded",
      "GS1 DataBar Expanded Stacked",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code"
    ],
    "regles_et_contraintes": [
       "Can be supplemented by AI (8019), (7241), (7242), (8030)."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "8018",
    "designation": "Global Service Relation Number – Recipient",
    "format_donnees": "N4+N18",
    "fnc1_requis": false,
    "titre_donnees": "GSRN - RECIPIENT",
    "description": "Représente le Global Service Relation Number (GSRN) d'une relation entre l'organisation offrant le service et le bénéficiaire du service.",
    "cle_gs1_associee": "GSRN",
    "contextes_usage": [
      "Santé",
      "Services",
      "Identification de personne"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar Expanded",
      "GS1 DataBar Expanded Stacked",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code"
    ],
    "regles_et_contraintes": [
       "Can be supplemented by AI (8019), (7241), (7242), (8030)."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "8019",
    "designation": "Service Relation Instance Number (SRIN)",
    "format_donnees": "N4+N..10 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "SRIN",
    "description": "Fournit un indicateur de séquence (Service Relation Instance Number - SRIN) pour rendre l'identification du prestataire ou du bénéficiaire de service (GSRN) plus granulaire, correspondant à chaque rencontre pendant la relation de service.",
    "cle_gs1_associee": "GSRN",
    "contextes_usage": [
      "Santé",
      "Services",
      "Traçabilité des interactions"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Data field length is up to 10 numeric digits.",
       "Optional attribute for AI (8017) and AI (8018)."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "8020",
    "designation": "Payment slip reference number",
    "format_donnees": "N4+X..25 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "PAYMENT REF.",
    "description": "Indique un numéro de référence de bulletin de paiement.",
    "cle_gs1_associee": null,
    "contextes_usage": [
      "Finance",
      "Paiements",
      "Facturation"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Uses characters from the GS1 AI encodable character set 82."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "8026",
    "designation": "Identification of pieces of a trade item (ITIP) contained in a logistic unit",
    "format_donnees": "N4+N18",
    "fnc1_requis": false,
    "titre_donnees": "ITIP CONTENT",
    "description": "Identifie les pièces individuelles d'un article de commerce (ITIP, AI 8006) contenues dans une unité logistique.",
    "cle_gs1_associee": "SSCC",
    "contextes_usage": [
      "Logistique",
      "Gestion des stocks",
      "Articles multi-pièces"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "SHALL be used only on a logistic unit if it is not a trade item itself AND all contained pieces have the same ITIP.",
       "Must be processed together with the count of items which must appear on the same unit."
    ],
    "association_mandatoire": [
       "AI (37) Count of trade items."
    ]
  },
  {
    "identifiant_ai": "8030",
    "designation": "Digital Signature (DigSig)",
    "format_donnees": "N4+Z..variable",
    "fnc1_requis": false,
    "titre_donnees": "DIGSIG",
    "description": "Représente une signature numérique (DigSig) pour les données. Un condensé de données qui permet la détection d'altération et la non-répudiation. Les spécifications pour les supports de données sont établies dans les normes d'application pour les clés d'identification GS1.",
    "cle_gs1_associee": null,
    "contextes_usage": [
      "Authentification",
      "Sécurité des données",
      "Traçabilité"
    ],
    "supports_donnees_autorises": [
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DotCode",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Uses characters from the GS1 AI encodable character set 64 (file-safe / URI-safe base64).",
       "Instance level identification is required in addition to AI (8030).",
       "Can be used as an optional attribute with GSRN (AI 8017, 8018)."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "8110",
    "designation": "Coupon code identification for use in North America",
    "format_donnees": "N4+N..30 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "GCN - NORTH AMERICA",
    "description": "Identifie un code de coupon pour une utilisation en Amérique du Nord, traditionnellement utilisé pour les coupons papier scannés au point de vente. Les données sont utilisées pour transmettre l'exigence d'achat et la valeur de l'économie pour traitement.",
    "cle_gs1_associee": "GCN",
    "contextes_usage": [
      "Point de vente détail (Amérique du Nord)",
      "Promotions",
      "Coupons papier"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Cannot reliably validate a specific list of GTINs or ensure serialised coupons are not used more than once across retailers.",
       "Refer to GS1 US for detailed guidelines."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "8111",
    "designation": "Loyalty points of a coupon",
    "format_donnees": "N4+N..4",
    "fnc1_requis": false,
    "titre_donnees": "POINTS",
    "description": "Indique les points de fidélité associés à un coupon. Peut être utilisé comme attribut optionnel avec GCN (AI 255).",
    "cle_gs1_associee": "GCN",
    "contextes_usage": [
      "Point de vente détail",
      "Promotions",
      "Programmes de fidélité"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Data field length is up to 4 numeric digits."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "8112",
    "designation": "Positive offer file coupon code identification for use in North America",
    "format_donnees": "N4+X..70 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "-",
    "description": "Identifie un code de coupon pour une utilisation en Amérique du Nord qui déclenche une requête vers un fichier d'offres positif externe. Utilisé pour valider l'offre et l'expirer afin d'empêcher une utilisation répétée. Peut être utilisé avec des offres sans papier ou papier.",
    "cle_gs1_associee": "GCN",
    "contextes_usage": [
      "Point de vente détail (Amérique du Nord)",
      "Promotions",
      "Coupons numériques",
      "Coupons papier"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar",
      "GS1 DataMatrix",
      "GS1 QR Code"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Prompts POS systems to call out to an external positive offer file.",
       "Data field length is up to 70 characters.",
       "Refer to GS1 US for detailed guidelines."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "8200",
    "designation": "Extended packaging URL",
    "format_donnees": "N4+X..70 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "PRODUCT URL",
    "description": "Identifie une URL autorisée par le propriétaire de la marque, à utiliser en association avec un GTIN pour fournir des informations ou des applications étendues via l'emballage. Cette approche peut être utilisée pour atteindre des informations autorisées par le propriétaire de la marque via un mode direct. Pour les nouvelles applications, l'approche GS1 Digital Link URI est utilisée.",
    "cle_gs1_associee": "GTIN",
    "contextes_usage": [
      "Emballage étendu (QR Code augmenté)",
      "Point de vente détail",
      "Engagement consommateur",
      "Commerce électronique"
    ],
    "supports_donnees_autorises": [
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1-128"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Data field length is up to 70 characters.",
       "Implementation has been limited globally by the need for an app to construct the URL.",
       "For healthcare applications, AI (8200) will be deprecated on 31 December 2026; healthcare applications SHALL NOT utilise AI (8200) after this date."
    ],
    "association_mandatoire": [
      "AI (01) or GTIN."
    ]
  },
  {
    "identifiant_ai": "90",
    "designation": "Information mutually agreed between trading partners",
    "format_donnees": "N2+X..30 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "INTERNAL",
    "description": "Contient toute information convenue mutuellement entre les partenaires commerciaux. Le champ de données est alphanumérique et peut contenir les caractères définis dans l'ensemble de caractères 82. Peut également être utilisé pour incorporer des données précédées des identifiants de données ASC MH10.",
    "cle_gs1_associee": null,
    "contextes_usage": [
      "Relations commerciales B2B (accords spécifiques)",
      "Applications internes"
    ],
    "supports_donnees_autorises": [
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "GS1 DataBar",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Uses characters from the GS1 AI encodable character set 82."
    ],
    "association_mandatoire": []
  },
  {
    "identifiant_ai": "91-99",
    "designation": "Company internal information",
    "format_donnees": "N2+X..90 (FNC1)",
    "fnc1_requis": true,
    "titre_donnees": "INTERNAL",
    "description": "Ces Identifiants d'Application sont réservés à l'usage interne de l'entreprise. Ils peuvent contenir des informations internes définies par l'entreprise.",
    "cle_gs1_associee": null,
    "contextes_usage": [
      "Applications internes (gestion des processus, traçabilité interne, etc.)"
    ],
    "supports_donnees_autorises": [
      "GS1 DataBar Expanded Versions",
      "GS1-128",
      "GS1 DataMatrix",
      "GS1 QR Code",
      "EPC/RFID"
    ],
    "regles_et_contraintes": [
       "Requires FNC1 separator if not the last element and data is variable length.",
       "Uses characters from the GS1 AI encodable character set 82.",
       "Data carrier specifications are to be determined internally."
    ],
    "association_mandatoire": []
  }
]
```

**Explication de la Structure JSON :**

Chaque objet JSON dans le tableau représente un AI GS1. Les champs clés sont les suivants, conformes à la description détaillée fournie dans la source "Catalogue JSON Identifiants Applications GS1" :

1. **`identifiant_ai`** : Le code numérique de l'AI, sous forme de chaîne de caractères (par exemple, "00", "10", "8200"). La longueur peut être de 2, 3 ou 4 chiffres. Des plages comme "91-99" sont également incluses si elles sont définies comme un groupe dans les sources.
2. **`designation`** : Le nom officiel de l'AI selon les standards GS1 (par exemple, "Identification of a logistic unit (SSCC)"). Il décrit le type d'information identifié.
3. **`format_donnees`** : Indique le format et la longueur des données associées à cet AI, en utilisant des conventions telles que N (numérique), X (alphanumérique de l'ensemble 82 de GS1), .. (longueur variable), n (position décimale implicite) et (FNC1) (séparateur FNC1 requis).
4. **`fnc1_requis`** : Un booléen (`true` ou `false`) indiquant si un caractère FNC1 est obligatoire après les données de cet AI si la longueur est variable ET qu'il n'est PAS le dernier AI encodé. Le FNC1 sert également de caractère de début dans certains symboles 2D GS1.
5. **`titre_donnees`** : Le titre court ou l'abréviation utilisé pour l'interprétation lisible par l'homme (HRI - Human Readable Interpretation) sous le symbole. Les parenthèses autour de l'AI ne font pas partie des données encodées ou du titre.
6. **`description`** : Une description plus complète de la signification et de l'utilisation de l'AI, incluant des détails sur le type d'information, l'entité qui l'attribue et son rôle. Ces informations proviennent des sections 2 et 3 de la source "GS1 General Specifications Standard".
7. **`cle_gs1_associee`** : La clé d'identification GS1 principale (GTIN, SSCC, etc.) avec laquelle cet AI est typiquement utilisé ou associé. Certains AI sont des attributs d'autres clés. Cette information est dérivée des descriptions d'applications et d'AI dans la source "GS1 General Specifications Standard".
8. **`contextes_usage`** : Une liste de chaînes de caractères indiquant les domaines, industries ou applications spécifiques où cet AI est couramment utilisé. Cette information est tirée des descriptions d'applications et d'AI.
9. **`supports_donnees_autorises`** : Une liste de chaînes de caractères indiquant les supports de données GS1 (codes-barres 1D, 2D, RFID) dans lesquels cet AI peut être encodé. Cette liste est basée sur les spécifications des supports de données et les applications dans la source "GS1 General Specifications Standard".
10. **`regles_et_contraintes`** : Une liste de chaînes de caractères décrivant les règles spécifiques, limitations ou contraintes d'utilisation définies dans les standards. Ces règles proviennent des sections 4 et des descriptions d'AI/applications.
11. **`association_mandatoire`** : Une liste de chaînes de caractères indiquant si cet AI **doit** obligatoirement être utilisé avec d'autres AIs ou identifiants dans certains contextes. Ces associations obligatoires sont mentionnées dans les descriptions d'AI/applications.

Ce catalogue inclut tous les Identifiants d'Application listés dans les sections 3.2 à 3.10 de la source "GS1-General-Specifications R25.pdf". Notez que certains AIs (comme 310n, 710-716, 723s, 91-99) sont représentés par une entrée unique pour couvrir une plage ou un format générique, comme indiqué dans les sources.

La source "GS1-General-Specifications R25.pdf" est le standard fondamental qui définit l'utilisation des clés d'identification, des attributs de données et des codes-barres GS1. Ce document est la référence technique globale pour le système GS1.