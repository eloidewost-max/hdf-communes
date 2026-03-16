# Mode Municipales 2026 — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a 5th "Municipales 2026" mode to the interactive map with a 2020↔2026 animated toggle, glow effect on political shift communes, hatched T2 communes, and marketing-focused filters.

**Architecture:** Single-file frontend (index.html ~2916 lines) + new Python script (`process_municipales2026.py`) producing `municipales2026.json`. New mode follows identical patterns to existing modes (politique as primary template). Data already available in `resultats_municipales_2026_t1.csv`.

**Tech Stack:** Vanilla JS (ES5), Leaflet.js, Python 3 + pandas, CSS transitions on SVG paths.

**Spec:** `docs/superpowers/specs/2026-03-16-municipales-2026-mode-design.md`

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `process_municipales2026.py` | Create | Read CSV, produce `municipales2026.json` with compact keys |
| `municipales2026.json` | Generated | ~1.5 MB, indexed by INSEE code, both 2020 and 2026 data |
| `index.html` | Modify | New mode button, global state, style function, cmd panel, detail section, bottom bar, URL state, CSS |

---

## Chunk 1: Data Pipeline

### Task 1: Create process_municipales2026.py

**Files:**
- Create: `process_municipales2026.py`
- Input: `resultats_municipales_2026_t1.csv` (already exists)
- Output: `municipales2026.json`

- [ ] **Step 1: Write the script**

