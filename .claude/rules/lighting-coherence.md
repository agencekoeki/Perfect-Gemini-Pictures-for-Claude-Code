# Cohérence d'éclairage

Le deuxième marqueur IA le plus visible, après la texture plastique, est
une incohérence d'éclairage. Un humain lit la lumière d'une photo en
moins d'une seconde. Si les ombres contredisent la source déclarée,
l'image est immédiatement classée comme "synthétique".

## Setup de base : 3-point lighting

### Key light (lumière principale)
Source dominante, définit l'exposition et la direction. Couleur et température
dictent l'ambiance globale. Doit être nommée explicitement dans le shot-plan
(ex : "fenêtre latérale", "spot LED plafonnier", "soleil à 45° gauche").

### Fill light (remplissage)
Éclaire les ombres du côté opposé à la key. Typiquement moins intense (ratio
1:2 à 1:4). Peut être une source réelle (deuxième lampe) ou un rebond
(mur blanc, réflecteur). Ne doit jamais être plus forte que la key.

### Rim / back light (contre-jour)
Sépare le sujet du fond en créant un liseré lumineux sur les contours.
Optionnel mais vend énormément la qualité "pro".

## Règles de cohérence non-négociables

1. **Direction d'ombre = direction inverse de la key light.** Si la key vient
   de la gauche, les ombres tombent à droite. Toujours.
2. **Dureté de l'ombre = taille apparente de la source.** Fenêtre 2m² à 3m
   de distance = ombres douces. Spot 5cm à 1m = ombres dures.
3. **Température de couleur cohérente.** Les pixels exposés par la key
   portent sa température. Mélange admis si sources multiples, mais
   justifié (fenêtre 5600K + lampe tungstène 2700K = normal).
4. **Falloff inversé au carré.** Double la distance = quart de l'intensité.
   Une source à 1m n'éclaire pas uniformément un sujet de 3m de large.
5. **Catchlight cohérent dans les yeux.** Forme et position doivent
   correspondre à la source primaire. Deux catchlights = deux sources.

## Températures de couleur standard

| Source                       | Temp (K)       | Rendu      |
| ---------------------------- | -------------- | ---------- |
| Bougie                       | 1800-2000      | Très chaud |
| Ampoule tungstène            | 2700-3000      | Chaud      |
| LED chaude intérieur         | 3000-3500      | Chaud doux |
| LED neutre                   | 4000-4500      | Neutre     |
| Lumière du jour nuageux      | 6000-7500      | Frais      |
| Ciel bleu clair ombre        | 10000+         | Très froid |
| Golden hour                  | 2500-3500      | Très chaud |
| Blue hour                    | 8000-12000     | Très froid |
| Flash / strobe cobra         | 5500-6000      | Neutre jour|
| Fenêtre nord (ombre)         | 7000-8000      | Frais doux |

Un photographe ne mélange pas 3000K et 7000K sans justification narrative.

## Qualité de lumière

- **Hard light** : source petite/distante, ombres nettes, contraste élevé.
  Midi soleil direct, flash cobra direct, petit spot LED.
- **Soft light** : source grande/proche, ombres douces, transitions graduelles.
  Fenêtre diffusée, softbox, ciel nuageux, mur réfléchissant.
- **Diffuse light** : source omnidirectionnelle, presque pas d'ombre.
  Plein jour voilé, lightbox produit, studio cyclo blanc.

Pour un look naturel "lifestyle", préférer soft light (fenêtre, reflet, nuages).

## Light wrap

Sur les bords du sujet, la lumière se diffuse légèrement sur la peau et
les matières translucides, créant un "halo" subtil qui adoucit la
silhouette. C'est un marqueur très fort de "vraie capture". Le prompter
doit inclure "believable light wrap on subject edges" pour l'obtenir.

## Occlusion shadow (mode with-product)

Un produit posé sur une surface projette une ombre de contact sombre
juste sous sa base (ambient occlusion). Sans cette ombre, l'objet a l'air
"collé en post". Toujours demander "soft occlusion shadow beneath the
product, matching the surface and ambient light".

## Pièges fréquents côté Gemini

- **Ombres multiples contradictoires** : Gemini parfois dessine une ombre
  selon le sujet et une autre selon l'arrière-plan. À corriger en
  régénérant avec un prompt plus précis sur la direction unique.
- **Lumière "everywhere"** : scène bien exposée partout sans source
  identifiable. Toujours nommer la source primaire.
- **Highlight sur logo** : reflet spéculaire sur un logo alors qu'aucune
  source ne le justifie. Ajouter "no glare or specular highlight on the
  product label" si récurrent.
