---
name: Museokalenteri
description: Helsingin seudun taidenäyttelyt — selaa ja suodata museoiden näyttelyitä
colors:
  ink-black: "#181818"
  charcoal: "#333333"
  charcoal-hover: "#4a4a4a"
  charcoal-active: "#2a2a2a"
  paper-fog: "#f9f9f9"
  gallery-white: "#ffffff"
  hairline-gray: "#e6e6e6"
  divider-gray: "#f0f0f0"
  slate: "#8a8a8a"
  body-gray: "#454545"
  meta-gray: "#636363"
  label-gray: "#595959"
  whisper-gray: "#c2c2c2"
  title-gray: "#444444"
  chip-bg: "#eeeeee"
  border-gray: "#cccccc"
  border-hover-gray: "#b5b5b5"
  image-bg: "#eef0f1"
  hover-tint: "#f4f4f4"
  active-tint: "#ececec"
  popup-ink: "#222222"
  popup-meta: "#666666"
  map-link-blue: "#1a6fb5"
  status-current: "#047857"
  status-upcoming: "#4338ca"
  status-opening-soon: "#0369a1"
  status-closing-soon: "#b91c1c"
  status-past: "#737373"
typography:
  title:
    fontFamily: "Roboto, Arial, sans-serif"
    fontSize: "1.12rem"
    fontWeight: 700
    lineHeight: 1.25
  eyebrow:
    fontFamily: "Roboto, Arial, sans-serif"
    fontSize: "0.78rem"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "0.07em"
  body:
    fontFamily: "Roboto, Arial, sans-serif"
    fontSize: "0.9rem"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Roboto, Arial, sans-serif"
    fontSize: "0.85rem"
    fontWeight: 400
    lineHeight: 1.3
  micro:
    fontFamily: "Roboto, Arial, sans-serif"
    fontSize: "0.7rem"
    fontWeight: 700
    lineHeight: 1
rounded:
  sm: "4px"
  btn: "6px"
  md: "8px"
  lg: "10px"
  pill: "999px"
spacing:
  xs: "0.35rem"
  sm: "0.5rem"
  md: "0.75rem"
  lg: "1rem"
  xl: "1.5rem"
  2xl: "2rem"
components:
  button-filter:
    backgroundColor: "#eeeeee"
    textColor: "{colors.charcoal}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "0.5rem 1rem"
  button-filter-active:
    backgroundColor: "{colors.charcoal}"
    textColor: "#ffffff"
    rounded: "{rounded.sm}"
    padding: "0.5rem 1rem"
  button-primary:
    backgroundColor: "{colors.charcoal}"
    textColor: "#ffffff"
    rounded: "{rounded.sm}"
    padding: "0.5rem 1rem"
  button-primary-hover:
    backgroundColor: "{colors.charcoal-hover}"
    textColor: "#ffffff"
    rounded: "{rounded.sm}"
  status-pill:
    backgroundColor: "{colors.slate}"
    textColor: "#ffffff"
    typography: "{typography.micro}"
    rounded: "{rounded.pill}"
    padding: "0.18rem 0.55rem"
  card-exhibition:
    backgroundColor: "{colors.gallery-white}"
    typography: "{typography.body}"
    rounded: "{rounded.lg}"
    padding: "0.95rem 1.05rem 1rem 0.95rem"
---

# Design System: Museokalenteri

## Overview

**Creative North Star: "The City Noticeboard"**

Museokalenteri reads like a well-run public noticeboard, not a marketing site: a neutral paper-gray ground, one workhorse typeface, and color spent on exactly one job — telling you whether an exhibition is running now, opening soon, or already over. Nothing competes with that signal. There is no brand hue, no illustration beyond a single bespoke museum-building glyph, and no gradient or drop shadow heavier than an ambient hint of paper lifting off a table.

The system is unapologetically flat and quiet at rest — sections and cards sit almost invisibly on the page (1–2px ambient shadows only) — and only animates in direct response to a hand on it: a card lifts 2px and its shadow deepens on hover, a filled button darkens on press. Depth is a reaction, not a decoration.

Its one recurring discipline is triple-redundant status coding: the same five colors always appear in the same three places for the same meaning (a card's left border, its status pill, and the matching filter button's leading dot), so no visitor has to rely on color alone to know what's on. That discipline is also why this system holds up as a small public service rather than a personal sketch, even though it started as one.

**Key Characteristics:**
- Neutral paper/charcoal base with color reserved entirely for exhibition status
- One typeface (Roboto/Arial), hierarchy from weight and size, never a second face
- Flat at rest, lift-on-hover as the only elevation event
- Rounded-rectangle geometry throughout; no sharp corners, no illustration except one line-art museum mark
- Status is always shown in both color and text — never color alone

## Colors

The palette is almost entirely achromatic — paper whites and charcoal grays — with hue appearing only in the five-color status system and a single utility link blue.

