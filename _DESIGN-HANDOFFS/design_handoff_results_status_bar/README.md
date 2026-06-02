# Handoff: Results Status Bar + Reset Filters

## Overview
A small **permanent status bar** for *Museokalenteri* (Helsingin seudun Museokalenteri) that sits
directly **above the exhibition list** (`#exhibitionList`). It does two things:

1. Always shows how many exhibitions are currently shown out of the total
   (e.g. `Näytetään 7 / 48 näyttelyä`).
2. Surfaces a **"Nollaa suodattimet"** (Reset filters) button — but **only when filters are active**.

This is a standalone addition. The surrounding page — header/logo, map, sidebar filters (time +
per-museum checkboxes + sort) and the exhibition cards themselves — is unchanged.

## About the Design Files
The file in this bundle (`results_status_bar_reference.html`) is a **design reference created in
HTML + CSS**. It is a static prototype showing the intended look and the three states — it is **not
production code to copy wholesale**.

The task is to **recreate this in the target codebase**. The existing app (`Museokalenteri.html`) is
a single static HTML page with a vanilla-JS render loop. The most faithful integration is to add the
markup + CSS below and hook the count/visibility logic into the existing `applyFilter()` function —
plain HTML + CSS + vanilla JS, no framework required. If the app is later migrated to a framework,
recreate the same structure and behavior there.

## Fidelity
**High-fidelity.** Final colors, typography, spacing, and behavior. All exact values are in
**Design Tokens** and **Components** below.

## Screens / Views

### Results status bar (single element above the list)
- **Name:** Results status bar (`#results-status-bar`)
- **Purpose:** Give the user constant feedback on how many results their current filters yield, and a
  one-click escape hatch back to the unfiltered view.
- **Layout:**
  - A horizontal **flex row**: `display: flex; align-items: center; justify-content: space-between;
    gap: 0.75rem; flex-wrap: wrap`.
  - **Left:** the count text (`#results-count`, a `<p>`).
  - **Right:** the reset button (`#reset-filters-btn`).
  - The bar is a white "section" card matching the site's existing `.section` styling (white bg,
    `1px` light border, `8px` radius, subtle shadow).
  - It sits **between the map section and `#exhibitionList`**, inside `.main-content`.
  - The bar is **always rendered** — it persists even when zero exhibitions match (the empty-state
    message renders *inside* `#exhibitionList`, separately, so it does not replace the bar).

## Components

### Bar container `#results-status-bar`
- `display: flex; align-items: center; justify-content: space-between; gap: 0.75rem; flex-wrap: wrap`
- `padding: 0.6rem 0.85rem`
- `margin: 0.25rem 0 0.5rem`
- `background: #ffffff`
- `border: 1px solid #e6e6e6`
- `border-radius: 8px`
- `box-shadow: 0 1px 2px rgba(0,0,0,0.03)`
- Gets an extra class **`filtered`** when any filter is active (this is what reveals the button).

### Count text `#results-count`
- `<p>`, `margin: 0; font-size: 0.9rem; color: #333333`
- The number is wrapped in `<strong>` (`color: #111`).
- Content (Finnish): `Näytetään <strong>{shown}</strong> / {total} näyttelyä`
  - `{shown}` = number of exhibitions currently rendered (after time + museum filters).
  - `{total}` = total number of exhibitions in the dataset (`exhibitions.length`), constant.

### Reset button `#reset-filters-btn`
- `<button type="button">`, label text: **`Nollaa suodattimet`**
- Default `display: none` — **hidden unless** the bar has the `filtered` class:
  `#results-status-bar.filtered #reset-filters-btn { display: inline-flex; }`
- `align-items: center; gap: 0.4rem`
- `padding: 0.4rem 0.8rem`
- `font-size: 0.82rem; font-weight: 500`
- `border: 1px solid #ccc; border-radius: 6px`
- `background: #fff; color: #333`
- `white-space: nowrap`
- `transition: background-color 0.15s ease, border-color 0.15s ease`
- Hover: `background: #f4f4f4; border-color: #b5b5b5`
- Active: `background: #ececec`

(The button styling intentionally matches the existing `#rajaukset-btn` / `#map-toggle-btn` outline
buttons on the page.)

## Interactions & Behavior

### "Filters active" definition
Filters are considered active (→ add `filtered` class, show button) when **either**:
- the active time filter is **not** `"ALL"` (i.e. user picked Käynnissä / Tulossa / Päättyneet /
  Avautuvat 2 vk / Päättyvät 2 vk), **or**
- **not all** museums are selected (`activeMuseums.size !== museumSet.length`).

Sort order is **not** a filter and does not toggle the button.

### Count update
- Recompute on **every** filter/museum/sort change — i.e. at the end of the existing `applyFilter()`.
- `{shown}` is the length of the already-filtered+sorted list that gets rendered (reuse it; do not
  recompute separately).

### Reset action
Clicking the button resets the **filters** (not sort):
- set active time filter back to `"ALL"`,
- re-check **all** museum checkboxes and set `activeMuseums` to the full set,
- refresh the map markers,
- re-run `applyFilter("ALL")` (which re-renders the list, updates per-filter counts, and updates this
  bar — hiding the button again because no filters are active).

