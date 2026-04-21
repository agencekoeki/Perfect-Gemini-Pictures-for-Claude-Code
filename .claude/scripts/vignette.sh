#!/usr/bin/env bash
# vignette.sh — Vignettage ImageMagick subtil par radial-gradient.
#
# Strategie : on genere un mask radial white-center -> gray(EDGE_BRIGHTNESS%) aux coins
# puis on multiplie l'original par ce mask. Garder EDGE_BRIGHTNESS proche de 100
# pour un effet subtil. Valeurs :
#   low    : coins a 92% de la luminance originale (tres discret)
#   medium : coins a 82%
#   high   : coins a 68%
#
# Usage :
#   ./vignette.sh --input stage-4.png --output stage-5.png --strength low

set -euo pipefail

INPUT=""
OUTPUT=""
STRENGTH="low"

usage() {
    cat <<'USAGE'
vignette.sh — Applique un vignettage subtil via radial-gradient ImageMagick.

Options :
  --input PATH        Image d'entrée (requis).
  --output PATH       Image de sortie (requis).
  --strength VALUE    low | medium | high (défaut: low).
  -h, --help          Affiche cette aide.
USAGE
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --input) INPUT="$2"; shift 2 ;;
        --output) OUTPUT="$2"; shift 2 ;;
        --strength) STRENGTH="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Option inconnue : $1" >&2; usage; exit 1 ;;
    esac
done

if [[ -z "$INPUT" || -z "$OUTPUT" ]]; then
    echo "Erreur : --input et --output sont requis." >&2
    exit 1
fi

if [[ ! -f "$INPUT" ]]; then
    echo "Erreur : fichier d'entrée introuvable : $INPUT" >&2
    exit 2
fi

case "$STRENGTH" in
    low)    EDGE="92" ;;
    medium) EDGE="82" ;;
    high)   EDGE="68" ;;
    *)
        echo "Erreur : --strength doit être low|medium|high" >&2
        exit 3
        ;;
esac

if command -v magick &>/dev/null; then
    CONVERT="magick"
elif command -v convert &>/dev/null; then
    CONVERT="convert"
else
    echo "Erreur : ImageMagick introuvable. Installe imagemagick." >&2
    exit 4
fi

mkdir -p "$(dirname "$OUTPUT")"

# Dimensions pour construire le mask a la bonne taille.
DIM="$("$CONVERT" "$INPUT" -format "%wx%h" info:)"

# Mask : blanc au centre -> gray(EDGE%) aux coins. Multiplie avec l'original.
# Le multiply conserve l'image la ou le mask est 100% blanc, assombrit progressivement
# vers les coins selon le gradient.
"$CONVERT" "$INPUT" \
    \( -size "$DIM" radial-gradient:"white-gray(${EDGE}%)" \) \
    -compose multiply -composite \
    "$OUTPUT"

echo "Vignettage appliqué (strength=$STRENGTH, edges at ${EDGE}% brightness) : $OUTPUT"
