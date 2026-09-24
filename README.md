# SF Tech Week 2026 Event Map

[Explore the live overview](https://lilyshen-sudo.github.io/sf-tech-week-Oct/) · [Open the interactive map](https://lilyshen-sudo.github.io/sf-tech-week-Oct/map.html) · [View the figure gallery](https://lilyshen-sudo.github.io/sf-tech-week-Oct/figures.html)

**1,700+ events, one week, and no single venue.** This project turns a snapshot of the [official SF Tech Week calendar](https://www.tech-week.com/calendar/sf) into a neighborhood map, a time explorer, and a test of whether related events actually cluster.

The calendar snapshot was collected on September 23, 2026. It contains 1,714 listings; 1,710 remain after limiting the analysis to October 5–11 and removing one duplicate. The site is a historical snapshot, not a live registration feed.

## Current status

The project is currently a deployed, static visualization with three public views: an overview, an interactive MapLibre map, and a figure gallery. The main event exploration workflow is complete: users can filter by date, time range, official topic, event format, registration status, inferred role, and inferred goal, then inspect matching events and open the original listing.

The role and goal filters are recommendation signals derived from public event metadata. They are not official audience fields, attendance counts, or popularity scores. Host-level analysis is also complete locally, but the source snapshot and derived data remain Git-ignored so the public repository does not publish the underlying event export.

---

## Problem and Goal

The official calendar is useful for finding individual events, but the week is hard to understand as a whole. Events span seven days, many topics and formats, and dozens of location labels. The public records identify a neighborhood or broad area, not a reliable venue coordinate.

**The goal is to make the week explorable without inventing precision.** The interactive map groups events by the neighborhood supplied by the host. Its left rail can filter directly by inferred audience and intent labels, while the top card filters by day, the 23 official topics, ten event formats, four time ranges and registration status. Search and the current map area further narrow the list. A separate analysis tab summarizes place and start-time patterns. Marker size and blue–yellow–red color both encode the number of matching events.

![Neighborhood bubbles show the concentration of 1,710 events; SOMA, FiDi, and Downtown account for 50.4%.](analysis/figures/A-16x9.png)

![Neighborhood by topic lift matrix; only two of 168 tested pairs meet the corrected significance threshold.](analysis/figures/E-16x9.png)

The [overview](https://lilyshen-sudo.github.io/sf-tech-week-Oct/), [interactive street map](https://lilyshen-sudo.github.io/sf-tech-week-Oct/map.html), and [figure gallery](https://lilyshen-sudo.github.io/sf-tech-week-Oct/figures.html) all read the same prebuilt `web/data.js` file. You can also run them with a local server using the instructions below.

---

## Architecture

```text
  SOURCE       SF Tech Week calendar snapshot    DataSF neighborhood boundaries
                        │                                   │
                        ▼                                   │
  PREP         infer audience + intent → clean and deduplicate │
               map official tags to 14 overlapping domains │
                        │                                   │
                        ▼                                   │
  ANALYSIS     neighborhood / day / hour summaries          │
               hypergeometric tests + BH correction         │
                        └─────────────────┬─────────────────┘
                                          ▼
  BUILD        web/build_data.py → web/data.js
               compact event rows · bitmasks · centers · simplified shapes
                                          │
                        ┌─────────────────┼──────────────────┐
                        ▼                 ▼                  ▼
  VIEW            overview SVG       MapLibre map       figure gallery
                  web/index.html     web/map.html       web/figures.html
```

The browser does not fetch the official calendar or run the statistical tests. Python processes one dated snapshot, then the static pages filter and draw the result. This keeps the views consistent and makes every displayed count traceable to the same 1,710 event set.

The map uses one bubble per location label, with clustering as the map zooms out. A bubble is placed at an approximate neighborhood center; it is **not** an event address. Virtual and unknown locations have no map coordinate, while broader Bay Area labels are presented separately or approximately.

---

## Tech stack


| Layer                  | Implementation                                                        |
| ---------------------- | --------------------------------------------------------------------- |
| Data processing        | Python, pandas, NumPy                                                 |
| Statistical analysis   | SciPy hypergeometric survival function; Benjamini–Hochberg correction |
| Static visualizations  | Plain HTML, CSS, JavaScript, SVG                                      |
| Interactive map        | MapLibre GL JS 4, OpenFreeMap light/dark basemaps                     |
| Neighborhood reference | DataSF Analysis Neighborhoods GeoJSON                                 |
| Figure export          | Headless Google Chrome via `analysis/export_figures.sh`               |


There is no frontend build step. GitHub Pages publishes only `web/` through the [deployment workflow](.github/workflows/deploy-pages.yml). MapLibre and the basemap load from the network; the overview and figure gallery draw their own SVG from the packaged data file.

---



## Data flow

1. **Capture.** The September 23 calendar snapshot records public event fields and official theme, format, and curated-track labels. The browser-side capture script was not retained, so refreshing the source snapshot is still a manual step.
2. **Infer and clean.** `data/scripts/infer_audience.py` adds rule-based audience and intent signals. `analysis/analyze.py` normalizes names and location labels, flags out-of-week rows, removes duplicate name/date/time listings, and marks 00:00–05:59 start times as uncertain.
3. **Group and test.** Official themes and tracks are mapped to 14 project domains. Domains can overlap. For neighborhoods with at least 25 physical events, the analysis computes domain lift and a one-sided hypergeometric p-value; it corrects the 168 comparisons with Benjamini–Hochberg. A significant cell also needs at least five events.
4. **Package.** `web/build_data.py` combines the clean CSV, analysis tables, approximate location centers, and simplified DataSF boundaries into `web/data.js`. Events are compact arrays; audience, intent, domain, official topic, and format membership use bitmasks.
5. **Explore.** The overview and map apply filters in the browser. The interactive map can filter directly by selected roles and goals, remembers those selections locally, and colors markers by matching event counts; the overview and figure gallery retain the precomputed full-week lift analysis.

`audience_inferred` and `intent_inferred` are project estimates, **not** official per-event fields or judgments of event quality. When both audience and intent filters are selected, an event must match at least one selection in each dimension.

### Local data layout

The reproducible snapshot is kept locally under the Git-ignored `data/` directory:

```text
data/
├── source-data/    raw calendar snapshot and neighborhood boundaries
├── data-clean/     cleaned CSV used by analysis and the web build
├── data-analysis/  host profiles and summary reports
├── output/         guest-count outputs and cache
└── scripts/        inference, host-analysis, and collection scripts
```

See [`data/README.md`](data/README.md) for field definitions and provenance. The folder is intentionally excluded from GitHub; the public site uses the prebuilt `web/data.js` artifact.

---

## Evaluation

I checked the prebuilt browser data against the analysis outputs:


| Check                                        | Result                                  |
| -------------------------------------------- | --------------------------------------- |
| Original calendar rows                       | 1,714                                   |
| In-week rows, after one duplicate is removed | 1,710                                   |
| Rows with a usable start hour                | 1,706                                   |
| Neighborhood labels / mapped boundary shapes | 45 / 41                                 |
| SOMA + FiDi + Downtown                       | 862 events, 50.4% of the analysis set   |
| Starts at 17:00 or 18:00                     | 684 events, 40.1% of usable start times |
| Significant neighborhood × domain pairs      | 2 of 168                                |


The two significant pairs are **Mission × Creator, Media & Consumer** (39 of 106 neighborhood events; lift 1.68, adjusted q 0.0306) and **Hayes Valley × Women-focused** (7 of 28; lift 4.85, q 0.0306). Some other cells have high lift but do not meet the corrected threshold; the interface distinguishes those from significant clusters.

Browser checks compared the map's topic, format, day, and time filters with the CSV and exercised the event/analysis tabs, language switching, and responsive layout. The audience and intent controls are implemented in the map and use the same prebuilt event payload. There is no automated test suite in this repository; external basemap, CDN, and registration-page availability remain outside the project's control.

### Hosts with the most listed events

Using the `primary_host` field in the 1,714-row calendar snapshot, the hosts with the most listed events are:

| Rank | Host | Events |
|---:|---|---:|
| 1 | Deel | 15 |
| 2 | Leverage | 12 |
| 3 | Business Sweden | 8 |
| 4 | Google for Startups | 7 |
| 5 | Flex | 6 |
| 6 | Unicorner | 6 |
| 7 | a16z | 5 |
| 8 | Airwallex | 5 |
| 9 | Fin | 5 |
| 10 | Workflow Builder | 5 |

This is a ranking of publishing activity, not a ranking of attendance or Guest List size. Guest List counts are not consistently public across the linked registration platforms, so the table should not be interpreted as a popularity ranking.

---

## Project structure

```text
web/
  index.html             neighborhood and time overview
  map.html               interactive street map, event list, and insights
  figures.html           exportable chart layouts
  data.js                prebuilt data shared by all three pages
  build_data.py          compiles cleaned data and map shapes

analysis/
  analyze.py             cleaning, summaries, and statistical tests
  out/                   generated analysis tables
  figures/               exported PNGs
  export_figures.sh      batch figure export on macOS

data/                     local, Git-ignored snapshot and processing workspace
  source-data/             raw CSV/JSON and neighborhood boundaries
  data-clean/              cleaned event CSV
  data-analysis/           host profiles and reports
  output/                  guest-count outputs and cache
  scripts/                 inference and analysis utilities
```

The public repository includes the pages, prebuilt `web/data.js`, analysis code and tables, and exported images. The `data/`, `docs/`, and `docs-local/` directories are intentionally excluded by `.gitignore`. A fresh clone can display the existing snapshot but cannot rebuild or independently audit the source extraction without the local data files.

---

## Quick start

From the repository root:

```bash
cd web
python3 -m http.server 8000
```

Open [http://localhost:8000/index.html](http://localhost:8000/index.html) for the overview or [http://localhost:8000/map.html](http://localhost:8000/map.html) for the street map. The street basemap, MapLibre, and web fonts require internet access; the event data is served locally from `data.js`.

To rebuild **only if you have the local, Git-ignored** `data/` **snapshot**, install `numpy`, `pandas`, and `scipy`, then run from the repository root:

```bash
python3 data/scripts/infer_audience.py
python3 analysis/analyze.py
python3 web/build_data.py
python3 data/scripts/analyze_hosts.py
```

On macOS with Google Chrome installed, `zsh analysis/export_figures.sh` regenerates the PNG figures after `web/data.js` is rebuilt.

---

Sources: [SF Tech Week calendar](https://www.tech-week.com/calendar/sf) for events and [DataSF Analysis Neighborhoods](https://data.sfgov.org/) for the boundary reference. The map uses [OpenFreeMap](https://openfreemap.org/) and OpenStreetMap contributors for its street basemap.
