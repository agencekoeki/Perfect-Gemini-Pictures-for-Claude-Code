#!/usr/bin/env bash
# install.sh — Setup initial du plugin.
#
# - Installe les paquets pip depuis requirements.txt
# - Télécharge optionnellement un pack de CLUTs libres (--download-cluts)
# - Avertit si les deps système sont manquantes (mais ne les installe pas)

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

DOWNLOAD_CLUTS=0
SKIP_PIP=0

usage() {
    cat <<'USAGE'
install.sh — Installation initiale.

Options :
  --download-cluts     Télécharge un pack de CLUTs libres dans data/cluts/.
  --skip-pip           Ne réinstalle pas les paquets Python.
  -h, --help           Affiche cette aide.
USAGE
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --download-cluts) DOWNLOAD_CLUTS=1; shift ;;
        --skip-pip) SKIP_PIP=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Option inconnue : $1" >&2; usage; exit 1 ;;
    esac
done

echo "== Installation de perfect-geminini-pictures-for-claude-code =="

if [[ $SKIP_PIP -eq 0 ]]; then
    if ! command -v python3 &>/dev/null; then
        echo "Erreur : python3 introuvable. Installe-le avant de continuer." >&2
        exit 2
    fi
    echo ""
    echo "-- Installation des paquets Python --"
    python3 -m pip install --upgrade -r "${SCRIPT_DIR}/requirements.txt"
fi

if [[ $DOWNLOAD_CLUTS -eq 1 ]]; then
    echo ""
    echo "-- Téléchargement des CLUTs --"
    CLUTS_DIR="${SCRIPT_DIR}/data/cluts"
    mkdir -p "$CLUTS_DIR"
    echo "Placeholder : aucun pack officiel distribué automatiquement pour éviter les problèmes de licence."
    echo "Consulte data/cluts/README.md pour les sources libres recommandées."
fi

echo ""
echo "-- Permissions scripts --"
chmod +x "${SCRIPT_DIR}/scripts/"*.sh 2>/dev/null || true
chmod +x "${SCRIPT_DIR}/scripts/"*.py 2>/dev/null || true
chmod +x "${SCRIPT_DIR}/check-deps.sh" 2>/dev/null || true

echo ""
echo "-- Vérification des dépendances système --"
bash "${SCRIPT_DIR}/check-deps.sh" || true

echo ""
cat <<'MSG'
Installation terminée.

Étapes suivantes :
  1. Exporte GEMINI_API_KEY ou ajoute-le à ton .env :
         echo 'GEMINI_API_KEY=xxx' >> .env
  2. Installe les deps système manquantes signalées ci-dessus.
  3. Lance une première génération :
         claude /pgp-full "portrait femme buvant café matinal style reel"
MSG
