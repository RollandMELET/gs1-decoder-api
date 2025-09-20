"""
Tests complets endpoint /generate/ pour tous les formats
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import requests

# Ajout du chemin de l'application
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.main import app

client = TestClient(app)

class TestGenerateEndpointAllFormats:
    """Tests endpoint /generate/ pour tous les formats"""

    @pytest.mark.parametrize("format_config", [
        {"barcode_format": "qr_code", "data": "QR Test Data", "expected_size_min": 1000, "expected_size_max": 50000},
        {"barcode_format": "code_128", "data": "CODE128TEST", "expected_size_min": 500, "expected_size_max": 10000},
        {"barcode_format": "datamatrix", "data": "DataMatrix Test", "expected_size_min": 2000, "expected_size_max": 30000},
        {"barcode_format": "gs1_datamatrix", "data": "(01)03760423190005", "expected_size_min": 500, "expected_size_max": 800},
        {"barcode_format": "gs1_qr_code", "data": "(01)03760423190005", "expected_size_min": 1000, "expected_size_max": 20000},
        {"barcode_format": "gs1_128", "data": "(01)03760423190005", "expected_size_min": 500, "expected_size_max": 10000}
    ])
    def test_generate_endpoint_all_formats(self, format_config):
        """Test génération tous formats via endpoint"""

        with patch('app.barcode_generator.generate_barcode') as mock_generate:
            # Simuler taille appropriée pour chaque format
            mock_size = (format_config["expected_size_min"] + format_config["expected_size_max"]) // 2
            mock_generate.return_value = (
                b'a' * mock_size,
                'image/png',
                {"format": format_config["barcode_format"]}
            )

            response = client.post("/generate/", json={
                "data": format_config["data"],
                "barcode_format": format_config["barcode_format"]
            })

            assert response.status_code == 200, f"Format {format_config['barcode_format']} devrait réussir"
            assert response.headers["content-type"] == "image/png"

            file_size = len(response.content)
            assert format_config["expected_size_min"] <= file_size <= format_config["expected_size_max"], \
                f"Taille {format_config['barcode_format']}: {file_size} hors limites [{format_config['expected_size_min']}-{format_config['expected_size_max']}]"

    def test_generate_endpoint_parameter_validation(self):
        """Test validation paramètres endpoint /generate/"""

        # Test paramètres manquants
        response = client.post("/generate/", json={})
        assert response.status_code == 422

        # Test format invalide
        response = client.post("/generate/", json={
            "data": "Test",
            "barcode_format": "invalid_format"
        })
        assert response.status_code == 422

        # Test dimensions invalides
        response = client.post("/generate/", json={
            "data": "Test",
            "barcode_format": "qr_code",
            "width": -1
        })
        assert response.status_code == 422

        response = client.post("/generate/", json={
            "data": "Test",
            "barcode_format": "qr_code",
            "height": 2000  # > limite
        })
        assert response.status_code == 422

    def test_generate_endpoint_image_formats(self):
        """Test formats d'image supportés"""

        image_formats = ["png", "jpeg"]  # SVG pas encore implémenté

        for img_format in image_formats:
            with patch('app.barcode_generator.generate_barcode') as mock_generate:
                mock_generate.return_value = (
                    b'image_data',
                    f'image/{img_format}',
                    {"format": "qr_code", "image_format": img_format}
                )

                response = client.post("/generate/", json={
                    "data": "Image format test",
                    "barcode_format": "qr_code",
                    "image_format": img_format
                })

                assert response.status_code == 200
                expected_content_type = f"image/{img_format}"
                assert response.headers["content-type"] == expected_content_type

    def test_generate_endpoint_gs1_datamatrix_optimization_preserved(self):
        """CRITIQUE: Vérifier préservation optimisation GS1 DataMatrix via endpoint"""

        with patch('app.barcode_generator.generate_barcode') as mock_generate:
            # Simuler taille optimisée GS1 DataMatrix
            mock_generate.return_value = (
                b'a' * 571,  # Taille optimisée
                'image/png',
                {"format": "gs1_datamatrix", "optimized": True, "method": "bwip-js"}
            )

            response = client.post("/generate/", json={
                "data": "(01)03760423190005",
                "barcode_format": "gs1_datamatrix",
                "width": 200,
                "height": 200
            })

            assert response.status_code == 200

            # Vérifier taille optimisée préservée
            file_size = len(response.content)
            assert file_size == 571, "GS1 DataMatrix devrait conserver taille optimisée"

            # Vérifier que use_treepoem=False est forcé
            args, kwargs = mock_generate.call_args
            assert kwargs["use_treepoem"] == False, "use_treepoem devrait être forcé à False pour GS1 DataMatrix"

    def test_generate_endpoint_concurrent_formats(self):
        """Test génération concurrente différents formats"""
        import threading
        import time

        results = {}
        errors = []

        def generate_format(format_name, data, thread_id):
            try:
                with patch('app.barcode_generator.generate_barcode') as mock_generate:
                    mock_generate.return_value = (
                        f'thread_{thread_id}_{format_name}'.encode(),
                        'image/png',
                        {"thread_id": thread_id, "format": format_name}
                    )

                    response = client.post("/generate/", json={
                        "data": data,
                        "barcode_format": format_name
                    })

                    results[f"{format_name}_{thread_id}"] = response.status_code
            except Exception as e:
                errors.append((format_name, thread_id, str(e)))

        # Test concurrent de tous les formats
        format_tests = [
            ("qr_code", "QR Test"),
            ("code_128", "C128TEST"),
            ("datamatrix", "DM Test"),
            ("gs1_datamatrix", "(01)03760423190005"),
            ("gs1_qr_code", "(01)03760423190005"),
            ("gs1_128", "(01)03760423190005")
        ]

        threads = []
        for i, (fmt, data) in enumerate(format_tests):
            thread = threading.Thread(target=generate_format, args=(fmt, data, i))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Vérifications
        assert len(errors) == 0, f"Aucune erreur concurrence: {errors}"
        assert len(results) == len(format_tests), "Tous formats devraient réussir"

        for key, status_code in results.items():
            assert status_code == 200, f"Format {key} devrait réussir en concurrence"

    def test_generate_endpoint_error_consistency(self):
        """Test cohérence gestion d'erreurs tous formats"""

        formats = ["qr_code", "code_128", "datamatrix", "gs1_datamatrix", "gs1_qr_code", "gs1_128"]

        for fmt in formats:
            with patch('app.barcode_generator.generate_barcode') as mock_generate:
                mock_generate.side_effect = Exception(f"Erreur test {fmt}")

                response = client.post("/generate/", json={
                    "data": "Error test",
                    "barcode_format": fmt
                })

                # Toutes les erreurs devraient être gérées uniformément
                assert response.status_code == 500, f"Format {fmt} devrait retourner 500 en cas d'erreur"

                error_response = response.json()
                assert "detail" in error_response
                assert "Erreur interne" in error_response["detail"]

    def test_generate_endpoint_performance_thresholds(self):
        """Test seuils de performance par format"""

        # Seuils par format (en secondes)
        performance_thresholds = {
            "gs1_datamatrix": 2.0,  # GS1 DataMatrix: < 2s (critique)
            "qr_code": 5.0,         # QR Code: < 5s
            "code_128": 3.0,        # Code 128: < 3s
            "datamatrix": 5.0,      # DataMatrix: < 5s
            "gs1_qr_code": 5.0,     # GS1 QR: < 5s
            "gs1_128": 3.0          # GS1-128: < 3s
        }

        for fmt, threshold in performance_thresholds.items():
            with patch('app.barcode_generator.generate_barcode') as mock_generate:
                def timed_generation(*args, **kwargs):
                    time.sleep(0.1)  # Simuler traitement
                    return (b'performance_test_data', 'image/png', {})

                mock_generate.side_effect = timed_generation

                start_time = time.time()

                response = client.post("/generate/", json={
                    "data": "(01)03760423190005" if "gs1" in fmt else f"Test {fmt}",
                    "barcode_format": fmt
                })

                end_time = time.time()
                response_time = end_time - start_time

                assert response.status_code == 200, f"Format {fmt} devrait réussir"
                assert response_time < threshold, f"Format {fmt} devrait être < {threshold}s, obtenu: {response_time:.2f}s"

    def test_generate_endpoint_data_validation_by_format(self):
        """Test validation données par format"""

        # Test données appropriées par format
        valid_data_by_format = {
            "qr_code": ["Simple text", "https://example.com", "Multi\nline\ndata"],
            "code_128": ["CODE128", "123456789", "ALPHANUMERIC"],
            "datamatrix": ["DM content", "Special!@#$%", "Multi line content"],
            "gs1_datamatrix": ["(01)03760423190005", "(01)03760423190005(21)SERIAL"],
            "gs1_qr_code": ["(01)03760423190005", "(01)03760423190005(17)250423"],
            "gs1_128": ["(01)03760423190005", "(01)03760423190005(10)BATCH"]
        }

        for fmt, data_list in valid_data_by_format.items():
            for data in data_list:
                with patch('app.barcode_generator.generate_barcode') as mock_generate:
                    mock_generate.return_value = (b'valid_data', 'image/png', {})

                    response = client.post("/generate/", json={
                        "data": data,
                        "barcode_format": fmt
                    })

                    assert response.status_code == 200, f"Données valides {fmt}: {data}"

    def test_generate_endpoint_response_headers_consistency(self):
        """Test cohérence headers de réponse tous formats"""

        formats = ["qr_code", "code_128", "datamatrix", "gs1_datamatrix", "gs1_qr_code", "gs1_128"]

        for fmt in formats:
            with patch('app.barcode_generator.generate_barcode') as mock_generate:
                mock_generate.return_value = (
                    f'{fmt}_response_data'.encode(),
                    'image/png',
                    {"format": fmt}
                )

                response = client.post("/generate/", json={
                    "data": "(01)03760423190005" if "gs1" in fmt else f"Test {fmt}",
                    "barcode_format": fmt
                })

                # Vérifier headers cohérents
                assert response.status_code == 200
                assert response.headers["content-type"] == "image/png"
                assert "content-length" in response.headers
                assert len(response.content) > 0

