# UI/UX Refonte Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform the carte-politique UI from white glassmorphism panels to a cohesive dark glassmorphism theme with micro-animations, integrated mode toggle, and collapsible stats panel.

**Architecture:** Single-file `index.html` refonte. CSS changes first (dark palette, custom controls), then HTML restructuring (merge mode-toggle into title-bar, add collapse button to stats), then JS animation logic (cascade load, mode transitions, panel collapse, scroll indicators).

**Tech Stack:** Vanilla CSS + JS in `index.html`, Leaflet.js, no build system. Published on GitHub Pages.

---

### Task 1: Dark palette — CSS foundation

**Files:**
- Modify: `index.html` (CSS section, lines 8–148)

**Step 1: Replace the glassmorphism shared selector**

Change the shared card base from white to dark:

```css
/* --- Glassmorphism card base --- */
#legend, #info, #title-bar, #stats-panel, #surv-filters {
  background: rgba(15,15,30,0.82); backdrop-filter: blur(16px);
  border-radius: 10px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.08);
  transition: opacity 0.3s ease, transform 0.3s ease;
  color: #e0e0e0;
}
```

**Step 2: Update all text colors to light**

Apply these changes across all CSS rules in the `<style>` block:

- `#legend h3` → `color: #e0e0e0`
- `.legend-label` → `color: #ccc` (was `#444`)
- `.legend-count` → `color: #777` (was `#999`)
- `.legend-item:hover` → `background: rgba(255,255,255,0.06)` (was `rgba(0,0,0,0.05)`)
- `#info h3` → `color: #fff`
- `#info .detail strong` → `color: #999`
- `#title-bar h1` → `color: #fff`
- `#title-bar p` → `color: #999` (was `#888`)
- `#stats-panel h3` → `color: #e0e0e0`
- `#stats-panel th` → `color: #999` (was `#666`)
- `#stats-panel td` → border-bottom `rgba(255,255,255,0.06)` (was `#eee`)
- `#stats-panel th` → border-bottom same
- `#stats-panel tr.clickable:hover` → `background: rgba(255,255,255,0.04)`
- `#stats-panel .stats-note` → `color: #888`
- `#stats-panel .stats-summary` → `background: rgba(255,255,255,0.04)`
- `#surv-filters` → `color: #ccc`
- `.data-year` → `color: #777`

**Step 3: Update filter buttons to dark theme**

```css
.filter-btn {
  padding: 6px 14px; border-radius: 20px; border: 1.5px solid rgba(255,255,255,0.12);
  background: rgba(15,15,30,0.7); backdrop-filter: blur(8px);
  cursor: pointer; font-size: 12px; font-weight: 500;
  transition: all 0.2s; color: #ccc;
}
.filter-btn:hover { border-color: rgba(255,255,255,0.3); color: #fff; }
.filter-btn.active {
  border-color: #4a90d9; background: #4a90d9; color: white;
  box-shadow: 0 2px 12px rgba(74,144,217,0.3);
}
```

**Step 4: Update loading screen to dark**

```css
#loading {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%);
  z-index: 2000; background: rgba(15,15,30,0.95); padding: 30px 40px;
  border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5);
  text-align: center; font-size: 16px; color: #e0e0e0;
}
#loading .spinner {
  width: 40px; height: 40px; border: 4px solid rgba(255,255,255,0.1);
  border-top-color: #4a90d9; border-radius: 50%;
  animation: spin 0.8s linear infinite; margin: 0 auto 15px;
}
```

**Step 5: Add custom scrollbar for stats panel**

```css
#stats-panel::-webkit-scrollbar { width: 6px; }
#stats-panel::-webkit-scrollbar-track { background: rgba(255,255,255,0.05); border-radius: 3px; }
#stats-panel::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 3px; }
#stats-panel::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.25); }
```

**Step 6: Add custom slider styling**

```css
input[type="range"] {
  -webkit-appearance: none; appearance: none;
  height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; outline: none;
}
input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none; appearance: none;
  width: 14px; height: 14px; border-radius: 50%;
  background: #4ecdc4; cursor: pointer;
  box-shadow: 0 0 6px rgba(78,205,196,0.4);
}
input[type="range"]::-moz-range-thumb {
  width: 14px; height: 14px; border-radius: 50%; border: none;
  background: #4ecdc4; cursor: pointer;
  box-shadow: 0 0 6px rgba(78,205,196,0.4);
}
```

**Step 7: Update inline styles in HTML to match dark theme**

