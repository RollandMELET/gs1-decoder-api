"""
Configuration globale pour les tests pytest
"""
import pytest
import tempfile
import os
from pathlib import Path

@pytest.fixture
def test_data_dir():
    """Répertoire des données de test"""
    return Path(__file__).parent / "data"

@pytest.fixture
def temp_output_dir():
    """Répertoire temporaire pour les fichiers de sortie"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
def gs1_test_data():
    """Données GS1 de test standardisées"""
    return {
        "simple": "(01)12345678901234",
        "expert": "(01)03760423190005(11)250910(3100)012000(21)0000019C(90)7391023(93)DHA(94)UP(95)ENVELOPPE_NUE_4UF",
        "medium": "(01)12345678901234(21)ABC123(17)220630",
        "invalid": "invalid_gs1_data"
    }

@pytest.fixture
def expected_file_sizes():
    """Tailles de fichiers attendues (optimisées)"""
    return {
        "simple_min": 500,
        "simple_max": 600,
        "expert_min": 650,
        "expert_max": 750
    }

@pytest.fixture
def original_file_sizes():
    """Tailles de fichiers avant optimisation (référence régression)"""
    return {
        "simple": 16368,
        "expert": 22990
    }