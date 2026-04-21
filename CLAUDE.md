# CLAUDE.md

Instructions pour toute session Claude Code travaillant sur ce repo.

## Projet

Plugin Claude Code `perfect-geminini-pictures-for-claude-code` qui génère des images Gemini avec un rendu "vraie photo" via un pipeline cognitif en 7 phases (brief → moodboard → shot-plan → prompt-forge → generate → postprocess → qa).

Voir [README.md](README.md) pour la vue utilisateur complète.

## Structure

- `.claude-plugin/plugin.json` — manifest du plugin
- `skills/<nom>/SKILL.md` — 8 skills invocables via `/<plugin>:<nom>`
- `agents/<nom>.md` — 3 subagents (photographer, retoucher, art-director)
- `rules/*.md` — 5 rules de domaine chargées automatiquement
- `scripts/*.py|.sh` — 13 scripts du pipeline (voir `scripts/pipeline.py` pour l'orchestration)
- `data/exif-presets/*.json` — presets EXIF par appareil
- `data/film-stocks.json` — catalogue des films argentiques
- `data/cluts/` — CLUTs Hald PNG (gitignored, voir `data/cluts/README.md`)
- `examples/` — 2 exemples end-to-end
- `tests/` — smoke tests + mock Gemini
- `hooks/hooks.json` — PostToolUse cleanup

## Conventions

- **Doc, commentaires, messages d'erreur : français.** Code (noms de variables, fonctions, CLI flags) : anglais standard.
- **Conventional Commits** : `feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:`.
- **Pas de npm / Node.js.** Stack 100% Python + Bash + CLI Unix.
- **Pas de dépendance GPU.** Tout tourne sur CPU.
- **Pas d'API key hardcodée.** Toujours via `GEMINI_API_KEY` (env ou `.env`, jamais commité).
- **Pas de tentative de retirer SynthID.** Invisible, interdit par CGU Gemini, déjà incidemment dégradé par le pipeline.

## Règles anti-AI dans les prompts Gemini

Lire `rules/anti-ai-vocabulary.md` avant de modifier le template de `skills/pgp-prompt-forge/SKILL.md`. Jamais de "flawless", "8K", "trending on artstation", "hyperrealistic". Les contraintes négatives vont en fin de prompt comme checklist positive ("Clean composition free of X, Y, Z"), jamais en tête.

## Commandes utiles

```bash
# Vérifier les dépendances système et pip
./check-deps.sh

# Smoke tests (20 vérifs)
bash tests/test_scripts.sh

# Tests mock Gemini (3 vérifs, pas d'appel API réel)
python tests/test_gemini_mock.py

# Validation JSON de tous les fichiers de config
python -c "import json, pathlib; [json.load(open(p, encoding='utf-8')) for p in pathlib.Path('.').rglob('*.json') if '.git' not in str(p)]"

# Lancer le pipeline complet en mode draft
claude /perfect-geminini-pictures-for-claude-code:pgp-full "<description>"
```

## Points d'attention Windows

- Console cp1252 ne supporte pas certains caractères unicode (`→`, `✓`) dans les `print()` de Python : préférer `->` et `OK` pour les sorties stdout. Les fichiers JSON/MD restent en UTF-8.
- `bash` requis pour les scripts `.sh`. Git Bash ou WSL.
- Chemins : utiliser `pathlib.Path` côté Python, pas de backslash hardcodé.

## Ordre du pipeline (ne pas casser)

Dans `scripts/pipeline.py` :

```
downsample_up → chromatic_ab → film_grain → sensor_noise
→ micro_imperfection → color_grade → vignette → jpeg_cycle → exif_inject
```

- `downsample_up` **doit** rester en premier (casse le pattern VAE).
- `exif_inject` **doit** rester en dernier (sinon la ré-encodage JPEG écrase les tags EXIF).

## Ajouter du contenu

- **Nouveau film stock** → `data/film-stocks.json` + doc dans `rules/film-stock-library.md`
- **Nouvel appareil** → `data/exif-presets/<nom>.json` + doc dans `rules/camera-simulation-library.md`
- **Nouveau mood color grade** → nouveau case dans `scripts/color_grade.sh → apply_gmic_mood()`
- **Nouvelle skill** → `skills/<nom>/SKILL.md` avec frontmatter (name, description, allowed-tools)

## Ne pas faire

- Ajouter des `console.log` ou des `print` de debug oubliés dans le code livré.
- Introduire une dépendance Node ou un hard-require d'un outil GUI.
- Modifier `plugin.json` sans bump de version dans `CHANGELOG.md`.
- Commiter `.env`, `output/`, `.pgp-session/`, ou des CLUTs volumineux (déjà gitignorés).
- Skip les hooks git avec `--no-verify`.
