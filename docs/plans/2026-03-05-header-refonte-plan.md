# Header Refonte — Full-Width, Lisible, Beau

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transformer le header (title-bar + mode-tabs + filter-bar) d'un petit card flottant centré en un bandeau pleine largeur, grand, lisible, avec des textes bien visibles et une hiérarchie visuelle claire.

**Architecture:** Refonte CSS-first du `#title-bar` : passer de `position: absolute; left: 50%; transform: translateX(-50%)` (petit card) à un bandeau pleine largeur en haut de page. Augmenter toutes les tailles de texte. Intégrer le `#filter-bar` comme partie du bandeau. Ajuster les positions dépendantes (`#surv-filters`, cascade animation). Vérifier visuellement dans le navigateur à chaque étape.

**Tech Stack:** Vanilla CSS + JS dans `index.html`, Leaflet.js. Pas de build system.

---

### Task 1: Title-bar — bandeau pleine largeur

**Files:**
- Modify: `index.html:51-56` (CSS `#title-bar`)
- Modify: `index.html:14` (shared glassmorphism selector — remove `#title-bar` from it)

**Step 1: Retirer `#title-bar` du sélecteur glassmorphism partagé**

Le card base applique `border-radius: 10px` et des bordures de card. Un bandeau pleine largeur ne doit pas avoir ces propriétés. Modifier la ligne 14 :

```css
/* --- Glassmorphism card base --- */
#legend, #info, #stats-panel, #surv-filters {
  background: rgba(15,15,30,0.82); backdrop-filter: blur(16px);
  border-radius: 10px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.08);
  transition: opacity 0.3s ease, transform 0.3s ease;
  color: #e0e0e0;
}
```

**Step 2: Réécrire le CSS de `#title-bar`**

Remplacer les lignes 51-56 par un bandeau pleine largeur avec background propre :

```css
#title-bar {
  position: absolute; top: 0; left: 0; right: 0;
  z-index: 1000; padding: 18px 32px 14px;
  text-align: center;
  background: linear-gradient(180deg, rgba(15,15,30,0.92) 0%, rgba(15,15,30,0.75) 80%, transparent 100%);
  backdrop-filter: blur(12px);
  color: #e0e0e0;
  transition: opacity 0.3s ease, transform 0.3s ease;
}
#title-bar h1 {
  font-size: 26px; font-weight: 800; letter-spacing: -0.5px;
  color: #fff; text-shadow: 0 2px 8px rgba(0,0,0,0.4);
}
#title-bar p {
  font-size: 14px; color: rgba(255,255,255,0.6); margin-top: 4px;
  font-weight: 400; letter-spacing: 0.2px;
}
```

**Step 3: Vérifier dans le navigateur**

Ouvrir `index.html`. Le titre doit :
- S'étendre sur toute la largeur
- Avoir un fond gradient qui se fond dans la carte (pas de bord dur en bas)
- Titre en 26px blanc bien lisible
- Sous-titre en 14px visible (pas grisé illisible)

**Step 4: Commit**

```bash
git add index.html
git commit -m "style: full-width header banner with larger typography"
```

---

### Task 2: Mode tabs — plus grands et plus lisibles

**Files:**
- Modify: `index.html:87-103` (CSS `#mode-tabs`, `.mode-btn`, `#mode-indicator`)

**Step 1: Augmenter la taille des boutons de mode**

```css
#mode-tabs {
  display: inline-flex; justify-content: center; gap: 0;
  margin-top: 10px; position: relative;
  background: rgba(255,255,255,0.06); border-radius: 8px;
  padding: 2px;
}
.mode-btn {
  padding: 8px 24px; border: none; cursor: pointer;
  font-size: 14px; font-weight: 600; border-radius: 6px;
  background: transparent; color: rgba(255,255,255,0.5);
  transition: color 0.2s, background 0.2s;
}
.mode-btn:hover { color: rgba(255,255,255,0.85); }
.mode-btn.active {
  color: #fff;
  background: rgba(255,255,255,0.1);
}
#mode-indicator {
  position: absolute; bottom: 0; height: 2px;
  background: #4a90d9; border-radius: 1px;
  transition: left 0.3s ease, width 0.3s ease, background 0.3s ease;
}
```

**Step 2: Vérifier dans le navigateur**

Les onglets de mode doivent :
- Avoir un fond subtil qui les regroupe visuellement (pill container)
- Texte en 14px (au lieu de 12px)
- L'onglet actif a un fond légèrement lumineux
- L'indicateur coloré glisse toujours

**Step 3: Commit**

```bash
git add index.html
git commit -m "style: larger mode tabs with pill container background"
```

