"""
Tests de non-régression pour s'assurer que les modifications GS1 DataMatrix
n'impactent pas les autres fonctionnalités
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Ajout du chemin de l'application
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.main import app
from app.barcode_generator import BarcodeFormat

client = TestClient(app)

class TestRegressionPrevention:
    """Tests de non-régression pour éviter les impacts sur les autres formats"""

    def test_standard_datamatrix_not_affected(self):
        """CRITIQUE: Vérifier que DataMatrix standard n'est pas affecté par les changements GS1"""

        standard_data = "Standard DataMatrix content"

        with patch('app.barcode_generator.generate_barcode') as mock_generate:
            mock_generate.return_value = (
                b'standard_datamatrix_data',
                'image/png',
                {"format": "datamatrix", "method": "treepoem"}  # Devrait utiliser treepoem
            )

            response = client.post("/generate/", json={
                "data": standard_data,
                "barcode_format": "datamatrix"  # Format standard, pas GS1
            })

            assert response.status_code == 200

            # Vérifier que use_treepoem n'est PAS forcé à False pour DataMatrix standard
            args, kwargs = mock_generate.call_args
            assert kwargs.get("use_treepoem", True) == True, \
                "DataMatrix standard devrait pouvoir utiliser treepoem"

            # Vérifier que c'est bien le format standard
            assert kwargs["barcode_format"] == BarcodeFormat.DATAMATRIX
            assert kwargs["barcode_format"] != BarcodeFormat.GS1_DATAMATRIX

    def test_qr_code_generation_unchanged(self):
        """Vérifier que la génération QR Code n'est pas impactée"""

        qr_data = "QR Code test data with special chars !@#$%"

        with patch('app.barcode_generator.generate_barcode') as mock_generate:
            mock_generate.return_value = (
                b'qr_code_data',
                'image/png',
                {"format": "qr_code", "method": "qrcode"}
            )

            response = client.post("/generate/", json={
                "data": qr_data,
                "barcode_format": "qr_code"
            })

            assert response.status_code == 200

            # Vérifier paramètres QR Code
            args, kwargs = mock_generate.call_args
            assert kwargs["barcode_format"] == BarcodeFormat.QR_CODE
            assert kwargs.get("use_treepoem", True) == True  # QR Code peut utiliser treepoem

    def test_code128_generation_unchanged(self):
        """Vérifier que la génération Code 128 n'est pas impactée"""

        code128_data = "CODE128TEST123"

        with patch('app.barcode_generator.generate_barcode') as mock_generate:
            mock_generate.return_value = (
                b'code128_data',
                'image/png',
                {"format": "code_128", "method": "python-barcode"}
            )

            response = client.post("/generate/", json={
                "data": code128_data,
                "barcode_format": "code_128"
            })

            assert response.status_code == 200

            # Vérifier paramètres Code 128
            args, kwargs = mock_generate.call_args
            assert kwargs["barcode_format"] == BarcodeFormat.CODE_128

    def test_gs1_128_vs_gs1_datamatrix_differentiation(self, gs1_test_data):
        """Vérifier différenciation entre GS1-128 et GS1 DataMatrix"""

        # Test GS1-128
        with patch('app.barcode_generator.generate_barcode') as mock_generate:
            mock_generate.return_value = (
                b'gs1_128_data',
                'image/png',
                {"format": "gs1_128", "method": "python-barcode"}
            )

            response_128 = client.post("/generate/", json={
                "data": gs1_test_data["simple"],
                "barcode_format": "gs1_128"
            })

            assert response_128.status_code == 200

            # GS1-128 ne devrait PAS forcer use_treepoem=False
            args, kwargs = mock_generate.call_args
            assert kwargs["barcode_format"] == BarcodeFormat.GS1_128
            assert kwargs.get("use_treepoem", True) == True

        # Test GS1 DataMatrix (pour comparaison)
        with patch('app.barcode_generator.generate_barcode') as mock_generate:
            mock_generate.return_value = (
                b'gs1_datamatrix_data',
                'image/png',
                {"format": "gs1_datamatrix", "method": "bwip-js"}
            )

            response_datamatrix = client.post("/generate/", json={
                "data": gs1_test_data["simple"],
                "barcode_format": "gs1_datamatrix"
            })

            assert response_datamatrix.status_code == 200

            # GS1 DataMatrix DEVRAIT forcer use_treepoem=False
            args, kwargs = mock_generate.call_args
            assert kwargs["barcode_format"] == BarcodeFormat.GS1_DATAMATRIX
            assert kwargs["use_treepoem"] == False

    def test_decode_functionality_not_affected(self):
        """Vérifier que la fonctionnalité de décodage n'est pas affectée"""

        test_image_data = b"fake_image_for_decode_test"

        with patch('app.barcode_detector.detect_barcode') as mock_detect:
            mock_detect.return_value = {
                "found": True,
                "format": "QR Code",
                "data": "Decoded QR content",
                "confidence": 0.95,
                "gs1_detected": False
            }

            response = client.post(
                "/decode/",
                files={"file": ("test.png", test_image_data, "image/png")}
            )

            assert response.status_code == 200
            decoded_result = response.json()

            assert decoded_result["found"] == True
            assert decoded_result["format"] == "QR Code"
            assert "data" in decoded_result

    def test_parse_functionality_not_affected(self, gs1_test_data):
        """Vérifier que la fonctionnalité de parsing n'est pas affectée"""

        # Test parsing GS1
        response_gs1 = client.post("/parse/", json={
            "data": gs1_test_data["simple"],
            "verbose": True
        })

        assert response_gs1.status_code == 200
        parsed_gs1 = response_gs1.json()
        assert parsed_gs1["format_detected"] == "GS1"

        # Test parsing non-GS1
        response_standard = client.post("/parse/", json={
            "data": "Standard non-GS1 data",
            "verbose": False
        })

        assert response_standard.status_code == 200

    def test_api_response_format_consistency(self):
        """Vérifier que le format des réponses API reste cohérent"""

        test_formats = ["datamatrix", "qr_code", "code_128", "gs1_datamatrix"]

        for barcode_format in test_formats:
            with patch('app.barcode_generator.generate_barcode') as mock_generate:
                mock_generate.return_value = (
                    f'{barcode_format}_data'.encode(),
                    'image/png',
                    {"format": barcode_format}
                )

                response = client.post("/generate/", json={
                    "data": f"Test data for {barcode_format}",
                    "barcode_format": barcode_format
                })

                # Tous les formats devraient avoir la même structure de réponse
                assert response.status_code == 200
                assert response.headers.get("content-type") == "image/png"
                assert len(response.content) > 0

    def test_error_handling_consistency(self):
        """Vérifier que la gestion d'erreurs reste cohérente pour tous les formats"""

        test_formats = ["datamatrix", "qr_code", "code_128", "gs1_datamatrix"]

        for barcode_format in test_formats:
            with patch('app.barcode_generator.generate_barcode') as mock_generate:
                mock_generate.side_effect = Exception(f"Erreur test {barcode_format}")

                response = client.post("/generate/", json={
                    "data": "Test data",
                    "barcode_format": barcode_format
                })

                # Toutes les erreurs devraient être gérées de manière cohérente
                assert response.status_code == 500
                error_data = response.json()
                assert "detail" in error_data
                assert "Erreur interne" in error_data["detail"]

    def test_health_endpoint_still_reports_all_capabilities(self):
        """Vérifier que le endpoint /health rapporte toujours toutes les capacités"""

        response = client.get("/health")
        assert response.status_code == 200

        health_data = response.json()
        assert health_data["status"] == "OK"

        # Vérifier que toutes les capacités sont présentes
        supported_codes = health_data["capabilities"]["supported_codes"]
        expected_codes = [
            "DataMatrix",
            "QR Code",
            "Code 128",
            "GS1-128",
            "GS1 DataMatrix",
            "GS1 QR Code"
        ]

        for expected_code in expected_codes:
            assert expected_code in supported_codes, f"{expected_code} devrait être supporté"

        # Vérifier capacités de génération
        generators = health_data["capabilities"]["generators"]
        assert generators["bwipjs"] == True, "bwip-js devrait être disponible"
        assert generators["treepoem"] == True, "treepoem devrait être disponible"

    def test_image_format_support_unchanged(self):
        """Vérifier que le support des formats d'image n'est pas affecté"""

        image_formats = ["png", "jpeg", "svg"]

        for image_format in image_formats:
            with patch('app.barcode_generator.generate_barcode') as mock_generate:
                mock_generate.return_value = (
                    b'image_data',
                    f'image/{image_format}',
                    {"format": "qr_code", "image_format": image_format}
                )

                response = client.post("/generate/", json={
                    "data": "Test data",
                    "barcode_format": "qr_code",
                    "image_format": image_format
                })

                assert response.status_code == 200
                expected_content_type = "image/svg+xml" if image_format == "svg" else f"image/{image_format}"
                assert response.headers.get("content-type") == expected_content_type

    def test_parameter_validation_not_affected(self):
        """Vérifier que la validation des paramètres n'est pas affectée"""

        # Test avec paramètres invalides pour différents formats
        invalid_cases = [
            {"data": "", "barcode_format": "qr_code"},  # Données vides
            {"data": "test", "barcode_format": "invalid_format"},  # Format invalide
            {"data": "test", "barcode_format": "qr_code", "width": -1},  # Largeur invalide
            {"data": "test", "barcode_format": "qr_code", "height": 0},  # Hauteur invalide
        ]

        for invalid_case in invalid_cases:
            response = client.post("/generate/", json=invalid_case)
            assert response.status_code == 422, f"Cas invalide devrait être rejeté: {invalid_case}"

    def test_concurrent_different_formats_no_interference(self):
        """Test que les générations concurrentes de différents formats n'interfèrent pas"""

        import threading

        results = {}
        errors = []

        def generate_format(format_name, data):
            try:
                with patch('app.barcode_generator.generate_barcode') as mock_generate:
                    mock_generate.return_value = (
                        f'{format_name}_data'.encode(),
                        'image/png',
                        {"format": format_name}
                    )

                    response = client.post("/generate/", json={
                        "data": data,
                        "barcode_format": format_name
                    })

                    results[format_name] = response.status_code
            except Exception as e:
                errors.append((format_name, str(e)))

        # Lancer génération concurrent de différents formats
        formats = [
            ("datamatrix", "Standard data"),
            ("gs1_datamatrix", "(01)12345678901234"),
            ("qr_code", "QR data"),
            ("code_128", "CODE128")
        ]

        threads = []
        for format_name, data in formats:
            thread = threading.Thread(target=generate_format, args=(format_name, data))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Vérifier que tous les formats réussissent
        assert len(errors) == 0, f"Aucune erreur attendue: {errors}"
        assert len(results) == 4, "Tous les formats devraient réussir"

        for format_name, status_code in results.items():
            assert status_code == 200, f"Format {format_name} devrait réussir"