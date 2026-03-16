# Mode Municipales 2026 — Design Spec

## Objectif

Ajouter un 5e mode "Municipales 2026" à la carte interactive, permettant de visualiser les résultats du T1 des municipales 2026 avec un toggle animé avant/après (2020 ↔ 2026), un halo lumineux sur les communes qui changent de bord politique, et des filtres ciblés pour les équipes marketing.

## Source de données

Fichier généré par `build_csv_t1.py` : `resultats_municipales_2026_t1.csv` (34 870 communes, 29 colonnes). Ce CSV sera transformé en JSON compact (`municipales2026.json`) par un nouveau script Python, suivant le pattern des autres fichiers de données du projet (clés courtes, indexé par code INSEE).

### Structure JSON cible : `municipales2026.json`

Indexé par code INSEE. Champs par commune :

```json
{
  "69123": {
    "ms": "Grégory Doucet",        // maire sortant (format naturel)
    "n20": "LUG",                   // nuance 2020
    "b20": "Gauche",                // bloc 2020
    "vt1": "Grégory Doucet",        // vainqueur T1
    "lt1": "Lyon en commun",        // liste vainqueur
    "n26": "LUG",                   // nuance 2026
    "b26": "Gauche",                // bloc 2026
    "sc": 37.4,                     // score T1 %
    "st": "T2",                     // statut: "T1" (élu) | "T2" (second tour)
    "pa": 48.7,                     // participation %
    "s2": "Pierre Oliver",          // second T1
    "sc2": 24.1,                    // score second %
    "nm": 0,                        // nouveau maire: 1=oui, 0=non, -1=incertain T2
    "cb": 0,                        // changement bord: 1=oui, 0=non, -1=incertain
    "sb": "",                       // sens bascule ex: "Gauche → Droite"
    "cl20": "#E2001A",              // couleur bloc 2020
    "cl26": "#E2001A"               // couleur bloc 2026
  }
}
```

### Mapping bloc → couleur

Réutilise les couleurs FAMILLES existantes + ajouts :

