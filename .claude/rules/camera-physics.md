# Physique caméra et optique

Un shot-plan incohérent physiquement produit une image qui sent l'IA même
avec un bon prompt. Respecter les règles suivantes quand l'agent
`photographer` choisit les paramètres.

## Triangle d'exposition

Trois variables liées : ISO, ouverture (f/N), vitesse d'obturation (1/N s).
Une variation d'un cran (stop) sur l'un doit être compensée par un cran
inverse sur un autre pour conserver la même exposition.

| Contexte                 | ISO plausible | Aperture typique | Shutter typique |
| ------------------------ | ------------- | ---------------- | --------------- |
| Extérieur plein soleil   | 50-100        | f/5.6 - f/11     | 1/500 - 1/1000  |
| Extérieur ombré          | 100-400       | f/2.8 - f/5.6    | 1/200 - 1/500   |
| Golden hour              | 200-800       | f/1.8 - f/4      | 1/125 - 1/500   |
| Intérieur fenêtre jour   | 400-1600      | f/1.8 - f/2.8    | 1/100 - 1/200   |
| Intérieur nuit lampes    | 800-3200      | f/1.4 - f/2.8    | 1/50 - 1/125    |
| Concert / scène sombre   | 1600-6400     | f/1.4 - f/2.8    | 1/125 - 1/250   |

Erreurs fréquentes à éviter :

- ISO 100 en intérieur nuit = mouvement flou ou image noire. Impossible.
- ISO 50 sur smartphone = aucun capteur téléphone ne descend à 50. Min 25-32 pour iPhone, souvent 64.
- 1/30 s handheld sans stabilisation = motion blur garantie.

## Ouverture et profondeur de champ

DoF dépend de 3 facteurs : aperture, focal length, distance sujet.

### Règles qualitatives

- **f/1.2 - f/1.8** : DoF très étroite, seul le sujet net, arrière plan fondu. Réservé à 50mm+ pour du bokeh classique.
- **f/2.8** : DoF contrôlée, arrière-plan lisible mais flou. Standard portrait.
- **f/4 - f/5.6** : DoF confortable, deux personnes net, bokeh léger.
- **f/8 - f/11** : DoF large, tout plan lisible. Standard paysage, packshot.
- **f/16+** : DoF maximale, diffraction visible. Paysage grand angle ou photo macro.

### Focal vs bokeh

À même aperture, plus la focale est longue, plus le bokeh est doux et prononcé :

- 24mm f/1.8 → bokeh léger, arrière-plan lisible
- 50mm f/1.8 → bokeh correct, sujet détaché
- 85mm f/1.8 → bokeh crémeux, standard portrait
- 135mm f/1.8 → bokeh très doux, compression forte

Sur smartphone, les capteurs sont trop petits pour produire un bokeh optique
profond. Les bokeh smartphones sont soit légers (f/1.78 équivalent 24mm),
soit simulés (mode portrait).

## Compression perspective

- **Grand angle (14-24mm)** : étire la perspective, exagère la distance entre plans. Menton proéminent en portrait proche.
- **Standard (35-50mm)** : perspective naturelle, proche de l'œil humain.
- **Téléphoto (85-200mm)** : compression de plans, aplatit le relief, flatte le visage.
- **Super-télé (200mm+)** : compression extrême, reliefs aplatis.

Ne jamais mettre "shot at 200mm" pour une scène d'intérieur de 3 mètres
— physiquement impossible (cadre hors sujet).

## Limites physiques

Contraintes que l'agent `photographer` doit respecter :

- **Smartphone** : aperture fixe, typiquement f/1.5 à f/1.78 pour la principale, f/2.8 pour l'ultra grand-angle, f/2.8 pour le téléphoto.
- **Optiques reflex/hybride** : les primes atteignent f/1.2 - f/1.4. Les zooms plafonnent à f/2.8 typiquement.
- **Shutter plafond** : mécanique jusqu'à 1/8000, électronique jusqu'à 1/32000 sur hybrides modernes.
- **ISO sans bruit** : jusqu'à ISO 800-1600 sur plein format moderne, ISO 400 sur APS-C, ISO 100-200 sur smartphone.
- **Longueur focale minimale** : 10-14mm en ultra grand-angle, au-delà = fisheye (distorsion visible).

## Cohérence film / capteur

- Si on nomme un film argentique dans le prompt, l'ISO doit être proche du natif du film (Portra 400 = ISO 400, Velvia 50 = ISO 50).
- Pousser un film de 1-2 stops est possible mais doit être mentionné ("Portra 400 pushed to 800").
- Un capteur numérique "simulé film" doit avoir un grain cohérent avec l'ISO du capteur, pas avec l'ISO du film simulé.
