# UI Redesign — Sales Intelligence Tool — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rewrite the entire `index.html` interface from a map-first visualization to a split-panel sales intelligence tool with ranked prospect list, unified detail panel, and methodology transparency.

**Architecture:** Single-file HTML with split layout: left command panel (360px) + right map (remaining). All current JS logic (scoring, styling, data loading) is preserved and refactored into the new layout. New features: ranked prospect list, detail panel on click, methodology drawer, score distribution histogram, data quality indicators.

**Tech Stack:** Vanilla JS (ES5-compatible), Leaflet.js 1.9.4, TopoJSON-client 3.1.0, inline CSS, no build system.

---

## Task 1: CSS Reset — New Layout Shell

**Files:**
- Modify: `index.html:1-313` (entire `<style>` block)

**Step 1: Replace the entire CSS with the new layout foundation**

Delete all existing CSS (lines 8-313) and replace with the new layout system. This establishes:
- Split layout: `#app` grid with `360px` left panel + `1fr` map
- Top bar: 44px fixed height
- Bottom bar: 28px fixed height
- Command panel: full height, scrollable
- Map: fills remaining space
- No glassmorphism anywhere — solid dark backgrounds

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #0a0b10; color: #e2e4e9; font-size: 13px; line-height: 1.4; }

/* --- App Layout --- */
#app { display: grid; grid-template-rows: 44px 1fr 28px; grid-template-columns: 360px 1fr; height: 100vh; width: 100vw; }
#top-bar { grid-column: 1 / -1; display: flex; align-items: center; padding: 0 16px; background: #0d0f17; border-bottom: 1px solid rgba(255,255,255,0.06); z-index: 100; gap: 12px; }
#cmd-panel { grid-row: 2; grid-column: 1; background: #111318; border-right: 1px solid rgba(255,255,255,0.06); overflow-y: auto; overflow-x: hidden; }
#map { grid-row: 2; grid-column: 2; background: #1a1a2e; position: relative; }
#bottom-bar { grid-column: 1 / -1; display: flex; align-items: center; padding: 0 16px; background: #0d0f17; border-top: 1px solid rgba(255,255,255,0.06); font-size: 12px; color: #8b8f98; gap: 16px; }

/* --- Scrollbar --- */
#cmd-panel::-webkit-scrollbar { width: 5px; }
#cmd-panel::-webkit-scrollbar-track { background: transparent; }
#cmd-panel::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
#cmd-panel::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

