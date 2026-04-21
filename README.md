# perfect-geminini-pictures-for-claude-code

> Générer des images Gemini qui ressemblent vraiment à des photos.

Setup Claude Code **natif** (pas packagé en plugin distribuable) : tout le pipeline vit sous `.claude/`, les skills sont auto-découvertes quand tu ouvres Claude Code dans ce repo. Invocation directe sans préfixe : `/pgp-full`, `/pgp-brief`, etc.

Pipeline cognitif complet en 7 phases pour produire, à partir de l'API Gemini (Nano Banana / Nano Banana 2 / Nano Banana Pro), des images avec un rendu "vraie photo humaine" et non "image IA générique". Une chaîne de skills + scripts locaux (ImageMagick, G'MIC, exiftool, Python scientifique) qui reproduit ce qu'un photographe pro + un retoucheur feraient, y compris les imperfections qui signent le réel.

---

## 1. Pourquoi ce projet

Les images générées par Gemini ont une signature "IA" reconnaissable à
l'œil et en analyse forensique :

- Textures trop lisses, peau plastique, matières sans friction
- Lumière trop parfaite, ombres qui ne racontent pas la source
- Absence de bruit capteur cohérent (PRNU)
- Pattern de grille dans le spectre de Fourier (artefact VAE upsampling)
- Aucun artefact JPEG naturel
- Métadonnées EXIF vides ou non-crédibles

Ce plugin adresse chaque point séparément, via :

1. **Un prompt soigné**, débarrassé des tokens "IA" qui ramènent le modèle dans le cluster concept-art (`.claude/rules/anti-ai-vocabulary.md`).
2. **Un shot-plan technique cohérent** (ISO, aperture, focale, éclairage), produit par un subagent `photographer` (`.claude/rules/camera-physics.md`, `.claude/rules/lighting-coherence.md`).
3. **Un post-processing cascade** qui casse les signatures VAE, injecte du bruit sensor crédible, applique une émulation film, une aberration chromatique radiale, du micro-vignettage, un cycle JPEG et des métadonnées EXIF de vraie caméra.
4. **Un QA forensique** qui mesure la naturalité du résultat via FFT, cohérence du bruit et EXIF.

---

## 2. Prérequis système

| Outil          | Version min | macOS                        | Debian/Ubuntu                           | Windows (WSL)                            |
| -------------- | ----------- | ---------------------------- | --------------------------------------- | ---------------------------------------- |
| `imagemagick`  | 7.0+        | `brew install imagemagick`   | `sudo apt install imagemagick`          | via WSL, ou `choco install imagemagick`  |
| `gmic`         | 3.0+        | `brew install gmic`          | `sudo apt install gmic`                 | via WSL, ou build depuis `gmic.eu`       |
| `exiftool`     | 12.0+       | `brew install exiftool`      | `sudo apt install libimage-exiftool-perl` | `choco install exiftool` ou via WSL    |
| `python`       | 3.10+       | `brew install python@3.11`   | `sudo apt install python3`              | `python.org` ou `choco install python`   |
| `jq`           | 1.6+        | `brew install jq`            | `sudo apt install jq`                   | `choco install jq`                       |
| `git`          | 2.30+       | `brew install git`           | `sudo apt install git`                  | `git-scm.com`                            |

Vérifie le tout via :

```bash
./.claude/check-deps.sh
```

---

## 3. Installation

```bash
git clone https://github.com/koeki-agency/perfect-geminini-pictures-for-claude-code.git
cd perfect-geminini-pictures-for-claude-code
./.claude/install.sh
```

Le script `install.sh` :

1. Installe les paquets Python (`.claude/requirements.txt`).
2. Rend les scripts exécutables.
3. Lance `.claude/check-deps.sh` pour signaler les manques système.

Option : télécharger un pack de CLUTs couleur libres (non fourni par défaut pour raisons de licence) :

```bash
./.claude/install.sh --download-cluts
```

### Utilisation dans Claude Code

Aucune installation de plugin n'est requise. Ouvre simplement Claude Code dans ce dossier — les skills sous `.claude/skills/` sont auto-découvertes. Tu peux les invoquer directement : `/pgp-full`, `/pgp-brief`, etc.

