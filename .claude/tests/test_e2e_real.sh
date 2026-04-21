#!/usr/bin/env bash
# test_e2e_real.sh — Test end-to-end RÉEL avec appel API Gemini.
#
# Exécute le pipeline complet sans passer par Claude Code :
#   1. Load .env (GEMINI_API_KEY)
#   2. Brief + shot-plan écrits en dur (scène demandée)
#   3. Compose le prompt Gemini
#   4. Appel réel Gemini Flash (draft, ~$0.045)
#   5. Cascade post-processing complète
#   6. Score QA forensique
#   7. Affiche le chemin de l'image finale + score
#
# Scène : plan américain, personne sortant d'un camping-car.

set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." &>/dev/null && pwd)"
cd "$ROOT_DIR"

# Charge .env
if [[ -f .env ]]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
fi

if [[ -z "${GEMINI_API_KEY:-}" ]]; then
    echo "ERREUR : GEMINI_API_KEY absent. Vérifie ton .env." >&2
    exit 1
fi

SESSION_DIR="./.pgp-session-e2e"
OUTPUT_DIR="./output"
mkdir -p "$SESSION_DIR/stages" "$OUTPUT_DIR"

echo "== Test E2E réel pipeline Gemini =="
echo "Scène : plan américain, personne sortant d'un camping-car, matin doux."
echo ""

# ------------------------------------------------------------------
# Étape 1 : brief
# ------------------------------------------------------------------
echo "[1/6] Écriture du brief…"
cat > "$SESSION_DIR/brief.json" <<'JSON'
{
  "mode": "without-product",
  "product": null,
  "scene": {
    "environment": "extérieur devant un camping-car aménagé garé en bord de forêt",
    "specific_elements": [
      "porte coulissante du camping-car ouverte",
      "herbes hautes au premier plan flou",
      "bois de pins en arrière-plan",
      "marche du camping-car visible"
    ],
    "time_of_day": "matin doux 8h30",
    "season": "fin d été",
    "weather": "lumière chaude douce, ciel légèrement voilé"
  },
  "subject_action": "personne trentenaire en t-shirt gris et jean descendant la marche du camping-car, main posée sur le montant de porte, regard vers le paysage",
  "story_beat": "premier moment dehors au réveil, pause contemplative avant le café",
  "platform": {
    "target": "instagram-post",
    "aspect_ratio": "4:5",
    "resolution": "1K"
  },
  "audience": "vanlifers 30-45, slow-travel",
  "tone": ["authentique", "matinal", "libre", "contemplatif"],
  "brand_cues": {
    "logo_visibility": "aucun",
    "brand_colors": []
  },
  "forbidden": [
    "logos de marque visibles",
    "téléphones et écrans",
    "visages reconnaissables en gros plan"
  ]
}
JSON
echo "  ✓ $SESSION_DIR/brief.json"

# ------------------------------------------------------------------
# Étape 2 : shot-plan (photographer style, écrit en dur ici)
# ------------------------------------------------------------------
echo "[2/6] Écriture du shot-plan…"
cat > "$SESSION_DIR/shot-plan.json" <<'JSON'
{
  "framing": "american medium shot (plan américain, genoux à tête)",
  "composition": "rule of thirds, sujet tier droit, porte du van en ligne directrice gauche",
  "camera_simulation": "fujifilm_xt5",
  "focal_length_mm": 35,
  "aperture": "f/2.8",
  "shutter": "1/250",
  "iso": 400,
  "primary_light": {
    "type": "soleil matinal diffus à travers les arbres",
    "direction": "camera-right back",
    "quality": "soft warm diffuse",
    "color_temp": 4200
  },
  "fill_light": {
    "type": "ambient bounce de la paroi blanche du van",
    "intensity": "low",
    "color_temp": 5000
  },
  "rim_light": {
    "type": "sunlight rim",
    "direction": "back-right",
    "quality": "warm thin"
  },
  "film_stock": "kodak_portra_400",
  "desired_imperfections": [
    "grain fin visible",
    "léger vignetting aux coins",
    "chromatic aberration subtile aux bords de feuillage",
    "très légère texture peau authentique"
  ],
  "post_processing_intent": {
    "grain_intensity": "medium",
    "vignette_strength": "low",
    "chromatic_aberration": "subtle",
    "color_grade_mood": "warm-matinal"
  }
}
JSON
echo "  ✓ $SESSION_DIR/shot-plan.json"

