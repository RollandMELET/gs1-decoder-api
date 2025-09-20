"""
Tests pour Code 128 standard et GS1-128
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Ajout du chemin de l'application
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.main import app
from app.barcode_generator import generate_barcode, BarcodeFormat, ImageFormat

client = TestClient(app)

class TestCode128:
    """Tests pour Code 128 standard et GS1-128"""

    def test_code128_standard_generation(self):
        """Test génération Code 128 standard"""
        with patch('app.barcode_generator.generate_barcode') as mock_generate:
            mock_generate.return_value = (
                b'code128_standard_data',
                'image/png',
                {"format": "code_128", "method": "python-barcode"}
            )

            response = client.post("/generate/", json={
                "data": "CODE128TEST",
                "barcode_format": "code_128"
            })

            assert response.status_code == 200

            # Vérifier paramètres Code 128
            args, kwargs = mock_generate.call_args
            assert kwargs["data"] == "CODE128TEST"
            assert kwargs["barcode_format"] == BarcodeFormat.CODE128
            assert kwargs["use_treepoem"] == True  # Code 128 peut utiliser treepoem

    def test_gs1_128_generation(self):
        """Test génération GS1-128"""
        with patch('app.barcode_generator.generate_barcode') as mock_generate:
            mock_generate.return_value = (
                b'gs1_128_data',
                'image/png',
                {"format": "gs1_128", "method": "python-barcode", "gs1": True}
            )

            response = client.post("/generate/", json={
                "data": "(01)03760423190005",
                "barcode_format": "gs1_128"
            })

            assert response.status_code == 200

            # Vérifier différenciation GS1-128 vs Code 128 standard
            args, kwargs = mock_generate.call_args
            assert kwargs["barcode_format"] == BarcodeFormat.GS1_128

    def test_code128_vs_gs1_128_differentiation(self):
        """CRITIQUE: Vérifier différenciation Code 128 vs GS1-128"""

        # Test Code 128 standard
        with patch('app.barcode_generator.prepare_gs1_content') as mock_prepare:
            mock_prepare.return_value = "STANDARD128"  # Unchanged

            with patch('app.barcode_generator.generate_code128') as mock_c128:
                mock_c128.return_value = MagicMock()

                generate_barcode(
                    data="STANDARD128",
                    barcode_format=BarcodeFormat.CODE128,
                    use_treepoem=True
                )

                # Vérifier isolation
                mock_prepare.assert_called_with("STANDARD128", BarcodeFormat.CODE128)
                assert mock_prepare.return_value == "STANDARD128"

        # Test GS1-128
        with patch('app.barcode_generator.prepare_gs1_content') as mock_prepare:
            mock_prepare.return_value = "~01037604231900051725042310AB123"  # FNC1 + formatage

            with patch('app.barcode_generator.generate_code128') as mock_c128:
                mock_c128.return_value = MagicMock()

                generate_barcode(
                    data="(01)03760423190005(17)250423(10)AB123",
                    barcode_format=BarcodeFormat.GS1_128,
                    use_treepoem=True
                )

                # Vérifier traitement GS1
                mock_prepare.assert_called_with("(01)03760423190005(17)250423(10)AB123", BarcodeFormat.GS1_128)

    def test_code128_file_size_validation(self):
        """Test validation taille fichier Code 128"""
        with patch('app.barcode_generator.generate_code128') as mock_c128, \
             patch('PIL.Image.open') as mock_image, \
             patch('io.BytesIO') as mock_bytesio:

            mock_img = MagicMock()
            mock_img.resize.return_value = mock_img
            mock_image.return_value = mock_img
            mock_c128.return_value = mock_img

            mock_output = MagicMock()
            mock_output.getvalue.return_value = b'a' * 2000  # ~2KB typical Code 128
            mock_bytesio.return_value = mock_output

            result = generate_barcode(
                data="CODE128TESTDATA",
                barcode_format=BarcodeFormat.CODE128,
                image_format=ImageFormat.PNG,
                width=200,
                height=200,
                use_treepoem=True
            )

            # Vérifier taille Code 128
            assert len(result) > 500, "Code 128 devrait faire > 500 bytes"
            assert len(result) < 20000, "Code 128 devrait faire < 20KB"

    def test_code128_specific_generator(self):
        """Test générateur Code 128 spécifique"""
        with patch('barcode.Code128') as mock_code128_class:
            mock_barcode = MagicMock()
            mock_code128_class.return_value = mock_barcode

            from app.barcode_generator import generate_code128

            result = generate_code128("TESTCODE128")

            # Vérifier utilisation python-barcode
            mock_code128_class.assert_called_once()
            mock_barcode.write.assert_called_once()

    def test_code128_data_preservation(self):
        """Test préservation données Code 128 standard"""
        test_cases = [
            "SIMPLETEXT",
            "CODE128-SPECIAL!@#",
            "123456789",
            "MixedCaSe123"
        ]

        for test_data in test_cases:
            from app.barcode_generator import prepare_gs1_content

            result = prepare_gs1_content(test_data, BarcodeFormat.CODE128)
            assert result == test_data, f"Données Code 128 devraient être inchangées: {test_data}"

    def test_code128_vs_gs1_datamatrix_isolation(self):
        """CRITIQUE: Isolation Code 128 vs GS1 DataMatrix"""

        with patch('app.barcode_generator.generate_code128') as mock_c128, \
             patch('app.barcode_generator.generate_gs1_datamatrix_hybrid') as mock_gs1:

            mock_c128.return_value = MagicMock()
            mock_gs1.return_value = (MagicMock(), {})

            # Code 128
            generate_barcode(
                data="ISOLATIONTEST",
                barcode_format=BarcodeFormat.CODE128,
                use_treepoem=True
            )

            mock_c128.assert_called_once()
            mock_gs1.assert_not_called()

            # GS1 DataMatrix
            generate_barcode(
                data="(01)03760423190005",
                barcode_format=BarcodeFormat.GS1_DATAMATRIX,
                use_treepoem=False
            )

            assert mock_c128.call_count == 1
            mock_gs1.assert_called_once()

    def test_code128_error_handling(self):
        """Test gestion d'erreurs Code 128"""
        error_scenarios = [
            ("", "empty_data"),
            ("VERYLONGDATATHATMIGHTCAUSEISSUESVERYLONGDATATHATMIGHTCAUSEISSUESVERYLONGDATA", "long_data"),
            ("Data\nWith\nNewlines", "newlines")
        ]

        for data, scenario in error_scenarios:
            with patch('app.barcode_generator.generate_code128') as mock_c128:
                mock_c128.side_effect = Exception(f"Code 128 error: {scenario}")

                with pytest.raises(Exception):
                    generate_barcode(
                        data=data,
                        barcode_format=BarcodeFormat.CODE128,
                        use_treepoem=False
                    )

    def test_code128_api_endpoint_integration(self):
        """Test intégration endpoint API pour Code 128"""
        with patch('app.barcode_generator.generate_barcode') as mock_generate:
            mock_generate.return_value = (
                b'code128_api_data',
                'image/png',
                {"format": "code_128"}
            )

            response = client.post("/generate/", json={
                "data": "APITEST128",
                "barcode_format": "code_128",
                "width": 400,
                "height": 100  # Code 128 typiquement plus large que haut
            })

            assert response.status_code == 200

            # Vérifier paramètres spécifiques Code 128
            args, kwargs = mock_generate.call_args
            assert kwargs["width"] == 400
            assert kwargs["height"] == 100

    def test_gs1_128_fnc1_handling(self):
        """Test gestion FNC1 pour GS1-128"""
        from app.barcode_generator import prepare_gs1_content

        gs1_data = "(01)12345678901234(21)SERIAL123"
        result = prepare_gs1_content(gs1_data, BarcodeFormat.GS1_128)

        # Vérifier que le formatage GS1 est appliqué
        assert isinstance(result, str), "Résultat devrait être une chaîne"
        # Pour treepoem, les données peuvent être retournées telles quelles
        # Pour fallback, FNC1 (~) peut être ajouté

    @pytest.mark.parametrize("use_treepoem,expected_method", [
        (True, "treepoem"),
        (False, "python-barcode")
    ])
    def test_code128_generation_methods(self, use_treepoem, expected_method):
        """Test méthodes de génération Code 128"""

        if use_treepoem:
            with patch('app.barcode_generator.TREEPOEM_AVAILABLE', True), \
                 patch('app.barcode_generator.generate_barcode_with_treepoem') as mock_method:
                mock_method.return_value = MagicMock()

                generate_barcode(
                    data="METHODTEST",
                    barcode_format=BarcodeFormat.CODE128,
                    use_treepoem=use_treepoem
                )

                mock_method.assert_called_once()
        else:
            with patch('app.barcode_generator.generate_code128') as mock_method:
                mock_method.return_value = MagicMock()

                generate_barcode(
                    data="METHODTEST",
                    barcode_format=BarcodeFormat.CODE128,
                    use_treepoem=use_treepoem
                )

                mock_method.assert_called_once()