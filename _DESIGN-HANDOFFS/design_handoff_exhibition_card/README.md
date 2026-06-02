# Handoff: Exhibition Card Redesign (Option B)

## Overview
A redesigned **exhibition list card** for *Museokalenteri* (Helsingin seudun Museokalenteri) — the
compact, filterable list of art exhibitions in the Helsinki region. Each card is a directory entry
that summarises one exhibition and **links out to the museum's own page** for full details.

This handoff covers **only the card** (the repeating list item). The surrounding page — header/logo,
map, sidebar filters (time + per-museum checkboxes + sort) — is unchanged and is not part of this
redesign.

## About the Design Files
The file in this bundle (`exhibition_card_reference.html`) is a **design reference created in HTML +
React (via in-browser Babel)**. It is a prototype that shows the intended look and behaviour — it is
**not production code to copy directly**.

The task is to **recreate this card in the target codebase**. The existing app
(`Museokalenteri.html`) is a single static HTML page with a vanilla-JS render loop
(`renderExhibitions()` builds cards with `document.createElement` + template strings). The most
faithful integration is to **replace the existing card markup/styles in that render loop with the
structure documented below** — plain HTML + CSS, no React required. (React is used in the reference
only as a convenient prototyping tool.) If the app is later migrated to a framework, recreate the
same structure there using that framework's patterns.

## Fidelity
**High-fidelity.** Final colors, typography, spacing, and layout. Recreate pixel-for-pixel. All exact
values are listed under **Design Tokens** and **Components**.

## Screens / Views

### Exhibition list (single repeating card)
- **Name:** Exhibition card (`.exhibition` list item)
- **Purpose:** Let the user scan/filter exhibitions and click through to the museum's exhibition page.
- **Layout:**
  - The card is an `<a>` (whole card is the outbound link), `display: block`, `position: relative`.
  - Inside: a horizontal **flex row** (`gap: 0.95rem`, `align-items: flex-start`) with two columns:
    - **Left rail** (fixed `96px` wide, flex column, `gap: 0.5rem`, `align-items: flex-start`):
      thumbnail on top, **status pill** directly beneath it.
    - **Text column** (`flex: 1; min-width: 0; padding-right: 1.2rem`): museum eyebrow → title →
      date range → **divider + description**.
  - The **description and its top divider live inside the text column** (Option B), i.e. indented to
    start under the title/date, NOT spanning under the thumbnail.
  - A small **↗** glyph is absolutely positioned in the **top-right corner** as the outbound-link cue.
  - **Card height is intentionally variable** — the full description is always shown, never truncated.
    Do not clamp, ellipsize, or fix the height.
  - Cards are stacked in a vertical flex list with `gap: 0.75rem`. Page background `#f9f9f9`.

## Components

### Card container `<a>`
- Element: `<a href={link} target="_blank" rel="noopener noreferrer">`
- `background: #fff`
- `border-radius: 10px`
- `box-shadow: 0 1px 3px rgba(0,0,0,0.07)`
- `overflow: hidden`
- `border-left: 4px solid <status color>` (status color — see tokens)
- `padding: 0.95rem 1.05rem 1rem 0.95rem`
- `position: relative; display: block; text-decoration: none; color: inherit`
- `font-family: Arial, sans-serif`
- Hover (recommended, matches existing site): lift + stronger shadow, e.g.
  `transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.08)` with `transition: 0.2s`.
- Focus-visible (accessibility): `outline: 2px solid #333; outline-offset: 4px`.

