"""
Tests d'intégration des endpoints API
"""
import pytest
import sys
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Ajout du chemin de l'application
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.main import app

client = TestClient(app)

class TestAPIEndpoints:
    """Tests d'intégration pour les endpoints API"""

    def test_health_endpoint_integration(self):
        """Test d'intégration du endpoint /health"""
        response = client.get("/health")

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "OK"
        assert "capabilities" in data
        assert "generators" in data["capabilities"]
        assert data["capabilities"]["generators"]["bwipjs"] == True
        assert "GS1 DataMatrix" in data["capabilities"]["supported_codes"]

    def test_generate_endpoint_gs1_datamatrix_integration(self, gs1_test_data):
        """CRITIQUE: Test d'intégration complet /generate/ pour GS1 DataMatrix"""

        with patch('app.barcode_generator.generate_barcode') as mock_generate:
            # Mock génération réussie
            mock_generate.return_value = (
                b'fake_optimized_png_data',  # 571 bytes simulés
                'image/png',
                {
                    "format": "gs1_datamatrix",
                    "size": (100, 100),
                    "optimized": True,
                    "method": "bwip-js"
                }
            )

            # Test avec données simples
            response = client.post("/generate/", json={
                "data": gs1_test_data["simple"],
                "barcode_format": "gs1_datamatrix",
                "width": 200,
                "height": 200
            })

            assert response.status_code == 200
            assert response.headers["content-type"] == "image/png"

            # Vérifier que generate_barcode a été appelé avec les bons paramètres
            mock_generate.assert_called_once()
            args, kwargs = mock_generate.call_args

            assert kwargs["data"] == gs1_test_data["simple"]
            assert kwargs["barcode_format"].value == "gs1_datamatrix"
            assert kwargs["use_treepoem"] == False  # CRITIQUE: Forcé pour GS1 DataMatrix

    def test_generate_endpoint_with_expert_data(self, gs1_test_data):
        """Test avec données GS1 expert complexes"""

        with patch('app.barcode_generator.generate_barcode') as mock_generate:
            mock_generate.return_value = (
                b'fake_expert_png_data',  # 689 bytes simulés
                'image/png',
                {
                    "format": "gs1_datamatrix",
                    "size": (150, 150),
                    "optimized": True,
                    "method": "bwip-js"
                }
            )

            response = client.post("/generate/", json={
                "data": gs1_test_data["expert"],
                "barcode_format": "gs1_datamatrix"
            })

            assert response.status_code == 200
            assert len(response.content) > 0

            # Vérifier les paramètres passés
            args, kwargs = mock_generate.call_args
            assert kwargs["data"] == gs1_test_data["expert"]
            assert kwargs["use_treepoem"] == False

    def test_generate_endpoint_error_handling(self, gs1_test_data):
        """Test de gestion d'erreurs API"""

        with patch('app.barcode_generator.generate_barcode') as mock_generate:
            # Simuler une erreur de génération
            mock_generate.side_effect = Exception("Erreur de génération test")

            response = client.post("/generate/", json={
                "data": gs1_test_data["simple"],
                "barcode_format": "gs1_datamatrix"
            })

            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "Erreur interne" in data["detail"]

    def test_generate_endpoint_validation(self):
        """Test de validation des données d'entrée"""

        # Test données manquantes
        response = client.post("/generate/", json={
            "barcode_format": "gs1_datamatrix"
            # data manquant
        })
        assert response.status_code == 422

        # Test format invalide
        response = client.post("/generate/", json={
            "data": "(01)12345678901234",
            "barcode_format": "invalid_format"
        })
        assert response.status_code == 422

    def test_parse_endpoint_integration(self, gs1_test_data):
        """Test d'intégration du endpoint /parse/"""

        response = client.post("/parse/", json={
            "data": gs1_test_data["simple"],
            "verbose": True
        })

        assert response.status_code == 200
        data = response.json()

        assert "parsed_data" in data
        assert "format_detected" in data
        assert data["format_detected"] == "GS1"

    def test_decode_endpoint_integration(self):
        """Test d'intégration du endpoint /decode/"""

        # Mock d'un fichier image
        fake_image_content = b"fake_image_data"

        with patch('app.barcode_detector.detect_barcode') as mock_detect:
            mock_detect.return_value = {
                "found": True,
                "format": "DataMatrix",
                "data": "(01)12345678901234",
                "confidence": 0.95,
                "gs1_detected": True,
                "aim_identifier": "]d2"
            }

            response = client.post(
                "/decode/",
                files={"file": ("test.png", fake_image_content, "image/png")}
            )

            assert response.status_code == 200
            data = response.json()

            assert data["found"] == True
            assert data["format"] == "DataMatrix"
            assert data["gs1_detected"] == True
            assert data["aim_identifier"] == "]d2"

    def test_cross_endpoint_workflow_integration(self, gs1_test_data):
        """Test de workflow complet: génération → décodage → parsing"""

        # 1. Génération
        with patch('app.barcode_generator.generate_barcode') as mock_generate:
            mock_generate.return_value = (
                b'fake_gs1_datamatrix_data',
                'image/png',
                {"format": "gs1_datamatrix"}
            )

            generate_response = client.post("/generate/", json={
                "data": gs1_test_data["simple"],
                "barcode_format": "gs1_datamatrix"
            })

            assert generate_response.status_code == 200
            generated_image = generate_response.content

        # 2. Décodage du code généré
        with patch('app.barcode_detector.detect_barcode') as mock_detect:
            mock_detect.return_value = {
                "found": True,
                "format": "DataMatrix",
                "data": gs1_test_data["simple"],
                "gs1_detected": True,
                "aim_identifier": "]d2"
            }

            decode_response = client.post(
                "/decode/",
                files={"file": ("generated.png", generated_image, "image/png")}
            )

            assert decode_response.status_code == 200
            decoded_data = decode_response.json()

        # 3. Parsing des données décodées
        parse_response = client.post("/parse/", json={
            "data": decoded_data["data"],
            "verbose": False
        })

        assert parse_response.status_code == 200
        parsed_data = parse_response.json()

        # Vérification du workflow complet
        assert decoded_data["data"] == gs1_test_data["simple"]
        assert decoded_data["aim_identifier"] == "]d2"
        assert parsed_data["format_detected"] == "GS1"

    def test_api_consistency_across_formats(self, gs1_test_data):
        """Test de cohérence API pour différents formats"""

        formats_to_test = [
            ("gs1_datamatrix", gs1_test_data["simple"]),
            ("qr_code", gs1_test_data["simple"]),
            ("datamatrix", "Non-GS1 data")
        ]

        for barcode_format, test_data in formats_to_test:
            with patch('app.barcode_generator.generate_barcode') as mock_generate:
                mock_generate.return_value = (b'fake_data', 'image/png', {})

                response = client.post("/generate/", json={
                    "data": test_data,
                    "barcode_format": barcode_format
                })

                # Tous les formats devraient être supportés
                assert response.status_code == 200

                # Vérifier le paramètre use_treepoem spécifique à GS1 DataMatrix
                args, kwargs = mock_generate.call_args
                if barcode_format == "gs1_datamatrix":
                    assert kwargs["use_treepoem"] == False
                else:
                    # Les autres formats peuvent utiliser treepoem
                    assert kwargs.get("use_treepoem", True) == True