```python
#!/usr/bin/env python3
"""Convert resultats_municipales_2026_t1.csv to municipales2026.json (compact, INSEE-keyed)."""

import csv, json, sys

BLOC_COLORS = {
    "Extrême gauche": "#B71C1C",
    "Gauche": "#E2001A",
    "Centre": "#FFB300",
    "Droite": "#0056A6",
    "Extrême droite": "#0D1B4A",
    "Divers": "#9E9E9E",
    "Sans étiquette": "#666666",
}

def main():
    out = {}
    with open("resultats_municipales_2026_t1.csv", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row["code_insee"]
            if not code:
                continue

            def num(key):
                v = row.get(key, "")
                if v == "" or v == "nan":
                    return None
                try:
                    return round(float(v), 1)
                except ValueError:
                    return None

            st_raw = row.get("statut_t1", "")
            st = "T1" if st_raw == "ELU_T1" else ("T2" if st_raw == "SECOND_TOUR" else "")

            nm_raw = row.get("nouveau_maire", "")
            nm = 1 if nm_raw == "OUI" else (0 if nm_raw == "NON" else -1)

            cb_raw = row.get("changement_bord", "")
            cb = 1 if cb_raw == "OUI" else (0 if cb_raw == "NON" else -1)

            b20 = row.get("bloc_2020", "Sans étiquette") or "Sans étiquette"
            b26 = row.get("bloc_2026", "Sans étiquette") or "Sans étiquette"

            entry = {
                "ms": row.get("maire_sortant", "") or "",
                "n20": row.get("nuance_2020", "") or "",
                "b20": b20,
                "vt1": row.get("vainqueur_t1", "") or "",
                "lt1": row.get("liste_vainqueur", "") or "",
                "n26": row.get("nuance_2026", "") or "",
                "b26": b26,
                "sc": num("score_t1_pct"),
                "st": st,
                "pa": num("participation_pct"),
                "s2": row.get("second_t1", "") or "",
                "sc2": num("score_second_pct"),
                "nm": nm,
                "cb": cb,
                "sb": row.get("sens_bascule", "") or "",
                "cl20": BLOC_COLORS.get(b20, "#666666"),
                "cl26": BLOC_COLORS.get(b26, "#666666"),
            }

            # Strip empty string values to save space
            entry = {k: v for k, v in entry.items() if v is not None and v != ""}
            # Always keep st, nm, cb even if falsy
            if "st" not in entry:
                entry["st"] = st
            if "nm" not in entry:
                entry["nm"] = nm
            if "cb" not in entry:
                entry["cb"] = cb
            entry["cl20"] = BLOC_COLORS.get(b20, "#666666")
            entry["cl26"] = BLOC_COLORS.get(b26, "#666666")

            out[code] = entry

    with open("municipales2026.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))

    size_kb = len(json.dumps(out, ensure_ascii=False, separators=(",", ":"))) / 1024
    print(f"municipales2026.json: {len(out)} communes, {size_kb:.0f} KB")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run it and verify output**

Run: `python3 process_municipales2026.py`
Expected: `municipales2026.json: 34870 communes, ~XXXX KB`

Verify a sample:
```bash
python3 -c "import json; d=json.load(open('municipales2026.json')); print(json.dumps(d.get('69123',{}), indent=2, ensure_ascii=False))"
```

- [ ] **Step 3: Commit**

```bash
git add process_municipales2026.py municipales2026.json
git commit -m "feat: add process_municipales2026.py and generate municipales2026.json"
```

---

## Chunk 2: index.html — Foundations (state, data loading, style constants, CSS)

### Task 2: Add global state variables

**Files:**
- Modify: `index.html:340` (after `var currentMode = 'prospection';`)

- [ ] **Step 1: Add state variables after line 340**

Find `var currentMode = 'prospection';` and add after it:

```javascript
var mun2026 = null;
var mun2026Year = '2026';
var mun2026Filter = null;      // null | 'bascules' | 'nouveaux' | 't2'
var mun2026BlocFilter = null;  // null | 'Gauche' | 'Droite' | etc.
```

- [ ] **Step 2: Commit**

```bash
git add index.html
git commit -m "feat(mun2026): add global state variables"
```

### Task 3: Add data loading

**Files:**
- Modify: `index.html:266-288` (fetch block)

- [ ] **Step 1: Add municipales2026.json to the fetch array**

Add before the `results = await Promise.all(...)` line:

```javascript
var mun2026P = fetchJSON('municipales2026.json').catch(function(e) { console.warn('municipales2026.json non disponible :', e.message); return {}; });
```

Add `mun2026P` to the Promise.all array as 8th element.

After `var insights = results[6];` (line 288), add:

```javascript
mun2026 = results[7];
```

- [ ] **Step 2: Commit**

```bash
git add index.html
git commit -m "feat(mun2026): load municipales2026.json on startup"
```

### Task 4: Add style constants and CSS

**Files:**
- Modify: `index.html:302` (after existing STYLE_ constants)
- Modify: `index.html` CSS section

- [ ] **Step 1: Add CSS for glow effect and SVG transitions**

In the `<style>` section, add:

```css
.bascule-glow { filter: drop-shadow(0 0 6px rgba(255,255,255,0.8)) drop-shadow(0 0 2px rgba(255,255,255,0.6)); }
.mun2026-transition .leaflet-overlay-pane svg path { transition: fill 300ms ease, fill-opacity 300ms ease, stroke 300ms ease; }
```

- [ ] **Step 2: Add MODE_COLORS entry**

Find `var MODE_COLORS = {` (line 1399) and add `municipales2026: '#8E24AA'` to the object.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat(mun2026): add CSS transitions, glow class, and mode color"
```

---

## Chunk 3: index.html — Mode button, getStyle, switchMode

### Task 5: Add mode button

**Files:**
- Modify: `index.html:202` (after securite button)

- [ ] **Step 1: Add the button**

After `<button class="mode-btn" data-mode="securite">Securite</button>` (line 202), add:

```html
<button class="mode-btn" data-mode="municipales2026">Municipales 2026</button>
```

- [ ] **Step 2: Commit**

```bash
git add index.html
git commit -m "feat(mun2026): add mode button in top bar"
```

### Task 6: Add getStyleMunicipales2026 function

**Files:**
- Modify: `index.html` — insert before `function getStyle(feature)` (line 697)

- [ ] **Step 1: Write the style function**

Insert before `function getStyle(feature) {`:

```javascript
// Style function -- municipales 2026 mode
function getStyleMunicipales2026(feature) {
  var code = feature.properties.c;
  var d = mun2026 ? mun2026[code] : null;
  if (!d) return STYLE_NO_DATA;

  // Bloc filter
  var bloc = mun2026Year === '2020' ? (d.b20 || 'Sans étiquette') : (d.b26 || 'Sans étiquette');
  if (mun2026BlocFilter && bloc !== mun2026BlocFilter) return STYLE_FILTERED;

  // Special filters (bascules / nouveaux / t2)
  if (mun2026Filter === 'bascules' && d.cb !== 1) return STYLE_FILTERED;
  if (mun2026Filter === 'nouveaux' && d.nm !== 1) return STYLE_FILTERED;
  if (mun2026Filter === 't2' && d.st !== 'T2') return STYLE_FILTERED;

  var fillColor = mun2026Year === '2020' ? (d.cl20 || '#666') : (d.cl26 || '#666');

  // T2 communes in 2026 view: hatched
  if (d.st === 'T2' && mun2026Year === '2026') {
    return { fillColor: fillColor, fillOpacity: 0.6, weight: 0.5, color: '#888', opacity: 0.6, dashArray: '4 4' };
  }

  // Bascule communes in 2026 view: thick white border (glow added via CSS class post-restyle)
  if (d.cb === 1 && mun2026Year === '2026') {
    return { fillColor: fillColor, fillOpacity: 0.85, weight: 2.5, color: '#FFFFFF', opacity: 0.9, dashArray: null };
  }

  // Normal commune
  return { fillColor: fillColor, fillOpacity: 0.75, weight: 0.3, color: '#555', opacity: 0.5, dashArray: null };
}
```

- [ ] **Step 2: Update getStyle dispatcher**

In `function getStyle(feature)` (line 697), add before the final `return getStylePolitique(feature);`:

```javascript
if (currentMode === 'municipales2026') return getStyleMunicipales2026(feature);
```

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat(mun2026): add getStyleMunicipales2026 and update dispatcher"
```

### Task 7: Update switchMode

**Files:**
- Modify: `index.html:1410-1444` (switchMode function)

- [ ] **Step 1: Add municipales2026 handling**

After the `if (mode === 'securite') { ... }` block (line 1427), add:

```javascript
if (mode === 'municipales2026') {
  mun2026Filter = null;
  mun2026BlocFilter = null;
  mun2026Year = '2026';
}
```

In the render dispatch block (lines 1429-1432), add:

```javascript
else if (mode === 'municipales2026') renderCmdMunicipales2026();
```

- [ ] **Step 2: Commit**

```bash
git add index.html
git commit -m "feat(mun2026): update switchMode for new mode"
```

---

## Chunk 4: index.html — Glow effect helper

### Task 8: Add applyBasculeGlow helper function

**Files:**
- Modify: `index.html` — insert after getStyleMunicipales2026

- [ ] **Step 1: Write the glow helper**

Insert after `getStyleMunicipales2026`:

```javascript
// Apply/remove bascule glow CSS class on shift communes
function applyBasculeGlow() {
  if (!mun2026) return;
  var isGlow = (currentMode === 'municipales2026' && mun2026Year === '2026');
  for (var code in layerByCode) {
    var layer = layerByCode[code];
    if (!layer._path) continue;
    var d = mun2026[code];
    if (d && d.cb === 1 && isGlow) {
      // Respect active filters
      if (mun2026BlocFilter) {
        var bloc = d.b26 || 'Sans étiquette';
        if (bloc !== mun2026BlocFilter) { layer._path.classList.remove('bascule-glow'); continue; }
      }
      if (mun2026Filter && mun2026Filter !== 'bascules') {
        if (mun2026Filter === 'nouveaux' && d.nm !== 1) { layer._path.classList.remove('bascule-glow'); continue; }
        if (mun2026Filter === 't2' && d.st !== 'T2') { layer._path.classList.remove('bascule-glow'); continue; }
      }
      layer._path.classList.add('bascule-glow');
    } else {
      layer._path.classList.remove('bascule-glow');
    }
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add index.html
git commit -m "feat(mun2026): add applyBasculeGlow helper"
```

---

## Chunk 5: index.html — renderCmdMunicipales2026

### Task 9: Write the command panel renderer

**Files:**
- Modify: `index.html` — insert before `function updateBottomBar()` (line 2643)

- [ ] **Step 1: Write renderCmdMunicipales2026**

Insert before `function updateBottomBar()`. This function builds the left sidebar with:
1. Year toggle (2020/2026) with animated thumb
2. Bloc filter pills
3. Special filter checkboxes (mutually exclusive)
4. Dynamic legend with counts
5. Source note

Key implementation details:

**Toggle:** Two labels + a track/thumb div. `doToggle()` flips `mun2026Year`, adds `.mun2026-transition` to `#map` for CSS transitions, calls `geoLayer.setStyle(getStyle)`, then after 150ms applies glow via `applyBasculeGlow()`, and after 350ms removes the transition class.

**Pills:** Array of `MUN_BLOCS` objects `[{key, label, color}]`. Active pill gets its color as background. Click sets `mun2026BlocFilter`, restyles, re-renders cmd panel.

**Checkboxes:** Mutually exclusive via `mun2026Filter` variable. Checking one sets the filter to that key; unchecking sets it to null. On change: restyle + applyBasculeGlow + re-render.

**Legend:** Separate `renderMun2026Legend()` function counts communes per bloc (respecting year toggle and active filters), renders colored swatches with counts, plus notes explaining hatching and glow symbols. Uses a container div with `id='mun2026-legend'` so it can be re-rendered independently.

**Source note:** Static div at the bottom: "Source : Ministere de l'Interieur / MAJ : 16/03/2026 (T1)". Use `textContent` for all text, DOM creation for all elements (no innerHTML).

See the spec `docs/superpowers/specs/2026-03-16-municipales-2026-mode-design.md` section "Panneau de commande" for the exact layout wireframe.

**BLOC_COLORS_JS map** (needed in legend):
```javascript
var BLOC_COLORS_JS = {
  'Extrême gauche': '#B71C1C', 'Gauche': '#E2001A', 'Centre': '#FFB300',
  'Droite': '#0056A6', 'Extrême droite': '#0D1B4A', 'Divers': '#9E9E9E', 'Sans étiquette': '#666'
};
```

**Legend notes for symbols:** Create spans styled as small squares: one with `border: 1px dashed #888` for T2 hatching, one with `border: 2px solid #fff; box-shadow: 0 0 4px rgba(255,255,255,0.6)` for bascule glow. Append text nodes next to them.

- [ ] **Step 2: Commit**

```bash
git add index.html
git commit -m "feat(mun2026): add renderCmdMunicipales2026 with toggle, pills, filters, legend"
```

---

## Chunk 6: index.html — Bottom bar, URL state, detail panel

### Task 10: Update updateBottomBar

**Files:**
- Modify: `index.html:2643-2709` (updateBottomBar function)

- [ ] **Step 1: Add municipales2026 block**

Before the final `else {` block (surveillance, line 2694), insert:

```javascript
} else if (currentMode === 'municipales2026') {
  var munBascules = 0, munNouveaux = 0, munT2 = 0, munTotal = 0, munPartSum = 0, munPartCount = 0;
  for (var code in mun2026) {
    var md = mun2026[code];
    if (mun2026BlocFilter) {
      var mBloc = mun2026Year === '2020' ? (md.b20 || 'Sans étiquette') : (md.b26 || 'Sans étiquette');
      if (mBloc !== mun2026BlocFilter) continue;
    }
    munTotal++;
    if (md.cb === 1) munBascules++;
    if (md.nm === 1) munNouveaux++;
    if (md.st === 'T2') munT2++;
    if (md.pa) { munPartSum += md.pa; munPartCount++; }
  }
  var munAvgPart = munPartCount > 0 ? (munPartSum / munPartCount).toFixed(1) : '0';
  el.textContent = munBascules + ' bascules | ' + munNouveaux.toLocaleString('fr') + ' nouveaux maires | ' + munT2.toLocaleString('fr') + ' en attente T2 | Participation moy. : ' + munAvgPart + '%';
```

- [ ] **Step 2: Commit**

```bash
git add index.html
git commit -m "feat(mun2026): add bottom bar stats for municipales mode"
```

### Task 11: Update URL state management

**Files:**
- Modify: `index.html:374-401` (updateURL, updateURLWithCommune, readURLState)

- [ ] **Step 1: Update updateURL**

In `updateURL()`, after `if (activeFilter) params.set('filter', activeFilter);` add:

```javascript
if (currentMode === 'municipales2026') {
  if (mun2026Year === '2020') params.set('year', '2020');
  if (mun2026Filter) params.set('filter', mun2026Filter);
  if (mun2026BlocFilter) params.set('bloc', mun2026BlocFilter);
}
```

- [ ] **Step 2: Update readURLState**

In `readURLState()`, add to the returned object:

```javascript
year: params.get('year') || null,
bloc: params.get('bloc') || null
```

- [ ] **Step 3: Update URL restoration on page load**

After the existing URL restoration block (lines 2892-2907), add:

```javascript
if (urlState.mode === 'municipales2026') {
  if (urlState.year === '2020') mun2026Year = '2020';
  if (urlState.filter) mun2026Filter = urlState.filter;
  if (urlState.bloc) mun2026BlocFilter = urlState.bloc;
  renderCmdMunicipales2026();
  geoLayer.setStyle(getStyle);
  applyBasculeGlow();
}
```

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat(mun2026): add URL deep linking for year/filter/bloc"
```

### Task 12: Add detail panel section for Municipales 2026

**Files:**
- Modify: `index.html:806-1360` (openDetail function)

- [ ] **Step 1: Add mun2026 section in openDetail**

At the end of `openDetail()`, before the closing `}`, add a new section. Build entirely with DOM methods (createElement, textContent, appendChild — no innerHTML). Structure:

1. **Section wrapper** — `div` with top border, padding, margin
2. **Title** — "MUNICIPALES 2026" in purple (#8E24AA), uppercase, small
3. **Maire sortant block** — label "Maire sortant (2020)", name + nuance, bloc badge with `cl20` color
4. **Resultat T1 block** — background panel with:
   - Winner: triangle marker + name + score%
   - Liste name (indented)
   - Bloc badge with `cl26` color + nuance code
   - T2 badge if `st === 'T2'` (dashed border)
   - Second place: hollow triangle + name + score%
   - Marge: computed `sc - sc2` pts
5. **Participation** — simple text line
6. **Status badges row** — flex container:
   - If `cb === 1`: purple badge with bascule direction (sb)
   - If `cb === 0`: grey "Meme bord politique" badge
   - If `nm === 1`: yellow "Nouveau maire" badge
   - If `nm === 0`: grey "Sortant reconduit" badge

Use `detailContent` variable (already defined in openDetail) for `appendChild`.

See spec section "Panneau de detail" for exact wireframe.

- [ ] **Step 2: Commit**

```bash
git add index.html
git commit -m "feat(mun2026): add municipales section in detail panel"
```

---

## Chunk 7: Final integration and cleanup

### Task 13: Clean up glow on mode switch

**Files:**
- Modify: `index.html` switchMode function

- [ ] **Step 1: Remove glow classes when leaving mun2026 mode**

At the top of `switchMode()`, after `activeFilter = null;`, add:

```javascript
// Remove bascule glow when leaving municipales mode
if (currentMode === 'municipales2026') {
  document.getElementById('map').classList.remove('mun2026-transition');
  var glows = document.querySelectorAll('.bascule-glow');
  for (var g = 0; g < glows.length; g++) glows[g].classList.remove('bascule-glow');
}
```

- [ ] **Step 2: Apply glow when entering mun2026 mode**

At the end of `switchMode()`, after `updateURL();`, add:

```javascript
if (mode === 'municipales2026') {
  setTimeout(applyBasculeGlow, 50);
}
```

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat(mun2026): clean up glow on mode switch"
```

### Task 14: Test the full flow manually

- [ ] **Step 1: Generate data**

```bash
python3 process_municipales2026.py
```

- [ ] **Step 2: Open index.html in browser and verify all features**

Checklist:
- [ ] 5th button "Municipales 2026" appears in top bar
- [ ] Clicking it shows the command panel with toggle, pills, filters, legend
- [ ] Map colors communes by 2026 bloc
- [ ] Toggle to 2020 animates color transition (300ms fade)
- [ ] Toggle back to 2026 shows glow on bascule communes (~610)
- [ ] T2 communes show hatched pattern in 2026 view
- [ ] Bloc filter pills work (greying out non-matching communes)
- [ ] "Bascules uniquement" checkbox highlights only shift communes
- [ ] "Nouveaux maires" checkbox highlights new mayors
- [ ] "Second tour" checkbox highlights T2 communes
- [ ] Clicking a commune opens detail panel with Municipales 2026 section
- [ ] Bottom bar shows correct stats
- [ ] URL updates with mode/year/filter params
- [ ] Refreshing page restores state from URL
- [ ] Switching away from mun2026 mode removes all glow classes
- [ ] Other modes still work correctly

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "feat: complete Municipales 2026 mode with toggle, glow, filters"
```
