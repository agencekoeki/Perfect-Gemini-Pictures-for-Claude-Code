---
name: pgp-brief
description: Structure un besoin image en brief cognitif JSON. Invoquer quand l'utilisateur décrit un besoin visuel à générer avec Gemini, qu'il y ait ou non un produit à intégrer. Par exemple "je veux une image de X dans Y pour Instagram".
argument-hint: [description libre du besoin]
allowed-tools: Read, Write
---

# Skill `pgp-brief` — Extraire l'intent utilisateur

## Rôle

Transformer une description libre de l'utilisateur en **brief cognitif
structuré** (JSON) qui servira d'entrée à toutes les étapes suivantes du
pipeline.

Deux modes à détecter automatiquement :

- **`with-product`** : l'utilisateur mentionne une image produit (`--product-image PATH`, ou référence explicite à un fichier).
- **`without-product`** : aucune image de référence, scène humaine / lifestyle pure.

## Déroulé

1. Analyse la description reçue en argument.
2. Si des champs critiques sont ambigus (environnement trop vague, audience inconnue, ratio non précisé), pose **une question courte** à l'utilisateur. Une seule. Sinon, infère avec les valeurs par défaut listées plus bas.
3. Produis un JSON strict selon le schéma ci-dessous.
4. Sauvegarde dans `./.pgp-session/brief.json` (crée le dossier si besoin).
5. Affiche un résumé en 3 lignes : mode, scène, plateforme.

## Schéma du brief

```json
{
  "mode": "with-product",
  "product": {
    "name": "Bluetti AC200",
    "reference_image_path": "./bluetti.jpg",
    "key_features_to_preserve": ["logo Bluetti", "forme rectangulaire", "façade grise"]
  },
  "scene": {
    "environment": "intérieur van aménagé",
    "specific_elements": ["plan de travail bois", "fenêtre latérale", "plaid laine"],
    "time_of_day": "matin 9h",
    "season": "printemps",
    "weather": "ensoleillé doux"
  },
  "subject_action": "main ouvrant un carton",
  "story_beat": "moment de découverte",
  "platform": {
    "target": "instagram-reel",
    "aspect_ratio": "9:16",
    "resolution": "2K"
  },
  "audience": "nomades digitaux 30-45",
  "tone": ["authentique", "matinal", "chaleureux"],
  "brand_cues": {
    "logo_visibility": "discret",
    "brand_colors": []
  },
  "forbidden": ["logos concurrents", "personnes reconnaissables"]
}
```

### Mode without-product

Si aucune image produit n'est fournie :

```json
{
  "mode": "without-product",
  "product": null,
  "scene": { ... },
  ...
}
```

## Valeurs par défaut quand l'utilisateur ne précise pas

- `platform.target` : `instagram-post`
- `platform.aspect_ratio` : `1:1` si target instagram-post, `9:16` si instagram-reel ou tiktok, `16:9` si youtube
- `platform.resolution` : `2K`
- `tone` : déduire de l'environnement (van = authentique/nomade, studio = premium/clean, etc.)
- `brand_cues.logo_visibility` : `discret`
- `forbidden` : tableau vide si rien de spécifié

## Règles

- **Toujours remplir `scene.time_of_day`, `scene.environment` et `subject_action`**. Ce sont les trois éléments qui structurent le rendu.
- `key_features_to_preserve` est critique en mode with-product : c'est ce que Gemini doit absolument conserver. Sois explicite : logo, couleur exacte, proportions, texte sur label.
- Ne jamais inventer des éléments non demandés par l'utilisateur (personne s'il a parlé de nature morte, animal s'il a parlé de portrait, etc.).
- Si la plateforme cible n'est pas mentionnée, demande-la — c'est critique pour le ratio.

## Sortie attendue en fin de skill

```
Brief sauvegardé : ./.pgp-session/brief.json
Mode : with-product (Bluetti AC200)
Scène : intérieur van aménagé, matin 9h
Plateforme : instagram-reel 9:16 2K
```
