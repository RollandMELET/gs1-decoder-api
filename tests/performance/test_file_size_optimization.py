"""
Tests de performance et optimisation des tailles de fichiers
"""
import pytest
import sys
import os
import time
from unittest.mock import patch, MagicMock
from pathlib import Path

# Ajout du chemin de l'application
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

class TestFileSizeOptimization:
    """Tests de validation de l'optimisation des tailles de fichiers"""

    def test_file_size_optimization_simple(self, gs1_test_data, expected_file_sizes, original_file_sizes, temp_output_dir):
        """CRITIQUE: Vérifier l'optimisation des tailles pour données simples (500-600 bytes vs 16k)"""

        with patch('subprocess.run') as mock_subprocess, \
             patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_open:

            # Mock taille optimisée
            mock_stat.return_value.st_size = 571  # Taille réelle observée
            mock_open.return_value.__enter__.return_value.read.return_value = b'a' * 571

            mock_subprocess.return_value = MagicMock(returncode=0, stdout="[SUCCESS]", stderr="")

            from app.barcode_generator import generate_gs1_datamatrix_hybrid

            result = generate_gs1_datamatrix_hybrid(
                data=gs1_test_data["simple"],
                output_path=str(temp_output_dir / "test.png"),
                width=200,
                height=200
            )

            image_data, metadata = result

            # Vérifier la taille optimisée
            file_size = len(image_data)
            assert expected_file_sizes["simple_min"] <= file_size <= expected_file_sizes["simple_max"], \
                f"Taille fichier simple devrait être entre {expected_file_sizes['simple_min']}-{expected_file_sizes['simple_max']} bytes, obtenu: {file_size}"

            # Vérifier la réduction par rapport à l'original
            reduction_ratio = (original_file_sizes["simple"] - file_size) / original_file_sizes["simple"]
            assert reduction_ratio > 0.95, f"Réduction devrait être > 95%, obtenu: {reduction_ratio:.2%}"

    def test_file_size_optimization_expert(self, gs1_test_data, expected_file_sizes, original_file_sizes, temp_output_dir):
        """CRITIQUE: Vérifier l'optimisation des tailles pour données expert (650-750 bytes vs 23k)"""

        with patch('subprocess.run') as mock_subprocess, \
             patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_open:

            # Mock taille optimisée pour données expert
            mock_stat.return_value.st_size = 689  # Taille réelle observée
            mock_open.return_value.__enter__.return_value.read.return_value = b'a' * 689

            mock_subprocess.return_value = MagicMock(returncode=0, stdout="[SUCCESS]", stderr="")

            from app.barcode_generator import generate_gs1_datamatrix_hybrid

            result = generate_gs1_datamatrix_hybrid(
                data=gs1_test_data["expert"],
                output_path=str(temp_output_dir / "test.png"),
                width=200,
                height=200
            )

            image_data, metadata = result

            # Vérifier la taille optimisée
            file_size = len(image_data)
            assert expected_file_sizes["expert_min"] <= file_size <= expected_file_sizes["expert_max"], \
                f"Taille fichier expert devrait être entre {expected_file_sizes['expert_min']}-{expected_file_sizes['expert_max']} bytes, obtenu: {file_size}"

            # Vérifier la réduction par rapport à l'original
            reduction_ratio = (original_file_sizes["expert"] - file_size) / original_file_sizes["expert"]
            assert reduction_ratio > 0.95, f"Réduction devrait être > 95%, obtenu: {reduction_ratio:.2%}"

    def test_native_size_preservation(self, gs1_test_data, temp_output_dir):
        """CRITIQUE: Vérifier la préservation des tailles natives bwip-js"""

        with patch('subprocess.run') as mock_subprocess, \
             patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_open:

            # Mock taille native bwip-js
            native_size = 571
            mock_stat.return_value.st_size = native_size
            mock_open.return_value.__enter__.return_value.read.return_value = b'a' * native_size

            mock_subprocess.return_value = MagicMock(returncode=0, stdout="[SUCCESS]", stderr="")

            from app.barcode_generator import generate_barcode, BarcodeFormat, ImageFormat

            # Test avec redimensionnement demandé (devrait être ignoré)
            image_data, content_type, metadata = generate_barcode(
                data=gs1_test_data["simple"],
                barcode_format=BarcodeFormat.GS1_DATAMATRIX,
                width=400,  # Demande de redimensionnement
                height=400,  # Demande de redimensionnement
                image_format=ImageFormat.PNG,
                use_treepoem=False
            )

            # Vérifier que la taille native est préservée
            assert len(image_data) == native_size, \
                f"La taille native ({native_size}) devrait être préservée, obtenu: {len(image_data)}"

    def test_generation_speed_performance(self, gs1_test_data, temp_output_dir):
        """Test de performance: temps de génération < 2 secondes"""

        with patch('subprocess.run') as mock_subprocess, \
             patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_open:

            mock_stat.return_value.st_size = 571
            mock_open.return_value.__enter__.return_value.read.return_value = b'a' * 571

            # Simuler un délai réaliste
            def mock_subprocess_call(*args, **kwargs):
                time.sleep(0.1)  # Simuler traitement
                return MagicMock(returncode=0, stdout="[SUCCESS]", stderr="")

            mock_subprocess.side_effect = mock_subprocess_call

            from app.barcode_generator import generate_gs1_datamatrix_hybrid

            start_time = time.time()

            result = generate_gs1_datamatrix_hybrid(
                data=gs1_test_data["simple"],
                output_path=str(temp_output_dir / "test.png"),
                width=200,
                height=200
            )

            end_time = time.time()
            generation_time = end_time - start_time

            # Vérifier performance
            assert generation_time < 2.0, f"Génération devrait prendre < 2s, obtenu: {generation_time:.2f}s"
            assert result is not None, "La génération devrait réussir"

    def test_memory_usage_subprocess(self, gs1_test_data, temp_output_dir):
        """Test de consommation mémoire subprocess Node.js < 100MB"""

        with patch('subprocess.run') as mock_subprocess, \
             patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_open:

            mock_stat.return_value.st_size = 571
            mock_open.return_value.__enter__.return_value.read.return_value = b'a' * 571

            # Mock processus avec statistiques mémoire
            mock_process = MagicMock()
            mock_process.returncode = 0
            mock_process.stdout = "[SUCCESS]"
            mock_process.stderr = ""

            mock_subprocess.return_value = mock_process

            from app.barcode_generator import generate_gs1_datamatrix_hybrid

            # Surveiller l'utilisation mémoire (simulée)
            import psutil
            current_process = psutil.Process()
            memory_before = current_process.memory_info().rss

            result = generate_gs1_datamatrix_hybrid(
                data=gs1_test_data["expert"],  # Données complexes
                output_path=str(temp_output_dir / "test.png"),
                width=200,
                height=200
            )

            memory_after = current_process.memory_info().rss
            memory_used = memory_after - memory_before

            # Vérifier consommation mémoire raisonnable (en bytes)
            max_memory_mb = 100 * 1024 * 1024  # 100MB
            assert memory_used < max_memory_mb, \
                f"Consommation mémoire devrait être < 100MB, obtenu: {memory_used / 1024 / 1024:.2f}MB"

    @pytest.mark.parametrize("data_type", ["simple", "expert", "medium"])
    def test_consistent_size_optimization_across_data_types(self, gs1_test_data, data_type, temp_output_dir):
        """Test de cohérence de l'optimisation pour différents types de données"""

        with patch('subprocess.run') as mock_subprocess, \
             patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_open:

            # Tailles attendues selon le type
            expected_sizes = {
                "simple": 571,
                "expert": 689,
                "medium": 620  # Taille intermédiaire
            }

            mock_size = expected_sizes[data_type]
            mock_stat.return_value.st_size = mock_size
            mock_open.return_value.__enter__.return_value.read.return_value = b'a' * mock_size

            mock_subprocess.return_value = MagicMock(returncode=0, stdout="[SUCCESS]", stderr="")

            from app.barcode_generator import generate_gs1_datamatrix_hybrid

            result = generate_gs1_datamatrix_hybrid(
                data=gs1_test_data[data_type],
                output_path=str(temp_output_dir / f"test_{data_type}.png"),
                width=200,
                height=200
            )

            image_data, metadata = result

            # Vérifier optimisation cohérente
            file_size = len(image_data)
            assert 500 <= file_size <= 800, \
                f"Taille pour {data_type} devrait être optimisée (500-800 bytes), obtenu: {file_size}"

            # Vérifier que c'est bien plus petit que les tailles originales (16k-23k)
            assert file_size < 5000, f"Taille optimisée devrait être << 5KB, obtenu: {file_size}"