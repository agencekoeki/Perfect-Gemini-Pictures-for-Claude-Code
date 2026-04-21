---
name: pgp-prompt-forge
description: Compose le prompt Gemini final en intégrant toutes les données cognitives et les règles anti-AI look. Invoquer après pgp-shot-plan.
allowed-tools: Read, Write
---

# Skill `pgp-prompt-forge` — Composer le prompt Gemini

## Rôle

Assembler le **prompt final** qui sera envoyé à l'API Gemini, en
combinant brief + moodboard + shot-plan et en respectant strictement
les règles `.claude/rules/anti-ai-vocabulary.md`, `.claude/rules/camera-physics.md`,
`.claude/rules/lighting-coherence.md`, `.claude/rules/film-stock-library.md`,
`.claude/rules/camera-simulation-library.md`.

## Pré-requis

- `./.pgp-session/brief.json`
- `./.pgp-session/moodboard.json`
- `./.pgp-session/shot-plan.json`

## Déroulé

1. Lire les 3 JSON.
2. Charger les tokens prompt du film stock et du camera simulation depuis `.claude/data/film-stocks.json` et les rules correspondantes.
3. Appliquer le template ci-dessous.
4. Vérifier l'absence de tokens bannis (liste dans `.claude/rules/anti-ai-vocabulary.md`) — si présents, les remplacer ou supprimer.
5. Écrire dans `./.pgp-session/gemini-prompt.txt`.

## Template de prompt

### Mode with-product

```
Using the provided image of <product.name> as the exact product reference —
preserve the logo, exact color, proportions, and label text — <relationship_instruction>.

Scene: <subject_action> in <scene.environment>. <specific_elements joined in
natural sentence>. Time: <time_of_day>, <season>, <weather>.

Shot on <camera.prompt_description>, <focal_length>mm at <aperture>, ISO <iso>.
<primary_light.type> light from <primary_light.direction>, <primary_light.quality>,
color temp ~<primary_light.color_temp>K. <fill_light description if present>.

Rendered as if captured on <film_stock.prompt_tokens>. Visible <grain style>,
natural <color bias>.

Unretouched, straight out of camera, ISO noise visible in shadows,
realistic skin pore detail where skin is visible, peach fuzz on faces,
natural fabric weave texture, believable light wrap on subject edges.
Match shadow density and softness to the described lighting.

Ground the product with a soft occlusion shadow beneath. Match perspective
and scale to background. No glare or specular highlight over the logo or label.
Preserve accurate label text and edges exactly as in the reference image.

<composition>, <aspect_ratio> framing, <resolution> native.

Clean composition free of <forbidden items joined>, no digital sheen,
no airbrushing.
```

### Mode without-product

Identique mais **sans** le paragraphe "Using the provided image…" et
**sans** le paragraphe "Ground the product…". La scène décrit directement
le sujet humain ou la nature morte.

## Règles absolues

1. **Aucune négation en début de prompt.** Toutes les contraintes négatives vont en dernier paragraphe sous forme "Clean composition free of X, Y, Z".
2. **Ne jamais inclure** les tokens bannis : flawless, perfect, pristine, trending on artstation, octane render, 8K, ultra HD, hyperrealistic, stunning, breathtaking, masterpiece, highly detailed.
3. **Toujours inclure** au moins :
   - un token "film stock precise" (copié depuis `.claude/data/film-stocks.json → prompt_tokens`)
   - un token "camera precise" (copié depuis `.claude/rules/camera-simulation-library.md`)
   - un token "visible imperfection" (pore density, grain, CA)
   - un token "light wrap / shadow coherence"
4. **Formulation narrative, pas bullet list.** Le prompt se lit comme un brief humain envoyé à un assistant photographe.
5. **Longueur** : viser 180-280 mots. Moins = trop peu de direction, plus = dilution du signal.

## Contrôle qualité

Avant d'écrire le fichier :

- Vérifier que le prompt ne commence pas par "A" ou "An" suivi d'un nom abstrait (cliché IA).
- Vérifier présence de "Shot on" et d'un nom d'appareil précis.
- Vérifier présence d'une directive lumière avec source + direction + température.
- Vérifier présence d'au moins un token peau ou matière texturée si un humain est dans la scène.

## Sortie

```
Prompt forgé : ./.pgp-session/gemini-prompt.txt (237 mots)
Film : fujifilm_pro_400h
Camera : iphone_15_pro
Ratio : 9:16
```
