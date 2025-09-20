"""
Tests complets endpoint /decode/ pour tous les formats
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import io

# Ajout du chemin de l'application
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.main import app

client = TestClient(app)

class TestDecodeEndpointComplete:
    """Tests endpoint /decode/ complets"""

    @pytest.mark.parametrize("format_config", [
        {
            "format": "QR Code",
            "data": "Decoded QR content",
            "gs1_detected": False,
            "confidence": 0.95,
            "expected_aim": None
        },
        {
            "format": "DataMatrix",
            "data": "Decoded DataMatrix content",
            "gs1_detected": False,
            "confidence": 0.90,
            "expected_aim": "]d1"  # DataMatrix standard
        },
        {
            "format": "Code 128",
            "data": "DECODED128",
            "gs1_detected": False,
            "confidence": 0.85,
            "expected_aim": None
        },
        {
            "format": "DataMatrix",
            "data": "(01)03760423190005",
            "gs1_detected": True,
            "confidence": 0.98,
            "expected_aim": "]d2"  # GS1 DataMatrix
        },
        {
            "format": "QR Code",
            "data": "(01)03760423190005(21)SERIAL",
            "gs1_detected": True,
            "confidence": 0.95,
            "expected_aim": None  # QR Code n'a pas d'AIM specifique
        }
    ])
    def test_decode_endpoint_all_formats(self, format_config):
        """Test décodage tous formats via endpoint"""

        fake_image_data = b"fake_image_for_" + format_config["format"].replace(" ", "_").encode()

        with patch('app.barcode_detector.detect_barcode') as mock_detect:
            mock_detect.return_value = {
                "found": True,
                "format": format_config["format"],
                "data": format_config["data"],
                "gs1_detected": format_config["gs1_detected"],
                "confidence": format_config["confidence"],
                "aim_identifier": format_config.get("expected_aim")
            }

            response = client.post(
                "/decode/",
                files={"file": ("test.png", fake_image_data, "image/png")},
                data={"verbose": "false"}
            )

            assert response.status_code == 200

            decoded_result = response.json()
            assert decoded_result["success"] == True
            assert len(decoded_result["barcodes"]) > 0

            barcode = decoded_result["barcodes"][0]
            assert barcode["raw"] == format_config["data"]
            assert barcode["decoder_info"]["format"] == format_config["format"]

            if format_config["expected_aim"]:
                # Vérifier AIM identifier si applicable
                assert "aim_identifier" in barcode["decoder_info"]

    def test_decode_endpoint_gs1_vs_standard_differentiation(self):
        """CRITIQUE: Différenciation décodage GS1 vs standard"""

        # DataMatrix standard vs GS1 DataMatrix
        test_cases = [
            {
                "image_name": "standard_datamatrix.png",
                "decoded_data": "Standard DataMatrix content",
                "format": "DataMatrix",
                "gs1_detected": False,
                "aim_identifier": "]d1"
            },
            {
                "image_name": "gs1_datamatrix.png",
                "decoded_data": "(01)03760423190005",
                "format": "DataMatrix",
                "gs1_detected": True,
                "aim_identifier": "]d2"
            }
        ]

        for case in test_cases:
            with patch('app.barcode_detector.detect_barcode') as mock_detect:
                mock_detect.return_value = {
                    "found": True,
                    "format": case["format"],
                    "data": case["decoded_data"],
                    "gs1_detected": case["gs1_detected"],
                    "aim_identifier": case["aim_identifier"],
                    "confidence": 0.95
                }

                response = client.post(
                    "/decode/",
                    files={"file": (case["image_name"], b"fake_image", "image/png")}
                )

                assert response.status_code == 200

                result = response.json()
                barcode = result["barcodes"][0]

                # Vérifications critiques
                assert barcode["decoder_info"]["is_gs1"] == case["gs1_detected"]
                if case["aim_identifier"]:
                    # AIM identifier crucial pour différenciation
                    assert case["aim_identifier"] in str(barcode["decoder_info"])

    def test_decode_endpoint_verbose_mode(self):
        """Test mode verbose endpoint /decode/"""

        gs1_data = "(01)03760423190005(17)250423(10)BATCH123"

        with patch('app.barcode_detector.detect_barcode') as mock_detect:
            mock_detect.return_value = {
                "found": True,
                "format": "DataMatrix",
                "data": gs1_data,
                "gs1_detected": True,
                "aim_identifier": "]d2",
                "confidence": 0.98
            }

            # Test mode verbose
            response_verbose = client.post(
                "/decode/",
                files={"file": ("test.png", b"fake_gs1_image", "image/png")},
                data={"verbose": "true"}
            )

            assert response_verbose.status_code == 200

            verbose_result = response_verbose.json()
            barcode = verbose_result["barcodes"][0]

            # En mode verbose, parsed devrait être une liste détaillée
            assert isinstance(barcode["parsed"], list), "Mode verbose devrait retourner liste détaillée"

            # Test mode simple
            response_simple = client.post(
                "/decode/",
                files={"file": ("test.png", b"fake_gs1_image", "image/png")},
                data={"verbose": "false"}
            )

            assert response_simple.status_code == 200

            simple_result = response_simple.json()
            barcode_simple = simple_result["barcodes"][0]

            # En mode simple, parsed devrait être un dict
            assert isinstance(barcode_simple["parsed"], dict), "Mode simple devrait retourner dict"

    def test_decode_endpoint_error_scenarios(self):
        """Test scénarios d'erreur endpoint /decode/"""

        error_scenarios = [
            # (file_content, content_type, expected_status, description)
            (b"", "image/png", 422, "fichier_vide"),
            (b"not_an_image", "image/png", 500, "données_invalides"),
            (b"fake_image_no_barcode", "image/png", 200, "pas_de_code"),  # Réponse valide mais found=False
        ]

        for file_content, content_type, expected_status, description in error_scenarios:
            if description == "pas_de_code":
                # Mock pour aucun code trouvé
                with patch('app.barcode_detector.detect_barcode') as mock_detect:
                    mock_detect.return_value = {
                        "found": False,
                        "error": "Aucun code-barres détecté",
                        "format": None,
                        "data": None
                    }

                    response = client.post(
                        "/decode/",
                        files={"file": ("test.png", file_content, content_type)}
                    )

                    assert response.status_code == 200  # Réponse valide
                    result = response.json()
                    assert result["success"] == True  # Mais pas de codes trouvés
                    assert len(result["barcodes"]) == 0

            else:
                # Autres erreurs
                response = client.post(
                    "/decode/",
                    files={"file": ("test.png", file_content, content_type)}
                )

                assert response.status_code == expected_status, \
                    f"Scénario {description} devrait retourner {expected_status}"

    def test_decode_endpoint_multiple_barcodes(self):
        """Test décodage image avec plusieurs codes-barres"""

        with patch('app.barcode_detector.detect_barcode') as mock_detect:
            # Simuler détection multiple codes
            mock_detect.return_value = {
                "found": True,
                "codes": [
                    {
                        "format": "QR Code",
                        "data": "First QR Code",
                        "confidence": 0.95,
                        "gs1_detected": False
                    },
                    {
                        "format": "DataMatrix",
                        "data": "(01)03760423190005",
                        "confidence": 0.98,
                        "gs1_detected": True,
                        "aim_identifier": "]d2"
                    }
                ]
            }

            response = client.post(
                "/decode/",
                files={"file": ("multi_codes.png", b"fake_multi_image", "image/png")}
            )

            assert response.status_code == 200

            result = response.json()
            assert result["success"] == True

            # Note: Implementation actuelle peut ne pas supporter codes multiples
            # Ce test vérifie la gestion de ce cas

    def test_decode_endpoint_file_format_support(self):
        """Test support différents formats de fichiers image"""

        supported_formats = [
            ("image/png", "test.png"),
            ("image/jpeg", "test.jpg"),
            ("image/bmp", "test.bmp")
        ]

        for content_type, filename in supported_formats:
            with patch('app.barcode_detector.detect_barcode') as mock_detect:
                mock_detect.return_value = {
                    "found": True,
                    "format": "QR Code",
                    "data": f"Decoded from {filename}",
                    "confidence": 0.90
                }

                response = client.post(
                    "/decode/",
                    files={"file": (filename, b"fake_image_data", content_type)}
                )

                # PNG et JPEG devraient être supportés
                if content_type in ["image/png", "image/jpeg"]:
                    assert response.status_code == 200, f"Format {content_type} devrait être supporté"
                # Autres formats peuvent être rejetés ou convertis

    def test_decode_endpoint_performance_benchmarks(self):
        """Test performance endpoint /decode/"""

        image_sizes = [
            (1024, "small_1kb"),
            (10240, "medium_10kb"),
            (102400, "large_100kb")
        ]

        for size, description in image_sizes:
            fake_image = b"a" * size

            with patch('app.barcode_detector.detect_barcode') as mock_detect:
                def timed_decode(*args, **kwargs):
                    import time
                    time.sleep(0.05)  # Simuler traitement
                    return {
                        "found": True,
                        "format": "QR Code",
                        "data": f"Decoded {description}",
                        "confidence": 0.95
                    }

                mock_detect.side_effect = timed_decode

                import time
                start_time = time.time()

                response = client.post(
                    "/decode/",
                    files={"file": (f"{description}.png", fake_image, "image/png")}
                )

                end_time = time.time()
                decode_time = end_time - start_time

                assert response.status_code == 200
                assert decode_time < 10.0, f"Décodage {description} devrait prendre < 10s, obtenu: {decode_time:.2f}s"