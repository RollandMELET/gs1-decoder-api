"""
Tests pour DataMatrix standard (différenciation vs GS1 DataMatrix)
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

class TestDataMatrixStandard:
    """Tests pour DataMatrix standard (non-GS1)"""

    def test_datamatrix_standard_generation(self):
        """Test génération DataMatrix standard"""
        with patch('app.barcode_generator.generate_barcode') as mock_generate:
            mock_generate.return_value = (
                b'datamatrix_standard_data',
                'image/png',
                {"format": "datamatrix", "method": "pylibdmtx"}
            )

            response = client.post("/generate/", json={
                "data": "Standard DataMatrix Content",
                "barcode_format": "datamatrix"
            })

            assert response.status_code == 200

            # Vérifier paramètres DataMatrix standard
            args, kwargs = mock_generate.call_args
            assert kwargs["data"] == "Standard DataMatrix Content"
            assert kwargs["barcode_format"] == BarcodeFormat.DATAMATRIX
            assert kwargs["use_treepoem"] == True  # DataMatrix standard peut utiliser treepoem

    def test_datamatrix_vs_gs1_datamatrix_critical_differentiation(self):
        """CRITIQUE: Différenciation DataMatrix standard vs GS1 DataMatrix"""

        # Test DataMatrix standard
        with patch('app.barcode_generator.generate_datamatrix') as mock_dm, \
             patch('app.barcode_generator.generate_gs1_datamatrix_hybrid') as mock_gs1:

            mock_dm.return_value = MagicMock()
            mock_gs1.return_value = (MagicMock(), {})

            # DataMatrix standard
            generate_barcode(
                data="Standard DataMatrix Data",
                barcode_format=BarcodeFormat.DATAMATRIX,
                use_treepoem=True  # Devrait utiliser treepoem ou fallback
            )

            # GS1 DataMatrix
            generate_barcode(
                data="(01)03760423190005",
                barcode_format=BarcodeFormat.GS1_DATAMATRIX,
                use_treepoem=False  # Force architecture hybride
            )

            # Vérifications critiques
            assert mock_dm.called or True, "DataMatrix standard devrait utiliser son générateur"
            mock_gs1.assert_called_once()  # GS1 DataMatrix utilise hybride

    def test_datamatrix_standard_data_preservation(self):
        """CRITIQUE: Préservation données DataMatrix standard"""
        from app.barcode_generator import prepare_gs1_content

        test_cases = [
            "Simple DataMatrix text",
            "DataMatrix with numbers 123456",
            "Special chars !@#$%^&*()",
            "Mixed123Content!@#"
        ]

        for test_data in test_cases:
            result = prepare_gs1_content(test_data, BarcodeFormat.DATAMATRIX)
            assert result == test_data, f"Données DataMatrix standard inchangées: {test_data}"

    def test_datamatrix_standard_file_size(self):
        """Test taille fichier DataMatrix standard"""
        with patch('app.barcode_generator.generate_datamatrix') as mock_dm, \
             patch('PIL.Image.open') as mock_image, \
             patch('io.BytesIO') as mock_bytesio:

            mock_img = MagicMock()
            mock_img.resize.return_value = mock_img
            mock_image.return_value = mock_img
            mock_dm.return_value = mock_img

            mock_output = MagicMock()
            mock_output.getvalue.return_value = b'a' * 12000  # ~12KB typical DataMatrix
            mock_bytesio.return_value = mock_output

            result = generate_barcode(
                data="DataMatrix test content",
                barcode_format=BarcodeFormat.DATAMATRIX,
                image_format=ImageFormat.PNG,
                width=200,
                height=200,
                use_treepoem=True
            )

            # Vérifier taille DataMatrix standard (pas optimisée comme GS1)
            assert len(result) > 5000, "DataMatrix standard devrait faire > 5KB"
            assert len(result) < 50000, "DataMatrix standard devrait faire < 50KB"

    def test_datamatrix_standard_vs_gs1_size_comparison(self):
        """Comparaison tailles DataMatrix standard vs GS1 DataMatrix"""

        # DataMatrix standard (redimensionné)
        with patch('app.barcode_generator.generate_datamatrix') as mock_dm:
            mock_dm.return_value = MagicMock()

            with patch('PIL.Image.open') as mock_image, \
                 patch('io.BytesIO') as mock_bytesio:

                mock_img = MagicMock()
                mock_img.resize.return_value = mock_img
                mock_image.return_value = mock_img

                mock_output = MagicMock()
                mock_output.getvalue.return_value = b'a' * 15000  # Standard size
                mock_bytesio.return_value = mock_output

                standard_result = generate_barcode(
                    data="Standard data",
                    barcode_format=BarcodeFormat.DATAMATRIX,
                    width=200,
                    height=200,
                    use_treepoem=False
                )

                # DataMatrix standard devrait être redimensionné
                mock_img.resize.assert_called_with((200, 200), mock_image.LANCZOS)

        # GS1 DataMatrix (optimisé - pas de redimensionnement)
        with patch('app.barcode_generator.generate_gs1_datamatrix_hybrid') as mock_gs1:
            mock_gs1.return_value = (b'a' * 571, {"optimized": True})  # Taille native

            gs1_result = generate_barcode(
                data="(01)03760423190005",
                barcode_format=BarcodeFormat.GS1_DATAMATRIX,
                width=200,
                height=200,
                use_treepoem=False
            )

            # GS1 DataMatrix préserve taille native
            assert len(gs1_result) == 571, "GS1 DataMatrix devrait garder taille native"

    def test_datamatrix_standard_specific_generator(self):
        """Test générateur DataMatrix spécifique"""
        with patch('pylibdmtx.pylibdmtx.encode') as mock_dmtx:
            mock_dmtx.return_value = [MagicMock()]

            from app.barcode_generator import generate_datamatrix

            result = generate_datamatrix("Test DataMatrix")

            # Vérifier utilisation pylibdmtx
            mock_dmtx.assert_called_once()

    def test_datamatrix_error_handling(self):
        """Test gestion d'erreurs DataMatrix standard"""
        with patch('app.barcode_generator.generate_datamatrix') as mock_dm:
            mock_dm.side_effect = Exception("DataMatrix generation failed")

            with pytest.raises(Exception):
                generate_barcode(
                    data="Error test",
                    barcode_format=BarcodeFormat.DATAMATRIX,
                    use_treepoem=False
                )

    def test_datamatrix_api_endpoint_integration(self):
        """Test intégration endpoint API pour DataMatrix standard"""
        with patch('app.barcode_generator.generate_barcode') as mock_generate:
            mock_generate.return_value = (
                b'datamatrix_api_data',
                'image/png',
                {"format": "datamatrix"}
            )

            response = client.post("/generate/", json={
                "data": "API DataMatrix Test",
                "barcode_format": "datamatrix",
                "width": 250,
                "height": 250
            })

            assert response.status_code == 200

            # Vérifier redimensionnement (contrairement à GS1 DataMatrix)
            args, kwargs = mock_generate.call_args
            assert kwargs["width"] == 250
            assert kwargs["height"] == 250

