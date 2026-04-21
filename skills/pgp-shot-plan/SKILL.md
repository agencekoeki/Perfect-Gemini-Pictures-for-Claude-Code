---
name: pgp-shot-plan
description: Produit un shot list technique et lighting plan façon photographe pro. Invoquer après pgp-moodboard. Décide cadrage, angle, focale virtuelle, aperture, ISO, film stock, éclairage, imperfections visées.
allowed-tools: Read, Write, Agent(photographer)
---

# Skill `pgp-shot-plan` — Shot list et lighting plan

## Rôle

Produire un **shot-plan technique complet** (framing, composition, camera
simulation, focale, aperture, ISO, éclairage) via le subagent
`photographer`. Ce plan est consommé par `pgp-prompt-forge` pour composer
le prompt Gemini final, et par `scripts/pipeline.py` pour calibrer le
post-process.

## Pré-requis

- `./.pgp-session/brief.json`
- `./.pgp-session/moodboard.json`

## Déroulé

1. Lire les deux JSON.
2. Composer un prompt pour le subagent `photographer` avec cette structure :

   ```
   Voici le brief :
   <contenu brief.json>

   Voici le moodboard :
   <contenu moodboard.json>

   Produis le shot-plan JSON selon le schéma indiqué dans ton prompt système.
   ```

3. Invoquer le subagent avec `Agent(photographer)` et récupérer sa réponse JSON.
4. Valider que le JSON contient TOUS les champs requis :
   - `framing`, `composition`, `camera_simulation`, `focal_length_mm`, `aperture`, `shutter`, `iso`
   - `primary_light` (dict), `fill_light` (dict ou null), `rim_light` (dict ou null)
   - `film_stock`, `desired_imperfections` (list)
   - `post_processing_intent` (dict avec grain_intensity, vignette_strength, chromatic_aberration, color_grade_mood)
5. Si un champ manque ou si un film/appareil nommé n'existe pas dans les rules, relancer l'agent une fois avec un message correcteur.
6. Écrire dans `./.pgp-session/shot-plan.json`.

## Règles de validation

- `camera_simulation` doit être une clé existante dans `data/exif-presets/*.json` (iphone_15_pro, sony_a7iv, canon_r5, fujifilm_xt5).
- `film_stock` doit être une clé existante dans `data/film-stocks.json`.
- `iso` entier entre 25 et 25600.
- `focal_length_mm` entier entre 10 et 400.
- `aperture` string commençant par `f/`.
- `post_processing_intent.color_grade_mood` doit être une des valeurs : `warm-matinal`, `cold-clinical`, `neutral-editorial`, `moody-cinematic`, `teal-orange`, `faded-kodak`.

## Si aucun subagent `photographer` n'est disponible

Fallback : composer le shot-plan directement en suivant la logique du prompt
système du `photographer` (voir `agents/photographer.md`). Charger
`rules/camera-physics.md` pour la cohérence ISO/aperture/scène.

## Sortie

```
Shot-plan sauvegardé : ./.pgp-session/shot-plan.json
Camera : iPhone 15 Pro @ 24mm f/1.8 ISO 400
Film : fujifilm_pro_400h
Light : window camera-left soft diffuse 5600K
Mood : warm-matinal
```