---

### Task 3: Filter-bar — repositionner sous le bandeau

**Files:**
- Modify: `index.html:71-74` (CSS `#filter-bar`)
- Modify: `index.html:129-134` (CSS `#surv-filters`)

**Step 1: Ajuster la position du filter-bar**

Le `#filter-bar` est actuellement à `top: 80px` (hardcodé pour l'ancien petit header). Avec le nouveau bandeau plus grand, il faut le pousser plus bas :

```css
#filter-bar {
  position: absolute; top: 110px; left: 50%; transform: translateX(-50%);
  z-index: 1000; display: flex; gap: 6px; flex-wrap: wrap; justify-content: center;
  max-width: 90vw;
}
```

**Step 2: Ajuster la position du `#surv-filters`**

Même logique — le `#surv-filters` est aussi à `top: 80px` :

```css
#surv-filters {
  position: absolute; top: 110px; left: 50%; transform: translateX(-50%);
  z-index: 1000; display: none; padding: 12px 20px;
  font-size: 13px; gap: 12px; align-items: center;
  flex-wrap: wrap; justify-content: center;
  color: #ccc;
}
```

**Step 3: Vérifier dans le navigateur**

Les filtres doivent apparaître juste sous le bandeau, pas se chevaucher avec le titre.

**Step 4: Commit**

```bash
git add index.html
git commit -m "style: reposition filter bars below new full-width header"
```

---

### Task 4: Responsive — adapter le bandeau au mobile

**Files:**
- Modify: `index.html:183-194` (CSS responsive `@media`)

**Step 1: Ajouter les règles responsive pour le nouveau header**

Ajouter dans le bloc `@media (max-width: 768px)` :

```css
#title-bar {
  padding: 12px 16px 10px;
}
#title-bar h1 {
  font-size: 18px;
}
#title-bar p {
  font-size: 12px;
}
.mode-btn {
  padding: 6px 14px; font-size: 12px;
}
#filter-bar, #surv-filters {
  top: 90px;
}
```

**Step 2: Vérifier en responsive**

Ouvrir les DevTools, simuler mobile (375px). Le bandeau doit rester lisible sans déborder.

**Step 3: Commit**

```bash
git add index.html
git commit -m "style: responsive header adjustments for mobile"
```

---

### Task 5: Cascade animation — adapter au nouveau layout

**Files:**
- Modify: `index.html:171-181` (CSS cascade animation)

**Step 1: Vérifier que la cascade fonctionne avec le bandeau**

La cascade animation utilise `translateY(-12px)` pour l'apparition. Avec un bandeau `position: absolute; top: 0`, cela devrait fonctionner. Mais l'animation met `opacity: 0` initialement, ce qui peut causer un flash si le bandeau est visible avant que le JS s'exécute.

Ajouter une règle CSS pour s'assurer que le title-bar commence caché :

```css
#title-bar {
  /* ajouter à la règle existante */
  opacity: 0;
}
```

Le JS de cascade (ligne 1494-1502) ajoutera la classe `.cascade-in` puis `.visible` avec un délai, ce qui déclenchera l'animation d'apparition.

**Step 2: Vérifier dans le navigateur**

Au chargement : loading spinner → disparition → le bandeau glisse vers le bas avec fade-in → puis la légende → puis les filtres.

**Step 3: Commit**

```bash
git add index.html
git commit -m "style: cascade animation compatibility with full-width header"
```

---

### Task 6: Vérification visuelle complète et polish final

**Files:**
- Modify: `index.html` (ajustements fins si nécessaire)

**Step 1: Test mode politique**
- Le bandeau est pleine largeur, titre grand et blanc
- Les filtres de famille politique apparaissent sous le bandeau
- Hover sur une commune montre le tooltip correctement (pas masqué par le bandeau)
- La légende en bas à gauche n'est pas affectée

**Step 2: Test mode surveillance**
- Switch vers surveillance : l'indicateur glisse avec la bonne couleur
- Les surv-filters apparaissent à la bonne position
- Le sous-titre change correctement

**Step 3: Test mode prospection**
- Switch vers prospection
- Les filtres prospection apparaissent correctement

**Step 4: Test contraste et lisibilité**
- Le titre "Carte politique des maires de France" est clairement lisible
- Le sous-titre est lisible (pas un gris quasi-invisible)
- Les onglets Politique / Surveillance / Prospection sont tous lisibles
- L'onglet actif se distingue clairement des inactifs
- Les filtres sont lisibles

**Step 5: Commit final**

```bash
git add index.html
git commit -m "style: header refonte - full-width banner with improved readability"
```
