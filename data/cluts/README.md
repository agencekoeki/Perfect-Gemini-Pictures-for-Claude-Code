# CLUTs (Color Look-Up Tables)

Ce dossier stocke les CLUTs Hald PNG ou `.cube` utilisées par `scripts/color_grade.sh` et `scripts/film_grain.sh`.

## Format attendu

- **Hald PNG** : fichier PNG carré (typiquement 512×512 ou 1728×1728) encodant une table 3D de transformations couleur. Format natif G'MIC et ImageMagick.
- **`.cube`** : format LUT texte (standard Adobe), 17/33/65 entrées, compatible FFmpeg et certains outils.

## Où obtenir les CLUTs

### CLUTs embarquées dans G'MIC (recommandé)

G'MIC inclut plus de 1100 émulations de films dans son commande `fx_simulate_film`. Aucun téléchargement n'est nécessaire : elles sont appelées par nom depuis les scripts.

Liste complète :

```bash
gmic fx_simulate_film 0 help
```

Mapping vers `data/film-stocks.json` :

| Nom interne dans film-stocks.json | Nom G'MIC proche          |
| --------------------------------- | ------------------------- |
| kodak_portra_400                  | `portra400`               |
| kodak_portra_160                  | `portra160`               |
| fujifilm_pro_400h                 | `fuji_pro400h`            |
| kodak_gold_200                    | `kodak_gold_200`          |
| cinestill_800t                    | `cinestill_800t`          |
| ilford_hp5                        | `ilford_hp5`              |
| fujifilm_velvia_50                | `velvia_50`               |
| polaroid_600                      | `polaroid_600`            |

Les noms exacts varient selon la version G'MIC. `scripts/film_grain.sh` fait un fallback automatique si un nom n'existe pas.

### CLUTs externes (optionnel)

Si tu veux ajouter tes propres CLUTs signature :

1. Dépose un fichier `.png` (Hald) ou `.cube` dans ce dossier.
2. Édite `scripts/color_grade.sh` pour ajouter un mapping `--mood <nom>` → fichier.
3. Le fichier sera ignoré par Git (voir `.gitignore`).

Sources libres :

- [RawTherapee film simulations](https://rawpedia.rawtherapee.com/Film_Simulation) — Hald PNG téléchargeables.
- [G'MIC GitHub](https://github.com/GreycLab/gmic-community) — CLUTs communautaires.
- [Freepresets.com](https://www.freepresets.com/) — presets Lightroom à convertir.

## Script d'installation automatique

`install.sh` peut télécharger un pack minimal de CLUTs libres. Exécute :

```bash
./install.sh --download-cluts
```

Si G'MIC est installé, les émulations natives suffisent pour la plupart des cas.
