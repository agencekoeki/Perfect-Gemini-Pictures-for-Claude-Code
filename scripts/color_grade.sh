#!/usr/bin/env bash
# color_grade.sh — Color grade final via G'MIC ou CLUT externe.
#
# Moods disponibles :
#   warm-matinal     — jaunes chauds, ombres bleutées
#   cold-clinical    — neutre froid, contrast élevé
#   neutral-editorial — balance propre, légèrement désaturé
#   moody-cinematic  — noirs profonds, highlights plombés
#   teal-orange      — split-toning cinéma Hollywood
#   faded-kodak      — highlights lavés, shadows plombés

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
ROOT_DIR="$(cd -- "${SCRIPT_DIR}/.." &>/dev/null && pwd)"
CLUTS_DIR="${ROOT_DIR}/data/cluts"

INPUT=""
OUTPUT=""
MOOD="neutral-editorial"
INTENSITY="0.8"

usage() {
    cat <<'USAGE'
color_grade.sh — Color grade final.

Options :
  --input PATH         Image d'entrée (requis).
  --output PATH        Image de sortie (requis).
  --mood NAME          warm-matinal | cold-clinical | neutral-editorial |
                       moody-cinematic | teal-orange | faded-kodak
                       (défaut: neutral-editorial).
  --intensity VALUE    0.0-1.0 (défaut: 0.8).
  -h, --help           Affiche cette aide.
USAGE
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --input) INPUT="$2"; shift 2 ;;
        --output) OUTPUT="$2"; shift 2 ;;
        --mood) MOOD="$2"; shift 2 ;;
        --intensity) INTENSITY="$2"; shift 2 ;;
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

mkdir -p "$(dirname "$OUTPUT")"

external_clut_for_mood() {
    case "$1" in
        warm-matinal) echo "warm_matinal.png" ;;
        cold-clinical) echo "cold_clinical.png" ;;
        neutral-editorial) echo "neutral_editorial.png" ;;
        moody-cinematic) echo "moody_cinematic.png" ;;
        teal-orange) echo "teal_orange.png" ;;
        faded-kodak) echo "faded_kodak.png" ;;
        *) echo "" ;;
    esac
}

apply_gmic_mood() {
    case "$1" in
        warm-matinal)
            gmic "$INPUT" fx_color_balance 0,0,-8,8,10,-5,0,10,-10,0,1,0 -output "$OUTPUT"
            ;;
        cold-clinical)
            gmic "$INPUT" fx_color_balance 0,0,5,-10,-5,5,0,-5,5,0,1,0 fx_adjust_colors 0,3,-3,0,0,0,0,50,50 -output "$OUTPUT"
            ;;
        neutral-editorial)
            gmic "$INPUT" fx_adjust_colors 2,-2,-5,0,0,0,0,50,50 -output "$OUTPUT"
            ;;
        moody-cinematic)
            gmic "$INPUT" fx_adjust_colors 5,-5,-8,0,-10,0,0,50,50 fx_color_balance 0,0,3,-3,5,-5,-8,3,-3,0,1,0 -output "$OUTPUT"
            ;;
        teal-orange)
            gmic "$INPUT" fx_color_balance 0,0,-12,0,12,10,15,0,-10,0,1,0 -output "$OUTPUT"
            ;;
        faded-kodak)
            gmic "$INPUT" fx_adjust_colors 0,-8,-10,0,5,0,0,50,50 fx_color_balance 0,0,-5,5,3,-3,-8,5,-3,0,1,0 -output "$OUTPUT"
            ;;
        *)
            return 1
            ;;
    esac
}

CLUT_FILE="$(external_clut_for_mood "$MOOD")"
if [[ -n "$CLUT_FILE" && -f "${CLUTS_DIR}/${CLUT_FILE}" ]] && command -v gmic &>/dev/null; then
    gmic "$INPUT" _apply_clut "${CLUTS_DIR}/${CLUT_FILE}","$INTENSITY" -output "$OUTPUT" &>/dev/null && {
        echo "Color grade via CLUT externe ($CLUT_FILE) : $OUTPUT"
        exit 0
    }
fi

if command -v gmic &>/dev/null; then
    if apply_gmic_mood "$MOOD" &>/dev/null; then
        echo "Color grade G'MIC appliqué (mood=$MOOD) : $OUTPUT"
        exit 0
    fi
    echo "Avertissement : mood $MOOD non pris en charge par G'MIC. Fallback ImageMagick." >&2
fi

if command -v magick &>/dev/null; then
    CONVERT="magick"
elif command -v convert &>/dev/null; then
    CONVERT="convert"
else
    echo "Erreur : ni G'MIC ni ImageMagick installés." >&2
    exit 3
fi

case "$MOOD" in
    warm-matinal)      MOD="100,95,102" ;;
    cold-clinical)     MOD="100,90,98" ;;
    neutral-editorial) MOD="100,95,100" ;;
    moody-cinematic)   MOD="95,90,98" ;;
    teal-orange)       MOD="100,100,100" ;;
    faded-kodak)       MOD="100,85,98" ;;
    *)                 MOD="100,100,100" ;;
esac

"$CONVERT" "$INPUT" -modulate "$MOD" -contrast-stretch 1%x1% "$OUTPUT"
echo "Fallback color grade ImageMagick (mood=$MOOD) : $OUTPUT"
