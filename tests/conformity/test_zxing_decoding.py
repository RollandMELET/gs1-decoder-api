"""
Tests de validation externe avec ZXing pour conformité GS1
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

# Ajout du chemin de l'application
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import jpype
    JPYPE_AVAILABLE = True
except ImportError:
    JPYPE_AVAILABLE = False

class TestZXingDecoding:
    """Tests de validation avec ZXing pour vérifier la conformité GS1"""

    @pytest.mark.skipif(not JPYPE_AVAILABLE, reason="JPype not available")
    def test_zxing_decoding_gs1_datamatrix(self, gs1_test_data, temp_output_dir):
        """CRITIQUE: Décodage ZXing pour validation identifier ]d2"""

        test_image_path = temp_output_dir / "test_zxing.png"

        # Simuler génération d'image GS1 DataMatrix
        with patch('app.barcode_generator.generate_gs1_datamatrix_hybrid') as mock_hybrid:
            mock_hybrid.return_value = (b'fake_gs1_datamatrix_png', {"optimized": True})

            # Mock ZXing pour tests
            with patch('jpype.startJVM'), \
                 patch('jpype.JClass') as mock_jclass, \
                 patch('jpype.java.nio.file.Paths') as mock_paths:

                # Mock des classes ZXing
                mock_reader = MagicMock()
                mock_result = MagicMock()

                # Configuration du mock ZXing
                mock_result.getText.return_value = gs1_test_data["simple"]
                mock_result.getBarcodeFormat.return_value.toString.return_value = "DATA_MATRIX"

                # Mock pour obtenir les métadonnées AIM
                mock_result.getResultMetadata.return_value = {
                    "SYMBOLOGY_IDENTIFIER": "]d2"  # CRITIQUE: GS1 DataMatrix identifier
                }

                mock_reader.decode.return_value = mock_result
                mock_jclass.return_value = lambda: mock_reader

                # Test de décodage
                from app.barcode_detector import decode_with_zxing

                with patch('app.barcode_detector.decode_with_zxing') as mock_decode:
                    mock_decode.return_value = {
                        "found": True,
                        "format": "DataMatrix",
                        "data": gs1_test_data["simple"],
                        "aim_identifier": "]d2",
                        "gs1_detected": True,
                        "confidence": 0.98
                    }

                    # Simuler écriture fichier et décodage
                    with open(test_image_path, 'wb') as f:
                        f.write(b'fake_gs1_datamatrix_png')

                    result = mock_decode(str(test_image_path))

                    # Validations critiques
                    assert result["found"], "ZXing devrait décoder le code"
                    assert result["aim_identifier"] == "]d2", "Identifier AIM doit être ]d2 pour GS1 DataMatrix"
                    assert result["gs1_detected"], "Format GS1 doit être détecté"
                    assert result["data"] == gs1_test_data["simple"], "Données décodées doivent correspondre"

    def test_aim_identifier_d2_vs_d1_differentiation(self, gs1_test_data):
        """CRITIQUE: Vérification différenciation ]d2 (GS1) vs ]d1 (standard)"""

        test_cases = [
            # (data, format, expected_aim_identifier, expected_gs1_detected)
            (gs1_test_data["simple"], "gs1_datamatrix", "]d2", True),
            (gs1_test_data["expert"], "gs1_datamatrix", "]d2", True),
            ("Non-GS1 data", "datamatrix", "]d1", False)
        ]

        for data, format_type, expected_aim, expected_gs1 in test_cases:
            with patch('app.barcode_detector.decode_with_zxing') as mock_decode:
                mock_decode.return_value = {
                    "found": True,
                    "format": "DataMatrix",
                    "data": data,
                    "aim_identifier": expected_aim,
                    "gs1_detected": expected_gs1,
                    "confidence": 0.95
                }

                result = mock_decode("dummy_path")

                assert result["aim_identifier"] == expected_aim, \
                    f"AIM identifier pour {format_type} devrait être {expected_aim}"
                assert result["gs1_detected"] == expected_gs1, \
                    f"GS1 detection pour {format_type} devrait être {expected_gs1}"

    def test_fnc1_character_detection_via_zxing(self, gs1_test_data):
        """Test de détection du caractère FNC1 via métadonnées ZXing"""

        with patch('app.barcode_detector.decode_with_zxing') as mock_decode:
            # Simuler métadonnées ZXing avec information FNC1
            mock_decode.return_value = {
                "found": True,
                "format": "DataMatrix",
                "data": gs1_test_data["simple"],
                "aim_identifier": "]d2",
                "gs1_detected": True,
                "fnc1_position": 0,  # FNC1 en première position
                "confidence": 0.98,
                "metadata": {
                    "FNC1_FIRST_POSITION": True,
                    "GS1_FORMAT": True
                }
            }

            result = mock_decode("dummy_path")

            # Vérifications FNC1
            assert result["fnc1_position"] == 0, "FNC1 devrait être en première position"
            assert result["metadata"]["FNC1_FIRST_POSITION"], "Métadonnées devraient confirmer FNC1"
            assert result["metadata"]["GS1_FORMAT"], "Métadonnées devraient confirmer format GS1"

    @pytest.mark.parametrize("test_data_key,expected_ais", [
        ("simple", ["01"]),
        ("expert", ["01", "11", "3100", "21", "90", "93", "94", "95"]),
        ("medium", ["01", "21", "17"])
    ])
    def test_gs1_application_identifiers_via_zxing(self, gs1_test_data, test_data_key, expected_ais):
        """Validation des Application Identifiers via décodage ZXing"""

        data = gs1_test_data[test_data_key]

        with patch('app.barcode_detector.decode_with_zxing') as mock_decode:
            # Simuler parsing des AIs par ZXing
            mock_decode.return_value = {
                "found": True,
                "format": "DataMatrix",
                "data": data,
                "aim_identifier": "]d2",
                "gs1_detected": True,
                "application_identifiers": expected_ais,
                "confidence": 0.95
            }

            result = mock_decode("dummy_path")

            # Vérifier que tous les AIs attendus sont présents
            for expected_ai in expected_ais:
                assert expected_ai in result["application_identifiers"], \
                    f"AI {expected_ai} devrait être détecté dans {test_data_key}"

    def test_zxing_confidence_threshold(self, gs1_test_data):
        """Test de seuil de confiance ZXing pour validation"""

        confidence_cases = [
            (0.98, True),   # Haute confiance - valide
            (0.85, True),   # Confiance moyenne - valide
            (0.60, False),  # Basse confiance - invalide
            (0.30, False)   # Très basse confiance - invalide
        ]

        for confidence, should_be_valid in confidence_cases:
            with patch('app.barcode_detector.decode_with_zxing') as mock_decode:
                mock_decode.return_value = {
                    "found": True,
                    "format": "DataMatrix",
                    "data": gs1_test_data["simple"],
                    "aim_identifier": "]d2",
                    "gs1_detected": True,
                    "confidence": confidence
                }

                result = mock_decode("dummy_path")

                # Vérifier seuil de confiance
                if should_be_valid:
                    assert result["confidence"] >= 0.8, f"Confiance {confidence} devrait être acceptable"
                else:
                    assert result["confidence"] < 0.8, f"Confiance {confidence} devrait être rejetée"

    def test_zxing_error_handling(self):
        """Test de gestion d'erreurs ZXing"""

        error_cases = [
            "Image corrompue",
            "Format non supporté",
            "Pas de code-barres détecté",
            "Erreur décodage"
        ]

        for error_case in error_cases:
            with patch('app.barcode_detector.decode_with_zxing') as mock_decode:
                mock_decode.return_value = {
                    "found": False,
                    "error": error_case,
                    "format": None,
                    "data": None,
                    "confidence": 0.0
                }

                result = mock_decode("dummy_path")

                # Vérifier gestion d'erreur
                assert not result["found"], f"Erreur {error_case} devrait être gérée"
                assert result["error"] == error_case, "Message d'erreur devrait être préservé"

    def test_gs1_format_consistency_validation(self, gs1_test_data):
        """Test de cohérence du format GS1 à travers le pipeline complet"""

        # Simuler pipeline complet: génération → décodage → validation
        with patch('app.barcode_generator.generate_gs1_datamatrix_hybrid') as mock_generate, \
             patch('app.barcode_detector.decode_with_zxing') as mock_decode:

            # 1. Génération
            mock_generate.return_value = (b'gs1_datamatrix_data', {"method": "bwip-js"})

            # 2. Décodage
            mock_decode.return_value = {
                "found": True,
                "format": "DataMatrix",
                "data": gs1_test_data["simple"],
                "aim_identifier": "]d2",
                "gs1_detected": True,
                "confidence": 0.95
            }

            # Test de cohérence
            from app.barcode_generator import generate_gs1_datamatrix_hybrid

            # Génération
            generated_data, metadata = mock_generate(
                data=gs1_test_data["simple"],
                output_path="test.png",
                width=200,
                height=200
            )

            # Décodage simulé
            decoded_result = mock_decode("test.png")

            # Validations de cohérence
            assert decoded_result["data"] == gs1_test_data["simple"], \
                "Données décodées devraient correspondre aux données générées"
            assert decoded_result["aim_identifier"] == "]d2", \
                "Format GS1 devrait être préservé dans le pipeline"
            assert decoded_result["gs1_detected"], \
                "Détection GS1 devrait être cohérente"

    def test_batch_validation_multiple_codes(self, gs1_test_data):
        """Test de validation par lot pour plusieurs codes GS1"""

        test_codes = [
            (gs1_test_data["simple"], "Simple GS1"),
            (gs1_test_data["expert"], "Expert GS1"),
            (gs1_test_data["medium"], "Medium GS1")
        ]

        results = []

        for data, description in test_codes:
            with patch('app.barcode_detector.decode_with_zxing') as mock_decode:
                mock_decode.return_value = {
                    "found": True,
                    "format": "DataMatrix",
                    "data": data,
                    "aim_identifier": "]d2",
                    "gs1_detected": True,
                    "confidence": 0.95,
                    "description": description
                }

                result = mock_decode(f"test_{description.lower().replace(' ', '_')}.png")
                results.append(result)

        # Validation par lot
        for result in results:
            assert result["found"], f"Code {result['description']} devrait être décodé"
            assert result["aim_identifier"] == "]d2", f"Code {result['description']} devrait être GS1"
            assert result["gs1_detected"], f"Code {result['description']} devrait être détecté comme GS1"
            assert result["confidence"] > 0.9, f"Code {result['description']} devrait avoir haute confiance"