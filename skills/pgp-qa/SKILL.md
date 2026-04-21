---
name: pgp-qa
description: Analyse forensique de l'image post-processée. Vérifie spectre Fourier, cohérence bruit, présence EXIF, rend un score 0-100 et des suggestions. Invoquer après pgp-postprocess.
allowed-tools: Read, Bash(python:*)
---

# Skill `pgp-qa` — Vérification forensique

## Rôle

Analyser l'image finale pour détecter les signatures IA résiduelles et
produire un **score composite 0-100** avec suggestions actionnables si
besoin.

## Pré-requis

- Une image finale dans `./output/`
- `./.pgp-session/gemini-metadata.json` (optionnel, pour le contexte)

## Déroulé

1. Identifier la dernière image dans `./output/` (timestamp le plus récent).
2. Lancer :

   ```bash
   python scripts/naturality_score.py \
     --input <image> \
     --output ./.pgp-session/qa-report.json
   ```

3. Lire le JSON produit et le présenter à l'utilisateur au format suivant :

   ```
   QA Report — final-20260421-093615.jpg
   Score total : 82/100

   Breakdown :
     Fourier (pattern VAE)   : 0.88   (plus c'est haut, plus c'est naturel)
     Noise coherence         : 0.75
     EXIF présent            : 1.00
     EXIF cohérent           : 0.95
     Texture variance        : 0.70

   Warnings :
     (aucun)

   Suggestions :
     (aucune — image prête à livrer)
   ```

4. Si warnings présents, les afficher tous et suggérer quelles étapes relancer.

## Grille d'interprétation

| Score  | Verdict                              | Action                     |
| ------ | ------------------------------------ | -------------------------- |
| 90-100 | Excellent, livrable tel quel         | Go prod                    |
| 75-89  | Bon, quelques imperfections mineures | Go prod ou retouche locale |
| 60-74  | Correct mais perfectible             | Envisager re-post-process  |
| 40-59  | Moyen, signatures IA visibles        | Régénérer ou retoucher     |
| < 40   | Mauvais                              | Régénérer depuis prompt    |

## Règles

- Le seuil de validation pour passer `draft → final` dans `pgp-full` est **75**.
- Si `score_total < 70`, afficher en premier les 3 suggestions les plus impactantes.
- Ne jamais cacher les warnings. La transparence du QA est critique pour l'utilisateur.

## Sortie attendue

Le contenu du `qa-report.json` formaté lisiblement pour l'utilisateur,
avec un verdict court en dernière ligne :

```
Verdict : BON (82/100). Livrable.
```

ou

```
Verdict : FAIBLE (58/100). Recommandation : re-run pgp-postprocess avec
intensity=high sur sensor_noise, ou régénérer depuis pgp-generate.
```