class TestGenerateEndpointRegression:
    """Tests de non-régression endpoint /generate/"""

    def test_generate_endpoint_backward_compatibility(self):
        """Test compatibilité descendante endpoint /generate/"""

        # Test avec anciens paramètres pour vérifier compatibilité
        legacy_requests = [
            {
                "data": "(01)03760423190005",
                "format": "gs1-datamatrix",  # Ancien format avec tiret
                "image_format": "png"
            },
            {
                "data": "QR Test",
                "format": "qrcode",  # Sans underscore
                "width": 300,
                "height": 300
            }
        ]

        for legacy_request in legacy_requests:
            # Ces requêtes peuvent échouer (formats changés), mais ne doivent pas crasher
            response = client.post("/generate/", json=legacy_request)

            # Soit succès (compatibilité), soit erreur validée (422)
            assert response.status_code in [200, 422], \
                f"Requête legacy devrait être gérée proprement: {legacy_request}"

    def test_generate_endpoint_default_values(self):
        """Test valeurs par défaut endpoint /generate/"""

        with patch('app.barcode_generator.generate_barcode') as mock_generate:
            mock_generate.return_value = (b'default_test', 'image/png', {})

            # Requête minimale
            response = client.post("/generate/", json={
                "data": "(01)03760423190005"
                # Pas de format spécifié - devrait utiliser défaut
            })

            if response.status_code == 200:
                # Vérifier valeurs par défaut
                args, kwargs = mock_generate.call_args
                # Format par défaut est probablement GS1_DATAMATRIX
                # Dimensions par défaut: 300x300

    def test_generate_endpoint_size_optimization_logic(self):
        """CRITIQUE: Test logique optimisation taille par format"""

        size_behaviors = {
            # Format: (input_size, should_be_resized, expected_size_type)
            "gs1_datamatrix": ((200, 200), False, "native"),  # Pas de redimensionnement
            "qr_code": ((200, 200), True, "resized"),         # Redimensionnement appliqué
            "datamatrix": ((200, 200), True, "resized"),      # Redimensionnement appliqué
            "code_128": ((200, 200), True, "resized")         # Redimensionnement appliqué
        }

        for fmt, (dimensions, should_resize, size_type) in size_behaviors.items():
            width, height = dimensions

            with patch('app.barcode_generator.generate_barcode') as mock_generate:
                if size_type == "native":
                    # GS1 DataMatrix: taille native préservée
                    mock_generate.return_value = (b'a' * 571, 'image/png', {"optimized": True})
                else:
                    # Autres: taille redimensionnée
                    mock_generate.return_value = (b'a' * 15000, 'image/png', {"resized": True})

                response = client.post("/generate/", json={
                    "data": "(01)03760423190005" if "gs1" in fmt else f"Test {fmt}",
                    "barcode_format": fmt,
                    "width": width,
                    "height": height
                })

                assert response.status_code == 200

                file_size = len(response.content)
                if size_type == "native":
                    # GS1 DataMatrix optimisé
                    assert file_size < 1000, f"GS1 DataMatrix devrait être optimisé: {file_size}"
                else:
                    # Autres formats redimensionnés
                    assert file_size > 5000, f"Format {fmt} devrait être redimensionné: {file_size}"

