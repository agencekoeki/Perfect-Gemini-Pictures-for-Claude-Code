# Bibliothèque de films argentiques

Catalogue textuel utilisable dans le prompt Gemini et le shot-plan.
Les noms correspondent aux clés de `data/film-stocks.json` utilisées par
`scripts/film_grain.sh`.

## Films couleur

### kodak_portra_400
- **Grain** : fin, crémeux
- **Color bias** : peau chaude et neutre, verts doux, rouges légèrement désaturés
- **Contrast** : doux
- **Dynamic range** : très large (+3 / -3 stops tolérés)
- **ISO natif** : 400
- **Usage typique** : mariage, portrait, lifestyle lumière naturelle
- **Tokens prompt** : *"Kodak Portra 400, fine creamy grain, warm neutral skin tones, soft contrast, wide dynamic range"*

### kodak_portra_160
- **Grain** : très fin
- **Color bias** : peau légèrement crémeuse, palette pastel
- **Contrast** : très doux
- **Dynamic range** : large
- **ISO natif** : 160
- **Usage typique** : portrait éditorial, studio naturel
- **Tokens prompt** : *"Kodak Portra 160, ultra fine grain, pastel palette, creamy skin tones, soft editorial contrast"*

### fujifilm_pro_400h
- **Grain** : fin, neutre
- **Color bias** : verts et cyans naturels, peau légèrement rosée
- **Contrast** : doux
- **Dynamic range** : large
- **ISO natif** : 400
- **Usage typique** : mariage, lifestyle extérieur naturel, nature
- **Tokens prompt** : *"Fujifilm Pro 400H, fine neutral grain, natural greens and cyans, soft contrast, airy feel"*

### kodak_gold_200
- **Grain** : fin à moyen, chaleureux
- **Color bias** : jaunes dorés, rouges saturés, ambiance nostalgique
- **Contrast** : moyen
- **Dynamic range** : standard
- **ISO natif** : 200
- **Usage typique** : nostalgie années 90, vacances, famille
- **Tokens prompt** : *"Kodak Gold 200, warm golden grain, saturated reds and yellows, vintage 90s summer look"*

### cinestill_800t
- **Grain** : moyen, visible
- **Color bias** : bleus cyan forts, halos rouges autour des lumières (halation)
- **Contrast** : élevé
- **Dynamic range** : moyen
- **ISO natif** : 800
- **Usage typique** : scènes nocturnes, néons urbains, ambiance cinématique
- **Tokens prompt** : *"CineStill 800T, visible tungsten grain, red halation around light sources, cyan shadows, cinematic night look"*

### fujifilm_velvia_50
- **Grain** : très fin
- **Color bias** : saturation élevée, verts profonds, bleus intenses
- **Contrast** : élevé
- **Dynamic range** : étroit
- **ISO natif** : 50
- **Usage typique** : paysage, nature, panorama ensoleillé
- **Tokens prompt** : *"Fujifilm Velvia 50, fine grain, saturated greens and blues, high contrast landscape look"*

### polaroid_600
- **Grain** : texture chimique instantanée
- **Color bias** : dominante cyan-verte, peau légèrement délavée
- **Contrast** : faible, tons pastels
- **Dynamic range** : étroit
- **ISO natif** : 640
- **Usage typique** : souvenirs instantanés, années 80-90, ambiance intime
- **Tokens prompt** : *"Polaroid 600 instant film, chemical texture, washed cyan-green cast, soft pastel contrast, vintage intimate feel"*

## Films noir et blanc

### ilford_hp5
- **Grain** : moyen à marqué
- **Color bias** : noir et blanc contrasté
- **Contrast** : élevé
- **Dynamic range** : large
- **ISO natif** : 400
- **Usage typique** : reportage noir et blanc, street, documentaire
- **Tokens prompt** : *"Ilford HP5 Plus black and white, visible silver grain, high contrast, documentary reportage feel"*

## Règles d'usage

1. Toujours nommer un film **précis** dans le prompt (pas "film" générique). Le modèle ancre son rendu sur le corpus de référence du film nommé.
2. Vérifier la cohérence ISO natif vs contexte lumineux (voir `camera-physics.md`). Velvia 50 en intérieur nuit = incohérent.
3. Un film argentique ne se "retouche" pas comme un RAW numérique. Éviter les tokens numériques ("hyper-sharpened", "crisp digital") quand un film est nommé.
4. Une émulation Fujifilm interne (X-T5 "Classic Chrome") n'est PAS un film argentique. Si l'appareil est numérique, préférer "Fujifilm Classic Chrome film simulation" plutôt que "shot on Fujifilm Pro 400H".

## Extension

Pour ajouter un nouveau film :

1. Ajouter une entrée dans `data/film-stocks.json` avec les mêmes champs.
2. Documenter ici avec le même format.
3. Si G'MIC a une émulation proche, le nom se retrouve via `gmic fx_simulate_film 0 help`.
4. Sinon, fournir une CLUT Hald PNG dans `data/cluts/` et ajuster `scripts/film_grain.sh`.
