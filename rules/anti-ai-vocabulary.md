# Vocabulaire anti-AI look

Règle fondamentale du pipeline : le choix des mots dans le prompt Gemini
détermine 60% du look. Les modèles de diffusion sont entraînés sur des
corpus massifs où certains mots sont fortement corrélés au "rendu
concept-art numérique" (ArtStation, DeviantArt, 3D rendering). Les mentionner
ramène l'image vers ce cluster — même si on demande "photo réaliste".

## Mots à BANNIR dans le prompt principal

Liste à ne JAMAIS inclure dans la description de scène :

- **flawless**, **perfect**, **pristine**, **smooth**, **airbrushed**, **polished**, **immaculate**
- **trending on artstation**, **octane render**, **unreal engine**, **blender render**, **V-Ray**
- **cinematic masterpiece**, **stunning**, **breathtaking**, **epic**, **majestic**
- **8K**, **ultra HD**, **4K ultra realistic**, **hyperrealistic** (paradoxalement contre-productif, trop corrélé au look IA)
- **highly detailed**, **intricate details**, **ultra detailed**
- **concept art**, **digital painting**, **matte painting**
- **bokeh-licious**, **dramatic lighting** (tolérable mais produit du cliché)

Effet typique : peau plastique, yeux vitreux, lumière "studio IA", grain artificiel.

## Mots à PRIVILÉGIER

Ces tokens ancrent le modèle dans des corpus photo professionnels et
documentaires, pas dans des corpus CG :

### Texture peau et matières
- **visible pore density**, **peach fuzz**, **natural skin imperfections**
- **realistic skin texture with fine lines and minor blemishes**
- **natural fabric weave texture**, **material texture with friction**, **matte texture**
- **catchlight reflections**, **natural iris detail**, **wet surface on lips**

### Caractéristiques capteur / film
- **ISO noise visible in shadows**, **film grain**, **chromatic aberration**
- **subtle sensor noise**, **banding in gradients**
- **Kodak Portra 400 rendering**, **Fujifilm Pro 400H look**
- **medium format feel**, **35mm film aesthetic**

### Lumière et ombres
- **believable light wrap**, **soft occlusion shadow**
- **natural rim light**, **window light falloff**
- **ambient light bounce from nearby walls**
- **shadow coherence matching the light direction**

### Signaux "vraie capture"
- **unretouched**, **straight out of camera**, **raw file feel**
- **candid moment**, **documentary style**, **snapshot aesthetic**
- **slight handheld motion**, **shot handheld**
- **imperfect framing**, **asymmetric composition**

### Produit (mode with-product)
- **soft occlusion shadow beneath the product**
- **matching perspective and scale to background**
- **preserve accurate label text and edges**
- **no glare over the logo**

## Gestion des contraintes négatives

Ne JAMAIS formuler en négation directe dans la description principale. Gemini
(comme Imagen et les modèles de diffusion en général) amplifie souvent les
concepts qu'on lui demande d'éviter.

### Mauvais
```
A portrait of a woman, no blur, no plastic skin, no CGI, not airbrushed,
no visible airpods, no logos.
```

### Bon
```
A portrait of a woman with visible skin texture, natural pore detail,
window light from camera-left. Shot on Kodak Portra 400.

Clean composition free of visible logos, brand marks, or identifying
technology. Subject fills the frame naturally.
```

La checklist finale "clean composition free of X, Y, Z" est placée à la fin
du prompt, phrasée de façon positive (ce qu'on veut voir : une composition
nette), avec les items à exclure comme énumération neutre.

## Règle d'or

Le prompt doit pouvoir être lu comme un brief réel de photographe à son
assistant. Un photographe ne dit pas "ISO 400, no noise, no blur". Il dit
"ISO 400 pushed one stop, natural grain visible, focus on the hands".
Formule tes prompts pareil.
