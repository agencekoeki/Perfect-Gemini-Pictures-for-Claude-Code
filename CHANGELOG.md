# Changelog

Toutes les modifications notables de ce plugin sont documentées dans ce fichier.

Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/), et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [0.2.0] - 2026-04-21

### Modifié — Migration native

- Réorganisation complète : toute la donnée et tout le code vivent désormais sous `.claude/` (skills, agents, data, examples, rules, scripts, tests, requirements.txt, check-deps.sh, install.sh).
- Suppression de la structure plugin (`skills/`, `agents/`, `.claude-plugin/plugin.json`, `hooks/hooks.json`). Le projet est désormais un "setup Claude Code natif" : les skills sont auto-découvertes via `.claude/skills/`, les hooks via `.claude/settings.json`.
- Invocations simplifiées : `/pgp-full` au lieu de `/pgp:pgp-full`.
- Tous les chemins internes ont été mis à jour dans SKILL.md, scripts, docs, et .gitignore.
- Racine du repo ne contient plus que les méta fichiers (README, LICENSE, CHANGELOG, CLAUDE.md, .env*, .gitignore).
- Smoke tests 20/20 passent après migration.

## [0.1.1] - 2026-04-21

### Modifié

- Renommage du slug de plugin de `perfect-geminini-pictures-for-claude-code` vers `pgp` dans `.claude-plugin/plugin.json` pour raccourcir les invocations (ex : `/pgp:pgp-full` au lieu de `/perfect-geminini-pictures-for-claude-code:pgp-full`). Nom long conservé comme titre dans README.
- Mise à jour des instructions d'installation dans README et CLAUDE.md.

## [0.1.0] - 2026-04-21

### Ajouté

- Scaffold initial du plugin Claude Code `perfect-geminini-pictures-for-claude-code`.
- 8 skills cognitives : `pgp-brief`, `pgp-moodboard`, `pgp-shot-plan`, `pgp-prompt-forge`, `pgp-generate`, `pgp-postprocess`, `pgp-qa`, `pgp-full`.
- 3 sous-agents : `photographer`, `retoucher`, `art-director`.
- 5 rules de domaine : physique caméra, cohérence éclairage, vocabulaire anti-AI, bibliothèque de films argentiques, bibliothèque d'appareils simulables.
- 13 scripts de pipeline (Python + Bash) pour l'appel Gemini et la cascade de post-processing.
- 4 presets EXIF (iPhone 15 Pro, Sony A7 IV, Canon R5, Fujifilm X-T5).
- Catalogue de 8 films argentiques minimum.
- 2 exemples end-to-end : mode avec produit (Bluetti) et mode sans produit (portrait humain).
- Hook `PostToolUse` pour nettoyage des fichiers temporaires.
- Script `check-deps.sh` et `install.sh` pour la mise en place.
- Tests smoke pour les scripts et mock Gemini.
