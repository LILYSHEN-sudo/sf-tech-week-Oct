# SF Tech Week 2026 Event Intelligence Map

 [Open the interactive map](https://lilyshen-sudo.github.io/sf-tech-week-Oct/map.html)

**1,700+ events, one week, and no single venue.** This project turns a snapshot of the [official SF Tech Week calendar](https://www.tech-week.com/calendar/sf) into a neighborhood-first event map enriched with public Partiful links, visible guest-count signals, host identity fields, and logo review status.

The calendar snapshot was collected on September 23, 2026. It contains 1,714 listings; 1,710 remain after limiting the analysis to October 5–11 and removing one duplicate. The site is a historical snapshot, not a live registration feed.

## Current status

The project is now centered on `web/map.html`: a full-screen MapLibre map with neighborhood bubbles, filters, and an event drawer. Event links have been replaced with final public Partiful URLs where available, and the frontend has a companion metadata layer for public guest counts and host/logo fields.

The current data workflow is:

```text
data/source-data/     original evidence, do not hand-edit
data/interim/         current master working layer
data/00-ready-to-use-data/
  event-level/        regenerated event exports
  host-level/         regenerated host exports and logo priority queue
```

The role and goal filters are recommendation signals derived from public event metadata. They are not official audience fields, attendance counts, or popularity scores. Public guest counts are only used when the Partiful page exposes them; hidden counts are treated as unknown, not zero.

---

## Problem and Goal

The official calendar is useful for finding individual events, but the week is hard to understand as a whole. Events span seven days, many topics and formats, and dozens of location labels. The public records identify a neighborhood or broad area, not a reliable venue coordinate.

The goal is to make the week explorable without inventing precision. The map groups events by host-supplied neighborhood labels, exposes official themes/formats/tracks, adds inferred audience and intent filters, and surfaces host/guest signals where the public registration page supports them.

---

## Architecture

```text
  SOURCE       official Tech Week calendar snapshot
               public Tech Week /go/event redirects
               public Partiful event pages and host images
                        │
                        ▼
  INTERIM      data/interim/sf-tech-week-master.csv/json
               event fields · themes/formats/tracks · inferred audience/intent
               Partiful URL · public guest count · selected icon · logo status
                        │
                        ▼
  READY        data/00-ready-to-use-data/event-level/
               data/00-ready-to-use-data/host-level/
               event export · host export · logo replacement priority queue
                        │
                        ▼
  VIEW         web/data.js + web/event-meta.js + web/partiful-links.js
               full-screen MapLibre event map
```

The browser does not fetch the official calendar or scrape Partiful. Python processes one dated snapshot and public registration-page extracts, then the static page filters and draws the result. This keeps displayed counts traceable to the same 1,710 event set.

The map uses one bubble per location label, with clustering as the map zooms out. A bubble is placed at an approximate neighborhood center; it is **not** an event address. Virtual and unknown locations have no map coordinate, while broader Bay Area labels are presented separately or approximately.

---

## Tech stack


| Layer                  | Implementation                                                        |
| ---------------------- | --------------------------------------------------------------------- |
| Data processing        | Python, pandas, NumPy                                                 |
| Static visualizations  | Plain HTML, CSS, JavaScript, SVG                                      |
| Interactive map        | MapLibre GL JS 4, OpenFreeMap light/dark basemaps                     |
| Neighborhood reference | DataSF Analysis Neighborhoods GeoJSON                                 |


There is no frontend build step. GitHub Pages publishes only `web/` through the deployment workflow. MapLibre and the basemap load from the network; the event data is packaged into static JavaScript files.

---

## Data flow

1. **Capture.** The September 23 calendar snapshot records public event fields and official theme, format, and curated-track labels.
2. **Enrich.** Public `/go/event` redirects are resolved to Partiful URLs. Public Partiful pages provide guest-count status, visible counts when exposed, owner candidates, and host/profile images.
3. **Master.** `data/scripts/build_interim_master_dataset.py` joins the official event table, Partiful URL map, guest enrichment, selected icons, and logo review fields into `data/interim/sf-tech-week-master.csv/json`.
4. **Derive.** `data/scripts/build_ready_data_from_interim.py` regenerates clean event-level and host-level exports from the interim master.
5. **Explore.** The static map filters by day, topic, format, role, goal, registration status, and visible map area, then opens the final public Partiful event page.

`audience_inferred` and `intent_inferred` are project estimates, **not** official per-event fields or judgments of event quality. When both audience and intent filters are selected, an event must match at least one selection in each dimension.

### Local data layout

The reproducible snapshot is kept locally under the Git-ignored `data/` directory:

```text
data/
├── source-data/             raw evidence and extraction outputs
├── interim/                 current event master and working analysis files
├── 00-ready-to-use-data/    regenerated event-level and host-level exports
└── scripts/                 data build and analysis scripts
```

See [data/data-overview.md](data/data-overview.md) for field definitions and provenance. The folder is intentionally excluded from GitHub; the public site uses prebuilt `web/*.js` artifacts.

---

## Evaluation

Current local checks:

| Check | Result |
| --- | ---: |
| Original official calendar rows | 1,714 |
| Interim master rows | 1,721 |
| Ready event rows | 1,710 |
| Ready host rows | 1,205 |
| Final Partiful link hits in frontend data | 1,710 / 1,710 |
| Event metadata hits in frontend data | 1,710 / 1,710 |
| Ready events with visible public guest count | 1,334 |
| Ready logo replacement queue | 683 hosts |
| High-priority logo replacements | 53 hosts |

The `domains` field from the older analysis line is no longer part of the active master or ready exports. Current filtering and grouping use official `themes`, `formats`, and `tracks`, plus clearly labeled project inference fields: `audience_inferred` and `intent_inferred`.

There is no automated test suite in this repository. External basemap, CDN, Tech Week page, and Partiful page availability remain outside the project's control.

### Hosts with the most listed events

Using the ready host export, the hosts with the most listed events are:


| Rank | Host                | Events |
| ---- | ------------------- | ------ |
| 1    | Deel                | 15     |
| 2    | Leverage            | 12     |
| 3    | Business Sweden     | 8      |
| 4    | Google for Startups | 7      |
| 5    | Flex                | 6      |
| 6    | Unicorner           | 6      |
| 7    | a16z                | 5      |
| 8    | Airwallex           | 5      |
| 9    | Fin                 | 5      |
| 10   | Workflow Builder    | 5      |


This is a ranking of publishing activity, not a ranking of attendance. Public guest counts are a separate signal and only exist for events whose Partiful pages expose them.

---

## Project structure

```text
web/
  index.html             neighborhood and time overview
  map.html               interactive street map, event drawer, and neighborhood signals
  data.js                compact event payload used by the map
  event-meta.js          public guest-count and host/logo metadata
  partiful-links.js      final public Partiful URLs

analysis/
  archive/               older domain/lift analysis and logo experiments
  host-analysis/         logo quality workflow inputs

data/                     local, Git-ignored snapshot and processing workspace
  source-data/             raw evidence and extraction outputs
  interim/                 current master working layer
  00-ready-to-use-data/    regenerated event-level and host-level exports
  scripts/                 data build and analysis utilities
```

The public repository includes the static pages and prebuilt web artifacts. The `data/`, `docs/`, and `docs-local/` directories are intentionally excluded by `.gitignore`. A fresh clone can display the existing snapshot but cannot rebuild or independently audit the source extraction without the local data files.

---

## Quick start

From the repository root:

```bash
cd web
python3 -m http.server 8000
```

Open [http://localhost:8000/index.html](http://localhost:8000/index.html) for the overview or [http://localhost:8000/map.html](http://localhost:8000/map.html) for the street map. The street basemap, MapLibre, and web fonts require internet access; the event data is served locally from `data.js`.

To rebuild the active ready exports from the current interim master:

```bash
python3 data/scripts/build_ready_data_from_interim.py
```

To rebuild the web payload after changing event inputs, use the existing `web/build_data.py` workflow and then regenerate `web/event-meta.js` / `web/partiful-links.js` from the interim master.

---

Sources: [SF Tech Week calendar](https://www.tech-week.com/calendar/sf) for events and [DataSF Analysis Neighborhoods](https://data.sfgov.org/) for the boundary reference. The map uses [OpenFreeMap](https://openfreemap.org/) and OpenStreetMap contributors for its street basemap.
