#!/usr/bin/env bash
# exif_inject.sh — Injecte des métadonnées EXIF crédibles.
#
# Charge un preset JSON depuis data/exif-presets/ et applique les valeurs
# via exiftool. Les valeurs CLI (iso, aperture, focal, shutter) surchargent
# celles du preset.
#
# IMPORTANT : on n'injecte JAMAIS de tag Software mentionnant "Gemini" ou
# "AI". L'objectif est de simuler une vraie capture caméra.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
ROOT_DIR="$(cd -- "${SCRIPT_DIR}/.." &>/dev/null && pwd)"
PRESETS_DIR="${ROOT_DIR}/data/exif-presets"

INPUT=""
OUTPUT=""
CAMERA="iphone_15_pro"
ISO=""
APERTURE=""
FOCAL=""
SHUTTER=""

usage() {
    cat <<'USAGE'
exif_inject.sh — Injecte des métadonnées EXIF crédibles via exiftool.

Options :
  --input PATH       Image d'entrée (requis).
  --output PATH      Image de sortie (requis).
  --camera NAME      Clé du preset (défaut: iphone_15_pro).
  --iso VALUE        Override ISO.
  --aperture VALUE   Override f-number (ex: 1.8).
  --focal VALUE      Override focale en mm.
  --shutter VALUE    Override vitesse (ex: 1/120).
  -h, --help         Affiche cette aide.

Les presets disponibles sont listés dans data/exif-presets/.
USAGE
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --input) INPUT="$2"; shift 2 ;;
        --output) OUTPUT="$2"; shift 2 ;;
        --camera) CAMERA="$2"; shift 2 ;;
        --iso) ISO="$2"; shift 2 ;;
        --aperture) APERTURE="$2"; shift 2 ;;
        --focal) FOCAL="$2"; shift 2 ;;
        --shutter) SHUTTER="$2"; shift 2 ;;
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

PRESET_FILE="${PRESETS_DIR}/${CAMERA}.json"
if [[ ! -f "$PRESET_FILE" ]]; then
    echo "Erreur : preset introuvable : $PRESET_FILE" >&2
    echo "Presets disponibles :" >&2
    ls -1 "$PRESETS_DIR" | sed 's/\.json$//' >&2
    exit 3
fi

skip_with_copy() {
    local reason="$1"
    echo "Avertissement : $reason — étape EXIF ignorée (image livrée sans métadonnées)." >&2
    mkdir -p "$(dirname "$OUTPUT")"
    if [[ "$INPUT" != "$OUTPUT" ]]; then
        cp "$INPUT" "$OUTPUT"
    fi
    echo "Skip EXIF : $OUTPUT"
    exit 0
}

if ! command -v exiftool &>/dev/null; then
    echo "  Install exiftool : choco install exiftool (Windows) | brew install exiftool (macOS) | apt install libimage-exiftool-perl (Linux)" >&2
    skip_with_copy "exiftool introuvable"
fi

if ! command -v jq &>/dev/null; then
    echo "  Install jq : choco install jq (Windows) | brew install jq (macOS) | apt install jq (Linux)" >&2
    skip_with_copy "jq introuvable"
fi

mkdir -p "$(dirname "$OUTPUT")"
cp "$INPUT" "$OUTPUT"

TAGS_JSON="$(jq -r '.exif | to_entries | map("-\(.key)=\(.value|tostring)") | .[]' "$PRESET_FILE")"

EXIFTOOL_ARGS=()
while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    EXIFTOOL_ARGS+=("$line")
done <<< "$TAGS_JSON"

if [[ -n "$ISO" ]]; then
    EXIFTOOL_ARGS+=("-ISO=${ISO}")
fi
if [[ -n "$APERTURE" ]]; then
    EXIFTOOL_ARGS+=("-FNumber=${APERTURE}")
    EXIFTOOL_ARGS+=("-ApertureValue=${APERTURE}")
fi
if [[ -n "$FOCAL" ]]; then
    EXIFTOOL_ARGS+=("-FocalLength=${FOCAL}")
fi
if [[ -n "$SHUTTER" ]]; then
    EXIFTOOL_ARGS+=("-ExposureTime=${SHUTTER}")
fi

EXIFTOOL_ARGS+=("-DateTimeOriginal=now")
EXIFTOOL_ARGS+=("-CreateDate=now")
EXIFTOOL_ARGS+=("-ModifyDate=now")

exiftool -overwrite_original -q "${EXIFTOOL_ARGS[@]}" "$OUTPUT"

echo "EXIF injecté (camera=$CAMERA) : $OUTPUT"