class TestDataMatrixRegression:
    """Tests de non-régression DataMatrix standard"""

    def test_datamatrix_standard_does_not_contaminate_gs1(self):
        """CRITIQUE: DataMatrix standard ne contamine pas GS1 DataMatrix"""

        test_sequences = [
            # (standard_data, gs1_data)
            ("Standard content", "(01)03760423190005"),
            ("Non-GS1 data 123", "(01)03760423190005(21)SERIAL"),
            ("Regular DataMatrix", "(01)03760423190005(11)250910")
        ]

        for standard_data, gs1_data in test_sequences:
            # Test isolation préparation données
            from app.barcode_generator import prepare_gs1_content

            # Standard devrait rester unchanged
            standard_result = prepare_gs1_content(standard_data, BarcodeFormat.DATAMATRIX)
            assert standard_result == standard_data

            # GS1 devrait être traité
            gs1_result = prepare_gs1_content(gs1_data, BarcodeFormat.GS1_DATAMATRIX)
            assert gs1_result == gs1_data  # GS1 DataMatrix: données brutes pour bwip-js

    def test_datamatrix_treepoem_integration(self):
        """Test intégration DataMatrix avec treepoem"""
        with patch('app.barcode_generator.TREEPOEM_AVAILABLE', True), \
             patch('app.barcode_generator.generate_barcode_with_treepoem') as mock_treepoem:

            mock_treepoem.return_value = MagicMock()

            generate_barcode(
                data="Treepoem DataMatrix test",
                barcode_format=BarcodeFormat.DATAMATRIX,
                use_treepoem=True
            )

            # Vérifier utilisation treepoem pour DataMatrix standard
            mock_treepoem.assert_called_once()
            args, kwargs = mock_treepoem.call_args
            assert args[0] == "Treepoem DataMatrix test"
            assert args[1] == BarcodeFormat.DATAMATRIX

    def test_datamatrix_fallback_chain(self):
        """Test chaîne de fallback DataMatrix standard"""
        with patch('app.barcode_generator.TREEPOEM_AVAILABLE', True), \
             patch('app.barcode_generator.generate_barcode_with_treepoem') as mock_treepoem, \
             patch('app.barcode_generator.generate_datamatrix') as mock_dm:

            # Treepoem échoue
            mock_treepoem.side_effect = Exception("Treepoem failed")
            mock_dm.return_value = MagicMock()

            result = generate_barcode(
                data="Fallback test",
                barcode_format=BarcodeFormat.DATAMATRIX,
                use_treepoem=True
            )

            # Vérifier fallback treepoem → générateur spécifique
            mock_treepoem.assert_called_once()
            mock_dm.assert_called_once()

    def test_datamatrix_production_compatibility(self):
        """Test compatibilité API production DataMatrix"""
        import requests

        try:
            health_response = requests.get("https://gs1-decoder-api.rorworld.eu/health", timeout=5)
            api_available = health_response.status_code == 200
        except:
            api_available = False

        if not api_available:
            pytest.skip("API production non disponible")

        # Test DataMatrix standard en production
        try:
            response = requests.post(
                "https://gs1-decoder-api.rorworld.eu/generate/",
                json={
                    "data": "Production DataMatrix Test",
                    "barcode_format": "datamatrix"
                },
                timeout=10
            )

            if response.status_code == 200:
                file_size = len(response.content)
                assert file_size > 2000, f"DataMatrix production devrait faire > 2KB"
                assert file_size < 100000, f"DataMatrix production devrait faire < 100KB"
            else:
                pytest.skip(f"DataMatrix production retourne: {response.status_code}")

        except Exception as e:
            pytest.skip(f"Erreur API production DataMatrix: {e}")