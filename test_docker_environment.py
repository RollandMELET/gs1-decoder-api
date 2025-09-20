#!/usr/bin/env python3
"""
🚨 SCRIPT DE DIAGNOSTIC CRITIQUE - Environnement Docker

Ce script teste tous les aspects de l'environnement Docker pour identifier
pourquoi l'architecture hybride ne fonctionne pas.

Usage:
    python test_docker_environment.py
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

def print_section(title):
    """Affiche une section de diagnostic avec formatage."""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def test_basic_environment():
    """Test l'environnement de base."""
    print_section("ENVIRONNEMENT DE BASE")

    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"PATH: {os.environ.get('PATH', 'NOT SET')}")

    # Test des commandes de base
    commands = ['which', 'node', 'npm', 'python3', 'java']
    for cmd in commands:
        result = shutil.which(cmd)
        print(f"{cmd:10}: {result if result else 'NOT FOUND'}")

def test_node_installation():
    """Test l'installation Node.js."""
    print_section("NODE.JS INSTALLATION")

    node_path = shutil.which('node')
    if node_path:
        print(f"✅ Node.js trouvé: {node_path}")

        # Version Node.js
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ Version Node.js: {result.stdout.strip()}")
            else:
                print(f"❌ Erreur version Node.js: {result.stderr}")
        except Exception as e:
            print(f"❌ Exception test Node.js: {e}")

        # Version npm
        try:
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ Version npm: {result.stdout.strip()}")
            else:
                print(f"❌ Erreur version npm: {result.stderr}")
        except Exception as e:
            print(f"❌ Exception test npm: {e}")
    else:
        print(f"❌ Node.js NON TROUVÉ")

def test_file_paths():
    """Test les chemins de fichiers critiques."""
    print_section("CHEMINS DE FICHIERS CRITIQUES")

    critical_paths = [
        '/app',
        '/app/generate_gs1_bwip.js',
        '/app/package.json',
        '/app/node_modules',
        '/app/node_modules/bwip-js',
        '/app/node_modules/bwip-js/package.json'
    ]

    for path in critical_paths:
        exists = os.path.exists(path)
        if exists:
            if os.path.isfile(path):
                size = os.path.getsize(path)
                print(f"✅ {path:<35}: Fichier ({size} bytes)")
            else:
                print(f"✅ {path:<35}: Répertoire")
        else:
            print(f"❌ {path:<35}: MANQUANT")

def test_bwip_js_availability():
    """Test la détection BWIPJS_AVAILABLE."""
    print_section("BWIPJS_AVAILABLE DETECTION")

    node_available = shutil.which('node') is not None
    script_exists = os.path.exists('/app/generate_gs1_bwip.js')
    bwipjs_exists = os.path.exists('/app/node_modules/bwip-js')

    print(f"Condition 1 - node disponible: {node_available}")
    print(f"Condition 2 - script existe: {script_exists}")
    print(f"Condition 3 - bwip-js module: {bwipjs_exists}")

    bwipjs_available = node_available and script_exists and bwipjs_exists
    print(f"\n🎯 BWIPJS_AVAILABLE final: {bwipjs_available}")

    if not bwipjs_available:
        print(f"❌ PROBLÈME IDENTIFIÉ: Une ou plusieurs conditions échouent")
        if not node_available:
            print(f"   - Node.js non trouvé dans PATH")
        if not script_exists:
            print(f"   - Script /app/generate_gs1_bwip.js manquant")
        if not bwipjs_exists:
            print(f"   - Module /app/node_modules/bwip-js manquant")

def test_bwip_js_direct():
    """Test direct du script bwip-js."""
    print_section("TEST DIRECT BWIP-JS")

    if not os.path.exists('/app/generate_gs1_bwip.js'):
        print("❌ Script generate_gs1_bwip.js non trouvé")
        return

    if not shutil.which('node'):
        print("❌ Node.js non trouvé")
        return

    # Test avec données simples
    test_data = "(01)03760423190005(11)250326"

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        cmd = ['node', '/app/generate_gs1_bwip.js', test_data, tmp.name]

        print(f"🚀 Test commande: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd='/app'
            )

            print(f"Code retour: {result.returncode}")
            print(f"Stdout: {repr(result.stdout)}")
            print(f"Stderr: {repr(result.stderr)}")

            if result.returncode == 0:
                if os.path.exists(tmp.name):
                    size = os.path.getsize(tmp.name)
                    print(f"✅ SUCCESS: Fichier généré ({size} bytes)")
                else:
                    print(f"❌ ÉCHEC: Fichier non créé malgré returncode=0")
            else:
                print(f"❌ ÉCHEC: subprocess failed (returncode={result.returncode})")

        except Exception as e:
            print(f"❌ EXCEPTION: {type(e).__name__}: {e}")
        finally:
            # Nettoyage
            try:
                if os.path.exists(tmp.name):
                    os.unlink(tmp.name)
            except:
                pass

def test_package_json_content():
    """Test le contenu du package.json."""
    print_section("PACKAGE.JSON CONTENT")

    if os.path.exists('/app/package.json'):
        try:
            with open('/app/package.json', 'r') as f:
                content = f.read()
                print("✅ Contenu package.json:")
                print(content)
        except Exception as e:
            print(f"❌ Erreur lecture package.json: {e}")
    else:
        print("❌ package.json non trouvé")

def main():
    """Fonction principale du diagnostic."""
    print("🚨 DIAGNOSTIC CRITIQUE - Environnement Docker API GS1")
    print("=" * 60)

    test_basic_environment()
    test_node_installation()
    test_file_paths()
    test_bwip_js_availability()
    test_package_json_content()
    test_bwip_js_direct()

    print_section("RÉSUMÉ DIAGNOSTIC")
    print("Si tous les tests sont ✅ alors le problème est dans l'architecture hybride Python")
    print("Si des tests sont ❌ alors le problème est dans l'environnement Docker")

if __name__ == "__main__":
    main()