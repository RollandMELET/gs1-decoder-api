"""
Tests d'intégration pour l'architecture hybride Python ↔ Node.js
"""
import pytest
import sys
import os
import subprocess
import tempfile
from unittest.mock import patch, MagicMock, call
from pathlib import Path

# Ajout du chemin de l'application
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.barcode_generator import generate_gs1_datamatrix_hybrid

class TestHybridArchitecture:
    """Tests d'intégration pour l'architecture hybride bwip-js → fallbacks"""

    def test_subprocess_communication_python_to_nodejs(self, gs1_test_data, temp_output_dir):
        """CRITIQUE: Communication Python → Node.js subprocess"""

        output_file = temp_output_dir / "test_subprocess.png"

        with patch('subprocess.run') as mock_subprocess, \
             patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_open:

            # Mock subprocess success
            mock_subprocess.return_value = MagicMock(
                returncode=0,
                stdout="[SUCCESS] GS1 DataMatrix généré avec configuration simple",
                stderr=""
            )

            mock_stat.return_value.st_size = 571
            mock_open.return_value.__enter__.return_value.read.return_value = b'fake_png_data'

            # Appeler la fonction hybride
            result = generate_gs1_datamatrix_hybrid(
                data=gs1_test_data["simple"],
                output_path=str(output_file),
                width=200,
                height=200
            )

            # Vérifier que subprocess a été appelé
            assert mock_subprocess.called, "subprocess.run() devrait être appelé"

            # Vérifier les arguments de la commande
            call_args = mock_subprocess.call_args[0][0]
            assert isinstance(call_args, list), "Arguments devraient être une liste"
            assert "node" in call_args[0], "Premier argument devrait être 'node'"
            assert "generate_gs1_bwip.js" in call_args[1], "Script Node.js devrait être appelé"
            assert gs1_test_data["simple"] in call_args, "Données GS1 devraient être passées"
            assert str(output_file) in call_args, "Fichier de sortie devrait être spécifié"

            # Vérifier le résultat
            image_data, metadata = result
            assert image_data == b'fake_png_data', "Données image devraient être retournées"
            assert isinstance(metadata, dict), "Métadonnées devraient être un dictionnaire"

    def test_nodejs_script_execution_success(self, gs1_test_data, temp_output_dir):
        """Test d'exécution réussie du script Node.js"""

        output_file = temp_output_dir / "test_nodejs.png"

        with patch('subprocess.run') as mock_subprocess, \
             patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_open:

            # Mock logs détaillés de bwip-js
            mock_subprocess.return_value = MagicMock(
                returncode=0,
                stdout="""[DEBUG] bwip-js: Génération GS1 DataMatrix SIMPLIFIÉE
[DEBUG] Données brutes: (01)12345678901234
[DEBUG] Sortie: test_nodejs.png
[SUCCESS] GS1 DataMatrix généré avec configuration simple
[SUCCESS] Fichier: test_nodejs.png (571 bytes)""",
                stderr=""
            )

            mock_stat.return_value.st_size = 571
            mock_open.return_value.__enter__.return_value.read.return_value = b'optimized_png_data'

            result = generate_gs1_datamatrix_hybrid(
                data=gs1_test_data["simple"],
                output_path=str(output_file),
                width=200,
                height=200
            )

            # Vérifier l'exécution
            assert mock_subprocess.called
            assert mock_subprocess.return_value.returncode == 0

            # Vérifier le résultat
            image_data, metadata = result
            assert len(image_data) == 571, "Taille optimisée attendue"

    def test_hybrid_fallback_chain_order(self, gs1_test_data, temp_output_dir):
        """CRITIQUE: Vérifier l'ordre des fallbacks bwip-js → treepoem → zint → dmtxwrite"""

        output_file = temp_output_dir / "test_fallback.png"

        # Simuler échec bwip-js pour déclencher fallbacks
        with patch('subprocess.run') as mock_subprocess, \
             patch('app.barcode_generator.generate_with_treepoem') as mock_treepoem:

            # Premier appel (bwip-js) échoue
            mock_subprocess.return_value = MagicMock(
                returncode=1,
                stdout="",
                stderr="Error: Node.js script failed"
            )

            # Deuxième appel (treepoem) réussit
            mock_treepoem.return_value = (b'treepoem_fallback_data', {"fallback": "treepoem"})

            result = generate_gs1_datamatrix_hybrid(
                data=gs1_test_data["simple"],
                output_path=str(output_file),
                width=200,
                height=200
            )

            # Vérifier que bwip-js a été essayé en premier
            assert mock_subprocess.called, "bwip-js devrait être essayé en premier"

            # Vérifier que treepoem a été appelé en fallback
            assert mock_treepoem.called, "treepoem devrait être appelé en fallback"

            # Vérifier le résultat du fallback
            image_data, metadata = result
            assert image_data == b'treepoem_fallback_data', "Données du fallback devraient être retournées"
            assert metadata.get("fallback") == "treepoem", "Métadonnées de fallback devraient être présentes"

    def test_error_handling_subprocess_failure(self, gs1_test_data, temp_output_dir):
        """Test de gestion d'erreurs subprocess"""

        output_file = temp_output_dir / "test_error.png"

        with patch('subprocess.run') as mock_subprocess:
            # Simuler erreur subprocess
            mock_subprocess.side_effect = subprocess.CalledProcessError(
                returncode=1,
                cmd=["node", "generate_gs1_bwip.js"],
                stderr="Script execution failed"
            )

            # Vérifier que l'erreur est gérée
            with pytest.raises(Exception):  # Devrait lever une exception appropriée
                generate_gs1_datamatrix_hybrid(
                    data=gs1_test_data["simple"],
                    output_path=str(output_file),
                    width=200,
                    height=200
                )

    def test_timeout_management(self, gs1_test_data, temp_output_dir):
        """Test de gestion des timeouts subprocess"""

        output_file = temp_output_dir / "test_timeout.png"

        with patch('subprocess.run') as mock_subprocess:
            # Simuler timeout
            mock_subprocess.side_effect = subprocess.TimeoutExpired(
                cmd=["node", "generate_gs1_bwip.js"],
                timeout=30
            )

            # Vérifier que le timeout est géré
            with pytest.raises(Exception):  # Devrait lever une exception de timeout
                generate_gs1_datamatrix_hybrid(
                    data=gs1_test_data["simple"],
                    output_path=str(output_file),
                    width=200,
                    height=200
                )

    def test_file_system_integration(self, gs1_test_data, temp_output_dir):
        """Test d'intégration avec le système de fichiers"""

        output_file = temp_output_dir / "test_filesystem.png"

        with patch('subprocess.run') as mock_subprocess:
            # Mock subprocess qui crée vraiment un fichier
            def create_mock_file(*args, **kwargs):
                # Créer le fichier de sortie
                with open(output_file, 'wb') as f:
                    f.write(b'mock_file_content')
                return MagicMock(returncode=0, stdout="[SUCCESS]", stderr="")

            mock_subprocess.side_effect = create_mock_file

            result = generate_gs1_datamatrix_hybrid(
                data=gs1_test_data["simple"],
                output_path=str(output_file),
                width=200,
                height=200
            )

            # Vérifier que le fichier a été créé
            assert output_file.exists(), "Le fichier de sortie devrait être créé"

            # Vérifier le contenu
            image_data, metadata = result
            assert image_data == b'mock_file_content', "Contenu du fichier devrait correspondre"

    def test_multiple_data_formats_integration(self, gs1_test_data, temp_output_dir):
        """Test d'intégration avec différents formats de données GS1"""

        test_cases = [
            ("simple", gs1_test_data["simple"], 571),
            ("expert", gs1_test_data["expert"], 689),
            ("medium", gs1_test_data["medium"], 620)
        ]

        for case_name, data, expected_size in test_cases:
            output_file = temp_output_dir / f"test_{case_name}.png"

            with patch('subprocess.run') as mock_subprocess, \
                 patch('pathlib.Path.exists', return_value=True), \
                 patch('pathlib.Path.stat') as mock_stat, \
                 patch('builtins.open', create=True) as mock_open:

                mock_stat.return_value.st_size = expected_size
                mock_open.return_value.__enter__.return_value.read.return_value = b'a' * expected_size

                mock_subprocess.return_value = MagicMock(returncode=0, stdout="[SUCCESS]", stderr="")

                result = generate_gs1_datamatrix_hybrid(
                    data=data,
                    output_path=str(output_file),
                    width=200,
                    height=200
                )

                # Vérifier que chaque format est traité correctement
                image_data, metadata = result
                assert len(image_data) == expected_size, f"Taille pour {case_name} devrait être {expected_size}"

                # Vérifier que les bonnes données ont été passées
                call_args = mock_subprocess.call_args[0][0]
                assert data in call_args, f"Données {case_name} devraient être passées au script"

    @patch('app.barcode_generator.generate_with_treepoem')
    @patch('app.barcode_generator.generate_with_zint')
    @patch('app.barcode_generator.generate_with_dmtxwrite')
    def test_complete_fallback_chain_execution(self, mock_dmtxwrite, mock_zint, mock_treepoem, gs1_test_data, temp_output_dir):
        """Test complet de la chaîne de fallbacks"""

        output_file = temp_output_dir / "test_complete_fallback.png"

        # Configurer tous les fallbacks pour échouer sauf le dernier
        with patch('subprocess.run') as mock_subprocess:
            # bwip-js échoue
            mock_subprocess.return_value = MagicMock(returncode=1, stderr="bwip-js failed")

            # treepoem échoue
            mock_treepoem.side_effect = Exception("treepoem failed")

            # zint échoue
            mock_zint.side_effect = Exception("zint failed")

            # dmtxwrite réussit
            mock_dmtxwrite.return_value = (b'dmtxwrite_final_data', {"fallback": "dmtxwrite"})

            result = generate_gs1_datamatrix_hybrid(
                data=gs1_test_data["simple"],
                output_path=str(output_file),
                width=200,
                height=200
            )

            # Vérifier que tous les fallbacks ont été essayés dans l'ordre
            assert mock_subprocess.called, "bwip-js devrait être essayé en premier"
            assert mock_treepoem.called, "treepoem devrait être essayé en deuxième"
            assert mock_zint.called, "zint devrait être essayé en troisième"
            assert mock_dmtxwrite.called, "dmtxwrite devrait être essayé en dernier"

            # Vérifier le résultat final
            image_data, metadata = result
            assert image_data == b'dmtxwrite_final_data', "Données finales devraient venir de dmtxwrite"
            assert metadata.get("fallback") == "dmtxwrite", "Métadonnées devraient indiquer le fallback utilisé"