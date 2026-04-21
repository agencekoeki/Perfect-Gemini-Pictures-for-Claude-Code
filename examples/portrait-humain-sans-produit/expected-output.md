# Résultat attendu — portrait humain sans produit

## Description visuelle attendue

Cadre vertical 9:16. Femme trentenaire en chemise blanche oversize, plan
américain (des hanches au haut du crâne), tenant un mug beige près du
visage. Elle regarde la fenêtre à gauche du cadre (hors champ), expression
neutre et douce, les yeux mi-clos sous la chaleur du café.

Arrière-plan : cuisine parisienne floue, plan de travail marbre blanc,
cafetière Bialetti en inox au second plan. Volets intérieurs blancs créent
des lignes verticales.

Lumière : fenêtre grande camera-left, automne voilé, 6000-7000K, très douce
diffuse. Catchlight dans les yeux cohérent avec la fenêtre. Light wrap visible
sur l'épaule et le côté gauche du visage.

Film stock ciblé : **Kodak Portra 400** ou **Kodak Portra 160** pour la peau
crémeuse et le grain fin. Ambiance "slow-living éditorial Kinfolk".

## Checklist visuelle

- [ ] Peau avec pore density visible (pas plastique)
- [ ] Peach fuzz visible sur joues et arête du nez
- [ ] Cheveux avec mèches rebelles, pas "parfaits"
- [ ] Lèvres avec texture réaliste (pas de gloss IA)
- [ ] Catchlight dans les yeux cohérent avec la fenêtre
- [ ] Vapeur subtile au-dessus du mug (optionnel mais plus)
- [ ] Ombre des cils cohérente avec la lumière (douce, pas dure)
- [ ] Marbre avec veinures naturelles (pas pattern répétitif)
- [ ] Tissu chemise avec plis et texture lin visible
- [ ] EXIF post-pipeline : Sony A7 IV ou Canon R5, ISO 400-800, f/1.8-2.8, focale 50-85mm

## Lancer l'exemple

```bash
claude /pgp-full --from-brief examples/portrait-humain-sans-produit/brief.json
```

## Pourquoi cet exemple est intéressant

- Aucune image produit à injecter → teste le mode `without-product` pur.
- Peau + cheveux : la partie la plus dure à rendre naturelle en IA.
- Lumière naturelle voilée automne : cohérence lumière critique.
- Cadre vertical 9:16 : teste la composition portrait en mode reel.