| Bloc | Couleur | Correspondance FAMILLES |
|------|---------|------------------------|
| Extrême gauche | `#B71C1C` | (nouveau, rouge foncé) |
| Gauche | `#E2001A` | FAMILLES.Gauche |
| Centre | `#FFB300` | FAMILLES.Centre |
| Droite | `#0056A6` | FAMILLES.Droite |
| Extrême droite | `#0D1B4A` | FAMILLES."Extrême droite" |
| Divers | `#9E9E9E` | FAMILLES."Courants politiques divers" |
| Sans étiquette | `#666666` | (gris neutre, distinctif du no-data #444) |

## Architecture

### Nouveau fichier de données

- `process_municipales2026.py` — lit `resultats_municipales_2026_t1.csv`, produit `municipales2026.json`
- Ajouté au fetch parallèle initial dans `index.html` (8e fichier JSON)
- Variable globale : `var mun2026 = null;`

### Nouveau mode dans index.html

Suit exactement les patterns existants (mode politique comme modèle principal) :

1. **Bouton mode** : `<button class="mode-btn" data-mode="municipales2026">Municipales 2026</button>` dans `#top-bar`
2. **MODE_COLORS** : `municipales2026: '#8E24AA'` (violet — distinctif des 4 modes existants)
3. **getStyleMunicipales2026(feature)** : nouvelle fonction de style
4. **renderCmdMunicipales2026()** : panneau de commande gauche
5. **Mise à jour de** : `getStyle()`, `switchMode()`, `updateBottomBar()`, `openDetail()`, `readURLState()`/`updateURL()`

## Comportement détaillé

### Toggle 2020 ↔ 2026

- **Position** : en haut du panneau de commande gauche (#cmd-content), élément le plus visible
- **UI** : deux labels "2020" et "2026" de part et d'autre d'un slider/toggle. L'année active est mise en surbrillance.
- **État** : variable globale `var mun2026Year = '2026'` (défaut)
- **Transition** : au clic, appel `geoLayer.setStyle(getStyle)` qui restyle les 35k communes. Leaflet applique les changements de fillColor, ce qui crée une transition visuelle immédiate. On ajoute une CSS transition sur les paths SVG : `transition: fill 300ms ease, fill-opacity 300ms ease, filter 300ms ease` appliquée au conteneur Leaflet SVG.
- **Interaction avec filtres** : les filtres (bloc, bascules, etc.) s'appliquent dans les deux positions du toggle. Ex: filtre "Bascules uniquement" en position 2020 montre les communes qui vont basculer ; en position 2026, celles qui ont basculé.

### Fonction getStyleMunicipales2026(feature)

```
Entrée: feature (GeoJSON commune)
Lire: code INSEE depuis feature.properties.c
Lire: mun2026[code]

Si pas de données → STYLE_NO_DATA (dashArray: null)
Si filtré (bloc actif et pas le bon) → STYLE_FILTERED

Déterminer la couleur:
  - Si mun2026Year === '2020' → utiliser cl20
  - Si mun2026Year === '2026' → utiliser cl26

Déterminer dashArray:
  - Si statut === 'T2' ET mun2026Year === '2026' → dashArray: '4 4' (hachures)
  - Sinon → dashArray: null

Déterminer le filter (halo):
  - Si cb === 1 (bascule confirmée) ET mun2026Year === '2026'
    → retourner className additionnelle ou utiliser un border glow
  - Sinon → pas de halo

Retour: { fillColor, fillOpacity: 0.75, weight, color, opacity, dashArray }
```

### Halo lumineux sur les bascules

**Implémentation** : CSS filter `drop-shadow` sur les paths SVG des communes qui basculent.

Approche :
- `getStyleMunicipales2026()` retourne un `weight: 2.5` et `color: '#FFFFFF'` (bordure blanche épaisse) pour les communes avec `cb === 1` quand on est en position 2026
- En complément, on ajoute une classe CSS `.bascule-glow` aux paths concernés via un passage post-restyle
- CSS : `.bascule-glow { filter: drop-shadow(0 0 4px rgba(255,255,255,0.8)); }`

**Performance** : `drop-shadow` sur ~610 éléments SVG est acceptable. On ne l'applique PAS aux 35k communes. Le passage post-restyle itère `layerByCode` uniquement pour les communes avec `cb === 1` (~610), en ajoutant/retirant la classe sur `layer._path`.

**Transition animée** : quand le toggle passe de 2020 à 2026 :
1. D'abord restyle (couleurs changent avec transition CSS 300ms)
2. Après 150ms (setTimeout), ajout des classes `.bascule-glow` → les halos apparaissent en fondu
3. Quand le toggle repasse à 2020, les classes sont retirées immédiatement

### Panneau de commande (renderCmdMunicipales2026)

Structure verticale dans `#cmd-content` :

```
┌──────────────────────────────┐
│  ◀ 2020      ●───── 2026 ▶  │  ← Toggle principal
├──────────────────────────────┤
│  Filtres par bloc            │
│  [Tous] [Gau] [Cen] [Dro]   │  ← Pills cliquables (comme politique)
│  [ExD] [Div] [SE]           │
├──────────────────────────────┤
│  ☐ Bascules uniquement       │  ← Checkbox exclusive
│  ☐ Nouveaux maires           │
│  ☐ Second tour               │
├──────────────────────────────┤
│  Légende                     │
│  ■ Gauche ........... 825    │  ← Pastilles + compteurs
│  ■ Droite .......... 1254    │
│  ...                         │
│  ▨ = en attente du T2        │  ← Explication hachures
│  ✦ = bascule politique       │  ← Explication halo
├──────────────────────────────┤
│  Sources : MdI via data.gouv │
│  MAJ : 16/03/2026            │
└──────────────────────────────┘
```

**Checkboxes mutuellement exclusives** : cliquer sur "Bascules uniquement" décoche les deux autres. Mécanisme : variable `mun2026Filter` = `null` | `'bascules'` | `'nouveaux'` | `'t2'`. Quand actif, `getStyleMunicipales2026()` retourne `STYLE_FILTERED` pour les communes qui ne matchent pas le filtre.

**Compteurs dans la légende** : recalculés dynamiquement selon la position du toggle (2020 vs 2026 changent les nuances affichées) et le filtre actif.

### Panneau de détail (openDetail)

Nouvelle section ajoutée dans `openDetail()`, visible quel que soit le mode actif (comme les autres sections) :

```
┌──────────────────────────────┐
│  MUNICIPALES 2026            │  ← Titre section
├──────────────────────────────┤
│  Maire sortant (2020)        │
│  Grégory Doucet — LUG        │
│  ■ Gauche                    │
├──────────────────────────────┤
│  Résultat T1 2026            │
│  ▶ Grégory Doucet — 37.4%   │  ← Vainqueur
│    Liste: "Lyon en commun"   │
│    ■ Gauche (LUG)            │
│    ▨ Second tour             │  ← Badge si T2
│  ▷ Pierre Oliver — 24.1%    │  ← Second
│    Marge: +13.3 pts          │
├──────────────────────────────┤
│  Participation: 48.7%        │
├──────────────────────────────┤
│  ✓ Même bord politique       │  ← Ou: ✦ Bascule Gauche → Droite
│  ✓ Sortant reconduit         │  ← Ou: ★ Nouveau maire
└──────────────────────────────┘
```

### Bottom bar (updateBottomBar)

Format : `"610 bascules | 13 566 nouveaux maires | 1 684 en attente T2 | Participation moy. : 63.2%"`

Les chiffres se mettent à jour en fonction du filtre par bloc actif.

### URL / Deep linking

- Mode encodé : `?mode=municipales2026`
- Paramètre additionnel : `&year=2020` (uniquement si 2020 est sélectionné, 2026 est le défaut omis)
- Filtres : `&filter=bascules` | `&filter=nouveaux` | `&filter=t2`

### État global ajouté

```javascript
var mun2026 = null;           // données JSON chargées
var mun2026Year = '2026';     // position du toggle
var mun2026Filter = null;     // null | 'bascules' | 'nouveaux' | 't2'
var mun2026BlocFilter = null; // null | 'Gauche' | 'Droite' | etc.
```

## Performance

- **CSS transition sur SVG paths** : `transition: fill 300ms ease` ajouté une seule fois au conteneur SVG Leaflet (`.leaflet-overlay-pane svg path`). Pas de transition par élément.
- **Halo limité à ~610 éléments** : itération de `layerByCode` filtrée par `mun2026[code].cb === 1`. Pas de querySelectorAll.
- **Style constants pré-alloués** : `STYLE_MUN_NO_DATA`, `STYLE_MUN_FILTERED` avec `dashArray: null` explicite.
- **Pas de re-fetch** au toggle : les données 2020 et 2026 sont dans le même JSON, le toggle ne fait que changer quelle couleur est lue.
- **dashArray toggle** : les communes T2 passent de `null` (en 2020) à `'4 4'` (en 2026), géré proprement dans getStyle pour éviter les merge leaks.

## Fichiers modifiés

| Fichier | Modification |
|---------|-------------|
| `index.html` | Nouveau bouton, nouvelles fonctions (getStyle, renderCmd, updateBottomBar, openDetail section), état global, fetch, CSS |
| `process_municipales2026.py` | **Nouveau** — génère `municipales2026.json` depuis le CSV |
| `municipales2026.json` | **Nouveau** — données de résultats (~1.5 MB estimé) |
| `build_csv_t1.py` | Déjà existant, pas de modification |

## Hors scope

- Résultats T2 (pas encore dépouillé)
- Modification du mode politique existant
- Modification des autres modes (prospection, surveillance, securite)
- Données par bureau de vote