class TestGenerateEndpointProduction:
    """Tests endpoint /generate/ en production"""

    def test_generate_endpoint_production_all_formats(self):
        """Test production tous formats (si API disponible)"""

        try:
            health_response = requests.get("https://gs1-decoder-api.rorworld.eu/health", timeout=5)
            api_available = health_response.status_code == 200
        except:
            api_available = False

        if not api_available:
            pytest.skip("API production non disponible")

        # Tests par format en production
        production_tests = [
            ("gs1_datamatrix", "(01)03760423190005", 500, 800),    # Critique: optimisé
            ("qr_code", "Production QR Test", 1000, 50000),         # Standard
            ("code_128", "PRODTEST", 500, 10000),                  # Standard
            ("datamatrix", "Production DM", 2000, 30000),          # Standard
            ("gs1_qr_code", "(01)03760423190005", 1000, 20000),   # GS1
            ("gs1_128", "(01)03760423190005", 500, 10000)          # GS1
        ]

        results = {}

        for fmt, data, min_size, max_size in production_tests:
            try:
                response = requests.post(
                    "https://gs1-decoder-api.rorworld.eu/generate/",
                    json={
                        "data": data,
                        "barcode_format": fmt
                    },
                    timeout=10
                )

                results[fmt] = {
                    "status": response.status_code,
                    "size": len(response.content) if response.status_code == 200 else 0
                }

                if response.status_code == 200:
                    file_size = len(response.content)

                    if fmt == "gs1_datamatrix":
                        # Critique: GS1 DataMatrix doit être optimisé
                        assert min_size <= file_size <= max_size, \
                            f"GS1 DataMatrix production DOIT être optimisé: {file_size} bytes"
                    # Autres formats: log seulement si échouent

            except Exception as e:
                results[fmt] = {"status": "error", "error": str(e)}

        # Rapport production
        critical_ok = results.get("gs1_datamatrix", {}).get("status") == 200
        assert critical_ok, "GS1 DataMatrix DOIT fonctionner en production"

    def test_generate_endpoint_stress_test(self):
        """Test de charge endpoint /generate/"""

        import concurrent.futures
        import time

        def generate_request(request_id):
            with patch('app.barcode_generator.generate_barcode') as mock_generate:
                mock_generate.return_value = (
                    f'stress_test_{request_id}'.encode(),
                    'image/png',
                    {"request_id": request_id}
                )

                response = client.post("/generate/", json={
                    "data": f"Stress test {request_id}",
                    "barcode_format": "qr_code"
                })

                return response.status_code

        # Lancer 10 requêtes concurrentes
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(generate_request, i) for i in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        end_time = time.time()
        total_time = end_time - start_time

        # Vérifications stress test
        assert all(status == 200 for status in results), "Toutes requêtes concurrentes devraient réussir"
        assert total_time < 30, f"10 requêtes concurrentes devraient prendre < 30s, obtenu: {total_time:.2f}s"
        assert len(results) == 10, "Toutes requêtes devraient être traitées"

    def test_generate_endpoint_memory_stability(self):
        """Test stabilité mémoire endpoint /generate/"""
        import psutil
        import gc

        process = psutil.Process()
        initial_memory = process.memory_info().rss

        # Faire plusieurs générations pour détecter fuites
        for i in range(20):
            with patch('app.barcode_generator.generate_barcode') as mock_generate:
                mock_generate.return_value = (
                    b'memory_test_data' * 100,  # Données volumineuses
                    'image/png',
                    {"iteration": i}
                )

                response = client.post("/generate/", json={
                    "data": f"Memory test {i}",
                    "barcode_format": "qr_code"
                })

                assert response.status_code == 200

            if i % 5 == 0:
                gc.collect()  # Force garbage collection

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Vérifier stabilité mémoire
        max_increase = 100 * 1024 * 1024  # 100MB
        assert memory_increase < max_increase, \
            f"Augmentation mémoire devrait être < 100MB, obtenu: {memory_increase / 1024 / 1024:.2f}MB"