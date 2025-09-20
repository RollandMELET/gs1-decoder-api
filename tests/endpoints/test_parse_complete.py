"""
Tests complets endpoint /parse/ pour données GS1 et standard
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Ajout du chemin de l'application
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.main import app

client = TestClient(app)

class TestParseEndpointComplete:
    """Tests endpoint /parse/ complets"""

    @pytest.mark.parametrize("parse_config", [
        {
            "raw_data": "(01)03760423190005",
            "expected_format": "GS1",
            "expected_ais": ["01"],
            "verbose": False
        },
        {
            "raw_data": "(01)03760423190005(17)250423(10)BATCH123",
            "expected_format": "GS1",
            "expected_ais": ["01", "17", "10"],
            "verbose": True
        },
        {
            "raw_data": "01037604231900051725042310BATCH123",
            "expected_format": "GS1",
            "expected_ais": ["01", "17", "10"],
            "verbose": False
        },
        {
            "raw_data": "Non-GS1 standard data",
            "expected_format": "Unknown",
            "expected_ais": [],
            "verbose": False
        }
    ])
    def test_parse_endpoint_data_types(self, parse_config):
        """Test parsing différents types de données"""

        response = client.post("/parse/", json={
            "raw_data": parse_config["raw_data"],
            "verbose": parse_config["verbose"]
        })

        assert response.status_code == 200

        result = response.json()
        assert result["success"] == True
        assert len(result["barcodes"]) > 0

        barcode = result["barcodes"][0]
        assert barcode["raw"] == parse_config["raw_data"]

        # Vérifier format détecté
        if parse_config["expected_format"] != "Unknown":
            assert barcode["decoder_info"]["format"] == parse_config["expected_format"]

        # Vérifier AIs parsés
        if parse_config["verbose"] and parse_config["expected_ais"]:
            parsed_data = barcode["parsed"]
            assert isinstance(parsed_data, list), "Mode verbose devrait retourner liste"

            found_ais = [item["ai"] for item in parsed_data if "ai" in item]
            for expected_ai in parse_config["expected_ais"]:
                assert expected_ai in found_ais, f"AI {expected_ai} devrait être trouvé"

    def test_parse_endpoint_verbose_vs_simple_modes(self):
        """Test différence modes verbose vs simple"""

        gs1_data = "(01)03760423190005(17)250423(10)BATCH123(21)SERIAL456"

        # Mode verbose
        response_verbose = client.post("/parse/", json={
            "raw_data": gs1_data,
            "verbose": True
        })

        assert response_verbose.status_code == 200
        verbose_result = response_verbose.json()

        # Mode simple
        response_simple = client.post("/parse/", json={
            "raw_data": gs1_data,
            "verbose": False
        })

        assert response_simple.status_code == 200
        simple_result = response_simple.json()

        # Comparaison modes
        verbose_barcode = verbose_result["barcodes"][0]
        simple_barcode = simple_result["barcodes"][0]

        # Raw data identique
        assert verbose_barcode["raw"] == simple_barcode["raw"]

        # Format parsing différent
        assert isinstance(verbose_barcode["parsed"], list), "Mode verbose: liste détaillée"
        assert isinstance(simple_barcode["parsed"], dict), "Mode simple: dict clé-valeur"

        # Vérifier contenu verbose
        verbose_ais = [item["ai"] for item in verbose_barcode["parsed"]]
        expected_ais = ["01", "17", "10", "21"]
        for ai in expected_ais:
            assert ai in verbose_ais, f"Mode verbose devrait contenir AI {ai}"

        # Vérifier contenu simple
        assert "GTIN" in simple_barcode["parsed"], "Mode simple devrait contenir clés nommées"

    def test_parse_endpoint_error_handling(self):
        """Test gestion d'erreurs endpoint /parse/"""

        error_scenarios = [
            ("", "données_vides"),
            ("malformed(01incomplete", "données_malformées"),
            ("(01)invalid_gtin_12345", "gtin_invalide"),
            ("(99)unknown_ai_value", "ai_inconnu")
        ]

        for raw_data, scenario in error_scenarios:
            response = client.post("/parse/", json={
                "raw_data": raw_data,
                "verbose": False
            })

            # Parse devrait toujours retourner 200 mais avec détails d'erreur
            assert response.status_code == 200

            result = response.json()
            # Peut contenir des erreurs dans parsed ou decoder_info

    def test_parse_endpoint_barcode_format_hint(self):
        """Test utilisation du hint barcode_format"""

        test_data = "01037604231900051725042310BATCH"

        # Avec hint format
        response_with_hint = client.post("/parse/", json={
            "raw_data": test_data,
            "barcode_format": "GS1 DataMatrix",
            "verbose": False
        })

        assert response_with_hint.status_code == 200

        # Sans hint format
        response_no_hint = client.post("/parse/", json={
            "raw_data": test_data,
            "verbose": False
        })

        assert response_no_hint.status_code == 200

        # Les deux devraient donner des résultats cohérents
        with_hint_result = response_with_hint.json()
        no_hint_result = response_no_hint.json()

        # Raw data devrait être identique
        assert with_hint_result["barcodes"][0]["raw"] == no_hint_result["barcodes"][0]["raw"]

    def test_parse_endpoint_performance(self):
        """Test performance endpoint /parse/"""

        # Données GS1 complexes
        complex_gs1_data = "(01)03760423190005(11)250910(3100)012000(21)0000019C(90)7391023(93)DHA(94)UP(95)ENVELOPPE_NUE_4UF"

        import time
        start_time = time.time()

        response = client.post("/parse/", json={
            "raw_data": complex_gs1_data,
            "verbose": True  # Mode verbose plus intensif
        })

        end_time = time.time()
        parse_time = end_time - start_time

        assert response.status_code == 200
        assert parse_time < 1.0, f"Parsing devrait prendre < 1s, obtenu: {parse_time:.2f}s"

        result = response.json()
        assert result["success"] == True

    def test_parse_endpoint_consistency_with_decode(self):
        """Test cohérence parse avec données issues de decode"""

        # Simuler workflow: image → decode → parse
        decoded_gs1_data = "(01)03760423190005(17)250910(10)BATCH"

        # 1. Simuler résultat decode
        with patch('app.barcode_detector.detect_barcode') as mock_detect:
            mock_detect.return_value = {
                "found": True,
                "format": "DataMatrix",
                "data": decoded_gs1_data,
                "gs1_detected": True,
                "aim_identifier": "]d2"
            }

            decode_response = client.post(
                "/decode/",
                files={"file": ("test.png", b"fake_gs1_image", "image/png")},
                data={"verbose": "false"}
            )

            assert decode_response.status_code == 200
            decode_result = decode_response.json()

        # 2. Parser les données décodées
        parse_response = client.post("/parse/", json={
            "raw_data": decoded_gs1_data,
            "barcode_format": "GS1 DataMatrix",
            "verbose": False
        })

        assert parse_response.status_code == 200
        parse_result = parse_response.json()

        # 3. Vérifier cohérence
        decode_barcode = decode_result["barcodes"][0]
        parse_barcode = parse_result["barcodes"][0]

        assert decode_barcode["raw"] == parse_barcode["raw"], "Données raw devraient être identiques"

        # Structure parsed peut différer, mais contenu devrait être cohérent
        if isinstance(decode_barcode["parsed"], dict) and isinstance(parse_barcode["parsed"], dict):
            # Comparer quelques clés communes
            common_keys = set(decode_barcode["parsed"].keys()) & set(parse_barcode["parsed"].keys())
            for key in common_keys:
                assert decode_barcode["parsed"][key] == parse_barcode["parsed"][key], \
                    f"Valeur {key} devrait être cohérente entre decode et parse"

