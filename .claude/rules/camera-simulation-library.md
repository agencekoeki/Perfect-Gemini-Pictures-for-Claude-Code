# Bibliothèque d'appareils simulables

Ancres caméra pour le prompt Gemini et l'injection EXIF via
`scripts/exif_inject.sh`. Chaque entrée a un `exif_profile` qui pointe vers
le JSON dans `data/exif-presets/`.

## Smartphones

### iphone_15_pro
- **Prompt description** : *"shot on iPhone 15 Pro main camera, computational photography"*
- **EXIF profile** : `iphone_15_pro.json`
- **Lens characteristics** : 24mm équivalent, f/1.78, léger distorsion grand-angle
- **Noise profile** : propre jusqu'à ISO 800, HDR banding occasionnel sur ciels
- **Usage typique** : UGC, reel Instagram authentique, snap quotidien, photo nocturne smartphone

## Plein format hybrides

### sony_a7iv
- **Prompt description** : *"shot on Sony A7 IV, full frame mirrorless"*
- **EXIF profile** : `sony_a7iv.json`
- **Lens characteristics** : zoom 24-70 f/2.8 GM II, rendu neutre, détail élevé
- **Noise profile** : excellent jusqu'à ISO 6400, grain fin doux
- **Usage typique** : lifestyle pro, éditorial, mariage, commercial

### canon_r5
- **Prompt description** : *"shot on Canon EOS R5 with RF 85mm f/1.2 L USM lens"*
- **EXIF profile** : `canon_r5.json`
- **Lens characteristics** : 85mm f/1.2 L, bokeh ultra doux, rendu cinématique
- **Noise profile** : propre jusqu'à ISO 3200, science couleur Canon chaude
- **Usage typique** : portrait premium, beauté, éditorial, wedding

### nikon_z8
- **Prompt description** : *"shot on Nikon Z8 with Nikkor Z 50mm f/1.2 S"*
- **EXIF profile** : à créer (optionnel)
- **Lens characteristics** : 50mm f/1.2, rendu Nikon net et neutre
- **Noise profile** : comparable Sony A7 IV, contraste un peu plus élevé
- **Usage typique** : reportage, wildlife, studio, paysage

### leica_q2
- **Prompt description** : *"shot on Leica Q2, fixed 28mm Summilux f/1.7"*
- **EXIF profile** : à créer (optionnel)
- **Lens characteristics** : 28mm fixe, rendu Leica "3D pop", micro-contraste élevé
- **Noise profile** : grain fin naturel, colorimétrie chaude signature Leica
- **Usage typique** : street, voyage, portrait environnemental, éditorial signature

## APS-C

### fujifilm_xt5
- **Prompt description** : *"shot on Fujifilm X-T5 with XF 35mm f/1.4 R, Classic Chrome film simulation"*
- **EXIF profile** : `fujifilm_xt5.json`
- **Lens characteristics** : 35mm f/1.4 équivalent 53mm, rendu Fujifilm couleur
- **Noise profile** : grain agréable dès ISO 800, simulations film intégrées
- **Usage typique** : street, lifestyle quotidien, documentaire, travel

## Compact expert

### ricoh_gr3
- **Prompt description** : *"shot on Ricoh GR III, 28mm f/2.8 fixed lens, street snapshot"*
- **EXIF profile** : à créer (optionnel)
- **Lens characteristics** : 28mm fixe, capteur APS-C, rendu quasi-argentique
- **Noise profile** : grain natif agréable, contraste marqué
- **Usage typique** : street discret, photo urbaine, journal intime

## Appareils jetables / vintage

### disposable_kodak
- **Prompt description** : *"shot on a single-use Kodak FunSaver 800 disposable camera, amateur snapshot"*
- **EXIF profile** : aucun (les jetables ne produisent pas d'EXIF)
- **Lens characteristics** : 32mm équivalent, f/10 fixe, flash pop-up
- **Noise profile** : grain 800 marqué, vignettage fort aux coins, CA visible
- **Usage typique** : esthétique années 90-2000, photo de soirée, UGC vintage

## Règles d'usage

1. Toujours associer un appareil à son preset EXIF correspondant quand il existe. Pour les entrées sans preset, créer le JSON dans `data/exif-presets/` en suivant la structure des existants.
2. La combinaison appareil + film est additive. "Shot on Canon R5 with RF 85mm, rendered as if captured on Kodak Portra 400" est valide : l'appareil est numérique, le rendu final simule le film.
3. Ne jamais mélanger deux appareils dans un même prompt ("shot on iPhone 15 Pro and Sony A7 IV"). Choisis-en un et tiens-le jusqu'au bout.
4. Le rendu Leica et Fujifilm est très corrélé à leur science couleur interne. Nommer explicitement "Leica Q2 rendering" ou "Fujifilm Classic Chrome" booste la justesse.

## Extension

Pour ajouter un appareil :

1. Créer `data/exif-presets/<nom>.json` avec la structure existante (voir `iphone_15_pro.json`).
2. Ajouter une entrée ici avec tous les champs.
3. Les scripts `scripts/exif_inject.sh` le picke automatiquement via `--camera <nom>`.
