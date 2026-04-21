---
name: pgp-postprocess
description: Applique la cascade complète de post-processing (grain, noise, CA, vignette, color grade, JPEG cycle, EXIF injection) sur l'image brute Gemini. Invoquer après pgp-generate.
allowed-tools: Read, Write, Bash(python:*), Bash(./.claude/scripts/*:*), Bash(gmic *), Bash(convert *), Bash(exiftool *)
---

# Skill `pgp-postprocess` — Cascade de post-processing

## Rôle

Appliquer la cascade complète de post-processing sur l'image brute Gemini.
La cascade casse les signatures IA (pattern VAE, bruit uniforme, texture
plastique, absence d'EXIF) et ancre l'image dans le réel.

## Pré-requis

- `./.pgp-session/raw-gemini.png` (produit par `pgp-generate`)
- `./.pgp-session/shot-plan.json` (produit par `pgp-shot-plan`)

## Déroulé

1. Créer `./output/` si inexistant.
2. Composer un timestamp : `final-YYYYMMDD-HHMMSS.jpg`.
3. Lancer l'orchestrateur :

   ```bash
   python .claude/scripts/pipeline.py \
     --shot-plan ./.pgp-session/shot-plan.json \
     --input ./.pgp-session/raw-gemini.png \
     --output ./output/final-<timestamp>.jpg
   ```

4. L'orchestrateur enchaîne dans cet ordre strict :

   | # | Script                    | But                                    |
   | - | ------------------------- | -------------------------------------- |
   | 1 | `downsample_up.py`        | Casser le pattern VAE                  |
   | 2 | `chromatic_ab.py`         | Aberration chromatique radiale         |
   | 3 | `film_grain.sh`           | Émulation film G'MIC                   |
   | 4 | `sensor_noise.py`         | Bruit PRNU-like ISO-dépendant          |
   | 5 | `micro_imperfection.py`   | 1-3 dust spots invisibles              |
   | 6 | `color_grade.sh`          | CLUT final selon color_grade_mood      |
   | 7 | `vignette.sh`             | Vignettage subtil                      |
   | 8 | `jpeg_cycle.py`           | Re-compression JPEG 92 → PNG → JPEG 95 |
   | 9 | `exif_inject.sh`          | EXIF du camera_simulation              |

5. Chaque étape produit un fichier dans `./.pgp-session/stages/XX-*.png`.
6. Afficher un récap : temps total, taille finale, chemin de sortie.

## Règles

- Si une étape échoue, propager l'erreur avec le code de retour et le
  nom de l'étape. Ne pas continuer.
- Si `gmic` est absent, le script `film_grain.sh` et `color_grade.sh`
  basculent automatiquement sur un fallback ImageMagick.
- Les fichiers intermédiaires ne sont jamais supprimés par cette skill
  (ils sont utiles pour `pgp-qa` et les itérations). Le hook
  `PostToolUse` se charge du cleanup des fichiers de plus de 24h.

## Sortie attendue

```
Pipeline complet appliqué.
Image finale : ./output/final-20260421-093615.jpg (2.1 MB)
Stages : ./.pgp-session/stages/01-08
EXIF injecté : iPhone 15 Pro, ISO 400, f/1.8, 24mm
```
