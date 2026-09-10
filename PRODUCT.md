# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Right now the primary user is Henri himself, building and testing the tool ("just testing some vibe coded stuff"). He has shared the stable URL with his close circle (lähipiiri), and the explicit intent is to grow and maintain it as if it were a public service, not just a personal experiment. Design and quality decisions should account for that trajectory rather than the project's throwaway origin.

The people the tool serves are anyone interested in Helsinki-region art exhibitions who want to decide what to go see: browsing and filtering what's currently on, opening soon, or closing soon, across many museums and (in beta) galleries at once.

## Product Purpose

Museokalenteri aggregates current and upcoming art exhibitions from Helsinki-region museums (and, in beta, galleries) into one browsable, filterable, mappable calendar, so visitors don't have to check dozens of individual museum/gallery websites to decide what to see. Success is an up-to-date, trustworthy, pleasant list that people actually use to plan visits.

## Positioning

No single museum or gallery maintains a cross-venue exhibition calendar; Museokalenteri does, and keeps itself current by having AI-driven update skills revisit each venue's own exhibition pages directly, rather than depending on a shared API or hand-typed entries.

## Operating Context

- Data source of truth is JSON checked into the repo: `museonayttelyt.json` / `museot.json` (museums) and `gallerianayttelyt.json` / `galleriat.json` (galleries), each with a `_meta.json` companion; periodic snapshots are kept under `archive/`.
- Data is refreshed primarily via dedicated skills (`museokalenteri-updater`, `museokalenteri-gallery-updater`) that compare listed exhibitions against each venue's own pages, remove ended ones, and add new ones; manual edits supplement this when a skill run can't cover something.
- An interactive Leaflet map (loaded from a CDN) plots venues; status filters (Kaikki / Tulossa / Aukeaa pian / Käynnissä / Päättyy pian / Päättyneet) drive the exhibition list.
- Basic usage analytics via GoatCounter.
- Three parallel HTML builds carry distinct roles rather than one deployable file (see Capabilities and Constraints).

## Capabilities and Constraints

- Static HTML/CSS/vanilla JS only, no framework and no bundler/build step. This is a deliberate, durable choice, confirmed by the user — not a gap for future work to "fix."
- Three-file workflow, all durable:
  - `Museokalenteri_beta.html` — development/experimentation build; also currently the only build with gallery features (gallery map markers, gallery filters, gallery exhibition cards). Don't port gallery features to the other two builds without an explicit request.
  - `Museokalenteri.html` — stable build at the publicly shared URL. No direct experiments here; changes land after being proven in beta.
  - `Museokalenteri_design.html` — a "dummy" build with all JSON data embedded inline via `<script type="application/json">` blocks, because the Claude Design preview environment has no filesystem (`fetch` fails there). Its `loadJson()` falls back from `fetch` to the embedded data. Kept in sync for Design-preview and redesign work.
- Data is fetched primarily by the update skills against each venue's own pages; manual supplementation of the JSON is acceptable, not a workaround to avoid.
- The stable `Museokalenteri.html` URL is shared publicly and with the user's close circle — treat it with the care of a small public service, not a scratchpad.

## Brand Commitments

Name: Museokalenteri, described in meta tags as "Helsingin seudun taidenäyttelyt" / "Helsingin seudun Museokalenteri". Logo and marker assets exist under `img/` (`museokalenteri_logo.png`, `museokalenteri_logo_wide.png`, museum/gallery map markers, OG image).

## Evidence on Hand

Venue and exhibition data lives in `museot.json`, `museonayttelyt.json`, `galleriat.json`, `gallerianayttelyt.json` (with `_meta.json` companions) in the repo — real content, not placeholders. No user testimonials, usage numbers beyond GoatCounter, or press exist; future work must not fabricate any of those.

## Product Principles

1. One trustworthy, current list beats visiting a dozen museum sites — freshness and accuracy of exhibition dates outrank added features.
2. Stay a simple static site: no framework or build-tool creep, regardless of how the app grows.
3. Protect the public production build (`Museokalenteri.html`); all exploration happens in the beta build first.
4. Design and build for the audience the project is becoming — a small public service for Henri's circle and beyond — not for the "just testing" label it started with.
5. Let the AI update skills, grounded in each venue's own pages, be the source of what's added or removed, rather than hand-maintained claims about exhibitions.

## Accessibility & Inclusion

WCAG AA is a standing, maintained standard — accessibility fixes already exist in the project's history and must not regress, not be treated as a one-off pass.
