# SF Tech Week 2026 Event Intelligence Map

[Open the interactive map](https://lilyshen-sudo.github.io/sf-tech-week-Oct/)

**1,700+ events, one week, and no single venue.** This project turns a snapshot of the official SF Tech Week calendar into a neighborhood-first event map with inferred audience and intent filters, public Partiful links, visible guest-count signals, and neighborhood-level density storytelling.

The site is a historical snapshot, not a live registration feed. Event locations are based on host-supplied neighborhood labels, so map circles represent approximate neighborhood centers rather than venue-level addresses.

---

## Current Status

The project is now centered on `web/index.html`: a full-screen MapLibre map with floating filter cards, a right-side neighborhood detail drawer, density bubbles, and an intro timeline animation.

Latest map behavior:

- Opens with an automatic replay from the first timed event on October 5 to the last timed event on October 11.
- Clicking any left-side filter switches the map into a static filtered view.
- The `Replay` control replays the currently selected subset.
- Clicking a neighborhood circle opens a right-side detail card with neighborhood signal, top theme mix, and the first visible events.
- Circle color indicates event density per neighborhood: `1-9`, `10-39`, `40+`.

The active web payload in `web/data.js` contains:

| Item | Count |
| --- | ---: |
| Events in web map payload | 1,711 |
| Timed events used by replay | 1,707 |
| Uncertain-time events | 4 |
| Neighborhood labels | 45 |
| Official themes | 23 |
| Formats | 10 |
| Audience labels | 8 |
| Intent labels | 7 |

The current local slim master is `data/00-ready-to-use-data/sf-tech-week-events-master-slim.json` with `1,721` rows. In that file, `intent_inferred` is filled for all rows; `audience_inferred` still has `107` empty rows and is the main remaining labeling gap.

---

## Product Goal

The official calendar is good for finding individual events, but it is hard to understand the week as a system. Events span seven days, many formats, many host types, and dozens of location labels. This project makes the week explorable without pretending to have venue-level precision.

The map focuses on four questions:

- Where is activity concentrated?
- How does the week unfold over time?
- Which events are relevant to different audiences?
- Which intent does an event mainly serve: funding, networking, building, learning, consumer, hiring, or entertainment?

`audience_inferred` and `intent_inferred` are project estimates. They are not official Tech Week fields, not attendance counts, and not judgments of event quality.

---

## Architecture

```text
SOURCE
  official SF Tech Week calendar snapshot
  public Tech Week /go/event redirects
  public Partiful pages and host/image metadata
        |
        v
LOCAL DATA
  data/interim/sf-tech-week-master.csv/json
  data/00-ready-to-use-data/sf-tech-week-events-master-slim.json
        |
        v
ANALYSIS
  analysis/audience-intent-analysis/
  scripts/*audience* and scripts/*intent*
  analysis/archive/ for older lift/logo experiments
        |
        v
WEB ARTIFACTS
  web/data.js
  web/event-meta.js
  web/partiful-links.js
        |
        v
STATIC SITE
  web/index.html
```

The browser does not scrape Tech Week or Partiful. Python and local scripts prepare a static payload, and the page filters that payload client-side.

---

## Map Experience

`web/index.html` is the main experience.

Core UI:

- Floating left control card for role, goal, date, start time, topic, and type.
- Top map search for event or host.
- Replay card showing the current timeline point and replay progress.
- Bottom-right map stats card with event count, density legend, and virtual/unknown-location note.
- Right-side neighborhood drawer for clicked circles.
- Dark OpenFreeMap basemap with MapLibre GL JS.

Filtering model:

- Role and goal filters are multi-select recommendation signals.
- Date and start-time filters toggle on/off with a second click.
- Topic and type use dropdowns because those lists are longer.
- Replay respects the current filters. After replay finishes, the map returns to the full static result for that same filter set.

Location model:

- San Francisco neighborhoods use hand-placed approximate centers.
- Bay Area labels such as Palo Alto or East Bay use indicative coordinates.
- Virtual and unknown locations are kept in the list/stat count but are not mapped unless explicitly added through the stats card.

---

## Audience And Intent Workflow

Audience and intent are the current data-design focus of the project.

Current labels:

```text
audience_inferred:
  Founder, Investor, Engineer, Marketing, Sales, HR, Creator, PM

intent_inferred:
  Funding, Networking, Building, Learning, Consumer, Hiring, Entertainment
```

Supporting files:

```text
analysis/audience-intent-analysis/
  category-label-method.md
  audience-evidence-audit.json
  audience-review-queue.json
  audience-unlabeled.json
  audience-manual-overrides.json
  audience-second-pass-summary.md
  intent-missing.json

scripts/
  infer_event_intents.py
  infer_audience_from_name.py
  add_audience_from_tracks.py
  add_audience_from_description.py
  add_audience_from_requested_fields.py
  add_creator_audience_from_theme.py
  audit_event_audiences.py
```

The practical approach is hybrid:

- Use explicit evidence first: tracks, themes, event titles, descriptions, and requested fields.
- Keep low-confidence audience cases in review queues instead of forcing labels.
- Allow multiple labels when an event genuinely spans audiences or intents.
- Keep `general` out of the web filter masks, so the user-facing filters remain meaningful.

---

## Data Flow

1. Capture the official calendar snapshot and public event fields.
2. Resolve public `/go/event` redirects to Partiful URLs.
3. Extract public Partiful metadata where available.
4. Build or update the local master data.
5. Infer audience and intent labels.
6. Run audits/manual review queues for uncertain labels.
7. Build `web/data.js`, `web/event-meta.js`, and `web/partiful-links.js`.
8. Serve the static map.

The local `data/` folder is intentionally not tracked in Git. The public repository includes the static site, analysis notes, inference scripts, archive materials, and prebuilt web artifacts needed for GitHub Pages.

---

## Project Structure

```text
web/
  index.html             main interactive map
  build_data.py          builds web/data.js from local ready data
  data.js                compact map payload
  event-meta.js          public guest-count and host/logo metadata
  partiful-links.js      final public Partiful URLs

analysis/
  audience-intent-analysis/
                         current category method, audit outputs, review queues
  archive/               old lift analysis and logo-quality experiments
  overview-analysis.md   current project-level analysis notes

scripts/
  inference and audit scripts for audience/intent fields

data/                    local, Git-ignored data workspace
  source-data/           raw evidence and extraction outputs
  interim/               current master working layer
  00-ready-to-use-data/  ready event master files used by web/build_data.py
```

---

## Quick Start

From the repository root:

```bash
cd web
python3 -m http.server 8000
```

Open:

- `http://localhost:8000/index.html`

The basemap, MapLibre, and web fonts require internet access. The event payload is served locally from `web/data.js`.

To rebuild the map payload after editing the local ready data:

```bash
cd web
python3 build_data.py
```

To inspect the current audience/intent gap:

```bash
node - <<'NODE'
const fs = require('fs');
const rows = JSON.parse(fs.readFileSync('data/00-ready-to-use-data/sf-tech-week-events-master-slim.json', 'utf8'));
const empty = v => v == null || v === '' || (Array.isArray(v) && v.length === 0);
for (const k of ['audience_inferred', 'intent_inferred']) {
  console.log(k, rows.filter(r => empty(r[k])).length, 'empty');
}
NODE
```

---

## Known Caveats

- The project is a dated snapshot, not a live feed.
- Map positions are approximate neighborhood centers.
- Public guest counts are only available when Partiful exposes them.
- Audience and intent labels are inferred and still under review, especially audience.
- The replay excludes uncertain-time events because they do not have reliable start times.

Sources: [SF Tech Week calendar](https://www.tech-week.com/calendar/sf), public Partiful event pages, [DataSF Analysis Neighborhoods](https://data.sfgov.org/), [OpenFreeMap](https://openfreemap.org/), and OpenStreetMap contributors.
