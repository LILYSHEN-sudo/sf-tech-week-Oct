# SF Tech Week 2026 Data & Map

An open dataset and interactive map for exploring 1,714 events listed for SF Tech Week 2026.

## Explore

- Open [`web/index.html`](web/index.html) for the main visualization.
- Open [`web/map.html`](web/map.html) for the interactive event map.

## Rebuild

```bash
python3 data/infer_audience.py
python3 analysis/analyze.py
python3 web/build_data.py
```

The dataset reflects the public event calendar captured on September 23, 2026. Event details may change before the conference.

