#!/usr/bin/env bash
# vignette.sh — Vignettage ImageMagick subtil.
#
# Usage :
#   ./scripts/vignette.sh --input stage-4.png --output stage-5.png --strength low

set -euo pipefail

INPUT=""
OUTPUT=""
STRENGTH="low"

usage() {
    cat <<'USAGE'
vignette.sh — Applique un vignettage subtil via ImageMagick.

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
    low)    BLUR="0x80"; DARK="15" ;;
    medium) BLUR="0x90"; DARK="25" ;;
    high)   BLUR="0x100"; DARK="40" ;;
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

"$CONVERT" "$INPUT" \
    \( +clone -fill "gray(${DARK}%)" -colorize 100 \) \
    \( -clone 0 -fill white -colorize 100 -shave 10%x10% -gravity center -extent "$("$CONVERT" "$INPUT" -format "%wx%h" info:)" -blur "$BLUR" \) \
    -compose multiply -composite \
    "$OUTPUT"

echo "Vignettage appliqué (strength=$STRENGTH) : $OUTPUT"