class TestParseEndpointRegression:
    """Tests de non-régression endpoint /parse/"""

    def test_parse_endpoint_backward_compatibility(self):
        """Test compatibilité descendante endpoint /parse/"""

        # Test avec anciens formats de requête
        legacy_requests = [
            {
                "raw_data": "(01)12345678901234",
                # Pas de verbose spécifié - devrait utiliser défaut
            },
            {
                "raw_data": "01123456789012341725042310BATCH",
                "barcode_format": "DataMatrix"  # Ancien format naming
            }
        ]

        for legacy_request in legacy_requests:
            response = client.post("/parse/", json=legacy_request)

            # Devrait soit réussir (compatibilité) soit échouer proprement
            assert response.status_code in [200, 422], \
                f"Requête legacy devrait être gérée: {legacy_request}"

    def test_parse_endpoint_data_integrity(self):
        """Test intégrité données à travers endpoint /parse/"""

        # Données test avec caractères spéciaux
        test_datasets = [
            "(01)03760423190005(21)SERIAL-123!@#",
            "(01)03760423190005(10)BATCH\u001dWITH\u001dGS",  # Avec séparateurs GS
            "01037604231900051725042310BATCH123",  # Sans parenthèses
            "(01)03760423190005(11)250910(3100)012000(21)0000019C(90)7391023(93)DHA(94)UP(95)ENVELOPPE_NUE_4UF"  # Expert
        ]

        for original_data in test_datasets:
            response = client.post("/parse/", json={
                "raw_data": original_data,
                "verbose": True
            })

            assert response.status_code == 200

            result = response.json()
            assert result["success"] == True

            barcode = result["barcodes"][0]
            assert barcode["raw"] == original_data, "Données originales devraient être préservées"

            # Vérifier que parsing a extrait des informations
            if "(01)" in original_data or original_data.startswith("01"):
                parsed_data = barcode["parsed"]
                assert len(parsed_data) > 0, "Données GS1 devraient être parsées"

    def test_parse_endpoint_edge_cases(self):
        """Test cas limites endpoint /parse/"""

        edge_cases = [
            ("(01)", "ai_sans_valeur"),
            ("01", "ai_minimal"),
            ("(01)12345678901234" * 10, "données_répétitives"),
            ("(01)03760423190005\u001d(17)250423", "avec_séparateurs_gs"),
            ("NOTGS1DATA123!@#$%", "données_non_gs1")
        ]

        for data, case_description in edge_cases:
            response = client.post("/parse/", json={
                "raw_data": data,
                "verbose": False
            })

            # Parse devrait toujours répondre (même si parsing échoue)
            assert response.status_code == 200, f"Cas {case_description} devrait être géré"

            result = response.json()
            assert result["success"] == True  # Endpoint fonctionne
            assert len(result["barcodes"]) > 0  # Contient au moins une réponse

    def test_parse_endpoint_output_validation(self):
        """Test validation structure de sortie endpoint /parse/"""

        response = client.post("/parse/", json={
            "raw_data": "(01)03760423190005(17)250910",
            "verbose": True
        })

        assert response.status_code == 200

        result = response.json()

        # Vérifier structure JSON
        assert "success" in result
        assert "barcodes" in result
        assert isinstance(result["barcodes"], list)

        if len(result["barcodes"]) > 0:
            barcode = result["barcodes"][0]

            # Structure barcode
            required_fields = ["raw", "parsed", "decoder_info"]
            for field in required_fields:
                assert field in barcode, f"Champ {field} requis dans structure barcode"

            # Structure decoder_info
            decoder_info = barcode["decoder_info"]
            info_fields = ["decoder", "format"]
            for field in info_fields:
                assert field in decoder_info, f"Champ {field} requis dans decoder_info"

            # Structure parsed (mode verbose)
            parsed_data = barcode["parsed"]
            assert isinstance(parsed_data, list), "Mode verbose devrait retourner liste"

            if len(parsed_data) > 0:
                ai_item = parsed_data[0]
                ai_fields = ["ai", "name", "value", "valid"]
                for field in ai_fields:
                    assert field in ai_item, f"Champ {field} requis dans élément AI"