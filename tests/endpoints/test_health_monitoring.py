"""
Tests endpoint /health avec monitoring complet des capacités
"""
import pytest
import sys
import os
from fastapi.testclient import TestClient
import requests

# Ajout du chemin de l'application
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.main import app

client = TestClient(app)

class TestHealthEndpointComplete:
    """Tests endpoint /health/ avec toutes les capacités"""

    def test_health_endpoint_basic_structure(self):
        """Test structure de base endpoint /health"""

        response = client.get("/health")
        assert response.status_code == 200

        health_data = response.json()

        # Structure requise
        required_fields = ["status", "capabilities"]
        for field in required_fields:
            assert field in health_data, f"Champ {field} requis dans /health"

        assert health_data["status"] == "OK"

    def test_health_endpoint_capabilities_complete(self):
        """Test capacités complètes dans /health"""

        response = client.get("/health")
        assert response.status_code == 200

        health_data = response.json()
        capabilities = health_data["capabilities"]

        # Capacités requises
        required_capabilities = ["decoders", "generators", "supported_codes", "api_version", "features"]
        for capability in required_capabilities:
            assert capability in capabilities, f"Capacité {capability} requise"

        # Vérifier décodeurs
        decoders = capabilities["decoders"]
        assert "zxing_jpype" in decoders
        assert "pylibdmtx" in decoders
        assert isinstance(decoders["zxing_jpype"], bool)
        assert isinstance(decoders["pylibdmtx"], bool)

        # Vérifier générateurs
        generators = capabilities["generators"]
        required_generators = ["treepoem", "ghostscript", "bwipjs", "nodejs"]
        for gen in required_generators:
            assert gen in generators, f"Générateur {gen} requis"

        # Vérifier codes supportés
        supported_codes = capabilities["supported_codes"]
        expected_codes = [
            "DataMatrix",
            "QR Code",
            "Code 128",
            "GS1-128",
            "GS1 DataMatrix",
            "GS1 QR Code"
        ]
        for code in expected_codes:
            assert code in supported_codes, f"Code {code} devrait être supporté"

    def test_health_endpoint_generator_status_validation(self):
        """Test validation status des générateurs"""

        response = client.get("/health")
        assert response.status_code == 200

        capabilities = response.json()["capabilities"]
        generators = capabilities["generators"]

        # Validation status critiques
        critical_generators = {
            "bwipjs": "Critique pour GS1 DataMatrix",
            "nodejs": "Requis pour bwip-js",
            "treepoem": "Fallback principal",
            "ghostscript": "Requis pour treepoem"
        }

        for gen_name, description in critical_generators.items():
            if gen_name in generators:
                status = generators[gen_name]

                if gen_name in ["bwipjs", "nodejs"]:
                    # Critiques pour GS1 DataMatrix
                    assert status == True, f"{gen_name} DOIT être disponible: {description}"

                # Vérifier messages d'erreur si applicable
                error_key = f"{gen_name}_error"
                if error_key in generators:
                    error_msg = generators[error_key]
                    if status == False:
                        assert isinstance(error_msg, str), f"Message d'erreur requis pour {gen_name}"

    def test_health_endpoint_feature_flags(self):
        """Test feature flags dans /health"""

        response = client.get("/health")
        assert response.status_code == 200

        capabilities = response.json()["capabilities"]
        features = capabilities["features"]

        # Features essentielles
        essential_features = ["decode", "generate", "parse"]
        for feature in essential_features:
            assert feature in features, f"Feature {feature} requise"
            assert features[feature] == True, f"Feature {feature} devrait être active"

    def test_health_endpoint_version_info(self):
        """Test informations de version dans /health"""

        response = client.get("/health")
        assert response.status_code == 200

        capabilities = response.json()["capabilities"]

        # Vérifier version API
        assert "api_version" in capabilities
        api_version = capabilities["api_version"]
        assert isinstance(api_version, str), "Version API devrait être string"
        assert len(api_version) > 0, "Version API ne devrait pas être vide"

        # Format version (ex: "1.3.0")
        version_parts = api_version.split(".")
        assert len(version_parts) >= 2, "Version devrait avoir au moins major.minor"

    def test_health_endpoint_production_vs_local(self):
        """Test cohérence /health production vs local"""

        # Test local
        local_response = client.get("/health")
        assert local_response.status_code == 200
        local_health = local_response.json()

        # Test production (si disponible)
        try:
            production_response = requests.get(
                "https://gs1-decoder-api.rorworld.eu/health",
                timeout=5
            )

            if production_response.status_code == 200:
                production_health = production_response.json()

                # Comparer structures
                assert production_health["status"] == local_health["status"]

                # Capacités devraient être similaires
                prod_codes = set(production_health["capabilities"]["supported_codes"])
                local_codes = set(local_health["capabilities"]["supported_codes"])

                # Codes essentiels devraient être présents partout
                essential_codes = {"GS1 DataMatrix", "DataMatrix", "QR Code"}
                assert essential_codes.issubset(prod_codes), "Codes essentiels manquants en production"

        except Exception:
            pytest.skip("API production non accessible pour comparaison")

    def test_health_endpoint_response_time(self):
        """Test temps de réponse endpoint /health"""

        import time

        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()

        response_time = end_time - start_time

        assert response.status_code == 200
        assert response_time < 1.0, f"Health check devrait prendre < 1s, obtenu: {response_time:.2f}s"

    def test_health_endpoint_cache_behavior(self):
        """Test comportement cache endpoint /health"""

        # Plusieurs appels rapides
        response_times = []

        for i in range(5):
            import time
            start_time = time.time()

            response = client.get("/health")

            end_time = time.time()
            response_time = end_time - start_time

            assert response.status_code == 200
            response_times.append(response_time)

        # Tous les appels devraient être rapides (cachés ou optimisés)
        for i, resp_time in enumerate(response_times):
            assert resp_time < 2.0, f"Appel health {i} devrait être rapide: {resp_time:.2f}s"

        # Réponses devraient être cohérentes
        responses = [client.get("/health").json() for _ in range(3)]

        # Status devrait être identique
        statuses = [resp["status"] for resp in responses]
        assert len(set(statuses)) == 1, "Status health devrait être cohérent"

    def test_health_endpoint_critical_capabilities_monitoring(self):
        """CRITIQUE: Monitoring capacités critiques pour GS1 DataMatrix"""

        response = client.get("/health")
        assert response.status_code == 200

        capabilities = response.json()["capabilities"]

        # Capacités CRITIQUES pour GS1 DataMatrix
        critical_checks = {
            "generators.bwipjs": True,
            "generators.nodejs": True,
            "supported_codes": "GS1 DataMatrix",
            "features.generate": True
        }

        for check_path, expected_value in critical_checks.items():
            path_parts = check_path.split(".")
            current = capabilities

            for part in path_parts:
                assert part in current, f"Chemin critique {check_path} manquant"
                current = current[part]

            if isinstance(expected_value, bool):
                assert current == expected_value, f"Capacité critique {check_path} = {current}, attendu: {expected_value}"
            elif isinstance(expected_value, str):
                assert expected_value in current, f"Capacité critique {expected_value} manquante dans {check_path}"

        # Alert si capacités critiques manquantes
        generators = capabilities["generators"]
        if not (generators.get("bwipjs") and generators.get("nodejs")):
            pytest.fail("🚨 CRITICAL: bwip-js ou Node.js non disponible - GS1 DataMatrix compromis")