/* --- Top Bar --- */
#search-box { position: relative; width: 260px; flex-shrink: 0; }
#search-input { width: 100%; padding: 7px 12px 7px 32px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; color: #e2e4e9; font-size: 13px; outline: none; transition: border-color 0.15s; }
#search-input::placeholder { color: #555; }
#search-input:focus { border-color: rgba(255,255,255,0.2); }
#search-icon { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: #555; font-size: 13px; pointer-events: none; }
#search-results { position: absolute; top: 100%; left: 0; right: 0; margin-top: 4px; max-height: 320px; overflow-y: auto; background: #1a1c24; border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; display: none; z-index: 200; }
.search-item { padding: 7px 12px; cursor: pointer; font-size: 13px; color: #8b8f98; display: flex; justify-content: space-between; align-items: center; }
.search-item:hover, .search-item.active { background: rgba(255,255,255,0.06); color: #e2e4e9; }
.search-item-code { font-size: 11px; color: #555; }
.search-item-swatch { display: inline-block; width: 8px; height: 8px; border-radius: 2px; margin-right: 6px; }

#mode-tabs { display: flex; gap: 0; margin-left: auto; background: rgba(255,255,255,0.04); border-radius: 6px; padding: 2px; position: relative; }
.mode-btn { padding: 6px 18px; border: none; cursor: pointer; font-size: 13px; font-weight: 600; border-radius: 4px; background: transparent; color: #8b8f98; transition: color 0.15s, background 0.15s; }
.mode-btn:hover { color: #c0c3ca; }
.mode-btn.active { color: #e2e4e9; background: rgba(255,255,255,0.08); }
#mode-indicator { position: absolute; bottom: 0; height: 2px; border-radius: 1px; transition: left 0.2s ease, width 0.2s ease, background 0.2s ease; }
#btn-methodo { background: none; border: 1px solid rgba(255,255,255,0.08); color: #8b8f98; width: 30px; height: 30px; border-radius: 6px; cursor: pointer; font-size: 14px; transition: all 0.15s; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
#btn-methodo:hover { color: #e2e4e9; border-color: rgba(255,255,255,0.2); }

/* --- Command Panel Sections --- */
.cmd-section { padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.06); }
.cmd-section-title { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #555; margin-bottom: 8px; }
.cmd-section-collapsible { cursor: pointer; display: flex; align-items: center; justify-content: space-between; }
.cmd-section-collapsible .chevron { transition: transform 0.15s; font-size: 11px; color: #555; }
.cmd-section-collapsible.open .chevron { transform: rotate(90deg); }
.cmd-section-body { overflow: hidden; }
.cmd-section-body.collapsed { display: none; }

/* --- Filters --- */
.filter-row { display: flex; align-items: center; gap: 6px; margin: 4px 0; font-size: 13px; }
.filter-row label { display: flex; align-items: center; gap: 5px; cursor: pointer; color: #8b8f98; }
.filter-row label:hover { color: #e2e4e9; }
input[type="checkbox"] { accent-color: #4ecdc4; }
input[type="range"] { -webkit-appearance: none; appearance: none; height: 3px; background: rgba(255,255,255,0.1); border-radius: 2px; outline: none; flex: 1; }
input[type="range"]::-webkit-slider-thumb { -webkit-appearance: none; width: 12px; height: 12px; border-radius: 50%; background: #4ecdc4; cursor: pointer; }
input[type="range"]::-moz-range-thumb { width: 12px; height: 12px; border-radius: 50%; border: none; background: #4ecdc4; cursor: pointer; }
.slider-value { min-width: 32px; text-align: right; font-weight: 600; font-size: 12px; color: #8b8f98; }

/* --- Filter pills (politique mode) --- */
.filter-pills { display: flex; flex-wrap: wrap; gap: 4px; }
.filter-pill { padding: 4px 10px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.08); background: transparent; cursor: pointer; font-size: 12px; color: #8b8f98; transition: all 0.15s; }
.filter-pill:hover { border-color: rgba(255,255,255,0.2); color: #e2e4e9; }
.filter-pill.active { border-color: currentColor; color: #fff; }

/* --- Score Distribution Histogram --- */
.histogram { display: flex; align-items: flex-end; gap: 2px; height: 40px; margin: 4px 0; }
.histogram-bar { flex: 1; background: rgba(255,255,255,0.08); border-radius: 2px 2px 0 0; min-height: 2px; transition: background 0.15s; }
.histogram-labels { display: flex; justify-content: space-between; font-size: 10px; color: #555; margin-top: 2px; }

/* --- Prospect List --- */
.prospect-list { list-style: none; }
.prospect-row { display: grid; grid-template-columns: 1fr auto; gap: 4px; padding: 8px 16px; cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.03); transition: background 0.1s; align-items: center; }
.prospect-row:hover { background: rgba(255,255,255,0.04); }
.prospect-row.selected { background: rgba(78,205,196,0.08); }
.prospect-name { font-size: 13px; color: #e2e4e9; display: flex; align-items: center; gap: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.prospect-dot { width: 8px; height: 8px; border-radius: 2px; flex-shrink: 0; }
.prospect-meta { font-size: 11px; color: #555; }
.prospect-score-wrap { display: flex; align-items: center; gap: 6px; }
.prospect-score { font-size: 13px; font-weight: 600; font-variant-numeric: tabular-nums; min-width: 24px; text-align: right; }
.prospect-bar { width: 40px; height: 5px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden; }
.prospect-bar-fill { height: 100%; border-radius: 3px; }
.prospect-signals { display: flex; gap: 3px; font-size: 11px; color: #555; }
.prospect-more { padding: 10px 16px; text-align: center; font-size: 12px; color: #4ecdc4; cursor: pointer; }
.prospect-more:hover { background: rgba(255,255,255,0.04); }

/* --- Legend (compact) --- */
.legend-row { display: flex; align-items: center; gap: 8px; margin: 3px 0; font-size: 12px; color: #8b8f98; }
.legend-swatch { width: 14px; height: 14px; border-radius: 3px; flex-shrink: 0; }
.legend-count { margin-left: auto; font-size: 11px; color: #555; }

/* --- Info tooltip (hover, minimal) --- */
#info { position: fixed; z-index: 300; padding: 8px 12px; pointer-events: none; display: none; background: #1a1c24; border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; font-size: 12px; max-width: 260px; }
#info-name { font-weight: 600; color: #e2e4e9; margin-bottom: 2px; }
#info-metric { color: #8b8f98; }

/* --- Detail Panel (right overlay) --- */
#detail-panel { position: absolute; top: 0; right: 0; bottom: 0; width: 400px; background: #111318; border-left: 1px solid rgba(255,255,255,0.06); box-shadow: -8px 0 24px rgba(0,0,0,0.3); z-index: 150; overflow-y: auto; transform: translateX(100%); transition: transform 0.2s ease; }
#detail-panel.open { transform: translateX(0); }
#detail-close { position: sticky; top: 0; display: flex; justify-content: flex-end; padding: 8px 12px; background: #111318; z-index: 1; }
#detail-close button { background: none; border: none; color: #555; font-size: 18px; cursor: pointer; padding: 4px 8px; border-radius: 4px; }
#detail-close button:hover { color: #e2e4e9; background: rgba(255,255,255,0.06); }
.detail-section { padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.06); }
.detail-header-name { font-size: 18px; font-weight: 700; color: #fff; margin-bottom: 4px; }
.detail-header-sub { font-size: 13px; color: #8b8f98; }
.detail-badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.detail-score-big { font-size: 28px; font-weight: 700; font-variant-numeric: tabular-nums; }
.detail-rank { font-size: 12px; color: #8b8f98; margin-left: 8px; }
.detail-signal-row { display: flex; align-items: center; gap: 8px; margin: 6px 0; font-size: 13px; }
.detail-signal-bar-bg { width: 60px; height: 6px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden; flex-shrink: 0; }
.detail-signal-bar-fill { height: 100%; border-radius: 3px; }
.detail-signal-label { flex: 1; color: #8b8f98; }
.detail-signal-value { font-weight: 600; color: #e2e4e9; min-width: 32px; text-align: right; }
.detail-signal-year { font-size: 10px; color: #555; margin-left: 4px; }
.detail-kv { display: flex; justify-content: space-between; margin: 4px 0; font-size: 13px; }
.detail-kv-label { color: #8b8f98; }
.detail-kv-value { color: #e2e4e9; font-weight: 500; }
.detail-warning { font-size: 11px; color: #e8913a; margin-top: 4px; padding: 6px 8px; background: rgba(232,145,58,0.06); border-radius: 4px; }
.detail-missing { font-size: 11px; color: #555; font-style: italic; }

/* --- Methodology Drawer --- */
#methodo-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 500; display: none; }
#methodo-overlay.open { display: block; }
#methodo-drawer { position: fixed; top: 0; right: 0; bottom: 0; width: 520px; background: #111318; border-left: 1px solid rgba(255,255,255,0.06); z-index: 501; overflow-y: auto; transform: translateX(100%); transition: transform 0.2s ease; padding: 24px; }
#methodo-drawer.open { transform: translateX(0); }
#methodo-drawer h2 { font-size: 18px; font-weight: 700; color: #fff; margin-bottom: 16px; }
#methodo-drawer h3 { font-size: 14px; font-weight: 600; color: #e2e4e9; margin: 16px 0 8px; }
#methodo-drawer p, #methodo-drawer li { font-size: 13px; color: #8b8f98; line-height: 1.6; margin: 4px 0; }
#methodo-drawer table { width: 100%; border-collapse: collapse; font-size: 12px; margin: 8px 0; }
#methodo-drawer th, #methodo-drawer td { padding: 5px 8px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.06); }
#methodo-drawer th { color: #555; font-weight: 600; text-transform: uppercase; font-size: 10px; letter-spacing: 0.5px; }
#methodo-drawer td { color: #8b8f98; }
#methodo-drawer code { background: rgba(255,255,255,0.06); padding: 2px 5px; border-radius: 3px; font-size: 12px; }
.methodo-close { position: sticky; top: 0; display: flex; justify-content: space-between; align-items: center; background: #111318; padding-bottom: 12px; margin: -24px -24px 0; padding: 16px 24px 12px; z-index: 1; }
.methodo-close button { background: none; border: none; color: #555; font-size: 18px; cursor: pointer; padding: 4px 8px; border-radius: 4px; }
.methodo-close button:hover { color: #e2e4e9; background: rgba(255,255,255,0.06); }
.freshness-green { color: #4ecdc4; }
.freshness-yellow { color: #f39c12; }
.freshness-orange { color: #e8913a; }

/* --- Coverage banner --- */
.coverage-banner { padding: 8px 12px; background: rgba(74,144,217,0.06); border-radius: 4px; font-size: 12px; color: #8b8f98; margin-bottom: 8px; border-left: 3px solid #4a90d9; }

/* --- Loading --- */
#loading { position: fixed; inset: 0; z-index: 2000; background: #0a0b10; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px; }
#loading .spinner { width: 32px; height: 32px; border: 3px solid rgba(255,255,255,0.08); border-top-color: #4ecdc4; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
#load-text { font-size: 14px; color: #8b8f98; }
#load-status { font-size: 12px; color: #555; }

/* --- Responsive --- */
@media (max-width: 768px) {
  #app { grid-template-columns: 1fr; }
  #cmd-panel { grid-row: 3; grid-column: 1; max-height: 45vh; border-right: none; border-top: 1px solid rgba(255,255,255,0.06); }
  #map { grid-row: 2; grid-column: 1; }
  #bottom-bar { display: none; }
  #detail-panel { width: 100%; }
  #methodo-drawer { width: 100%; }
  #search-box { width: 180px; }
  .mode-btn { padding: 5px 12px; font-size: 12px; }
}
```

**Step 2: Verify CSS compiles (open in browser)**

Open `index.html` in browser. Expect: broken layout since HTML structure hasn't changed yet. This is expected — we're replacing incrementally.

**Step 3: Commit**

```bash
git add index.html
git commit -m "style: replace all CSS with new split-panel layout system"
```

---

## Task 2: HTML Structure — New Layout Shell

**Files:**
- Modify: `index.html:315-420` (HTML body before `<script>`)

**Step 1: Replace the entire HTML body structure**

Remove all existing HTML between `<body>` and `<script>` tags. Replace with the new layout:

```html
<div id="loading">
  <div class="spinner"></div>
  <div id="load-text">Chargement des 35 000 communes...</div>
  <div id="load-status"></div>
</div>

<div id="app">
  <!-- Top Bar -->
  <div id="top-bar">
    <div id="search-box">
      <span id="search-icon">&#x1F50D;</span>
      <input type="text" id="search-input" placeholder="Rechercher une commune..." autocomplete="off">
      <div id="search-results"></div>
    </div>
    <div id="mode-tabs">
      <button class="mode-btn active" data-mode="prospection">Prospection</button>
      <button class="mode-btn" data-mode="politique">Politique</button>
      <button class="mode-btn" data-mode="surveillance">Surveillance</button>
      <div id="mode-indicator"></div>
    </div>
    <button id="btn-methodo" title="Methodologie et sources">?</button>
  </div>

  <!-- Command Panel -->
  <div id="cmd-panel">
    <div id="cmd-content"></div>
  </div>

  <!-- Map -->
  <div id="map">
    <div id="detail-panel">
      <div id="detail-close"><button title="Fermer">&times;</button></div>
      <div id="detail-content"></div>
    </div>
  </div>

  <!-- Bottom Bar -->
  <div id="bottom-bar">
    <span id="bottom-stats"></span>
  </div>
</div>

<!-- Info tooltip (follows mouse) -->
<div id="info">
  <div id="info-name"></div>
  <div id="info-metric"></div>
</div>

<!-- Methodology Drawer -->
<div id="methodo-overlay"></div>
<div id="methodo-drawer">
  <div class="methodo-close">
    <h2>Methodologie et sources</h2>
    <button title="Fermer">&times;</button>
  </div>
  <div id="methodo-content"></div>
</div>
```

**Step 2: Verify structure loads**

Open in browser. Expect: dark background, grid layout visible, empty panels. Map won't load yet (JS needs updating).

**Step 3: Commit**

```bash
git add index.html
git commit -m "feat: new HTML structure with split-panel layout"
```

---

## Task 3: Core JS — Data Loading + Map Init (preserve existing logic)

**Files:**
- Modify: `index.html` JS section

**Step 1: Rewrite the JS initialization**

Keep all existing data loading and map creation logic, but adapt it to the new layout:
- Map now targets `#map` (same ID, but positioned by CSS grid)
- Remove all references to removed DOM elements (`#title-bar`, `#filter-bar`, `#surv-filters`, `#legend`, old `#stats-panel`, `#stats-tab`)
- Keep: `FAMILLES`, `SURV_COLORS`, `PROSP_COLORS`, `PROSP_SIGNALS`, all scoring functions, `getStyle*` functions
- Default mode is now `prospection` (not `politique`)
- Keep search functionality intact

Key changes in the JS init:
- `var currentMode = 'prospection';` (was `'politique'`)
- Remove all cascade animation code
- Remove old `renderLegend`, `renderStats`, `renderProspStats`, `updateProspSummary` — they'll be rewritten

**Step 2: Verify map renders with data**

Open in browser. Expect: map visible in right panel, communes styled in prospection mode (default), loading screen disappears.

**Step 3: Commit**

```bash
git add index.html
git commit -m "feat: adapt JS init to new layout, default to prospection mode"
```

---

## Task 4: Command Panel — Prospection Mode

**Files:**
- Modify: `index.html` JS section

**Step 1: Implement `renderCmdProspection()`**

This function builds the left panel content for prospection mode:

1. **Filters section** — checkboxes + pop slider (always visible)
2. **Parametres section** — weight sliders (collapsible, closed by default)
3. **Score distribution histogram** — 8 bars from the score distribution
4. **Ranked prospect list** — sorted by score descending, capped at 200, with "Voir plus" button
5. **Legend section** — compact color scale

The prospect list is the core feature. Each row:
- Political color dot (always visible)
- Commune name (truncated)
- Population (compact: "28k")
- Score bar + number
- Hover: highlight commune on map via `layerByCode[code]`
- Click: zoom map + open detail panel

Build the ranked list by iterating all `prosp` keys, computing scores, sorting, and rendering the top N.

**Step 2: Verify prospect list renders**

Open in browser. Expect: left panel shows filters, histogram, and a scrollable list of communes sorted by score. Hovering a row highlights the commune on the map.

**Step 3: Commit**

```bash
git add index.html
git commit -m "feat: command panel prospection mode with ranked prospect list"
```

---

## Task 5: Command Panel — Politique and Surveillance Modes

**Files:**
- Modify: `index.html` JS section

**Step 1: Implement `renderCmdPolitique()`**

Content:
- Coverage banner: "2 693 / 34 844 communes avec nuance officielle — Municipales 2020"
- Filter pills for each famille (clickable, toggle `activeFilter`)
- Legend with swatches + counts
- Surveillance sub-legend (border weight = PM effectif)

**Step 2: Implement `renderCmdSurveillance()`**

Content:
- Ratio slider + "Donnees uniquement" checkbox
- Stats table (famille breakdown with avg ratio)
- Summary text (max/min famille)
- Heatmap legend
- Source notes

**Step 3: Implement `switchMode()` rewrite**

The new `switchMode` clears `#cmd-content` and calls the appropriate render function. Also updates:
- Mode button active states
- Mode indicator position/color
- Map styling via `geoLayer.setStyle(getStyle)`
- Bottom bar stats
- Subtitle (removed — no subtitle in new design)

**Step 4: Verify all three modes work**

Open in browser. Switch between modes. Expect: left panel content changes, map colors change, filters work.

**Step 5: Commit**

```bash
git add index.html
git commit -m "feat: command panel for politique and surveillance modes"
```

---

## Task 6: Detail Panel — Unified Commune View

**Files:**
- Modify: `index.html` JS section

**Step 1: Implement `openDetail(code)`**

This function builds the detail panel content for a commune, showing **all three dimensions** regardless of active mode:

**Header section:**
- Commune name + INSEE code
- Population formatted
- Political badge (colored background with famille name)
- Mayor name + nuance label

**Score section:**
- Large score number + colored bar
- "Top X%" rank (computed from score distribution)
- 5 signal decomposition bars with:
  - Bar fill (colored by value: green > 60%, yellow > 30%, red)
  - Signal label
  - Raw value description
  - Contribution points
  - Year badge with freshness color (green < 2 ans, yellow 2-5 ans, orange > 5 ans)
- Coverage warning for stat_payant ("226 communes couvertes sur ~800+ reelles")

**Surveillance section:**
- PM agents + ASVP agents
- Ratio /10k (with raw value if capped, + tourist warning)
- PM trend sparkline (simple inline SVG: polyline over 3 data points)

**Signals section:**
- Stat payant: Oui/Non (year)
- Videoverbalisation: Oui/Non (year)
- Accidents: count (years)

**Missing data section:**
- "Budget securite : non disponible"
- "Statistiques delinquance : non disponible"

**Step 2: Wire click events**

- Click on prospect list row → `openDetail(code)` + zoom map
- Click on map commune → `openDetail(code)` (replace `map.fitBounds` only behavior)
- Click close button → close panel
- Click outside detail panel on map → close panel

**Step 3: Verify detail panel opens**

Click a commune on map or in list. Expect: detail panel slides in from right with full data. Close button works.

**Step 4: Commit**

```bash
git add index.html
git commit -m "feat: unified detail panel with all three data dimensions"
```

---

## Task 7: Hover Tooltip — Minimal

**Files:**
- Modify: `index.html` JS section

**Step 1: Simplify the hover tooltip**

Replace the current verbose tooltip with a minimal 2-line version:
- Line 1: Commune name (bold)
- Line 2: Key metric based on mode
  - Prospection: "Score: 74/100"
  - Politique: "Droite — Socialiste (LSOC)"
  - Surveillance: "12.4 /10k hab"

Reuse existing `positionInfo()` logic. Remove all the old `showInfo()` complexity (score decomposition in tooltip, surveillance details in tooltip — that's now in the detail panel).

**Step 2: Verify tooltip works**

Hover over communes. Expect: small tooltip follows mouse, shows name + one metric.

**Step 3: Commit**

```bash
git add index.html
git commit -m "feat: minimal hover tooltip, detail moved to click panel"
```

---

## Task 8: Methodology Drawer

**Files:**
- Modify: `index.html` JS section

**Step 1: Implement `renderMethodo()`**

Builds the methodology drawer content from hardcoded HTML (structured from METHODOLOGIE.md):

Sections:
1. **Vue d'ensemble** — 3 modes, coverage numbers
2. **Sources des donnees** — table with source, year, format, coverage, URL
3. **Score de prospection** — formula, 5 signals explained briefly
4. **Biais connus** — list of 4 known biases
5. **Fraicheur** — table with year + freshness color badge per dataset
6. **Limites** — data gaps (budgets, delinquance, police intercommunale)

**Step 2: Wire open/close**

- Click `#btn-methodo` → toggle `#methodo-overlay.open` + `#methodo-drawer.open`
- Click overlay → close
- Click close button → close

**Step 3: Verify drawer works**

Click "?" button. Expect: overlay darkens map, drawer slides in from right. Content is readable. Close works.

**Step 4: Commit**

```bash
git add index.html
git commit -m "feat: methodology drawer with sources and scoring transparency"
```

---

## Task 9: Bottom Status Bar

**Files:**
- Modify: `index.html` JS section

**Step 1: Implement `updateBottomBar()`**

Computes and displays live aggregate stats based on current mode and filters:

**Prospection:** "239 communes > 50 · 226 avec stat. payant · Donnees PM 2024 · Municipales 2020"
**Politique:** "2 693 communes avec nuance · Gauche: 820 · Droite: 1 075 · Municipales 2020"
**Surveillance:** "4 164 communes avec donnees · Ratio moyen: X.X /10k · Donnees 2024"

Called on mode switch, filter change, and initial load.

**Step 2: Verify status bar updates**

Switch modes, toggle filters. Expect: bottom bar text updates in real-time.

**Step 3: Commit**

```bash
git add index.html
git commit -m "feat: live bottom status bar with aggregate stats"
```

---

## Task 10: Polish and Cleanup

**Files:**
- Modify: `index.html`

**Step 1: Remove dead code**

Delete any remaining references to:
- `#title-bar`, `#filter-bar`, `#surv-filters` old HTML
- `cascadePanels`, `animatePanel`, `panelSlideIn/Out` animations
- `statsCollapse`, `statsTab`, `statsBadge` old panel logic
- Any unused CSS classes

**Step 2: Verify full workflow**

Complete test:
1. Page loads in prospection mode
2. Prospect list shows ranked communes
3. Click a commune → detail panel opens with full data
4. Switch to politique → filter pills work, list updates
5. Switch to surveillance → ratio slider works
6. Search bar finds communes and zooms
7. Methodology drawer opens and closes
8. Bottom bar updates on all interactions
9. Responsive: resize to 768px, panels stack correctly

**Step 3: Final commit**

```bash
git add index.html
git commit -m "chore: remove dead code, polish full workflow"
```

---

## Summary

| Task | Description | Key Deliverable |
|------|-------------|-----------------|
| 1 | CSS reset | New layout system, no glassmorphism |
| 2 | HTML structure | Split-panel grid layout |
| 3 | JS init | Data loading + map in new layout |
| 4 | Cmd panel: prospection | Ranked prospect list (core feature) |
| 5 | Cmd panel: politique/surveillance | Filter pills, stats tables |
| 6 | Detail panel | Unified all-dimension commune view |
| 7 | Hover tooltip | Minimal 2-line tooltip |
| 8 | Methodology drawer | Sources + scoring transparency |
| 9 | Bottom bar | Live aggregate stats |
| 10 | Polish | Dead code removal, full test |