### Primary
- **Ink Black** (#181818): the darkest tone in the system, reserved for exhibition titles — the single highest-emphasis text on the page.
- **Charcoal** (#333333): the "selected/active" UI color — active time filters, the primary Select-all/Deselect-all buttons, checkbox accent color, and the focus-visible outline. Charcoal, not a status color, always means "this control is selected," keeping selection state visually distinct from exhibition status.
  - **Charcoal Hover** (#4a4a4a) / **Charcoal Active** (#2a2a2a): press states for charcoal-filled buttons.

### Secondary
- **Map Link Blue** (#1a6fb5): used only inside Leaflet map popups, for the "Museon verkkosivut →" link. The one placed accent outside the neutral/status system, scoped tightly to the map.

### Status Colors (signature)
The core semantic vocabulary — five fixed hues, each meaning exactly one exhibition state, repeated identically across the card's left border, its status pill, and the matching filter button's dot:
- **Verdant Now** (#047857) — Käynnissä / running now
- **Indigo Ahead** (#4338ca) — Tulossa / upcoming
- **Harbor Blue** (#0369a1) — Aukeaa pian / opening soon
- **Signal Red** (#b91c1c) — Päättyy pian / closing soon
- **Archive Gray** (#737373) — Päättynyt / past

### Neutral
- **Paper Fog** (#f9f9f9): page background.
- **Gallery White** (#ffffff): card and section surface color.
- **Hairline Gray** (#e6e6e6): section/card borders.
- **Divider Gray** (#f0f0f0): internal hairlines (description separator, checkbox row dividers).
- **Slate** (#8a8a8a): the default/unset status dot and status-pill color before a real status resolves; also the exhibition-image fallback tint.
- **Body Gray** (#454545): description copy.
- **Meta Gray** (#636363): exhibition date ranges.
- **Label Gray** (#595959): the uppercase museum-name eyebrow.
- **Whisper Gray** (#c2c2c2): the faint external-link arrow indicator.
- **Chip Gray** (#eeeeee): inactive filter-chip background.
- **Ghost Border** (#cccccc) / **Ghost Border Hover** (#b5b5b5): border for outlined ("ghost") buttons — Rajaukset, Sulje, reset-filters, map fullscreen — at rest and on hover.
- **Hover Tint** (#f4f4f4) / **Active Tint** (#ececec): background shift for ghost buttons on hover/press.
- **Image Backdrop** (#eef0f1): fallback background behind an exhibition's image/marker before it loads.
- **Section Title Gray** (#444444): sidebar/section heading color, one step lighter than Charcoal.
- **Popup Ink** (#222222) / **Popup Meta** (#666666): map-popup venue name and address text — a self-contained pairing scoped to Leaflet popups only.

### Named Rules
**The Triple-Coding Rule.** Every exhibition status is shown three ways at once — a color, a plain-language label, and consistent position — never through color alone. The card's left border, its status pill text, and the matching filter's leading dot always share the same hue for the same status.

**The Selection-Is-Neutral Rule.** "Selected" or "active" never borrows a status color. Active filters and primary buttons are always Charcoal, so a selected control can never be mistaken for a CURRENT/UPCOMING/etc. status.

## Typography

**Body Font:** Roboto (fallback: Arial, sans-serif)

**Character:** Purely functional — there is no display or decorative face. Hierarchy is built entirely from weight, size, and color, never a second typeface. The exhibition title (700 weight, 1.12rem) is the largest text anywhere in the system; there is no larger "hero" scale.

### Hierarchy
- **Title** (700, 1.12rem, line-height 1.25, Ink Black): the exhibition name — the de facto headline of the interface.
- **Eyebrow** (600, 0.78rem, letter-spacing 0.07em, uppercase, Label Gray): the museum name tag above each title.
- **Section Title** (600, 0.95rem, `#444`): sidebar/section headers ("Aikasuodattimet", "Museot").
- **Body** (400, 0.9rem, line-height 1.55, Body Gray): the optional exhibition description, shown below a hairline divider.
- **Label** (400, 0.85–0.88rem, Meta Gray): dates, filter/checkbox labels, results count.
- **Micro** (700, 0.7rem, white on a status color): the status pill text — the smallest text, always high-weight for legibility at that size.

### Named Rules
**The One Family Rule.** Roboto/Arial is the only typeface anywhere in the system.

## Layout

A single centered column, max-width 980px, 2rem outer padding (0.75rem on mobile). Desktop splits into a fluid main content area plus a fixed 240px sidebar (1.5rem gap) holding the time filters, museum checklist, and sort control. Below 768px the sidebar becomes a fixed 280px right-hand drawer (`transform: translateX`) behind a dimming overlay, opened via a "Rajaukset" header button and closed via an explicit "Sulje" button or backdrop tap.

The exhibition list is a vertical stack (0.75rem gaps) of full-width row cards. Each card is a fixed 96px (80px mobile) image/status rail beside a flexible content column — the rail width never grows, so image and text always align across every card regardless of content length.

Spacing runs in a tight rem scale: 0.35rem / 0.5rem / 0.75rem / 1rem / 1.5rem, applied consistently for gaps, section padding, and button padding.

## Elevation & Depth

Flat by default. Sections and cards carry only an ambient hint of shadow at rest (`0 1px 2px–3px rgba(0,0,0,0.03–0.07)`) — just enough to read as a raised card on a gray page, not a deliberate elevation tier. Depth only becomes visible as a response to interaction.

### Shadow Vocabulary
- **Ambient rest** (`box-shadow: 0 1px 3px rgba(0,0,0,0.07)`): default card/section shadow.
- **Hover lift** (`box-shadow: 0 6px 20px rgba(0,0,0,0.08)` + `transform: translateY(-2px)`): exhibition cards on hover — the system's one elevation event.
- **Action shadow** (`box-shadow: 0 2px 4px rgba(0,0,0,0.08)` → `0 4px 10px rgba(0,0,0,0.12)` on hover): the filled Select-all/Deselect-all buttons.

### Named Rules
**The Flat-Until-Touched Rule.** Nothing sits elevated at rest. Shadow only deepens in direct response to hover or focus, never as ambient decoration.

## Shapes

Rounded rectangles throughout, scaled by role: sections and cards use the largest radius (8–10px), images use a mid radius (8px), filter/action chips use the smallest (4px), ghost buttons (Rajaukset, Sulje, reset-filters) and the map corner use an intermediate 6px, and status pills/filter dots are fully circular/pilled (999px / 50%). No sharp corners appear anywhere. The one non-geometric form in the system is the bespoke museum marker — a black-line-on-white icon of a columned building — the single illustrated glyph in an otherwise flat-color interface.

## Components

### Buttons
- **Filter buttons** (time filters): rounded 4px, `#eee` background, Charcoal text; each carries a small leading colored dot matching its status hue (except "Kaikki", which has no dot). **Active state uses solid Charcoal fill + white text — not the status color** (see Selection-Is-Neutral Rule).
- **Primary/special buttons** (Select all / Deselect all, "Rajaukset"): full-width or auto, solid Charcoal, white text, subtle ambient shadow; Charcoal Hover on hover, Charcoal Active on press. The only confidently "filled" buttons in the system.
- **Reset filters:** ghost button (white fill, gray border), appears only once a filter is active.

### Status Pill
- Fully rounded (999px), white micro-weight text (0.7rem/700) on a status color background. Always paired with the same-colored left border on its parent card and the same-colored dot on the matching filter button.

### Cards / Exhibition Card (signature component)
- **Corner Style:** 10px radius, with a 4px solid left border in the exhibition's status color as the primary at-a-glance signal.
- **Background:** Gallery White.
- **Shadow Strategy:** Ambient rest → Hover lift (see Elevation & Depth).
- **Structure:** a 96px square image rail (photo, or the museum's line-art marker at 45% opacity as fallback) with the status pill directly beneath it, beside a content column of Eyebrow (museum name) → Title → date Label → optional Body description behind a 1px divider. The whole card is a link when the exhibition has one, with a small arrow (↗) top-right indicator and a 2px `outline` focus ring on keyboard focus.

### Checkbox Rows (museum filter list)
- **Style:** plain list rows with a 1px bottom divider (last row has none), Charcoal `accent-color` checkbox, full row width as the click target via a paired `<label>`.

### Navigation / Map
- **Style:** Leaflet map on muted "CARTO light" tiles; the sole marker is the bespoke black-line museum-building icon. Popups are minimal: bold venue name (13px/700), gray address (12px), Map Link Blue website link (12px, underline on hover).
- **Mobile treatment:** the map collapses to 300px height and gains a fullscreen toggle that pins it to the viewport.

## Do's and Don'ts

### Do:
- **Do** spend color on exhibition status only — the five status hues are the system's entire chromatic vocabulary outside of Map Link Blue.
- **Do** show every status as both a color and a text label; never color alone (WCAG AA commitment — see PRODUCT.md).
- **Do** keep shadows near-invisible at rest and reserve visible depth for hover/focus feedback only.
- **Do** build all hierarchy from Roboto/Arial weight, size, and color — never introduce a second typeface.
- **Do** prove any visual change in `Museokalenteri_beta.html` before it reaches the stable, publicly-shared `Museokalenteri.html`.
- **Do** keep every interactive control (filter chips, checkboxes, ghost buttons) at a 44px minimum touch height, and expose toggle/selection state through `aria-pressed` rather than a CSS class alone.
- **Do** reference the `:root` custom properties for every color, radius, and spacing value instead of a new literal — the tokens in this file's frontmatter are also the actual CSS variables in `Museokalenteri.html`.

### Don't:
- **Don't** give a "selected/active" control (filters, buttons) a status color — active state is always Charcoal, so it's never confused with CURRENT/UPCOMING/etc.
- **Don't** add gradients, heavy drop shadows, or decorative imagery — the system is flat and functional throughout; the museum-marker glyph is the only illustration allowed.
- **Don't** introduce a second brand/accent hue — this system is neutral-plus-status, not neutral-plus-brand.
- **Don't** port beta-only gallery features (gallery map markers, gallery filters, gallery cards) into the stable or design build without an explicit request.
