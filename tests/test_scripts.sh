#!/usr/bin/env bash
# test_scripts.sh — Smoke tests des scripts du pipeline.
#
# Vérifie que chaque script accepte --help (ou -h) et retourne 0, et que
# les scripts Python d'image fonctionnent sur une fixture d'entrée.

set -uo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
ROOT_DIR="$(cd -- "${SCRIPT_DIR}/.." &>/dev/null && pwd)"
FIXTURE="${SCRIPT_DIR}/fixtures/sample_input.png"
TMP_DIR="$(mktemp -d)"
trap "rm -rf $TMP_DIR" EXIT

PASS=0
FAIL=0

GREEN='\033[0;32m'
RED='\033[0;31m'
RESET='\033[0m'

check() {
    local name="$1"
    local cmd="$2"
    if eval "$cmd" &>/dev/null; then
        printf "  ${GREEN}✓${RESET} %s\n" "$name"
        PASS=$((PASS + 1))
    else
        printf "  ${RED}✗${RESET} %s\n" "$name"
        FAIL=$((FAIL + 1))
    fi
}

echo "== Smoke tests des scripts =="
echo ""
echo "-- Help pages --"
check "gemini_call.py --help"        "python '$ROOT_DIR/scripts/gemini_call.py' --help"
check "downsample_up.py --help"      "python '$ROOT_DIR/scripts/downsample_up.py' --help"
check "sensor_noise.py --help"       "python '$ROOT_DIR/scripts/sensor_noise.py' --help"
check "chromatic_ab.py --help"       "python '$ROOT_DIR/scripts/chromatic_ab.py' --help"
check "jpeg_cycle.py --help"         "python '$ROOT_DIR/scripts/jpeg_cycle.py' --help"
check "micro_imperfection.py --help" "python '$ROOT_DIR/scripts/micro_imperfection.py' --help"
check "fourier_check.py --help"      "python '$ROOT_DIR/scripts/fourier_check.py' --help"
check "naturality_score.py --help"   "python '$ROOT_DIR/scripts/naturality_score.py' --help"
check "pipeline.py --help"           "python '$ROOT_DIR/scripts/pipeline.py' --help"
check "film_grain.sh --help"         "bash '$ROOT_DIR/scripts/film_grain.sh' --help"
check "vignette.sh --help"           "bash '$ROOT_DIR/scripts/vignette.sh' --help"
check "color_grade.sh --help"        "bash '$ROOT_DIR/scripts/color_grade.sh' --help"
check "exif_inject.sh --help"        "bash '$ROOT_DIR/scripts/exif_inject.sh' --help"

if [[ ! -f "$FIXTURE" ]]; then
    echo ""
    echo "Fixture absente ($FIXTURE), skip tests fonctionnels."
    echo ""
    echo "Résultat : $PASS ok, $FAIL ko"
    exit $FAIL
fi

echo ""
echo "-- Tests fonctionnels sur fixture --"
check "downsample_up produces output" \
    "python '$ROOT_DIR/scripts/downsample_up.py' --input '$FIXTURE' --output '$TMP_DIR/ds.png' && test -f '$TMP_DIR/ds.png'"
check "chromatic_ab produces output" \
    "python '$ROOT_DIR/scripts/chromatic_ab.py' --input '$FIXTURE' --output '$TMP_DIR/ca.png' --intensity subtle && test -f '$TMP_DIR/ca.png'"
check "sensor_noise produces output" \
    "python '$ROOT_DIR/scripts/sensor_noise.py' --input '$FIXTURE' --output '$TMP_DIR/sn.png' --iso 400 --seed 42 && test -f '$TMP_DIR/sn.png'"
check "micro_imperfection produces output" \
    "python '$ROOT_DIR/scripts/micro_imperfection.py' --input '$FIXTURE' --output '$TMP_DIR/mi.png' --count 2 --seed 42 && test -f '$TMP_DIR/mi.png'"
check "jpeg_cycle produces output" \
    "python '$ROOT_DIR/scripts/jpeg_cycle.py' --input '$FIXTURE' --output '$TMP_DIR/jc.jpg' && test -f '$TMP_DIR/jc.jpg'"
check "fourier_check produces JSON" \
    "python '$ROOT_DIR/scripts/fourier_check.py' --input '$FIXTURE' | grep -q fourier_score"
check "naturality_score produces JSON" \
    "python '$ROOT_DIR/scripts/naturality_score.py' --input '$FIXTURE' | grep -q score_total"

echo ""
if [[ $FAIL -eq 0 ]]; then
    echo -e "${GREEN}Résultat : $PASS ok, 0 ko${RESET}"
    exit 0
else
    echo -e "${RED}Résultat : $PASS ok, $FAIL ko${RESET}"
    exit 1
fi
