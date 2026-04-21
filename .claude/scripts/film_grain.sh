#!/usr/bin/env bash
# film_grain.sh — Applique une émulation de film via G'MIC.
#
# Usage :
#   ./scripts/film_grain.sh \
#     --input stage-2.png \
#     --output stage-3.png \
#     --film fujifilm_pro_400h \
#     --intensity 0.7
#
# Le nom --film correspond à une clé dans data/film-stocks.json. Si G'MIC n'a
# pas d'émulation exacte, on applique un fallback (ajustement couleur + grain
# simple) via ImageMagick.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
ROOT_DIR="$(cd -- "${SCRIPT_DIR}/.." &>/dev/null && pwd)"
FILM_STOCKS="${ROOT_DIR}/data/film-stocks.json"

INPUT=""
OUTPUT=""
FILM="kodak_portra_400"
INTENSITY="0.7"

usage() {
    cat <<'USAGE'
film_grain.sh — Émulation de film via G'MIC.

Options :
  --input PATH         Image d'entrée (requis).
  --output PATH        Image de sortie (requis).
  --film NAME          Clé dans data/film-stocks.json (défaut: kodak_portra_400).
  --intensity VALUE    Intensité 0.0-1.0 (défaut: 0.7).
  -h, --help           Affiche cette aide.
USAGE
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --input) INPUT="$2"; shift 2 ;;
        --output) OUTPUT="$2"; shift 2 ;;
        --film) FILM="$2"; shift 2 ;;
        --intensity) INTENSITY="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Option inconnue : $1" >&2; usage; exit 1 ;;
    esac
done

if [[ -z "$INPUT" || -z "$OUTPUT" ]]; then
    echo "Erreur : --input et --output sont requis." >&2
    usage
    exit 1
fi

if [[ ! -f "$INPUT" ]]; then
    echo "Erreur : fichier d'entrée introuvable : $INPUT" >&2
    exit 2
fi

mkdir -p "$(dirname "$OUTPUT")"

resolve_gmic_clut() {
    local film="$1"
    if [[ -f "$FILM_STOCKS" ]] && command -v jq &>/dev/null; then
        jq -r --arg f "$film" '.stocks[$f].gmic_clut // empty' "$FILM_STOCKS"
    fi
}

if command -v gmic &>/dev/null; then
    CLUT_NAME="$(resolve_gmic_clut "$FILM" || true)"
    CLUT_NAME="${CLUT_NAME:-$FILM}"
    if gmic "$INPUT" fx_emulate_film_colorslide 0,"$CLUT_NAME",0,"$INTENSITY" -output "$OUTPUT" &>/dev/null; then
        echo "Film émulé via G'MIC colorslide ($CLUT_NAME, intensity=$INTENSITY) : $OUTPUT"
        exit 0
    fi
    if gmic "$INPUT" fx_simulate_film 0,"$CLUT_NAME","$INTENSITY",0,0 -output "$OUTPUT" &>/dev/null; then
        echo "Film émulé via G'MIC simulate_film ($CLUT_NAME, intensity=$INTENSITY) : $OUTPUT"
        exit 0
    fi
    if gmic "$INPUT" fx_grain_film 0,"$INTENSITY",0,0,0 -output "$OUTPUT" &>/dev/null; then
        echo "Grain film générique G'MIC appliqué (intensity=$INTENSITY) : $OUTPUT"
        exit 0
    fi
    echo "Avertissement : G'MIC installé mais émulation $FILM indisponible. Fallback ImageMagick." >&2
fi

if command -v magick &>/dev/null; then
    CONVERT="magick"
elif command -v convert &>/dev/null; then
    CONVERT="convert"
else
    echo "Erreur : ni G'MIC ni ImageMagick installés. Installe gmic ou imagemagick." >&2
    exit 3
fi

"$CONVERT" "$INPUT" \
    -attenuate "$INTENSITY" +noise Gaussian \
    -modulate 100,95,100 \
    "$OUTPUT"
echo "Fallback grain+color appliqué via ImageMagick (intensity=$INTENSITY) : $OUTPUT"