Si Claude Code était déjà ouvert avant le clone, tape `/reload-plugins` pour rafraîchir.

---

## 4. Configuration

Crée ton `.env` local à partir du template fourni :

```bash
cp .env.example .env
```

Puis édite `.env` et remplis ta vraie clé API :

```bash
GEMINI_API_KEY=AIzaSy...       # obligatoire
PGP_DEFAULT_MODE=draft          # optionnel, draft|final
PGP_DATA_DIR=                   # optionnel, override du dossier data
```

**Sécurité** : le `.env` est ignoré par git (voir `.gitignore` ligne 6). Il ne sera jamais poussé, même avec `git add -A`. Seul `.env.example` (sans clé réelle) est versionné, comme template pour les nouveaux clones.

Obtiens une clé API sur [aistudio.google.com/apikey](https://aistudio.google.com/apikey). Elle est gratuite pour les premiers essais, tarifée ensuite à l'image (voir section 12).

---

## 5. Usage rapide

### Mode avec produit

```bash
claude /pgp-full "unboxing batterie Bluetti AC200 dans van aménagé matin" --product-image ./bluetti.jpg
```

### Mode sans produit

```bash
claude /pgp-full "portrait femme buvant café matinal style reel Instagram"
```

### Rejouer un exemple pré-rempli

```bash
claude /pgp-full --from-brief .claude/examples/portrait-humain-sans-produit/brief.json
```

Chaque invocation :

1. Crée `./.pgp-session/` avec tous les livrables intermédiaires.
2. Génère un draft (Flash, ~$0.045).
3. Post-processe la cascade complète.
4. Calcule un score QA.
5. Si score ≥ 75, te propose le passage en final (Pro, ~$0.134).
6. Dépose l'image finale dans `./output/final-<timestamp>.jpg`.
7. Affiche un verdict créatif honnête de l'agent `art-director`.

---

## 6. Les 7 phases expliquées

| # | Skill                | Rôle                                                        | Sortie                                    |
| - | -------------------- | ----------------------------------------------------------- | ----------------------------------------- |
| 1 | `pgp-brief`          | Structure le besoin libre en brief JSON                     | `./.pgp-session/brief.json`               |
| 2 | `pgp-moodboard`      | Ancre des références réelles via Gemini grounding search    | `./.pgp-session/moodboard.json`           |
| 3 | `pgp-shot-plan`      | Shot list technique + lighting plan (subagent photographer) | `./.pgp-session/shot-plan.json`           |
| 4 | `pgp-prompt-forge`   | Compose le prompt Gemini final anti-IA                      | `./.pgp-session/gemini-prompt.txt`        |
| 5 | `pgp-generate`       | Appel API Gemini (flash draft ou pro final)                 | `./.pgp-session/raw-gemini.png`           |
| 6 | `pgp-postprocess`    | Cascade complète de post-processing                         | `./output/final-<timestamp>.jpg`          |
| 7 | `pgp-qa`             | Analyse forensique + score composite                        | `./.pgp-session/qa-report.json`           |

La skill `pgp-full` enchaîne les 7 sans intervention utilisateur, sauf le
go/nogo pour passer en mode final.

---

## 7. Mode draft vs final

| Mode    | Modèle                              | Résolution | Thinking | Coût approx. | Usage                        |
| ------- | ----------------------------------- | ---------- | -------- | ------------ | ---------------------------- |
| `draft` | `gemini-3.1-flash-image-preview`    | 1K         | minimal  | ~$0.045      | itération, validation rapide |
| `final` | `gemini-3-pro-image-preview`        | 2K         | high     | ~$0.134      | livrable client              |

Par défaut `pgp-full` démarre en draft. Si la qualité est là (score QA
≥ 75), il propose le passage en final — tu peux accepter en un O.

---

## 8. Customisation

### Ajouter un film stock

1. Crée une entrée dans `.claude/data/film-stocks.json` avec les champs `display_name`, `grain`, `color_bias`, `contrast`, `iso_native`, `gmic_clut`, `prompt_tokens`.
2. Documente dans `rules/film-stock-library.md`.
3. Si G'MIC n'a pas d'émulation native, dépose une CLUT Hald PNG dans `.claude/data/cluts/` (voir `.claude/data/cluts/README.md`).

### Ajouter un appareil caméra

1. Crée `.claude/data/exif-presets/<nom>.json` en suivant le format d'un existant (`sony_a7iv.json`).
2. Documente dans `rules/camera-simulation-library.md` avec `prompt_description`, `lens_characteristics`, `noise_profile`, `usage_typique`.
3. Les scripts le picke automatiquement via `exif_inject.sh --camera <nom>`.

### Ajouter un mood de color grade

1. Ajoute un branch dans `.claude/scripts/color_grade.sh → apply_gmic_mood()` avec tes commandes G'MIC.
2. Ou dépose une CLUT Hald PNG dans `.claude/data/cluts/<mood>.png` — le script la détecte automatiquement.

### Ajuster le pipeline

L'ordre des étapes est dans `.claude/scripts/pipeline.py`. Tu peux le modifier, mais
garde **`downsample_up` en premier** (casse VAE) et **`exif_inject` en
dernier** (sinon la réencode JPEG écrase les tags).

---

## 9. Éthique et transparence

### SynthID (watermark invisible non-désactivable)

Toutes les images produites par l'API Gemini embarquent un watermark
**SynthID** stéganographique invisible à l'œil et déposé dans la texture
même de l'image. Ce watermark **ne peut pas être retiré proprement** sans
dégrader visiblement l'image, et les CGU de l'API Gemini interdisent
explicitement les tentatives de suppression.

Les opérations de ce pipeline (resize, JPEG cycle, grain, color grade)
dégradent **incidemment et partiellement** ce watermark sans que ce soit
l'objectif : c'est le coût naturel d'un post-processing photo réaliste.
Une détection SynthID reste néanmoins probablement possible sur les
images en sortie.

### Content Credentials (C2PA)

Gemini appose aussi des Content Credentials C2PA cryptographiquement
signés. Ces métadonnées C2PA peuvent coexister avec les EXIF injectées
par ce plugin, ou être écrasées par le cycle JPEG — le comportement dépend
des versions et des outils de lecture.

### Règles d'usage éthique

- N'utilise pas ce plugin pour produire du contenu destiné à tromper des
  humains sur la nature du média (fake news, deepfakes identitaires,
  contenu diffamatoire).
- Respecte les droits d'image et de marque : ne demande pas à intégrer
  des personnes réelles, des logos non-autorisés, des œuvres protégées.
- Pour tout usage commercial impliquant des humains identifiables,
  vérifie la compatibilité avec les CGU Gemini à jour.

Ce plugin est conçu pour **améliorer la qualité technique et esthétique**
d'images publicitaires et éditoriales, pas pour contourner les dispositifs
de transparence IA.

---

## 10. Limitations connues

- **Erreurs 503 fréquentes sur Nano Banana preview.** Les modèles preview
  Gemini 3 image sont régulièrement surchargés. Le script `gemini_call.py`
  retry jusqu'à 5 fois avec backoff exponentiel. En cas d'échec persistant,
  réessaie dans quelques minutes.
- **Multi-subject scenes encore faibles.** Gemini a du mal à composer des
  scènes avec 3+ personnes + produits interactifs cohérents. Préfère des
  scènes à 1-2 sujets.
- **Cutoff de connaissance** : jan 2025 côté modèle. Les événements
  récents (sorties produits, célébrités post-cutoff) peuvent être mal
  rendus même avec grounding.
- **Texte sur produits** : Gemini reproduit bien les labels courts en
  mode with-product, mais déforme fréquemment les textes longs ou
  complexes. Vérifie toujours l'orthographe des labels visibles.
- **Bokeh smartphone** : demander un bokeh pro sur une simulation iPhone
  produit un résultat artificiel. Pour du bokeh, choisir un reflex/hybride
  dans le shot-plan.
- **SynthID invisible dans l'image** : voir section 9.

---

## 11. Dépannage rapide

| Erreur                                        | Cause probable                          | Solution                                                |
| --------------------------------------------- | --------------------------------------- | ------------------------------------------------------- |
| `GEMINI_API_KEY non définie`                  | `.env` absent ou mal chargé             | `export GEMINI_API_KEY=...` ou créer `.env`             |
| `gmic: command not found`                     | G'MIC non installé                      | `brew install gmic` / `apt install gmic`                |
| `exiftool non trouvé`                         | exiftool non installé                   | `brew install exiftool` / `apt install libimage-exiftool-perl` |
| 503 en boucle après 5 retries                 | Quota Gemini ou modèle surchargé        | Attendre 10-30 min, revérifier la quota                 |
| Image trop saturée                            | Stack color_grade + film_grain trop fort | Baisser `intensity` dans le shot-plan                   |
| Score QA faible en draft                      | Prompt générique ou shot-plan incohérent | Relancer avec description plus précise                  |
| `ModuleNotFoundError: google.genai`           | pip pas à jour                          | `pip install -r .claude/requirements.txt --upgrade`             |

---

## 12. Coûts

Tarifs approximatifs au 2026-Q2 (vérifier sur [ai.google.dev/pricing](https://ai.google.dev/pricing)) :

| Modèle                            | Coût par image | Usage                        |
| --------------------------------- | -------------- | ---------------------------- |
| `gemini-3.1-flash-image-preview`  | ~$0.045        | draft                        |
| `gemini-3-pro-image-preview`      | ~$0.134        | final                        |
| `gemini-2.5-flash` (grounding)    | ~$0.0003/query | moodboard research           |

Budget typique pour une image livrée :

- 1 draft + 1 final = ~$0.18
- Avec 1 recherche moodboard = ~$0.18
- Avec 2 retries draft = ~$0.27

---

## 13. FAQ

**Q : Puis-je utiliser ce plugin sans clé Gemini ?**
R : Non. Toutes les générations passent par l'API Gemini. Les scripts de post-processing fonctionnent isolément sur une image existante, mais le pipeline complet requiert la clé.

**Q : Est-ce que ça marche sur Windows ?**
R : Oui via WSL. Nativement sous PowerShell, `bash` est requis. Prévois WSL ou Git Bash.

**Q : L'image finale trompera-t-elle un outil de détection IA ?**
R : Partiellement. La détection visuelle simple est efficacement contournée. La détection spectrale avancée (FFT, noise pattern, statistics) est fortement atténuée. La détection SynthID reste possible. Voir section 9.

**Q : Puis-je utiliser mes propres CLUTs Lightroom ?**
R : Oui, convertis-les en Hald PNG ou `.cube`, dépose-les dans `.claude/data/cluts/`, puis pointe-les depuis `.claude/scripts/color_grade.sh`.

**Q : Comment j'ajoute un film argentique exotique ?**
R : Voir section 8 "Customisation → Ajouter un film stock".

---

## 14. Contribuer

Forks et PR bienvenus, spécialement pour :

- Nouveaux presets EXIF d'appareils moins courants (Leica M11, Hasselblad X2D, Phase One)
- Nouvelles émulations de films (Tri-X, Ektachrome, Kodachrome, Provia)
- CLUTs signature (cinéma A24, Kodak stock fade, etc.)
- Amélioration du `naturality_score.py`

Procédure :

1. Fork du repo
2. Branche `feat/<nom-court>` ou `fix/<nom-court>`
3. Commits en Conventional Commits (`feat:`, `fix:`, `docs:`…)
4. Tests `bash .claude/tests/test_scripts.sh` doivent passer
5. PR vers `main` avec description claire et avant/après image si possible

---

## 15. Licence

MIT. Voir `LICENSE`.

---

## 16. Crédits

- **Plugin** : [Kōeki Agency](https://github.com/koeki-agency)
- **ImageMagick** : équipe ImageMagick, licence Apache 2.0
- **G'MIC** : David Tschumperlé et contributeurs, licence CeCILL
- **exiftool** : Phil Harvey, licence artistique Perl
- **Pillow** : équipe Python Imaging Library, licence HPND
- **google-genai** : Google, licence Apache 2.0

Merci aux communautés Dust, Freepresets, RawPedia pour les LUTs libres
référencées dans `.claude/data/cluts/README.md`.