### Empty state
When `{shown} === 0`, the bar still shows `Näytetään 0 / {total} näyttelyä` with the reset button
visible. The "no results" message (`Suodattimillasi ei löydy näyttelyitä.`) is rendered separately
inside `#exhibitionList`, below the bar.

## State Management
No new persistent state. Reads existing parent-list state:
- `activeStatus` (string) — current time filter.
- `activeMuseums` (Set) and `museumSet` (Array) — selected vs. all museums.
- `exhibitions` (Array) — full dataset; `exhibitions.length` is the total.
- the filtered+sorted list length — the shown count.

## Reference implementation (vanilla JS, current codebase)

**Markup** — add immediately before `<div id="exhibitionList"></div>` inside `.main-content`:
```html
<div id="results-status-bar">
  <p id="results-count" class="results-count"></p>
  <button id="reset-filters-btn" type="button">Nollaa suodattimet</button>
</div>
```

**Inside `initExhibitions()`** — grab refs alongside the other element lookups:
```js
const resultsBar     = document.getElementById("results-status-bar");
const resultsCount   = document.getElementById("results-count");
const resetFiltersBtn = document.getElementById("reset-filters-btn");
```

**Hook into `applyFilter()`** — after the list is rendered, pass the shown count:
```js
function applyFilter(statusType) {
  activeStatus = statusType;
  const filtered = getFilteredExhibitions(statusType);
  const sorted   = sortExhibitions(filtered);
  renderExhibitions(sorted);
  statusButtons.forEach(btn => btn.classList.remove("active"));
  document.querySelector(`[data-filter="${statusType}"]`).classList.add("active");
  updateStatusCounts();
  updateResultsBar(sorted.length);   // <-- added
}

function updateResultsBar(shown) {
  const total = exhibitions.length;
  const filtersActive = activeStatus !== "ALL" || activeMuseums.size !== museumSet.length;
  resultsCount.innerHTML = `Näytetään <strong>${shown}</strong> / ${total} näyttelyä`;
  resultsBar.classList.toggle("filtered", filtersActive);
}

function resetFilters() {
  activeStatus = "ALL";
  activeMuseums = new Set(museumSet);
  document.querySelectorAll('#museum-checkbox-list input[type="checkbox"]').forEach(cb => cb.checked = true);
  updateMap(activeMuseums, exhibitions);
  applyFilter("ALL");
}

resetFiltersBtn.addEventListener("click", resetFilters);
```

## Design Tokens

### Colors
| Token              | Value               | Used for                         |
|--------------------|---------------------|----------------------------------|
| Bar background     | `#ffffff`           | bar container                    |
| Bar border         | `#e6e6e6`           | bar container                    |
| Bar shadow         | `rgba(0,0,0,0.03)`  | `0 1px 2px` bar shadow           |
| Count text         | `#333333`           | count `<p>`                      |
| Count number       | `#111`              | `<strong>` number                |
| Button text/border | `#333` / `#ccc`     | reset button rest state          |
| Button hover bg    | `#f4f4f4`           | reset button hover               |
| Button hover border| `#b5b5b5`           | reset button hover               |
| Button active bg   | `#ececec`           | reset button active              |

### Typography (font-family: Arial, sans-serif throughout)
| Element     | Size      | Weight | Notes                |
|-------------|-----------|--------|----------------------|
| Count text  | `0.9rem`  | 400    | number is 700        |
| Button      | `0.82rem` | 500    | `white-space: nowrap`|

### Spacing / radius / shadow
| Token                | Value                  |
|----------------------|------------------------|
| Bar padding          | `0.6rem 0.85rem`       |
| Bar margin           | `0.25rem 0 0.5rem`     |
| Bar↔button gap       | `0.75rem`              |
| Bar radius           | `8px`                  |
| Button padding       | `0.4rem 0.8rem`        |
| Button radius        | `6px`                  |
| Button icon gap      | `0.4rem`               |

## Assets
None. Plain text label and CSS only — no images, icons, or fonts beyond the system Arial stack.

## Files
- `results_status_bar_reference.html` — standalone, self-contained reference. Open in a browser to
  see all three states (no filters → button hidden; filters → button shown; zero matches → bar
  persists).
- Target file in the app to modify: `Museokalenteri.html`
  - add the markup before `#exhibitionList` in `.main-content`,
  - add the `#results-status-bar` / `.results-count` / `#reset-filters-btn` rules to the `<style>`
    block,
  - add `updateResultsBar()` / `resetFilters()` and the one call inside `applyFilter()` in
    `initExhibitions()`.

## Notes for the developer
- The bar must be a **sibling above** `#exhibitionList`, never inside it — `renderExhibitions()`
  overwrites `#exhibitionList.innerHTML`, so anything inside it (including the empty-state message)
  would wipe the bar.
- "Filters active" is **time filter ≠ ALL OR not all museums selected**. Sort order is excluded on
  purpose.
- Keep all copy in **Finnish**: `Näytetään {n} / {total} näyttelyä` and `Nollaa suodattimet`.
- Button visibility is driven purely by the `.filtered` class via CSS — no inline `style.display`
  toggling needed.