### Thumbnail (`Thumb`)
- Fixed square: `width: 96px; height: 96px`
- `border-radius: 8px; overflow: hidden`
- `background: #eef0f1`
- `box-shadow: inset 0 0 0 1px rgba(0,0,0,0.05)` (subtle inner ring so letterboxed images don't look broken)
- Image: `object-fit: contain; max-width: 100%; max-height: 100%; display: block` (whole image visible inside the square — landscape banners letterbox, this is intended), `loading="lazy"`
- **Fallback:** if the image fails to load (`onerror`), replace it with a centered first-letter
  placeholder: the exhibition title's first character, uppercase, `font-size: ~38px` (40% of box),
  `font-weight: 700`, `color: rgba(0,0,0,0.25)`, on the same `#eef0f1` box. **This fallback is
  required** — many museum image URLs are hotlink-protected or will rot, and the current site shows
  blank grey boxes when they fail.

### Status pill (`StatusPill`) — solid
- Sits directly under the thumbnail in the left rail.
- `display: inline-block; white-space: nowrap`
- `padding: 0.18rem 0.55rem`
- `font-size: 0.7rem; font-weight: 700`
- `border-radius: 999px`
- `background: <status color>; color: #fff`
- Label text: `Käynnissä` / `Tulossa` / `Päättynyt` (see status logic).

### Museum eyebrow
- `<p>` above the title.
- `margin: 0 0 0.28rem`
- `font-size: 0.7rem; font-weight: 700`
- `letter-spacing: 0.07em; text-transform: uppercase`
- `color: #7a7a7a` — **neutral grey on purpose.** Do NOT tint it with the status color; status color
  must only appear on the border + pill, otherwise the repetition reads as confusing.
- Content: museum name (e.g. `EMMA`, `AMOS REX`).

### Title
- `<h2>`
- `margin: 0 0 0.25rem`
- `font-size: 1.12rem; font-weight: 700; line-height: 1.25`
- `color: #181818`
- `text-wrap: pretty` (wraps to 2+ lines for long titles; that's fine)

### Date range
- `<p>`
- `margin: 0`
- `font-size: 0.83rem; color: #888`
- Content: `<startDate> – <endDate>` using Finnish format `d.m.yyyy` (no leading zeros),
  e.g. `13.5.2026 – 6.9.2026`. Separator is an en-dash `–` with spaces.

### Divider + description
- `<p>` immediately after the date range, **inside the text column**.
- `margin: 0.8rem 0 0`
- `padding-top: 0.8rem`
- `border-top: 1px solid #f0f0f0` (the divider)
- `font-size: 0.9rem; line-height: 1.55; color: #454545`
- `text-wrap: pretty`
- Content: the **full** description, never truncated.

### Outbound-link arrow
- `<span aria-hidden="true">↗</span>`
- `position: absolute; top: 0.7rem; right: 0.85rem`
- `color: #c2c2c2; font-size: 1.05rem; line-height: 1`

## Interactions & Behavior
- **Whole card is a link** to `ex.link` (the museum's exhibition page), opening in a new tab
  (`target="_blank" rel="noopener noreferrer"`). If an entry has no link, render the same card as a
  `<div>` (no anchor) and omit the ↗.
- **Hover:** subtle lift + shadow (see card container).
- **Image load failure:** swap to the first-letter placeholder (see Thumbnail).
- **No truncation / no expand-collapse:** full description always visible; card grows to fit.
- **Responsive:** on narrow screens (≤768px in the current site) the existing layout stacks the
  filters into a drawer; the card itself can keep the same two-column structure (96px thumb + text).
  If space is very tight you may reduce the thumb to ~72–80px, but keep the structure.

## State Management
None specific to the card — it is a pure presentational component driven by one exhibition object.
Status is derived at render time (see below). Filtering/sorting/selection state lives in the parent
list, unchanged by this redesign.

## Status logic
Each exhibition's status is derived from today's date vs its run dates:
```
if (now < start)  -> "UPCOMING"  (Tulossa)
else if (now > end) -> "PAST"     (Päättynyt)
else               -> "CURRENT"   (Käynnissä)
```
(The list's "Avautuvat 2 vk" / "Päättyvät 2 vk" options are filter modes in the sidebar, not card
states — they do not change the pill.)

## Date formatting
ISO `YYYY-MM-DD` → Finnish `d.m.yyyy` with no leading zeros:
```
"2026-05-13"  ->  "13.5.2026"
```

## Design Tokens

### Status colors (border + solid pill)
| Status   | Label (fi) | Color     | Pill text |
|----------|------------|-----------|-----------|
| CURRENT  | Käynnissä  | `#1f8a3b` | `#fff`    |
| UPCOMING | Tulossa    | `#1f5fd6` | `#fff`    |
| PAST     | Päättynyt  | `#8a8a8a` | `#fff`    |

### Neutrals / text
| Token              | Value     | Used for                         |
|--------------------|-----------|----------------------------------|
| Card background    | `#fff`    | card                             |
| Page background    | `#f9f9f9` | list page                        |
| Thumb background   | `#eef0f1` | thumbnail box / placeholder      |
| Title text         | `#181818` | title                            |
| Body text          | `#454545` | description                      |
| Muted text         | `#888`    | date range                       |
| Eyebrow text       | `#7a7a7a` | museum name                      |
| Divider line       | `#f0f0f0` | rule above description           |
| Arrow glyph        | `#c2c2c2` | ↗                                |
| Inset ring (thumb) | `rgba(0,0,0,0.05)` | thumb inner border      |
| Placeholder letter | `rgba(0,0,0,0.25)` | image fallback          |

### Typography (font-family: Arial, sans-serif throughout)
| Element      | Size      | Weight | Line-height | Other                               |
|--------------|-----------|--------|-------------|-------------------------------------|
| Eyebrow      | `0.7rem`  | 700    | —           | `letter-spacing: 0.07em; uppercase` |
| Title        | `1.12rem` | 700    | 1.25        | `text-wrap: pretty`                 |
| Date range   | `0.83rem` | 400    | —           | —                                   |
| Description  | `0.9rem`  | 400    | 1.55        | `text-wrap: pretty`                 |
| Status pill  | `0.7rem`  | 700    | —           | —                                   |

### Spacing / radius / shadow
| Token                | Value                          |
|----------------------|--------------------------------|
| Card padding         | `0.95rem 1.05rem 1rem 0.95rem` |
| Row gap (thumb↔text) | `0.95rem`                      |
| Left-rail gap        | `0.5rem`                       |
| List gap (card↔card) | `0.75rem`                      |
| Text column pad-right| `1.2rem`                       |
| Divider margin-top   | `0.8rem` (+ `0.8rem` pad-top)  |
| Card radius          | `10px`                         |
| Thumb radius         | `8px`                          |
| Pill radius          | `999px`                        |
| Card shadow          | `0 1px 3px rgba(0,0,0,0.07)`   |
| Status border        | `4px` solid (left edge)        |
| Thumb size           | `96 × 96px` fixed              |

## Assets
- **Exhibition images:** remote URLs from each museum's own CMS (the `Image` field in
  `museonayttelyt.json`). No assets bundled. Must be rendered with `object-fit: contain` and the
  first-letter fallback described above.
- **Arrow:** plain text glyph `↗` (U+2197). No icon asset needed.
- **Fonts:** Arial / system sans — no web font.

## Data shape
Each exhibition object (from `museonayttelyt.json`) used by the card:
```json
{
  "museum": "EMMA",
  "title": "Antti Laitinen: Helisevä metsä",
  "start": "2025-09-24",
  "end": "2026-08-23",
  "description": "Kineettinen installaatio ...",
  "Link":  "https://emmamuseum.fi/nayttely/...",
  "Image": "https://emmamuseum.fi/wp-content/uploads/..."
}
```
Note the source JSON uses capitalised `Link` / `Image` (with `link` / `image` as fallbacks in the
current code). `museum`, `title`, `start`, `end`, `description` are lower-case.

## Files
- `exhibition_card_reference.html` — standalone, self-contained reference. Open in a browser to see
  the exact target rendering (4 sample cards spanning short→long descriptions, current + upcoming
  statuses). All card CSS values inline in the `ExhibitionCard` / `Thumb` / `StatusPill` components.
- Target file in the app to modify: `Museokalenteri.html` → `renderExhibitions()` (the card-building
  loop) and the `.exhibition*` rules in the `<style>` block.

## Notes for the developer
- Keep the **graceful image fallback** — it also fixes a current bug where failed images show empty
  grey boxes.
- Keep dates in **Finnish format**; the current site shows raw ISO (`2025-02-12`).
- Status color must appear on **border + pill only**, never on the museum name.
- Do not introduce truncation; variable height is by design.
