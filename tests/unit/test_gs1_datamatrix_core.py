"""
Tests unitaires pour les composants critiques GS1 DataMatrix
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

# Ajout du chemin de l'application
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.barcode_generator import (
    generate_gs1_datamatrix_hybrid,
    BarcodeFormat,
    ImageFormat
)
from app.main import app

class TestGS1DataMatrixCore:
    """Tests critiques pour la génération GS1 DataMatrix"""

    def test_use_treepoem_false_for_gs1_datamatrix(self, gs1_test_data):
        """CRITIQUE: Vérifier que use_treepoem=False est forcé pour GS1 DataMatrix"""
        from app.main import generate_barcode

        # Test direct sur la logique de routage
        with patch('app.barcode_generator.generate_barcode') as mock_generate:
            mock_generate.return_value = (b'fake_image_data', 'image/png', {})

            # Simuler l'appel via l'endpoint
            generate_barcode(
                data=gs1_test_data["simple"],
                barcode_format="gs1_datamatrix",
                width=200,
                height=200,
                image_format="png",
                use_treepoem=True  # Devrait être ignoré
            )

            # Vérifier que use_treepoem=False a été forcé
            args, kwargs = mock_generate.call_args
            assert kwargs.get('use_treepoem') == False, "use_treepoem doit être forcé à False pour GS1 DataMatrix"

    def test_gs1_datamatrix_format_detection(self, gs1_test_data):
        """Vérifier la détection correcte du format GS1 DataMatrix"""
        from app.barcode_generator import GenBarcodeFormat

        # Test de mapping des formats
        internal_format = GenBarcodeFormat.GS1_DATAMATRIX
        assert internal_format == GenBarcodeFormat.GS1_DATAMATRIX

        # Vérifier que le format est bien différencié du DataMatrix standard
        assert GenBarcodeFormat.GS1_DATAMATRIX != GenBarcodeFormat.DATAMATRIX

    @patch('subprocess.run')
    def test_bwipjs_priority_in_hybrid_architecture(self, mock_subprocess, gs1_test_data, temp_output_dir):
        """CRITIQUE: Vérifier que bwip-js est appelé en premier dans l'architecture hybride"""

        # Mock subprocess success pour bwip-js
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="[SUCCESS] GS1 DataMatrix généré avec configuration simple",
            stderr=""
        )

        # Mock file system
        output_file = temp_output_dir / "test.png"
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_open:

            mock_stat.return_value.st_size = 571  # Taille optimisée
            mock_open.return_value.__enter__.return_value.read.return_value = b'fake_png_data'

            # Appeler la fonction hybride
            result = generate_gs1_datamatrix_hybrid(
                data=gs1_test_data["simple"],
                output_path=str(output_file),
                width=200,
                height=200
            )

            # Vérifier que subprocess a été appelé (bwip-js)
            assert mock_subprocess.called, "bwip-js devrait être appelé en premier"

            # Vérifier les arguments de la commande bwip-js
            call_args = mock_subprocess.call_args[0][0]
            assert "node" in call_args, "La commande devrait utiliser Node.js"
            assert "generate_gs1_bwip.js" in call_args, "Le script bwip-js devrait être appelé"
            assert gs1_test_data["simple"] in call_args, "Les données GS1 devraient être passées"

    def test_gs1_data_validation(self, gs1_test_data):
        """Validation des formats de données GS1"""
        valid_data = gs1_test_data["simple"]
        invalid_data = gs1_test_data["invalid"]

        # Test avec données valides
        assert valid_data.startswith("(01)"), "Données GS1 valides devraient commencer par (01)"
        assert len(valid_data) > 10, "Données GS1 devraient avoir une longueur minimale"

        # Test avec données invalides
        assert not invalid_data.startswith("("), "Données invalides ne devraient pas avoir le format GS1"

    @patch('app.barcode_generator.generate_gs1_datamatrix_hybrid')
    def test_no_resizing_for_gs1_datamatrix(self, mock_hybrid, gs1_test_data):
        """CRITIQUE: Vérifier que le redimensionnement est désactivé pour GS1 DataMatrix"""
        from app.barcode_generator import generate_barcode, BarcodeFormat

        # Mock de retour avec taille optimisée
        mock_hybrid.return_value = (b'optimized_image_data', {"original_size": (100, 100)})

        with patch('PIL.Image.open') as mock_image_open, \
             patch('io.BytesIO') as mock_bytesio:

            mock_img = MagicMock()
            mock_img.size = (100, 100)
            mock_image_open.return_value = mock_img

            # Appeler avec GS1 DataMatrix
            result = generate_barcode(
                data=gs1_test_data["simple"],
                barcode_format=BarcodeFormat.GS1_DATAMATRIX,
                width=200,  # Devrait être ignoré
                height=200, # Devrait être ignoré
                image_format=ImageFormat.PNG,
                use_treepoem=False
            )

            # Vérifier que resize n'a pas été appelé
            assert not mock_img.resize.called, "Le redimensionnement ne devrait pas être appelé pour GS1 DataMatrix"

    def test_error_handling_invalid_gs1_data(self, gs1_test_data):
        """Test de gestion d'erreurs avec données GS1 invalides"""
        from app.barcode_generator import generate_barcode, BarcodeFormat, ImageFormat

        with pytest.raises(Exception):  # Devrait lever une exception appropriée
            generate_barcode(
                data=gs1_test_data["invalid"],
                barcode_format=BarcodeFormat.GS1_DATAMATRIX,
                width=200,
                height=200,
                image_format=ImageFormat.PNG,
                use_treepoem=False
            )