# ------------------------------------------------------------------
# Étape 3 : prompt Gemini
# ------------------------------------------------------------------
echo "[3/6] Composition du prompt Gemini…"
cat > "$SESSION_DIR/gemini-prompt.txt" <<'PROMPT'
American medium shot (from knees to head) of a person in their thirties stepping off the running board of a small converted campervan parked at the edge of a pine forest. The subject wears a faded grey t-shirt and jeans, one hand resting on the door frame, looking out toward the landscape. Tall grass blurs in the immediate foreground.

Time: soft morning around 8:30, late summer. Warm diffuse sunlight filters through the pine trees from the back-right, creating a thin warm rim on the subject's shoulder and hair. A low ambient fill bounces from the white side panel of the van. The scene breathes calm, a first moment outside before coffee.

Shot on a Fujifilm X-T5 with XF 35mm f/1.4 R, at f/2.8, ISO 400, 1/250s. Rendered as if captured on Kodak Portra 400 — fine creamy grain, warm neutral skin tones, soft contrast, wide dynamic range.

Unretouched, straight out of camera. Visible pore density on the face, peach fuzz, natural stubble details, believable skin imperfections. T-shirt cotton shows a visible weave and natural creases around the shoulder and waist. Light wrap on the right side of the body where sun grazes. ISO noise subtly visible in the shadowed side of the van. Grass blades in foreground have motion-soft edges, not digital sharpness. Pine needles in background with airy out-of-focus bokeh, not CG blur.

Natural occlusion shadow beneath the running board of the van. Shadow density matches the diffuse morning light, not harsh. Leaves cast dappled soft shadows on the ground.

Composition: rule of thirds with the subject on the right third, the van door frame as a leading vertical on the left, horizon line around upper third. 4:5 vertical framing, 1K native.

Clean composition free of brand logos, visible smartphone screens, recognizable faces in tight close-up, text overlays, filters.
PROMPT
echo "  ✓ $SESSION_DIR/gemini-prompt.txt ($(wc -w < "$SESSION_DIR/gemini-prompt.txt") mots)"

# ------------------------------------------------------------------
# Étape 4 : appel réel Gemini Flash
# ------------------------------------------------------------------
echo "[4/6] Appel API Gemini Flash (draft, ~\$0.045)…"
python .claude/scripts/gemini_call.py \
    --prompt-file "$SESSION_DIR/gemini-prompt.txt" \
    --model flash \
    --aspect-ratio "4:5" \
    --resolution 1K \
    --thinking-level minimal \
    --output "$SESSION_DIR/raw-gemini.png" \
    --metadata-output "$SESSION_DIR/gemini-metadata.json"

if [[ ! -f "$SESSION_DIR/raw-gemini.png" ]]; then
    echo "ÉCHEC : pas d'image générée." >&2
    exit 2
fi

# ------------------------------------------------------------------
# Étape 5 : cascade post-processing
# ------------------------------------------------------------------
echo "[5/6] Cascade post-processing…"
TS="$(date +%Y%m%d-%H%M%S)"
FINAL="$OUTPUT_DIR/e2e-final-$TS.jpg"
python .claude/scripts/pipeline.py \
    --shot-plan "$SESSION_DIR/shot-plan.json" \
    --input "$SESSION_DIR/raw-gemini.png" \
    --output "$FINAL" \
    --stages-dir "$SESSION_DIR/stages"

# ------------------------------------------------------------------
# Étape 6 : QA forensique
# ------------------------------------------------------------------
echo "[6/6] Analyse QA forensique…"
python .claude/scripts/naturality_score.py \
    --input "$FINAL" \
    --output "$SESSION_DIR/qa-report.json"

echo ""
echo "== RÉSULTAT E2E =="
echo "Image finale    : $FINAL"
echo "Raw Gemini      : $SESSION_DIR/raw-gemini.png"
echo "QA report       : $SESSION_DIR/qa-report.json"
echo ""
echo "-- Métadonnées génération --"
python -c "import json; d=json.load(open('$SESSION_DIR/gemini-metadata.json', encoding='utf-8')); print(f\"Modèle : {d['model']}\"); print(f\"Latency : {d['latency_ms']} ms\"); print(f\"Coût estimé : \${d['cost_estimate_usd']}\")"
echo ""
echo "-- EXIF injecté sur l'image finale --"
if command -v exiftool &>/dev/null; then
    exiftool "$FINAL" | head -20
else
    echo "exiftool non dispo, skip."
fi
