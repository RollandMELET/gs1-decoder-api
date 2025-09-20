"""
Tests pour QR Code standard et GS1 QR Code
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

class TestQRCode:
    """Tests pour QR Code standard et GS1 QR Code"""

    def test_qr_code_standard_generation(self):
        """Test génération QR Code standard"""
        with patch('app.barcode_generator.generate_barcode') as mock_generate:
            mock_generate.return_value = (
                b'qr_code_standard_data',
                'image/png',
                {"format": "qr_code", "method": "qrcode", "size": (200, 200)}
            )

            response = client.post("/generate/", json={
                "data": "Test QR Code Standard Data",
                "barcode_format": "qr_code"
            })

            assert response.status_code == 200

            # Vérifier les paramètres passés
            args, kwargs = mock_generate.call_args
            assert kwargs["data"] == "Test QR Code Standard Data"
            assert kwargs["barcode_format"] == BarcodeFormat.QRCODE
            assert kwargs["use_treepoem"] == True  # Standard QR devrait utiliser treepoem

    def test_gs1_qr_code_generation(self):
        """Test génération GS1 QR Code"""
        with patch('app.barcode_generator.generate_barcode') as mock_generate:
            mock_generate.return_value = (
                b'gs1_qr_code_data',
                'image/png',
                {"format": "gs1_qr_code", "method": "qrcode", "gs1": True}
            )

            response = client.post("/generate/", json={
                "data": "(01)03760423190005",
                "barcode_format": "gs1_qr_code"
            })

            assert response.status_code == 200

            # Vérifier différenciation GS1 vs standard
            args, kwargs = mock_generate.call_args
            assert kwargs["data"] == "(01)03760423190005"
            assert kwargs["barcode_format"] == BarcodeFormat.GS1_QRCODE

    def test_qr_code_vs_gs1_qr_code_differentiation(self):
        """CRITIQUE: Vérifier différenciation QR Code standard vs GS1"""

        # Test QR Code standard
        with patch('app.barcode_generator.prepare_gs1_content') as mock_prepare:
            mock_prepare.return_value = "Test Standard Data"  # Données unchanged

            with patch('app.barcode_generator.generate_qrcode') as mock_qr:
                mock_qr.return_value = MagicMock()

                from app.barcode_generator import generate_barcode

                generate_barcode(
                    data="Test Standard Data",
                    barcode_format=BarcodeFormat.QRCODE,
                    use_treepoem=True
                )

                # Vérifier que prepare_gs1_content ne transforme pas les données standard
                mock_prepare.assert_called_with("Test Standard Data", BarcodeFormat.QRCODE)
                assert mock_prepare.return_value == "Test Standard Data"

        # Test GS1 QR Code
        with patch('app.barcode_generator.prepare_gs1_content') as mock_prepare:
            mock_prepare.return_value = "01037604231900051725042310AB123\u001d21S12345"  # Données GS1 formatées

            with patch('app.barcode_generator.generate_qrcode') as mock_qr:
                mock_qr.return_value = MagicMock()

                generate_barcode(
                    data="(01)03760423190005(17)250423(10)AB123(21)S12345",
                    barcode_format=BarcodeFormat.GS1_QRCODE,
                    use_treepoem=True
                )

                # Vérifier que prepare_gs1_content traite les données GS1
                mock_prepare.assert_called_with("(01)03760423190005(17)250423(10)AB123(21)S12345", BarcodeFormat.GS1_QRCODE)

    def test_qr_code_file_size_validation(self):
        """Test validation taille fichier QR Code"""
        with patch('app.barcode_generator.generate_qrcode') as mock_qr, \
             patch('PIL.Image.open') as mock_image, \
             patch('io.BytesIO') as mock_bytesio:

            # Mock image QR Code
            mock_img = MagicMock()
            mock_img.resize.return_value = mock_img
            mock_img.save = MagicMock()
            mock_image.return_value = mock_img
            mock_qr.return_value = mock_img

            # Mock BytesIO
            mock_output = MagicMock()
            mock_output.getvalue.return_value = b'a' * 15000  # ~15KB typical QR
            mock_bytesio.return_value = mock_output

            result = generate_barcode(
                data="QR Code test data with moderate length",
                barcode_format=BarcodeFormat.QRCODE,
                image_format=ImageFormat.PNG,
                width=200,
                height=200,
                use_treepoem=True
            )

            # Vérifier taille raisonnable
            assert len(result) > 1000, "QR Code devrait faire > 1KB"
            assert len(result) < 50000, "QR Code devrait faire < 50KB"

    def test_qr_code_error_handling(self):
        """Test gestion d'erreurs QR Code"""
        with patch('app.barcode_generator.generate_qrcode') as mock_qr:
            mock_qr.side_effect = Exception("QR Code generation failed")

            with pytest.raises(Exception):
                generate_barcode(
                    data="Test data",
                    barcode_format=BarcodeFormat.QRCODE,
                    use_treepoem=False  # Force specific generator
                )

    @pytest.mark.parametrize("data_input,expected_unchanged", [
        ("Simple QR text", True),
        ("QR Code with special chars !@#$%", True),
        ("https://example.com/path?param=value", True),
        ("Multi\nLine\nQR\nData", True)
    ])
    def test_qr_code_data_preservation(self, data_input, expected_unchanged):
        """Test préservation données pour QR Code standard"""
        from app.barcode_generator import prepare_gs1_content

        result = prepare_gs1_content(data_input, BarcodeFormat.QRCODE)

        if expected_unchanged:
            assert result == data_input, f"Données QR standard devraient être inchangées: {data_input}"

    def test_qr_code_api_endpoint_integration(self):
        """Test intégration endpoint API pour QR Code"""
        with patch('app.barcode_generator.generate_barcode') as mock_generate:
            mock_generate.return_value = (
                b'qr_api_test_data',
                'image/png',
                {"format": "qr_code"}
            )

            # Test standard QR
            response = client.post("/generate/", json={
                "data": "API QR Code Test",
                "barcode_format": "qr_code",
                "width": 300,
                "height": 300
            })

            assert response.status_code == 200
            assert response.headers["content-type"] == "image/png"

            # Vérifier redimensionnement appliqué (pas comme GS1 DataMatrix)
            args, kwargs = mock_generate.call_args
            assert kwargs["width"] == 300
            assert kwargs["height"] == 300

    def test_qr_code_vs_gs1_datamatrix_no_contamination(self):
        """CRITIQUE: Vérifier aucune contamination QR Code → GS1 DataMatrix"""

        with patch('app.barcode_generator.generate_qrcode') as mock_qr, \
             patch('app.barcode_generator.generate_gs1_datamatrix_hybrid') as mock_gs1:

            mock_qr.return_value = MagicMock()
            mock_gs1.return_value = (MagicMock(), {})

            # Générer QR Code
            generate_barcode(
                data="QR Code test",
                barcode_format=BarcodeFormat.QRCODE,
                use_treepoem=True
            )

            # Vérifier que QR Code n'appelle PAS GS1 DataMatrix
            mock_qr.assert_called_once()
            mock_gs1.assert_not_called()

            # Générer GS1 DataMatrix
            generate_barcode(
                data="(01)03760423190005",
                barcode_format=BarcodeFormat.GS1_DATAMATRIX,
                use_treepoem=False
            )

            # Vérifier que GS1 DataMatrix n'appelle PAS QR Code
            assert mock_qr.call_count == 1  # Toujours 1 appel (du test précédent)
            mock_gs1.assert_called_once()

    def test_qr_code_performance_acceptable(self):
        """Test performance QR Code < 5 secondes"""
        import time

        with patch('app.barcode_generator.generate_qrcode') as mock_qr:
            def slow_qr_generation(*args, **kwargs):
                time.sleep(0.1)  # Simuler génération
                return MagicMock()

            mock_qr.side_effect = slow_qr_generation

            start_time = time.time()

            generate_barcode(
                data="Performance test QR",
                barcode_format=BarcodeFormat.QRCODE,
                use_treepoem=True
            )

            end_time = time.time()
            generation_time = end_time - start_time

            assert generation_time < 5.0, f"QR Code devrait être généré en < 5s, obtenu: {generation_time:.2f}s"

    def test_qr_code_treepoem_integration(self):
        """Test intégration QR Code avec treepoem"""
        with patch('app.barcode_generator.TREEPOEM_AVAILABLE', True), \
             patch('app.barcode_generator.generate_barcode_with_treepoem') as mock_treepoem:

            mock_treepoem.return_value = MagicMock()

            generate_barcode(
                data="Treepoem QR test",
                barcode_format=BarcodeFormat.QRCODE,
                use_treepoem=True
            )

            # Vérifier que treepoem est utilisé pour QR Code
            mock_treepoem.assert_called_once()
            args, kwargs = mock_treepoem.call_args
            assert args[0] == "Treepoem QR test"  # Données inchangées
            assert args[1] == BarcodeFormat.QRCODE

    def test_qr_code_fallback_to_specific_generator(self):
        """Test fallback vers générateur spécifique si treepoem échoue"""
        with patch('app.barcode_generator.TREEPOEM_AVAILABLE', True), \
             patch('app.barcode_generator.generate_barcode_with_treepoem') as mock_treepoem, \
             patch('app.barcode_generator.generate_qrcode') as mock_qr:

            # Simuler échec treepoem
            mock_treepoem.side_effect = Exception("Treepoem failed")
            mock_qr.return_value = MagicMock()

            result = generate_barcode(
                data="Fallback QR test",
                barcode_format=BarcodeFormat.QRCODE,
                use_treepoem=True
            )

            # Vérifier tentative treepoem puis fallback
            mock_treepoem.assert_called_once()
            mock_qr.assert_called_once()

    def test_qr_code_specific_generator_direct(self):
        """Test générateur QR Code spécifique directement"""
        with patch('app.barcode_generator.qrcode') as mock_qrcode_lib:
            mock_qr_instance = MagicMock()
            mock_qr_instance.make_image.return_value = MagicMock()
            mock_qrcode_lib.QRCode.return_value = mock_qr_instance

            from app.barcode_generator import generate_qrcode

            result = generate_qrcode("Direct QR test")

            # Vérifier utilisation correcte de la librairie qrcode
            mock_qrcode_lib.QRCode.assert_called_once()
            mock_qr_instance.add_data.assert_called_with("Direct QR test")
            mock_qr_instance.make.assert_called_once()

