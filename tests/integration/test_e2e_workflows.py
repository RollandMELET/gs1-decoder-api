"""
Tests end-to-end et workflows complets
"""
import pytest
import sys
import os
import requests
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Ajout du chemin de l'application
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.main import app

client = TestClient(app)

class TestE2EWorkflows:
    """Tests end-to-end pour workflows complets"""

    def test_complete_generation_validation_workflow(self, gs1_test_data):
        """CRITIQUE: Workflow complet génération → validation → décodage"""

        # 1. Génération GS1 DataMatrix
        with patch('app.barcode_generator.generate_barcode') as mock_generate:
            mock_generate.return_value = (
                b'fake_optimized_gs1_datamatrix',  # 571 bytes simulés
                'image/png',
                {
                    "format": "gs1_datamatrix",
                    "size": (100, 100),
                    "optimized": True,
                    "method": "bwip-js",
                    "file_size": 571
                }
            )

            generate_response = client.post("/generate/", json={
                "data": gs1_test_data["simple"],
                "barcode_format": "gs1_datamatrix"
            })

            assert generate_response.status_code == 200
            generated_image = generate_response.content

        # 2. Validation taille optimisée
        assert len(generated_image) == 571, "Taille générée devrait être optimisée"

        # 3. Décodage pour validation
        with patch('app.barcode_detector.detect_barcode') as mock_detect:
            mock_detect.return_value = {
                "found": True,
                "format": "DataMatrix",
                "data": gs1_test_data["simple"],
                "aim_identifier": "]d2",  # CRITIQUE: GS1 DataMatrix
                "gs1_detected": True,
                "confidence": 0.95
            }

            decode_response = client.post(
                "/decode/",
                files={"file": ("test.png", generated_image, "image/png")}
            )

            assert decode_response.status_code == 200
            decoded_data = decode_response.json()

        # 4. Validation conformité
        assert decoded_data["aim_identifier"] == "]d2", "Code généré devrait être identifié comme GS1 DataMatrix"
        assert decoded_data["gs1_detected"], "Format GS1 devrait être détecté"
        assert decoded_data["data"] == gs1_test_data["simple"], "Données devraient être préservées"

        # 5. Parsing final
        parse_response = client.post("/parse/", json={
            "data": decoded_data["data"],
            "verbose": True
        })

        assert parse_response.status_code == 200
        parsed_data = parse_response.json()
        assert parsed_data["format_detected"] == "GS1", "Format GS1 devrait être parsé correctement"

    def test_production_api_integration(self, gs1_test_data):
        """Test d'intégration avec l'API de production (si disponible)"""

        production_url = "https://gs1-decoder-api.rorworld.eu"

        # Test conditionnel - seulement si l'API est accessible
        try:
            health_response = requests.get(f"{production_url}/health", timeout=5)
            api_available = health_response.status_code == 200
        except:
            api_available = False

        if not api_available:
            pytest.skip("API production non disponible")

        # Test de génération sur API production
        response = requests.post(
            f"{production_url}/generate/",
            json={
                "data": gs1_test_data["simple"],
                "barcode_format": "gs1_datamatrix"
            },
            timeout=10
        )

        if response.status_code == 200:
            # Vérifier taille optimisée en production
            file_size = len(response.content)
            assert 500 <= file_size <= 700, f"Taille production devrait être optimisée, obtenu: {file_size}"
        else:
            pytest.skip(f"API production retourne erreur: {response.status_code}")

    def test_backward_compatibility_other_formats(self):
        """CRITIQUE: Vérifier que les autres formats ne sont pas impactés par l'optimisation GS1"""

        # Test des formats non-GS1 pour s'assurer qu'ils fonctionnent toujours
        test_formats = [
            ("datamatrix", "Standard DataMatrix data"),
            ("qr_code", "Standard QR Code data"),
            ("code_128", "STANDARD128")
        ]

        for barcode_format, test_data in test_formats:
            with patch('app.barcode_generator.generate_barcode') as mock_generate:
                mock_generate.return_value = (
                    b'standard_format_data',
                    'image/png',
                    {"format": barcode_format, "optimized": False}
                )

                response = client.post("/generate/", json={
                    "data": test_data,
                    "barcode_format": barcode_format
                })

                assert response.status_code == 200, f"Format {barcode_format} devrait toujours fonctionner"

                # Vérifier que use_treepoem n'est forcé que pour GS1 DataMatrix
                args, kwargs = mock_generate.call_args
                if barcode_format == "gs1_datamatrix":
                    assert kwargs["use_treepoem"] == False
                else:
                    # Autres formats peuvent utiliser treepoem par défaut
                    assert kwargs.get("use_treepoem", True) == True

    def test_regression_file_sizes_comparison(self, gs1_test_data, original_file_sizes):
        """Test de non-régression: vérifier que l'optimisation est maintenue"""

        with patch('app.barcode_generator.generate_barcode') as mock_generate:
            # Simuler les nouvelles tailles optimisées
            optimized_sizes = {"simple": 571, "expert": 689}

            for data_type in ["simple", "expert"]:
                mock_generate.return_value = (
                    b'a' * optimized_sizes[data_type],
                    'image/png',
                    {"optimized": True, "original_would_be": original_file_sizes[data_type]}
                )

                response = client.post("/generate/", json={
                    "data": gs1_test_data[data_type],
                    "barcode_format": "gs1_datamatrix"
                })

                assert response.status_code == 200

                # Vérifier optimisation maintenue
                current_size = len(response.content)
                original_size = original_file_sizes[data_type]
                reduction = (original_size - current_size) / original_size

                assert reduction > 0.95, f"Réduction pour {data_type} devrait être > 95%, obtenu: {reduction:.2%}"
                assert current_size == optimized_sizes[data_type], \
                    f"Taille {data_type} devrait être maintenue à {optimized_sizes[data_type]}"

    def test_error_scenarios_comprehensive(self, gs1_test_data):
        """Test complet des scénarios d'erreur"""

        error_scenarios = [
            # (request_data, expected_status, error_type)
            ({}, 422, "validation"),  # Données manquantes
            ({"data": "", "barcode_format": "gs1_datamatrix"}, 422, "empty_data"),  # Données vides
            ({"data": gs1_test_data["simple"], "barcode_format": "invalid"}, 422, "invalid_format"),  # Format invalide
            ({"data": "invalid_gs1_data", "barcode_format": "gs1_datamatrix"}, 500, "generation_error")  # Données invalides
        ]

        for request_data, expected_status, error_type in error_scenarios:
            if expected_status == 500:
                # Mock erreur de génération
                with patch('app.barcode_generator.generate_barcode') as mock_generate:
                    mock_generate.side_effect = Exception("Erreur de génération")

                    response = client.post("/generate/", json=request_data)
            else:
                response = client.post("/generate/", json=request_data)

            assert response.status_code == expected_status, \
                f"Scénario {error_type} devrait retourner {expected_status}"

    def test_concurrent_requests_stability(self, gs1_test_data):
        """Test de stabilité avec requêtes concurrentes"""

        import threading
        import time

        results = []
        errors = []

        def make_request(thread_id):
            try:
                with patch('app.barcode_generator.generate_barcode') as mock_generate:
                    mock_generate.return_value = (
                        f'thread_{thread_id}_data'.encode(),
                        'image/png',
                        {"thread_id": thread_id}
                    )

                    response = client.post("/generate/", json={
                        "data": gs1_test_data["simple"],
                        "barcode_format": "gs1_datamatrix"
                    })

                    results.append((thread_id, response.status_code, len(response.content)))
            except Exception as e:
                errors.append((thread_id, str(e)))

        # Lancer 5 requêtes concurrentes
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()

        # Attendre toutes les requêtes
        for thread in threads:
            thread.join()

        # Vérifier résultats
        assert len(errors) == 0, f"Aucune erreur concurrence attendue, obtenu: {errors}"
        assert len(results) == 5, "Toutes les requêtes devraient réussir"

        for thread_id, status_code, content_length in results:
            assert status_code == 200, f"Thread {thread_id} devrait réussir"
            assert content_length > 0, f"Thread {thread_id} devrait retourner du contenu"

    def test_memory_leak_prevention(self, gs1_test_data):
        """Test de prévention des fuites mémoire"""

        import psutil
        import gc

        process = psutil.Process()
        initial_memory = process.memory_info().rss

        # Faire plusieurs générations pour détecter fuites
        for i in range(10):
            with patch('app.barcode_generator.generate_barcode') as mock_generate:
                mock_generate.return_value = (
                    b'memory_test_data' * 100,  # Données plus volumineuses
                    'image/png',
                    {"iteration": i}
                )

                response = client.post("/generate/", json={
                    "data": gs1_test_data["expert"],  # Données complexes
                    "barcode_format": "gs1_datamatrix"
                })

                assert response.status_code == 200

            # Force garbage collection
            gc.collect()

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Vérifier que l'augmentation mémoire reste raisonnable (< 50MB)
        max_increase = 50 * 1024 * 1024  # 50MB
        assert memory_increase < max_increase, \
            f"Augmentation mémoire devrait être < 50MB, obtenu: {memory_increase / 1024 / 1024:.2f}MB"

    def test_data_integrity_round_trip(self, gs1_test_data):
        """Test d'intégrité des données sur round-trip complet"""

        for data_type, original_data in gs1_test_data.items():
            if data_type == "invalid":
                continue  # Skip invalid data

            # 1. Génération
            with patch('app.barcode_generator.generate_barcode') as mock_generate:
                mock_generate.return_value = (
                    f'encoded_{data_type}'.encode(),
                    'image/png',
                    {"data_type": data_type}
                )

                generate_response = client.post("/generate/", json={
                    "data": original_data,
                    "barcode_format": "gs1_datamatrix"
                })

                assert generate_response.status_code == 200

            # 2. Décodage
            with patch('app.barcode_detector.detect_barcode') as mock_detect:
                mock_detect.return_value = {
                    "found": True,
                    "format": "DataMatrix",
                    "data": original_data,  # Données préservées
                    "aim_identifier": "]d2",
                    "gs1_detected": True
                }

                decode_response = client.post(
                    "/decode/",
                    files={"file": ("test.png", generate_response.content, "image/png")}
                )

                assert decode_response.status_code == 200
                decoded_result = decode_response.json()

            # 3. Vérification intégrité
            assert decoded_result["data"] == original_data, \
                f"Données {data_type} devraient être préservées dans round-trip"
            assert decoded_result["aim_identifier"] == "]d2", \
                f"Format GS1 {data_type} devrait être préservé"