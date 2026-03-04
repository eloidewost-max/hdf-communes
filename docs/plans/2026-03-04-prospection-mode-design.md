# Prospection Mode — Design Document

## Overview

Add a third "Prospection" mode to the carte politique app, designed for identifying communes likely to buy a LAPI-based vidéoverbalisation solution. Enriches the map with new open data sources (budgets sécurité, police municipale trends, stationnement payant, vidéoverbalisation deployments) and provides interactive scoring to rank communes by sales potential.

## Data Pipeline

### New data sources

| Dataset | Source | Format | Freshness | URL |
|---------|--------|--------|-----------|-----|
| Budgets sécurité (function 1) | Balances comptables DGFiP | CSV ~95 MB | 2024 | data.gouv.fr balances-comptables-des-communes-en-2024 |
| Police municipale effectifs (multi-year) | Min. Intérieur | ODS/XLSX | 2019-2024 | data.gouv.fr police-municipale-effectifs-par-commune |
| Stationnement payant | GART/Cerema survey | CSV 64 KB | 2018 | data.gouv.fr enquete-sur-la-reforme-du-stationnement-payant-sur-voirie |
| Vidéoverbalisation communes | video-verbalisation.fr | HTML scrape | ~2024 | video-verbalisation.fr/villes.php |

### Reused data

- `maires.json` — political family, nuance, maire name
- `surveillance.json` — vidéoprotection flag (2012), police municipale counts (2024), ASVP, population

### New script: `process_prospection.py`

Downloads and processes the above sources, outputs `prospection.json`.

### Output schema: `prospection.json`

Keyed by INSEE code. Every data point carries a `_year` field for freshness display.

```json
{
  "92009": {
    "budget_secu": 1250000,
    "budget_secu_year": 2024,
    "pm_trend": [8, 10, 12, 15, 18, 21],
    "pm_trend_years": [2019, 2020, 2021, 2022, 2023, 2024],
    "stat_payant": true,
    "stat_payant_year": 2018,
    "videoverb": false,
    "videoverb_year": 2024,
    "vs": 1,
    "vs_year": 2012,
    "pop": 28909,
    "pop_year": 2021
  }
}
```

Communes with no data for a field omit that field entirely (no nulls).

## Prospection Mode UI

### Mode switching

Third button in the mode toggle: `Politique | Surveillance | Prospection`. The toggle becomes a pill-style segmented control (see UX section).

### Map coloring

Heatmap based on a composite "potential" score (0-100). Score computed client-side in JS so it updates live when the user adjusts weight sliders.

Color gradient: cold (blue/grey, low potential) → hot (orange/red, high potential). Communes with no data shown in neutral dark grey.

### Scoring signals and default weights

| Signal | Logic | Default weight |
|--------|-------|---------------|
| Has stationnement payant | Binary | 25 |
| No vidéoverbalisation | Binary (inverted — higher if NOT equipped) | 25 |
| Police municipale count | Normalized by population | 15 |
| PM trend growing | % change over available years | 10 |
| Budget sécurité | Normalized by population | 15 |
| Has vidéoprotection | Binary | 5 |
| Population in sweet spot | Gaussian around 5k-100k | 5 |

Total default weights = 100. Each weight adjustable via slider (0-100), scores renormalized.

### Interactive weight sliders

In the right sidebar, one slider per signal. Dragging a slider recalculates scores and recolors the map in real time. Each slider labeled with the signal name and current weight value.

### Info panel (on hover)

Displays all data for the hovered commune with freshness years:

```
Boulogne-Billancourt (92)
──────────────────────────
Score prospection     78/100
Budget sécurité       1 250 000 €    (2024)
Police municipale     21 agents       (2024)
Évolution PM          +62% sur 5 ans  (2019-2024)
Stationnement payant  Oui             (2018)
Vidéoverbalisation    Non             (2024)
Vidéoprotection       Oui             (2012)
Population            28 909          (2021)
Maire                 ...
Famille politique     ...
```

### Stats sidebar

Below the weight sliders:
- Nombre de communes scorées
- Nombre avec stationnement payant sans vidéoverbalisation
- Top 10 départements par score moyen
- Répartition par famille politique

### Filters

- Population range slider (min/max)
- Toggle: stationnement payant uniquement
- Toggle: sans vidéoverbalisation (exclure les équipées)
- Toggle: avec vidéoprotection

Filters exclude communes from both the map coloring and the stats.

## UX/UI Polish (all modes)

### Mode toggle
- Pill-style segmented control replacing plain buttons
- Active mode gets colored underline: blue (politique), orange (surveillance), green (prospection)
- Smooth transition on switch

### Panels & cards
- Unified card style: border-radius 10px, backdrop-blur glassmorphism over dark map
- Consistent padding (16-20px)
- CSS fade/slide transitions when switching modes (legend, sidebar, info panel)

### Typography
- Tighter hierarchy: 11/13/15/18px scale
- Text color levels: titles (#1a1a2e), labels (#444), secondary (#888)
- Year/freshness indicators in light grey (#aaa) italic

### Filter buttons
- Pill-shaped with rounded corners
- Clear active state: accent border + subtle background + optional checkmark
- Smooth hover transitions

### Legend
- Better swatch/label alignment
- More visible hover highlight on interactive items

### Responsive
- Sidebar collapses to bottom drawer on screens < 768px
- Filters stack vertically on mobile
- Info panel repositions to bottom on small viewports

### Transitions & interactions
- CSS transitions on mode switch (cross-fade legend, slide sidebar)
- Smooth opacity transition on commune polygon hover
- Consistent panel background opacity (rgba backdrop-blur)

### Accessibility
- All text meets WCAG AA contrast ratios
- Consistent focus indicators on interactive elements

## Data freshness principle

Every data point displayed in the UI must show its source year. This applies to:
- Info panel fields (year in parentheses, grey italic)
- Legend/sidebar where aggregate stats are shown (footnote with year range)
- Scoring sidebar (each signal slider labeled with data year)

No data is presented without its vintage being visible.
