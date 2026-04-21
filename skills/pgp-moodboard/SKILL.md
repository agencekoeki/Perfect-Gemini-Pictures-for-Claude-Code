---
name: pgp-moodboard
description: Construit un moodboard de références photographiques réelles et extrait les caractéristiques visuelles dominantes. Invoquer après pgp-brief.
allowed-tools: Read, Write, Bash(python:*)
---

# Skill `pgp-moodboard` — Ancrage visuel réel

## Rôle

Récupérer des références visuelles **réelles** (via Gemini grounding Google
Search) pour l'environnement décrit, et en extraire les caractéristiques
techniques dominantes (palette, éclairage, DoF, film stock typique).

Objectif : éviter de laisser le prompteur travailler "dans le vide" — on
donne à Gemini des ancres concrètes tirées de la vraie photographie lifestyle.

## Pré-requis

- `./.pgp-session/brief.json` doit exister (produit par `pgp-brief`).

## Déroulé

1. Lire le brief.
2. Composer une requête de recherche à partir de `scene.environment + scene.time_of_day + tone` (ex : "photographie lifestyle van aménagé matin ensoleillé").
3. Appeler `scripts/gemini_call.py` en mode research :

   ```bash
   python scripts/gemini_call.py \
     --mode research \
     --query "<requête composée>" \
     --metadata-output ./.pgp-session/moodboard-raw.json
   ```

4. Le script retourne un JSON avec un champ `raw_response` contenant le moodboard en texte.
5. Parser `raw_response` (JSON imbriqué) pour extraire :
   - `palette` : 3-5 couleurs hex dominantes
   - `lighting` : description brève du type d'éclairage dominant
   - `depth_of_field` : shallow, medium, large
   - `film_stock_suggestion` : un film depuis `data/film-stocks.json`
   - `angle` : low, eye-level, high, top-down
   - `references` : 3-5 descriptions ou URLs d'images trouvées
6. Écrire un moodboard propre dans `./.pgp-session/moodboard.json` :

```json
{
  "query": "photographie lifestyle van aménagé matin ensoleillé",
  "references": [
    "Nomadic couple cooking breakfast in campervan, warm window light",
    "Vintage camper van interior, wood countertop, morning coffee",
    "..."
  ],
  "palette": ["#E8CBA6", "#3B2A1E", "#C4A57F", "#F4EBD6"],
  "lighting": "window light from the side, warm 3000-4500K, medium-soft",
  "depth_of_field": "shallow, subject-first",
  "film_stock_suggestion": "fujifilm_pro_400h",
  "angle": "eye-level",
  "summary": "Ambiance chaude, bois clair, lumière diffuse fenêtre latérale, DoF faible, sensibilité film"
}
```

## Fallback

Si `scripts/gemini_call.py --mode research` échoue (pas de clé API, erreur
503 persistante), écrire un moodboard **par défaut cohérent avec le brief**
en utilisant les heuristiques :

- Intérieur matin → palette chaude (beiges, bruns, orangés), light 3000-4500K, film Portra 400
- Extérieur golden hour → palette doré-orange, light 2500-3500K, film Portra 400 / Gold 200
- Intérieur nuit néon → palette cyan-magenta, light 3000K + néons mélangés, film CineStill 800T
- Studio blanc → palette neutre, light diffuse 5500K, film Portra 160
- Extérieur plein jour → palette naturelle, light 5500-6500K, film Pro 400H

Mentionner dans le JSON `"source": "fallback-heuristic"`.

## Règles

- Ne jamais télécharger d'image réelle. Le moodboard est textuel.
- Vérifier que `film_stock_suggestion` est bien une clé valide de `data/film-stocks.json`.
- Si la réponse Gemini n'est pas un JSON parseable, extraire au mieux les champs avec du regex simple, et loguer un warning.

## Sortie attendue

```
Moodboard sauvegardé : ./.pgp-session/moodboard.json
Palette : #E8CBA6, #3B2A1E, #C4A57F
Film suggéré : fujifilm_pro_400h
Light : window light warm soft
```
