"""Clean SF Tech Week 2026 events and compute neighborhood / domain / hour stats.

Input : ../data/sf-tech-week-2026-events.csv  (run ../data/infer_audience.py first)
Output: ../data/sf-tech-week-2026-events-clean.csv
        ./out/*.csv  (tables used by docs/2-analysis.md and the map)

    python3 analyze.py
"""
import os
import re

import numpy as np
import pandas as pd
from scipy.stats import hypergeom

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

WEEK = ("2026-10-05", "2026-10-11")
MIN_HOOD_EVENTS = 25   # neighborhoods smaller than this are too noisy for lift
MIN_CELL_EVENTS = 5    # a hood x domain cell needs at least this many events
ALPHA = 0.05           # Benjamini-Hochberg false discovery rate

REGION = {
    "Palo Alto": "Peninsula & South Bay",
    "Stanford": "Peninsula & South Bay",
    "Mountain View": "Peninsula & South Bay",
    "San Mateo": "Peninsula & South Bay",
    "Hillsborough": "Peninsula & South Bay",
    "East Bay": "East Bay",
    "Virtual": "Virtual",
    "Other": "Unknown",
    "Unknown": "Unknown",
}

# Official themes / tracks grouped into video-friendly domains (multi-label).
# "AI" is on ~70% of events, so it is not a domain on its own.
DOMAINS = {
    "AI Agents & DevTools": ({"Engineering"}, {"AI Agents", "Developer Tools"}),
    "AI Infra & Compute": ({"Infrastructure"}, {"AI Infrastructure & Compute"}),
    "Deep Tech & Hardware": ({"Deep Tech", "Hardware", "Defense", "AR / VR"}, {"Deep Tech"}),
    "Bio & Health": ({"Healthcare / Healthtech"}, set()),
    "Fintech & Crypto": ({"Fintech", "Crypto / Web3"}, {"Fintech"}),
    "GTM & Sales": ({"GTM"}, set()),
    "Fundraising & Investing": ({"Fundraising / Investing"}, {"Fundraising & Investing"}),
    "Creator, Media & Consumer": (
        {"Creators", "Media / Entertainment", "B2C / Consumer", "Gaming"},
        {"Consumer & Creative AI"},
    ),
    "Enterprise & SaaS": ({"B2B", "SaaS"}, {"Enterprise AI"}),
    "Global Founders": ({"International / Expansion"}, {"Global Founders"}),
    "Cybersecurity": ({"Cybersecurity"}, set()),
    "Climate": ({"Climate"}, set()),
    "People & Hiring": ({"HR / Hiring"}, set()),
    "Women-focused": ({"Women-focused"}, set()),
}


def split(value):
    return [v.strip() for v in str(value).split(";") if v.strip() and v != "nan"]


def clean_name(name):
    name = re.sub(r"[​‌‍‎‏﻿]", "", str(name))
    return re.sub(r"\s+", " ", name).strip()


def load_and_clean():
    df = pd.read_csv(os.path.join(DATA, "sf-tech-week-2026-events.csv"), dtype=str, keep_default_na=False)
    df["name"] = df["name"].map(clean_name)
    df["neighborhood_clean"] = (
        df["neighborhood"].str.replace(r"\s*\(SF\)$", "", regex=True).replace("", "Unknown")
    )
    df["region"] = df["neighborhood_clean"].map(REGION).fillna("San Francisco")
    df["registration_status"] = df["registration_status"].replace("", "unknown")
    df["hour"] = df["time"].str.slice(0, 2).astype(int)
    df["in_week"] = df["date"].between(*WEEK)
    # Starts between 00:00 and 05:59 are placeholders or entry errors.
    df["time_suspect"] = df["hour"] < 6

    # Same name + date + time listed twice: keep the copy with more official tags.
    df["n_tags"] = df["themes"].map(lambda v: len(split(v))) + df["formats"].map(lambda v: len(split(v)))
    key = df["name"].str.lower() + "|" + df["date"] + "|" + df["time"]
    order = df.assign(_key=key).sort_values("n_tags", ascending=False)
    df["is_duplicate"] = order.duplicated("_key", keep="first").reindex(df.index)

    for domain, (themes, tracks) in DOMAINS.items():
        df[domain] = df.apply(
            lambda r: bool(set(split(r["themes"])) & themes or set(split(r["tracks"])) & tracks), axis=1
        )
    df["domains"] = df.apply(lambda r: "; ".join(d for d in DOMAINS if r[d]), axis=1)
    df.drop(columns=["n_tags"], inplace=True)
    return df


def bh(pvals):
    """Benjamini-Hochberg adjusted p-values."""
    p = np.asarray(pvals, dtype=float)
    n = len(p)
    order = np.argsort(p)
    ranked = p[order] * n / (np.arange(n) + 1)
    q = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(n)
    out[order] = np.minimum(q, 1)
    return out


def lift_table(physical, big, groups, label):
    """Hypergeometric over-representation of each group in each big neighborhood, BH-corrected."""
    N = len(physical)
    rows = []
    for h in big:
        in_hood = physical["neighborhood_clean"] == h
        n = int(in_hood.sum())
        for name, mask in groups.items():
            K = int(mask.sum())
            k = int((mask & in_hood).sum())
            expected = n * K / N
            rows.append({
                "neighborhood": h, label: name, "hood_events": n, f"{label}_events_in_hood": k,
                "share_in_hood_pct": round(k / n * 100, 1), "share_citywide_pct": round(K / N * 100, 1),
                "expected": round(expected, 1), "lift": round(k / expected, 2) if expected else np.nan,
                "p_over": hypergeom.sf(k - 1, N, K, n),   # P(X >= k): over-represented
            })
    lift = pd.DataFrame(rows)
    lift["q_over"] = bh(lift["p_over"])
    lift["significant_cluster"] = (lift["q_over"] < ALPHA) & (lift[f"{label}_events_in_hood"] >= MIN_CELL_EVENTS) & (lift["lift"] > 1)
    lift["p_over"] = lift["p_over"].round(4)
    lift["q_over"] = lift["q_over"].round(4)
    return lift


