---
name: pgp-generate
description: Appelle l'API Gemini avec le prompt forgé et génère l'image. Gère retry sur 503, thinking level, refs produit. Invoquer après pgp-prompt-forge.
argument-hint: [draft|final]
allowed-tools: Read, Write, Bash(python:*)
---

# Skill `pgp-generate` — Appel API Gemini

## Rôle

Appeler l'API Gemini avec le prompt composé par `pgp-prompt-forge` et
sauvegarder l'image brute + les métadonnées d'appel.

## Pré-requis

- `./.pgp-session/gemini-prompt.txt`
- `./.pgp-session/brief.json`
- Variable d'environnement `GEMINI_API_KEY` définie.

## Argument

- `draft` : modèle Flash, 1K, thinking minimal (~$0.045)
- `final` : modèle Pro, 2K, thinking high (~$0.134)

Default : valeur de `PGP_DEFAULT_MODE` ou `draft`.

## Déroulé

1. Parse l'argument `draft` ou `final`.
2. Lire `./.pgp-session/brief.json` pour récupérer :
   - `platform.aspect_ratio` → paramètre `--aspect-ratio`
   - `platform.resolution` (forcer à 1K en draft, 2K en final)
   - `mode` et `product.reference_image_path` si `with-product`
3. Construire la commande :

   ```bash
   python scripts/gemini_call.py \
     --prompt-file ./.pgp-session/gemini-prompt.txt \
     --model [flash|pro] \
     --aspect-ratio <ratio> \
     --resolution [1K|2K] \
     --thinking-level [minimal|high] \
     --output ./.pgp-session/raw-gemini.png \
     --metadata-output ./.pgp-session/gemini-metadata.json
   ```

4. Si mode `with-product`, ajouter `--ref-image <brief.product.reference_image_path>` (vérifier que le fichier existe, sinon erreur claire).
5. Exécuter. Le script gère automatiquement le retry exponentiel sur 503/429 (5 tentatives).
6. Si succès, afficher un résumé. Si échec, propager l'erreur avec un message utile.

## Gestion d'erreurs

- **GEMINI_API_KEY manquante** : rappeler d'exporter la variable, lien vers aistudio.google.com/apikey.
- **503 persistant après 5 retries** : suggérer de relancer plus tard, Gemini preview est souvent surchargé.
- **Image refusée (safety filter)** : afficher `finish_reason` et suggérer de régénérer le prompt avec moins de références humaines identifiables.
- **Fichier de référence produit introuvable** : afficher le chemin attendu, demander à l'utilisateur de vérifier.

## Sortie attendue

```
Image générée : ./.pgp-session/raw-gemini.png (4823 ms, ~$0.045)
Modèle : gemini-3.1-flash-image-preview
Ratio : 9:16 @ 1K
Thinking : minimal (budget 128)
```
