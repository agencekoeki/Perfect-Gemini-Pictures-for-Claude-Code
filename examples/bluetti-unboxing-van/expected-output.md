# Résultat attendu — Bluetti unboxing van

## Description visuelle attendue

Cadre vertical 9:16 (reel Instagram). On voit en plan moyen rapproché une main
(avant-bras visible jusqu'à l'épaule, pas de visage entier) en train de
retirer le dernier morceau de mousse d'un carton ouvert sur un plan de
travail bois clair à l'intérieur d'un van aménagé. La Bluetti AC200 Max
apparaît partiellement, sur le tiers gauche/centre du cadre, avec le logo
Bluetti lisible mais non surexposé.

Lumière : fenêtre latérale (camera-left) diffuse, matin, 3500-4500K. Ombres
douces tombant à droite. Catchlight subtil sur la façade LCD.

Arrière-plan : plaid laine posé, mug céramique légèrement flou (DoF faible),
suggestion de rideau lin derrière la fenêtre.

Film stock ciblé : **Fujifilm Pro 400H** ou **Kodak Portra 400**. Grain fin
visible sur les zones plates. Palette chaude, bois clair dominant.

## Checklist visuelle

- [ ] Logo Bluetti lisible, pas de reflet écrasant dessus
- [ ] Forme rectangulaire de l'AC200 préservée
- [ ] Écran LCD bleu visible
- [ ] Ombre de contact sous le produit (occlusion shadow)
- [ ] Main du sujet avec détail de peau (pas plastique)
- [ ] Bois du plan de travail avec grain visible
- [ ] Fenêtre latérale devinée en périphérie, pas dans le cadre net
- [ ] Pas de logo concurrent visible (pas d'Apple, Samsung, EcoFlow…)
- [ ] EXIF cohérent post-pipeline : iPhone 15 Pro ou Sony A7 IV, ISO 400, f/1.8-2.8, matin 9h

## Lancer l'exemple

```bash
claude /pgp-full --from-brief examples/bluetti-unboxing-van/brief.json
```

## Remplacer l'image produit

Le fichier `input_product.jpg` est un placeholder. Pour un vrai test,
remplacer par une vraie photo packshot propre de la Bluetti AC200 Max
(fond blanc, angle 3/4 avant, logo visible).
