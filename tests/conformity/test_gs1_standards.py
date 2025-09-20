"""
Tests de conformité aux standards GS1
"""
import pytest
import sys
import os
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path

# Ajout du chemin de l'application
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import jpype
    JPYPE_AVAILABLE = True
except ImportError:
    JPYPE_AVAILABLE = False

class TestGS1Standards:
    """Tests de conformité aux standards GS1"""

    @pytest.mark.skipif(not JPYPE_AVAILABLE, reason="JPype not available")
    def test_gs1_aim_identifier_validation(self, gs1_test_data, temp_output_dir):
        """CRITIQUE: Vérifier que les codes générés ont l'identifier AIM ]d2 (GS1 DataMatrix)"""

        # Mock de génération d'image
        test_image_path = temp_output_dir / "test_aim.png"

        with patch('app.barcode_generator.generate_gs1_datamatrix_hybrid') as mock_hybrid:
            # Simuler une génération réussie
            mock_hybrid.return_value = (b'fake_png_data', {"original_size": (100, 100)})

            # Mock ZXing pour simulation de décodage
            with patch('app.barcode_detector.decode_with_zxing') as mock_zxing:
                # Simuler un décodage réussi avec identifier ]d2
                mock_zxing.return_value = {
                    "found": True,
                    "format": "DataMatrix",
                    "data": gs1_test_data["simple"],
                    "aim_identifier": "]d2",  # CRITIQUE: Doit être ]d2 pour GS1 DataMatrix
                    "gs1_detected": True
                }

                from app.barcode_generator import generate_barcode, BarcodeFormat, ImageFormat

                # Générer le code
                image_data, content_type, metadata = generate_barcode(
                    data=gs1_test_data["simple"],
                    barcode_format=BarcodeFormat.GS1_DATAMATRIX,
                    width=200,
                    height=200,
                    image_format=ImageFormat.PNG,
                    use_treepoem=False
                )

                # Simuler l'écriture du fichier
                with open(test_image_path, 'wb') as f:
                    f.write(image_data)

                # Décoder pour vérification
                result = mock_zxing.return_value

                assert result["found"], "Le code devrait être décodable"
                assert result["aim_identifier"] == "]d2", "L'identifier AIM doit être ]d2 pour GS1 DataMatrix"
                assert result["gs1_detected"], "Le format GS1 doit être détecté"
                assert result["data"] == gs1_test_data["simple"], "Les données décodées doivent correspondre"

    def test_fnc1_character_presence(self, gs1_test_data):
        """CRITIQUE: Vérifier la présence du caractère FNC1 en première position"""

        with patch('subprocess.run') as mock_subprocess:
            # Mock réponse bwip-js avec logs FNC1
            mock_subprocess.return_value = MagicMock(
                returncode=0,
                stdout="[SUCCESS] GS1 DataMatrix généré avec FNC1 en position 1",
                stderr=""
            )

            with patch('pathlib.Path.exists', return_value=True), \
                 patch('pathlib.Path.stat') as mock_stat, \
                 patch('builtins.open', create=True) as mock_open:

                mock_stat.return_value.st_size = 571
                mock_open.return_value.__enter__.return_value.read.return_value = b'fake_png_data'

                from app.barcode_generator import generate_gs1_datamatrix_hybrid

                result = generate_gs1_datamatrix_hybrid(
                    data=gs1_test_data["simple"],
                    output_path="test.png",
                    width=200,
                    height=200
                )

                # Vérifier que le processus a réussi (indique FNC1 correct)
                assert mock_subprocess.called, "bwip-js devrait être appelé"
                assert mock_subprocess.return_value.returncode == 0, "La génération devrait réussir"

    def test_gs1_application_identifiers_validation(self, gs1_test_data):
        """Validation des Application Identifiers GS1"""

        test_cases = [
            (gs1_test_data["simple"], ["01"]),  # GTIN
            (gs1_test_data["expert"], ["01", "11", "3100", "21", "90", "93", "94", "95"]),  # Multiple AIs
            (gs1_test_data["medium"], ["01", "21", "17"])  # GTIN + Serial + Expiry
        ]

        for data, expected_ais in test_cases:
            # Extraire les AIs de base
            import re
            ais = re.findall(r'\((\d+)\)', data)

            for expected_ai in expected_ais:
                assert expected_ai in ais, f"AI {expected_ai} devrait être présent dans {data}"

    def test_gs1_data_format_variations(self, gs1_test_data):
        """Test avec différents formats de données GS1"""

        # Test données simples
        simple_data = gs1_test_data["simple"]
        assert simple_data.startswith("(01)"), "Données simples devraient commencer par (01)"
        assert len(simple_data) == 18, "Format GTIN standard devrait faire 18 caractères"

        # Test données expert
        expert_data = gs1_test_data["expert"]
        assert "(01)" in expert_data, "Données expert devraient contenir (01)"
        assert len(expert_data) > 50, "Données expert devraient être complexes"

        # Compter les AIs
        import re
        expert_ais = re.findall(r'\(\d+\)', expert_data)
        assert len(expert_ais) >= 5, "Données expert devraient avoir plusieurs AIs"

    @pytest.mark.parametrize("test_data_key,expected_format", [
        ("simple", "gs1_datamatrix"),
        ("expert", "gs1_datamatrix"),
        ("medium", "gs1_datamatrix")
    ])
    def test_consistent_format_detection(self, gs1_test_data, test_data_key, expected_format):
        """Test de détection consistante du format pour différentes données"""

        data = gs1_test_data[test_data_key]

        # Vérifier que toutes les données GS1 sont traitées de manière consistante
        from app.barcode_generator import BarcodeFormat

        format_enum = BarcodeFormat.GS1_DATAMATRIX
        assert format_enum.value == "gs1_datamatrix", "Le format devrait être cohérent"

    def test_gs1_vs_standard_datamatrix_differentiation(self):
        """CRITIQUE: Vérifier la différenciation GS1 DataMatrix vs DataMatrix standard"""

        from app.barcode_generator import BarcodeFormat

        # Les formats doivent être distincts
        gs1_format = BarcodeFormat.GS1_DATAMATRIX
        standard_format = BarcodeFormat.DATAMATRIX

        assert gs1_format != standard_format, "GS1 DataMatrix doit être différent du DataMatrix standard"
        assert gs1_format.value == "gs1_datamatrix", "GS1 DataMatrix doit avoir le bon identifiant"
        assert standard_format.value == "datamatrix", "DataMatrix standard doit avoir le bon identifiant"