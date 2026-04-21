#!/usr/bin/env bash
# check-deps.sh — Vérifie les dépendances système et Python.

set -uo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
RESET='\033[0m'

MISSING=0

check_cmd() {
    local cmd="$1"
    local hint="$2"
    if command -v "$cmd" &>/dev/null; then
        local version
        version="$("$cmd" --version 2>&1 | head -n 1)"
        printf "  ${GREEN}✓${RESET} %-15s %s\n" "$cmd" "$version"
    else
        printf "  ${RED}✗${RESET} %-15s introuvable. ${YELLOW}%s${RESET}\n" "$cmd" "$hint"
        MISSING=$((MISSING + 1))
    fi
}

check_python_pkg() {
    local pkg="$1"
    if python3 -c "import $pkg" &>/dev/null; then
        local version
        version="$(python3 -c "import $pkg; print(getattr($pkg, '__version__', 'n/a'))" 2>/dev/null || echo 'n/a')"
        printf "  ${GREEN}✓${RESET} %-25s v%s\n" "$pkg" "$version"
    else
        printf "  ${RED}✗${RESET} %-25s non installé. ${YELLOW}pip install -r requirements.txt${RESET}\n" "$pkg"
        MISSING=$((MISSING + 1))
    fi
}

echo -e "${BOLD}== Vérification des outils CLI ==${RESET}"
if command -v magick &>/dev/null; then
    check_cmd "magick" "ImageMagick 7+ requis (brew install imagemagick, apt install imagemagick)"
else
    check_cmd "convert" "ImageMagick requis (brew install imagemagick, apt install imagemagick)"
fi
check_cmd "gmic" "G'MIC requis pour émulation film (brew install gmic, apt install gmic)"
check_cmd "exiftool" "exiftool requis (brew install exiftool, apt install libimage-exiftool-perl)"
check_cmd "python3" "Python 3.10+ requis"
check_cmd "jq" "jq requis (brew install jq, apt install jq)"
check_cmd "git" "git 2.30+ requis"

echo ""
echo -e "${BOLD}== Vérification des paquets Python ==${RESET}"
if command -v python3 &>/dev/null; then
    check_python_pkg "google.genai"
    check_python_pkg "PIL"
    check_python_pkg "numpy"
    check_python_pkg "cv2"
    check_python_pkg "scipy"
    check_python_pkg "dotenv"
else
    echo -e "  ${RED}Python 3 absent — paquets non vérifiables.${RESET}"
    MISSING=$((MISSING + 1))
fi

echo ""
echo -e "${BOLD}== Variables d'environnement ==${RESET}"
if [[ -n "${GEMINI_API_KEY:-}" ]]; then
    printf "  ${GREEN}✓${RESET} GEMINI_API_KEY présente\n"
else
    printf "  ${RED}✗${RESET} GEMINI_API_KEY manquante. ${YELLOW}Obtiens-en une sur https://aistudio.google.com/apikey${RESET}\n"
    MISSING=$((MISSING + 1))
fi

echo ""
if [[ $MISSING -eq 0 ]]; then
    echo -e "${GREEN}${BOLD}Toutes les dépendances sont prêtes.${RESET}"
    exit 0
else
    echo -e "${RED}${BOLD}$MISSING élément(s) manquant(s). Exécute ./install.sh ou installe manuellement.${RESET}"
    exit 1
fi
