---
name: pgp-full
description: Pipeline complet bout-en-bout. Enchaîne brief → moodboard → shot-plan → prompt-forge → generate (draft) → postprocess → qa. Si score QA bon, propose de relancer en final. Invoquer pour une génération complète d'image naturelle Gemini. L'utilisateur peut fournir ou non une image produit de référence.
argument-hint: [description du besoin] [--product-image PATH] [--from-brief PATH]
allowed-tools: Read, Write, Bash(python:*), Bash(./scripts/*:*), Bash(gmic *), Bash(convert *), Bash(magick *), Bash(exiftool *), Agent(photographer), Agent(retoucher), Agent(art-director)
---

# Skill `pgp-full` — Orchestrateur bout-en-bout

## Rôle

Exécuter le pipeline cognitif complet en autonomie totale, de la
description utilisateur à l'image finale livrée, en 7 phases :

1. `pgp-brief` — structurer l'intent
2. `pgp-moodboard` — ancrer les références réelles
3. `pgp-shot-plan` — technique photographe (subagent `photographer`)
4. `pgp-prompt-forge` — composer le prompt Gemini final
5. `pgp-generate` — appel API en mode draft
6. `pgp-postprocess` — cascade complète
7. `pgp-qa` — score forensique

Puis :
- Si score QA ≥ 75, proposer le passage en **final** (Nano Banana Pro, 2K, thinking high).
- Le subagent `art-director` donne un verdict créatif honnête à la toute fin.

## Arguments

- Description libre (obligatoire si `--from-brief` absent)
- `--product-image PATH` : chemin vers une image produit (mode `with-product`)
- `--from-brief PATH` : saute `pgp-brief` en réutilisant un brief pré-rempli (pour les exemples)

## Déroulé

### Étape 0 — initialisation

1. Créer `./.pgp-session/` (propre : supprimer le contenu existant sauf si `--resume`).
2. Parser les arguments. Détecter le mode :
   - `--product-image` présent ET fichier existe → `with-product`
   - sinon → `without-product`

### Étape 1 — brief

- Si `--from-brief PATH` : copier le fichier dans `./.pgp-session/brief.json`.
- Sinon : invoquer la skill `pgp-brief` avec la description.

### Étape 2 — moodboard

Invoquer `pgp-moodboard`. Pas de pause utilisateur.

### Étape 3 — shot-plan

Invoquer `pgp-shot-plan` (qui délègue au subagent `photographer`).

### Étape 4 — prompt-forge

Invoquer `pgp-prompt-forge`.

### Étape 5 — generate (draft)

Invoquer `pgp-generate draft`.

### Étape 6 — postprocess

Invoquer `pgp-postprocess`.

### Étape 7 — qa

Invoquer `pgp-qa`. Récupérer `score_total` depuis `./.pgp-session/qa-report.json`.

### Étape 8 — upgrade final (conditionnel)

Si `score_total >= 75` :

```
Draft validé (score 82/100). Passer en final avec Nano Banana Pro (2K, thinking high, ~$0.134) ? [O/n]
```

Si réponse O (ou défaut) :
- Relancer `pgp-generate final`
- Relancer `pgp-postprocess`
- Relancer `pgp-qa`

Si score < 75 :

```
Draft faible (score 58/100). Recommandation : <première suggestion du QA>.
Veux-tu relancer le pipeline avec ajustement, ou rester sur le draft ? [ajuster/rester]
```

### Étape 9 — verdict art-director

Invoquer le subagent `art-director` avec le brief et le chemin de l'image finale. Afficher son verdict dans la console.

### Étape 10 — récapitulatif

Afficher un récap final :

```
✓ Pipeline terminé.
Image finale : ./output/final-20260421-093615.jpg
Mode : draft | final
Score QA : 82/100
Coût cumulé : ~$0.045
Temps total : 47 s

Verdict art-director :
<verdict>
```

## Règles

- **Aucune pause utilisateur** entre les étapes 1 et 7. Seule la décision draft→final demande une confirmation.
- Si une étape échoue, afficher l'erreur et l'étape précise, et arrêter le pipeline.
- Les fichiers intermédiaires restent dans `./.pgp-session/` pour debug/reprise.
- Respecter la variable `PGP_DEFAULT_MODE` si elle est définie (`draft` ou `final`).

## Exemples d'invocation

```bash
# Mode sans produit
claude /pgp-full "portrait femme buvant café matinal style reel Instagram"

# Mode avec produit
claude /pgp-full "unboxing batterie Bluetti AC200 dans van aménagé matin" --product-image ./bluetti.jpg

# Rejouer un exemple
claude /pgp-full --from-brief examples/bluetti-unboxing-van/brief.json
```