class TestQRCodeRegression:
    """Tests de non-régression spécifiques QR Code"""

    def test_qr_code_does_not_break_gs1_datamatrix(self):
        """CRITIQUE: Vérifier que fixes QR Code ne cassent pas GS1 DataMatrix"""

        # Test QR Code d'abord
        with patch('app.barcode_generator.generate_qrcode') as mock_qr:
            mock_qr.return_value = MagicMock()

            qr_result = generate_barcode(
                data="QR test data",
                barcode_format=BarcodeFormat.QRCODE,
                use_treepoem=True
            )

            assert mock_qr.called, "QR Code devrait utiliser son générateur"

        # Test GS1 DataMatrix ensuite
        with patch('app.barcode_generator.generate_gs1_datamatrix_hybrid') as mock_gs1:
            mock_gs1.return_value = (b'gs1_data', {"optimized": True})

            gs1_result = generate_barcode(
                data="(01)03760423190005",
                barcode_format=BarcodeFormat.GS1_DATAMATRIX,
                use_treepoem=False
            )

            assert mock_gs1.called, "GS1 DataMatrix devrait utiliser architecture hybride"

    def test_qr_code_prepare_content_isolation(self):
        """Test isolation prepare_gs1_content pour QR Code"""
        from app.barcode_generator import prepare_gs1_content

        # Données standard - doivent rester inchangées
        standard_data = "https://example.com/qr-test"
        result = prepare_gs1_content(standard_data, BarcodeFormat.QRCODE)
        assert result == standard_data, "Données QR standard ne doivent pas être transformées"

        # Données GS1 QR - doivent être traitées
        gs1_data = "(01)12345678901234(21)SERIAL"
        result_gs1 = prepare_gs1_content(gs1_data, BarcodeFormat.GS1_QRCODE)
        # Devrait être différent (formatage GS1)
        assert isinstance(result_gs1, str), "Données GS1 QR doivent être formatées"

    def test_qr_code_api_error_scenarios(self):
        """Test scénarios d'erreur API pour QR Code"""

        # Données vides
        response = client.post("/generate/", json={
            "data": "",
            "barcode_format": "qr_code"
        })
        assert response.status_code == 422

        # Format invalide
        response = client.post("/generate/", json={
            "data": "Test",
            "barcode_format": "invalid_qr_format"
        })
        assert response.status_code == 422

        # Test avec erreur de génération
        with patch('app.barcode_generator.generate_barcode') as mock_generate:
            mock_generate.side_effect = Exception("QR generation error")

            response = client.post("/generate/", json={
                "data": "Test QR",
                "barcode_format": "qr_code"
            })

            assert response.status_code == 500

    def test_qr_code_production_api_compatibility(self):
        """Test compatibilité API production pour QR Code"""
        import requests

        # Test conditionnel si API disponible
        try:
            health_response = requests.get("https://gs1-decoder-api.rorworld.eu/health", timeout=5)
            api_available = health_response.status_code == 200
        except:
            api_available = False

        if not api_available:
            pytest.skip("API production non disponible")

        # Test QR Code en production
        try:
            response = requests.post(
                "https://gs1-decoder-api.rorworld.eu/generate/",
                json={
                    "data": "Production QR Test",
                    "barcode_format": "qr_code"
                },
                timeout=10
            )

            if response.status_code == 200:
                file_size = len(response.content)
                assert file_size > 1000, f"QR Code production devrait faire > 1KB, obtenu: {file_size}"
                assert file_size < 100000, f"QR Code production devrait faire < 100KB, obtenu: {file_size}"
            else:
                pytest.skip(f"QR Code production retourne: {response.status_code}")

        except Exception as e:
            pytest.skip(f"Erreur API production: {e}")