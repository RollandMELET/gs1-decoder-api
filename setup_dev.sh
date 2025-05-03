#!/bin/bash
# Script d'installation et de configuration pour le développement du GS1-Decoder-API

# Couleurs pour une meilleure lisibilité
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

echo -e "${BLUE}=== Configuration de l'environnement de développement GS1-Decoder-API ===${NC}"

# Vérifier si Python est installé
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python est installé: ${PYTHON_VERSION}${NC}"
else
    echo -e "${RED}✗ Python 3 n'est pas installé. Veuillez l'installer avant de continuer.${NC}"
    exit 1
fi

# Vérifier si pip est installé
if command -v pip3 &>/dev/null; then
    PIP_VERSION=$(pip3 --version)
    echo -e "${GREEN}✓ pip est installé: ${PIP_VERSION}${NC}"
else
    echo -e "${RED}✗ pip n'est pas installé. Installation...${NC}"
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py
    rm get-pip.py
fi

# Vérifier si Java est installé (requis pour ZXing)
if command -v java &>/dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1)
    echo -e "${GREEN}✓ Java est installé: ${JAVA_VERSION}${NC}"
else
    echo -e "${YELLOW}⚠ Java n'est pas installé. ZXing ne fonctionnera pas sans Java.${NC}"
    echo -e "${YELLOW}⚠ Installez Java depuis https://adoptium.net/${NC}"
fi

# Créer un environnement virtuel
echo -e "\n${BLUE}=== Création de l'environnement virtuel ===${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠ Un environnement virtuel existe déjà.${NC}"
    read -p "Voulez-vous le recréer? (o/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        echo -e "${YELLOW}Suppression de l'environnement existant...${NC}"
        rm -rf venv
        python3 -m venv venv
        echo -e "${GREEN}✓ Nouvel environnement virtuel créé.${NC}"
    fi
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Environnement virtuel créé.${NC}"
fi

# Activer l'environnement virtuel
echo -e "\n${BLUE}=== Activation de l'environnement virtuel ===${NC}"
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    source venv/bin/activate
else
    source venv/Scripts/activate
fi
echo -e "${GREEN}✓ Environnement virtuel activé.${NC}"

# Installer les dépendances
echo -e "\n${BLUE}=== Installation des dépendances Python ===${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Installer les dépendances supplémentaires pour le développement
echo -e "\n${BLUE}=== Installation des dépendances de développement ===${NC}"
pip install pytest pytest-cov black isort mypy

# Vérifier si libdmtx est installé (requis pour pylibdmtx)
echo -e "\n${BLUE}=== Vérification de libdmtx ===${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v brew &>/dev/null; then
        if brew list libdmtx &>/dev/null; then
            echo -e "${GREEN}✓ libdmtx est installé via Homebrew.${NC}"
        else
            echo -e "${YELLOW}⚠ libdmtx n'est pas installé. Installation...${NC}"
            brew install libdmtx
        fi
    else
        echo -e "${YELLOW}⚠ Homebrew n'est pas installé. Installation manuelle de libdmtx requise.${NC}"
        echo -e "${YELLOW}⚠ Visitez: https://github.com/dmtx/libdmtx${NC}"
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v apt-get &>/dev/null; then
        if dpkg -l | grep -q libdmtx; then
            echo -e "${GREEN}✓ libdmtx est installé via apt.${NC}"
        else
            echo -e "${YELLOW}⚠ libdmtx n'est pas installé. Installation...${NC}"
            sudo apt-get update
            sudo apt-get install -y libdmtx0a
        fi
    else
        echo -e "${YELLOW}⚠ apt-get n'est pas disponible. Installation manuelle de libdmtx requise.${NC}"
        echo -e "${YELLOW}⚠ Visitez: https://github.com/dmtx/libdmtx${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Système d'exploitation non pris en charge pour la vérification automatique de libdmtx.${NC}"
    echo -e "${YELLOW}⚠ Veuillez l'installer manuellement: https://github.com/dmtx/libdmtx${NC}"
fi

# Télécharger ZXing si nécessaire
echo -e "\n${BLUE}=== Configuration de ZXing ===${NC}"
if [ ! -d "zxing" ]; then
    echo -e "${YELLOW}⚠ Création du répertoire zxing...${NC}"
    mkdir -p zxing
fi

if [ ! -f "zxing/javase.jar" ]; then
    echo -e "${YELLOW}⚠ Téléchargement de ZXing JavaSE...${NC}"
    curl -L https://repo1.maven.org/maven2/com/google/zxing/javase/3.4.1/javase-3.4.1.jar -o zxing/javase.jar
    echo -e "${GREEN}✓ ZXing JavaSE téléchargé.${NC}"
else
    echo -e "${GREEN}✓ ZXing JavaSE est déjà présent.${NC}"
fi

# Créer les répertoires de ressources si nécessaire
echo -e "\n${BLUE}=== Vérification des répertoires de ressources ===${NC}"
if [ ! -d "resources" ]; then
    echo -e "${YELLOW}⚠ Création du répertoire resources...${NC}"
    mkdir -p resources
    echo -e "${GREEN}✓ Répertoire resources créé.${NC}"
else
    echo -e "${GREEN}✓ Répertoire resources existe déjà.${NC}"
fi

# Configuration terminée
echo -e "\n${BLUE}=== Configuration terminée ===${NC}"
echo -e "${GREEN}✓ L'environnement de développement est prêt.${NC}"
echo -e "\n${YELLOW}Pour activer l'environnement virtuel à l'avenir:${NC}"
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo -e "${YELLOW}source venv/bin/activate${NC}"
else
    echo -e "${YELLOW}venv\\Scripts\\activate${NC}"
fi

echo -e "\n${YELLOW}Pour tester le décodage de codes-barres:${NC}"
echo -e "${YELLOW}python test_barcode_detection.py <chemin_image>${NC}"

echo -e "\n${YELLOW}Pour lancer l'API en mode développement:${NC}"
echo -e "${YELLOW}uvicorn app.main:app --reload${NC}"

# Rendre le script exécutable
chmod +x setup_dev.sh
