# CLAUDE.md

Instructions pour toute session Claude Code travaillant sur ce repo.

## Projet

Pipeline cognitif Claude Code pour générer des images Gemini avec un rendu "vraie photo" en 7 phases (brief → moodboard → shot-plan → prompt-forge → generate → postprocess → qa). Nom long du projet : `perfect-geminini-pictures-for-claude-code`.

**Mode de distribution** : commandes natives Claude Code, tout vit sous `.claude/`. Les skills sont auto-découvertes par Claude Code quand tu travailles dans ce dossier. Invocation directe : `/pgp-full`, `/pgp-brief`, etc.

Voir [README.md](README.md) pour la vue utilisateur complète.

## Structure

Tout le code et la donnée vivent sous `.claude/`. La racine ne contient que des méta fichiers projet (README, LICENSE, CHANGELOG, CLAUDE.md, .env*).

```
.claude/
├── skills/<nom>/SKILL.md       # 8 skills auto-decouvertes, invocables via /<nom>
├── agents/<nom>.md             # 3 subagents (photographer, retoucher, art-director)
├── settings.json               # hooks partages (PostToolUse cleanup) — committe
├── settings.local.json         # permissions locales personnelles — gitignore recommande
├── rules/*.md                  # 5 rules de domaine (lues par les skills via Read)
├── scripts/*.py|.sh            # 13 scripts du pipeline (cf scripts/pipeline.py)
├── data/exif-presets/*.json    # presets EXIF par appareil
├── data/film-stocks.json       # catalogue des films argentiques
├── data/cluts/                 # CLUTs Hald PNG (gitignored, voir data/cluts/README.md)
├── examples/                   # 2 exemples end-to-end (briefs + expected-output)
├── tests/                      # smoke tests + mock Gemini + fixtures
├── requirements.txt            # deps Python
├── check-deps.sh               # verifie les deps systeme
└── install.sh                  # installeur setup initial

.env                            # clef API Gemini (gitignore)
.env.example                    # template commite
.gitignore
README.md                       # doc utilisateur
CLAUDE.md                       # ce fichier
CHANGELOG.md
LICENSE
```

## Conventions

- **Doc, commentaires, messages d'erreur : français.** Code (noms de variables, fonctions, CLI flags) : anglais standard.
- **Conventional Commits** : `feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:`.
- **Pas de npm / Node.js.** Stack 100% Python + Bash + CLI Unix.
- **Pas de dépendance GPU.** Tout tourne sur CPU.
- **Pas d'API key hardcodée.** Toujours via `GEMINI_API_KEY` (env ou `.env`, jamais commité).
- **Pas de tentative de retirer SynthID.** Invisible, interdit par CGU Gemini, déjà incidemment dégradé par le pipeline.

## Règles anti-AI dans les prompts Gemini

Lire `.claude/rules/anti-ai-vocabulary.md` avant de modifier le template de `.claude/skills/pgp-prompt-forge/SKILL.md`. Jamais de "flawless", "8K", "trending on artstation", "hyperrealistic". Les contraintes négatives vont en fin de prompt comme checklist positive ("Clean composition free of X, Y, Z"), jamais en tête.

## Commandes utiles

```bash
# Vérifier les dépendances système et pip
./.claude/check-deps.sh

# Installation initiale (pip install + chmod)
./.claude/install.sh

# Smoke tests (20 vérifs)
bash .claude/tests/test_scripts.sh

# Tests mock Gemini (3 vérifs, pas d'appel API réel)
python .claude/tests/test_gemini_mock.py

# Validation JSON de tous les fichiers de config
python -c "import json, pathlib; [json.load(open(p, encoding='utf-8')) for p in pathlib.Path('.').rglob('*.json') if '.git' not in str(p)]"

# Lancer le pipeline complet en mode draft (depuis la racine du repo)
claude /pgp-full "<description>"
```

## Points d'attention Windows

- Console cp1252 ne supporte pas certains caractères unicode (`→`, `✓`) dans les `print()` de Python : préférer `->` et `OK` pour les sorties stdout. Les fichiers JSON/MD restent en UTF-8.
- `bash` requis pour les scripts `.sh`. Git Bash ou WSL.
- Chemins : utiliser `pathlib.Path` côté Python, pas de backslash hardcodé.

## Ordre du pipeline (ne pas casser)

Dans `.claude/scripts/pipeline.py` :

```
downsample_up -> chromatic_ab -> film_grain -> sensor_noise
-> micro_imperfection -> color_grade -> vignette -> jpeg_cycle -> exif_inject
```

- `downsample_up` **doit** rester en premier (casse le pattern VAE).
- `exif_inject` **doit** rester en dernier (sinon la ré-encodage JPEG écrase les tags EXIF).

## Ajouter du contenu

- **Nouveau film stock** → `.claude/data/film-stocks.json` + doc dans `.claude/rules/film-stock-library.md`
- **Nouvel appareil** → `.claude/data/exif-presets/<nom>.json` + doc dans `.claude/rules/camera-simulation-library.md`
- **Nouveau mood color grade** → nouveau case dans `.claude/scripts/color_grade.sh → apply_gmic_mood()`
- **Nouvelle skill** → `.claude/skills/<nom>/SKILL.md` avec frontmatter (name, description, allowed-tools)

## Contraintes sur les skills

Les skills utilisent des chemins relatifs (`.claude/scripts/pipeline.py`, `./.pgp-session/`, `./output/`). Elles supposent donc que la cwd de la session Claude Code est la racine de ce repo. Si tu veux rendre le pipeline invocable depuis un autre projet, deux options :

1. Dupliquer les skills dans `~/.claude/skills/` et adapter les chemins scripts avec un chemin absolu.
2. Repackager en plugin Claude Code (`.claude-plugin/plugin.json` + `skills/` à la racine) puis `claude --plugin-dir <chemin>` depuis n'importe où.

Par défaut, on suppose cwd = ce repo.

## Ne pas faire

- Ajouter des `console.log` ou des `print` de debug oubliés dans le code livré.
- Introduire une dépendance Node ou un hard-require d'un outil GUI.
- Modifier `.claude/settings.json` sans documenter dans `CHANGELOG.md`.
- Commiter `.env`, `output/`, `.pgp-session/`, ou des CLUTs volumineux (déjà gitignorés).
- Skip les hooks git avec `--no-verify`.