def main():
    df = load_and_clean()
    export_cols = [c for c in df.columns if c not in DOMAINS]
    df[export_cols].to_csv(os.path.join(DATA, "sf-tech-week-2026-events-clean.csv"), index=False)

    base = df[df["in_week"] & ~df["is_duplicate"]]
    physical = base[~base["region"].isin(["Virtual", "Unknown"])]
    timed = base[~base["time_suspect"]]
    summary = {
        "raw_rows": len(df),
        "in_week": int(df["in_week"].sum()),
        "duplicates_removed": int((df["in_week"] & df["is_duplicate"]).sum()),
        "analysis_base": len(base),
        "physical_location": len(physical),
        "virtual": int((base["region"] == "Virtual").sum()),
        "unknown_location": int((base["region"] == "Unknown").sum()),
        "time_suspect_excluded_from_hourly": int(base["time_suspect"].sum()),
    }
    pd.Series(summary).to_csv(os.path.join(OUT, "00_summary.csv"), header=["value"])

    # 1. Neighborhood counts
    hood = (
        base.groupby(["region", "neighborhood_clean"]).size().rename("events").reset_index()
        .sort_values("events", ascending=False)
    )
    hood["share_pct"] = (hood["events"] / len(base) * 100).round(1)
    hood["cum_share_pct"] = hood["share_pct"].cumsum().round(1)
    hood.to_csv(os.path.join(OUT, "01_neighborhood_counts.csv"), index=False)
    base.groupby("region").size().rename("events").sort_values(ascending=False).to_csv(
        os.path.join(OUT, "01b_region_counts.csv")
    )

    # 2. Domain counts
    dom_counts = pd.Series({d: int(base[d].sum()) for d in DOMAINS}).sort_values(ascending=False)
    dom_counts.rename("events").to_csv(os.path.join(OUT, "02_domain_counts.csv"), header=True)

    # 3. Neighborhood x domain lift (physical events only)
    big = physical["neighborhood_clean"].value_counts()
    big = big[big >= MIN_HOOD_EVENTS].index
    lift = lift_table(physical, big, {d: physical[d] for d in DOMAINS}, "domain")
    lift.sort_values(["significant_cluster", "lift"], ascending=[False, False]).to_csv(
        os.path.join(OUT, "03_neighborhood_domain_lift.csv"), index=False
    )
    lift.pivot(index="neighborhood", columns="domain", values="lift").loc[big].to_csv(
        os.path.join(OUT, "03b_lift_matrix.csv")
    )

    # 3c. Same test on the 23 official themes (used by the web map's topic buttons)
    themes = sorted({t for v in base["themes"] for t in split(v)})
    theme_cols = {t: physical["themes"].apply(lambda v, t=t: t in split(v)) for t in themes}
    tlift = lift_table(physical, big, theme_cols, "theme")
    tlift.sort_values(["significant_cluster", "lift"], ascending=[False, False]).to_csv(
        os.path.join(OUT, "03c_neighborhood_theme_lift.csv"), index=False
    )

    # 4. Hour distribution
    by_hour = timed.groupby("hour").size().rename("events")
    by_hour = by_hour.reindex(range(6, 24), fill_value=0)
    pd.DataFrame({"events": by_hour, "share_pct": (by_hour / by_hour.sum() * 100).round(1)}).to_csv(
        os.path.join(OUT, "04_hour_counts.csv")
    )
    timed.pivot_table(index="hour", columns="date", values="id", aggfunc="count", fill_value=0).to_csv(
        os.path.join(OUT, "04b_hour_by_day.csv")
    )
    hd = pd.DataFrame({d: timed[timed[d]].groupby("hour").size() for d in DOMAINS}).reindex(range(6, 24)).fillna(0).astype(int)
    hd.to_csv(os.path.join(OUT, "04c_hour_by_domain.csv"))

    def bucket(h):
        return "Morning (6-11)" if h < 12 else "Midday (12-16)" if h < 17 else "Evening (17+)"
    tb = timed.assign(bucket=timed["hour"].map(bucket))
    prof = pd.DataFrame({
        d: tb[tb[d]]["bucket"].value_counts(normalize=True).mul(100).round(1) for d in DOMAINS
    }).T.fillna(0)
    prof["events"] = [int(timed[d].sum()) for d in prof.index]
    prof["median_start_hour"] = [float(timed[timed[d]]["hour"].median()) for d in prof.index]
    prof = prof[["events", "Morning (6-11)", "Midday (12-16)", "Evening (17+)", "median_start_hour"]]
    prof.sort_values("Evening (17+)").to_csv(os.path.join(OUT, "04d_domain_time_profile.csv"))

    # 5. Day x domain (bonus: which day suits which domain)
    day_dom = pd.DataFrame({d: base[base[d]].groupby("date").size() for d in DOMAINS}).fillna(0).astype(int)
    day_dom.insert(0, "all_events", base.groupby("date").size())
    day_dom.to_csv(os.path.join(OUT, "05_day_by_domain.csv"))

    print(pd.Series(summary).to_string())
    print(f"\nwrote tables to {OUT}")


if __name__ == "__main__":
    main()