In the HTML body, update:
- `#legend-surv` border-top: `rgba(255,255,255,0.08)` (was `#ddd`)
- `#legend-surv h3` color: add `color:#ccc`
- SVG legend strokes: `stroke="#aaa"` (was `#888`)
- Videoprotection swatch border: `border:3px solid rgba(255,255,255,0.7)`
- Legend note text: `color:#777` (was `#999`)
- `#info-surv-row` border-top: `rgba(255,255,255,0.08)` (was `#eee`)
- `#info-prosp-row` same
- `#load-status` color: `#888` (was `#666`)

**Step 8: Update JS-generated inline styles in `renderProspStats()`**

Search for all `style.cssText` assignments in the JS and update colors:
- Intro div background: `rgba(78,205,196,0.08)`, border-left: `#4ecdc4`, text color: `#ccc`
- Section titles: `color:#999`
- Signal descriptions: `color:#888` → `color:#777`
- Detail expanded bg: `rgba(255,255,255,0.04)`, text `#aaa`
- Toggle link: keep `#3498db` → change to `#4ecdc4`
- Filters section bg: `rgba(255,255,255,0.04)`
- Filters title: `color:#999`

Also in `updateProspSummary()`:
- Famille swatch: keep colors as-is (they're political colors)
- Summary text: will inherit `color: #e0e0e0` from parent

Also in `showInfo()` for prospection decomposition bars:
- Bar background: `rgba(255,255,255,0.1)` (was `#eee`)
- Decomposition title: `color:#888`
- Label: `color:#aaa` (was `#666`)
- Contrib value: `color:#ccc` (was `#444`)

Also in `renderStats()` (surveillance mode):
- Any inline style overrides need dark-safe colors

**Step 9: Verify in browser and commit**

Open `index.html` in browser. All panels should have dark backgrounds, light text, no white/light remnants.

```bash
git add index.html
git commit -m "style: dark glassmorphism palette for all UI panels"
```

---

### Task 2: Merge mode toggle into title-bar

**Files:**
- Modify: `index.html` (HTML lines 158–167, CSS lines 81–99, JS lines 770–776)

**Step 1: Restructure HTML**

Replace the separate `#title-bar` and `#mode-toggle` divs with a single merged element:

```html
<div id="title-bar">
  <h1>Carte politique des maires de France</h1>
  <p id="subtitle">Nuance politique du maire — Municipales 2020</p>
  <div id="mode-tabs">
    <button class="mode-btn active" data-mode="politique">Politique</button>
    <button class="mode-btn" data-mode="surveillance">Surveillance</button>
    <button class="mode-btn" data-mode="prospection">Prospection</button>
    <div id="mode-indicator"></div>
  </div>
</div>
```

Delete the old `<div id="mode-toggle">` block entirely.

**Step 2: Update CSS**

Remove the old `#mode-toggle` and `.mode-btn` rules (lines 81–99). Replace with:

```css
#mode-tabs {
  display: flex; justify-content: center; gap: 0;
  margin-top: 8px; position: relative;
}
.mode-btn {
  padding: 6px 18px; border: none; cursor: pointer;
  font-size: 12px; font-weight: 600;
  background: transparent; color: rgba(255,255,255,0.5);
  transition: color 0.2s;
}
.mode-btn:hover { color: rgba(255,255,255,0.85); }
.mode-btn.active { color: #fff; }
#mode-indicator {
  position: absolute; bottom: 0; height: 2px;
  background: #4a90d9; border-radius: 1px;
  transition: left 0.3s ease, width 0.3s ease, background 0.3s ease;
}
```

**Step 3: Update JS — sliding indicator**

After the mode toggle click handler setup, add indicator positioning logic:

```javascript
var modeIndicator = document.getElementById('mode-indicator');
var MODE_COLORS = { politique: '#4a90d9', surveillance: '#e8913a', prospection: '#4ecdc4' };

function updateModeIndicator() {
  var activeBtn = document.querySelector('.mode-btn.active');
  if (!activeBtn || !modeIndicator) return;
  modeIndicator.style.left = activeBtn.offsetLeft + 'px';
  modeIndicator.style.width = activeBtn.offsetWidth + 'px';
  modeIndicator.style.background = MODE_COLORS[activeBtn.getAttribute('data-mode')] || '#4a90d9';
}
```

Call `updateModeIndicator()` at the end of `switchMode()` and once after initial setup.

Remove the old `data-mode`-based `border-bottom-color` CSS rules.

**Step 4: Verify and commit**

The title bar should show title + subtitle + tab buttons with a colored sliding underline.

```bash
git add index.html
git commit -m "feat: merge mode toggle into title-bar with sliding indicator"
```

---

### Task 3: Collapsible stats panel

**Files:**
- Modify: `index.html` (HTML lines 233–238, CSS, JS)

**Step 1: Add collapse button and tab to HTML**

Update the stats panel HTML:

```html
<div id="stats-panel">
  <div id="stats-header">
    <h3>Surveillance par famille politique</h3>
    <button id="stats-collapse" title="Replier">&rsaquo;</button>
  </div>
  <div id="stats-body">
    <div id="stats-table"></div>
    <div id="stats-summary" class="stats-summary"></div>
    <div class="stats-note" id="stats-note"></div>
  </div>
  <div id="stats-scroll-fade"></div>
</div>
<div id="stats-tab" style="display:none;">
  <span id="stats-tab-icon">&#9776;</span>
  <span id="stats-tab-badge"></span>
</div>
```

**Step 2: Add CSS for collapse**

```css
#stats-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 12px;
}
#stats-collapse {
  background: none; border: none; color: #999; font-size: 20px;
  cursor: pointer; padding: 2px 6px; border-radius: 4px;
  transition: all 0.2s;
}
#stats-collapse:hover { color: #fff; background: rgba(255,255,255,0.08); }

#stats-panel.collapsed { transform: translateX(calc(100% + 20px)); }

#stats-tab {
  position: absolute; top: 10px; right: 0; z-index: 1000;
  background: rgba(15,15,30,0.82); backdrop-filter: blur(16px);
  border-radius: 10px 0 0 10px; padding: 10px 12px;
  cursor: pointer; color: #e0e0e0; font-size: 14px;
  box-shadow: -4px 0 16px rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.08); border-right: none;
  transition: all 0.2s;
}
#stats-tab:hover { background: rgba(25,25,50,0.9); }
#stats-tab-badge {
  display: inline-block; background: #4ecdc4; color: #000;
  font-size: 10px; font-weight: 700; padding: 1px 6px;
  border-radius: 10px; margin-left: 6px;
}

#stats-scroll-fade {
  position: sticky; bottom: 0; left: 0; right: 0; height: 24px;
  background: linear-gradient(transparent, rgba(15,15,30,0.82));
  pointer-events: none; margin-top: -24px;
}
```

**Step 3: Add JS collapse/expand logic**

```javascript
var statsPanel = document.getElementById('stats-panel');
var statsTab = document.getElementById('stats-tab');
var statsCollapse = document.getElementById('stats-collapse');
var statsBadge = document.getElementById('stats-tab-badge');
var statsPanelCollapsed = false;

statsCollapse.addEventListener('click', function() {
  statsPanelCollapsed = true;
  statsPanel.style.display = 'none';
  statsTab.style.display = 'block';
});

statsTab.addEventListener('click', function() {
  statsPanelCollapsed = false;
  statsTab.style.display = 'none';
  statsPanel.style.display = 'block';
});
```

Update `switchMode()` to respect collapsed state: when showing stats panel, check `statsPanelCollapsed` — if true, show the tab instead.

Update `updateProspSummary()` and `renderStats()` to set `statsBadge.textContent` with the count.

**Step 4: Verify and commit**

The stats panel should have a `›` button that hides it and shows a small tab on the right edge. Clicking the tab brings it back.

```bash
git add index.html
git commit -m "feat: collapsible stats panel with tab indicator"
```

---

### Task 4: Micro-animations — mode transitions

**Files:**
- Modify: `index.html` (CSS + JS)

**Step 1: Add animation CSS classes**

```css
.panel-enter {
  animation: panelSlideIn 0.25s ease-out both;
}
.panel-exit {
  animation: panelSlideOut 0.2s ease-in both;
}
@keyframes panelSlideIn {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes panelSlideOut {
  from { opacity: 1; transform: translateY(0); }
  to { opacity: 0; transform: translateY(8px); }
}
```

**Step 2: Update `switchMode()` to animate panel transitions**

Instead of directly toggling `display`, animate panels out before hiding and animate in after showing. Use a helper:

```javascript
function animatePanel(el, show) {
  if (show) {
    el.style.display = el.id === 'filter-bar' ? 'flex' : 'block';
    el.classList.remove('panel-exit');
    el.classList.add('panel-enter');
  } else if (el.style.display !== 'none') {
    el.classList.remove('panel-enter');
    el.classList.add('panel-exit');
    el.addEventListener('animationend', function handler() {
      el.style.display = 'none';
      el.classList.remove('panel-exit');
      el.removeEventListener('animationend', handler);
    });
  }
}
```

Replace the direct `style.display` assignments in `switchMode()` with `animatePanel()` calls.

**Step 3: Add info panel scale-in animation**

```css
#info {
  /* add to existing */
  transform-origin: top left;
}
#info.tooltip-enter {
  animation: tooltipIn 0.15s ease-out both;
}
@keyframes tooltipIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
```

In `showInfo()`, add `infoPanel.classList.add('tooltip-enter')`. On mouseout, remove the class.

**Step 4: Verify and commit**

Switching modes should show smooth panel transitions. Hovering communes should show tooltip with subtle scale-in.

```bash
git add index.html
git commit -m "feat: micro-animations for mode transitions and tooltip"
```

---

### Task 5: Cascade loading animation

**Files:**
- Modify: `index.html` (CSS + JS)

**Step 1: Add cascade animation CSS**

```css
.cascade-in {
  opacity: 0;
  transform: translateY(-12px);
}
.cascade-in.visible {
  animation: cascadeSlideIn 0.4s ease-out both;
}
@keyframes cascadeSlideIn {
  from { opacity: 0; transform: translateY(-12px); }
  to { opacity: 1; transform: translateY(0); }
}
```

**Step 2: Set initial hidden state on panels**

After the loading spinner is hidden (at the end of the main async function), add cascade reveal:

```javascript
// Hide loading
document.getElementById('loading').style.display = 'none';

// Cascade reveal panels
var cascadePanels = ['title-bar', 'legend', 'filter-bar'];
cascadePanels.forEach(function(id, i) {
  var el = document.getElementById(id);
  el.classList.add('cascade-in');
  setTimeout(function() {
    el.classList.add('visible');
  }, i * 120);
});
```

**Step 3: Verify and commit**

On page load, after the spinner, panels should appear one by one with a slide-down + fade effect.

```bash
git add index.html
git commit -m "feat: cascade loading animation for panels"
```

---

### Task 6: Legend hover glow & typography polish

**Files:**
- Modify: `index.html` (CSS)

**Step 1: Update legend swatches**

```css
.legend-swatch {
  width: 18px; height: 18px; border-radius: 4px;
  margin-right: 10px; flex-shrink: 0; border: 1px solid rgba(255,255,255,0.15);
  transition: box-shadow 0.2s;
}
.legend-item:hover .legend-swatch {
  box-shadow: 0 0 8px currentColor;
}
```

**Step 2: Increase base typography**

```css
#legend { font-size: 14px; padding: 16px 20px; }
#legend h3 { font-size: 14px; }
.legend-label { font-size: 13px; }
.legend-count { font-size: 11px; }
#info { font-size: 14px; padding: 16px 20px; }
#info h3 { font-size: 16px; }
```

**Step 3: Update surv-filters font size**

```css
#surv-filters { font-size: 13px; padding: 12px 20px; }
```

**Step 4: Verify and commit**

Legend items should glow on hover, all text should be more readable.

```bash
git add index.html
git commit -m "style: legend hover glow and typography improvements"
```

---

### Task 7: Responsive dark theme updates

**Files:**
- Modify: `index.html` (CSS responsive section)

**Step 1: Update mobile breakpoint**

```css
@media (max-width: 768px) {
  #stats-panel {
    top: auto; bottom: 0; right: 0; left: 0; width: 100%;
    max-height: 40vh; border-radius: 10px 10px 0 0;
  }
  #stats-tab { top: auto; bottom: 0; right: 0; border-radius: 10px 10px 0 0; }
  #filter-bar { max-width: 95vw; }
  #filter-bar { overflow-x: auto; flex-wrap: nowrap; -webkit-overflow-scrolling: touch; }
  #surv-filters { flex-direction: column; align-items: flex-start; }
  #mode-tabs .mode-btn { padding: 6px 12px; font-size: 11px; }
  #legend { max-width: 200px; font-size: 12px; }
}
```

**Step 2: Verify and commit**

```bash
git add index.html
git commit -m "style: responsive layout updates for dark theme"
```

---

### Task 8: Final polish and cleanup

**Files:**
- Modify: `index.html`

**Step 1: Remove dead CSS**

- Remove `.surv-mode` and `.prosp-mode` overrides if now empty
- Remove any leftover white-theme colors

**Step 2: Update checkbox styling for dark theme**

```css
input[type="checkbox"] {
  accent-color: #4ecdc4;
}
```

**Step 3: Update the prospection score bars in `showInfo()` to dark theme**

In the JS section where decomposition bars are built, ensure:
- Bar bg: `rgba(255,255,255,0.1)` not `#eee`
- Label color: `#aaa` not `#666`
- Contrib color: `#ccc` not `#444`
- Decomposition title: `#888`

**Step 4: Full browser test and commit**

Test all 3 modes (politique, surveillance, prospection). Test:
- Panel transitions animated
- Stats panel collapses and expands
- Tooltip follows cursor in all modes
- Sliders work in dark theme
- Legend glow works
- Loading cascade plays
- Mobile layout works

```bash
git add index.html
git commit -m "style: final polish, dead CSS cleanup, dark theme consistency"
git push
```
