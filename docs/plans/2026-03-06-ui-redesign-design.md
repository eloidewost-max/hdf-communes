# Redesign UI/UX — Sales Intelligence Tool

## Direction

Transformer la carte d'un outil de visualisation en un **outil d'intelligence commerciale** ou la donnee drive les decisions. Layout split-panel : panneau de commande a gauche (360px) avec filtres, liste de prospects triee, et legende ; carte plein ecran a droite ; panneau de detail en overlay a droite au clic. Methodologie accessible pour credibiliser l'outil en demo.

Public cible : equipe go-to-market + commerciaux terrain.
Contrainte : single-file HTML, publiable sur GitHub Pages, vanilla JS + Leaflet.

## Workflow utilisateur

1. **Prospection mode** (defaut) : filtrer, scanner la liste triee, reperer les clusters sur la carte
2. **Clic sur une commune** (liste ou carte) : panneau de detail avec les 3 dimensions (score + politique + surveillance)
3. **Politique mode** : analyse regionale, preparation de rdv avec contexte politique
4. **Surveillance mode** : analyse de la densite securitaire par zone

## 1. Layout

### Top Bar (44px, solid dark)

- Gauche : champ de recherche integre (280px)
- Centre-droit : mode tabs (Prospection premier, puis Politique, Surveillance)
- Droite : bouton "?" (methodologie drawer)
- Fond : `#0d0f17`, bordure basse `1px solid rgba(255,255,255,0.06)`
- Pas de titre, pas de sous-titre

### Command Panel (360px, gauche, toujours visible)

Panneau fixe, scrollable, fond solid `#111318`. Contenu change selon le mode actif.

**En mode Prospection :**
1. **Filtres** (toujours visibles) : checkboxes (stat payant, sans videoverb), slider pop min
2. **Parametres** (section collapsible, fermee par defaut) : 5 sliders de poids des signaux
3. **Distribution des scores** : mini histogramme (8 barres), "239 communes > 50/100"
4. **Liste triee** : communes triees par score decroissant, chaque row affiche :
   - Nom commune + code INSEE
   - Barre de score coloree (bleu→orange→rouge)
   - Population (compact, ex: "28k")
   - Point couleur politique (toujours visible)
   - Icones signaux : stat payant, accidents, PM
   - Hover : highlight commune sur la carte
   - Click : zoom carte + ouverture detail panel
5. **Legende** (compact, bas du panneau)

**En mode Politique :**
1. Filter pills (familles politiques)
2. Bandeau couverture : "2 693 / 34 844 communes avec nuance officielle"
3. Liste par famille avec compteurs
4. Legende couleurs

**En mode Surveillance :**
1. Slider ratio min + checkbox donnees uniquement
2. Liste triee par ratio decroissant
3. Legende heatmap

### Map (espace restant, pleine hauteur)

- Basemap CartoDB Dark No Labels
- Coloration selon le mode actif
- Hover : tooltip minimal (nom + metrique cle, 2 lignes max)
- Click : ouvre le detail panel

### Detail Panel (overlay droit, ~400px, slide-in au clic)

Affiche **toutes les dimensions** quelle que soit le mode actif :

**Header :**
- Nom commune + code INSEE
- Population
- Badge politique colore (ex: "Droite" en bleu)
- Nom du maire + nuance

**Section Score :**
- Score large (ex: "74/100") + barre coloree + "Top 3%"
- Decomposition : 5 barres de signal avec label, valeur brute, contribution
- Badge fraicheur par signal (annee + couleur vert/jaune/orange)
- Warning couverture pour stat payant ("226 communes couvertes")

**Section Surveillance :**
- PM : X agents | ASVP : Y agents
- Ratio : Z /10k hab (+ brut si plafonne)
- Tendance PM : sparkline 2019→2024
- Warning si commune touristique (ratio plafonne)

**Section Signaux :**
- Stat. payant : Oui/Non (2019)
- Videoverbalisation : Oui/Non (2025)
- Accidents : N (2023-2024)

**Section Donnees manquantes :**
- Budget secu : non disponible
- Delinquance : non disponible

**Fermeture :** bouton X ou clic en dehors

### Methodology Drawer (slide-in depuis la droite, 500px)

Declenche par le bouton "?" du top bar. Contenu structure :
- Sources et URLs
- Formule de scoring avec exemples
- Biais connus (couverture stat payant, biais pop_sweet)
- Tableau fraicheur des donnees avec code couleur
- Taux de matching

### Bottom Status Bar (28px)

Ligne d'agregats live : "239 communes > 50 · 226 avec stat. payant · Donnees PM 2024 · Municipales 2020"
Se met a jour en temps reel quand les filtres changent.

## 2. Style Visuel

### Couleurs

| Element | Valeur |
|---------|--------|
| Top bar | `#0d0f17` |
| Command panel | `#111318` |
| Detail panel | `#111318` |
| Borders | `rgba(255,255,255,0.06)` |
| Texte principal | `#e2e4e9` |
| Texte secondaire | `#8b8f98` |
| Texte tertiaire | `#555` |
| Accent prospection | `#4ecdc4` |
| Accent politique | `#4a90d9` |
| Accent surveillance | `#e8913a` |

### Typographie

- System font stack (`-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`)
- Base : `13px`
- Titres sections : `14px` 600
- Score large : `28px` 700
- Nombres dans la liste : `13px` 600 tabular-nums
- Line-height : 1.4

### Pas de glassmorphism

- Pas de `backdrop-filter`
- Pas de `rgba` backgrounds avec transparence
- Fonds solid, bordures fines, pas de box-shadow lourdes
- Ombres legeres uniquement sur le detail panel (overlay)

### Animations

- Transitions : 150ms ease uniquement
- Detail panel : slide-in 200ms depuis la droite
- Methodology drawer : slide-in 200ms depuis la droite
- Pas de cascade, pas de scale, pas de theatralite

## 3. Responsive (mobile)

- Command panel : bottom sheet, swipe-up
- Detail panel : full-width bottom sheet
- Top bar : search icon (expand on tap), tabs compactes
- Liste prospect : simplifie (nom + score uniquement)

## 4. Performance

- Liste prospect : rendu limite aux N premiers visibles (pas de virtualisation complexe, juste un cap a 200 rows + "Voir plus")
- Score cache existant reutilise
- Pas de re-render carte au scroll de la liste
