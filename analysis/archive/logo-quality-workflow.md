# Host Logo Quality Workflow

This workflow defines how host logos should be reviewed, cleaned, replaced, and prepared for the SF Tech Week neighborhood map.

The goal is not to show every available image. The goal is to show trustworthy, readable organization logos that help users understand which hosts shape each neighborhood.

## Why this workflow exists

The current host icon dataset contains several image types:

- official company or organization logos
- Partiful profile images
- personal headshots
- Tech Week default logos
- event artwork
- low-quality or unclear images

For the new map UI, only reliable host logos should appear inside neighborhood boundaries. Person avatars and default Tech Week logos should not be used as map logos.

## Logo manifest fields

| Field | Purpose | Example |
| --- | --- | --- |
| `host_name` | Canonical host/company name used in the dataset. | `Google for Startups` |
| `current_icon_file` | Existing icon file from the current Partiful/icon pipeline. | `icons/processed/google-for-startups.png` |
| `current_icon_source` | Where the current icon came from. | `partiful`, `manual`, `official_site`, `favicon`, `unknown` |
| `current_icon_type` | Type of the current image. | `official_logo`, `partiful_logo`, `person_avatar`, `tech_week_default`, `event_artwork`, `unknown` |
| `displayable_on_map` | Whether this icon is safe to display on the map now. | `true`, `false` |
| `needs_logo_replacement` | Whether the icon should be replaced before map use. | `true`, `false` |
| `replacement_query` | Search query to find a better official logo. | `Google for Startups logo svg` |
| `official_logo_source_url` | Source URL for the replacement logo. Prefer official brand/media/assets pages. | `https://...` |
| `replacement_icon_file` | Raw downloaded replacement logo file. | `icons/replacements/raw/google-for-startups.svg` |
| `processed_icon_file` | Final map-ready icon file. | `icons/replacements/processed/google-for-startups.png` |
| `confidence` | Confidence that the displayed icon represents the host correctly. | `high`, `medium`, `low` |
| `needs_manual_review` | Whether a human should review before final map display. | `true`, `false` |
| `review_status` | Current review stage. | `pending`, `approved`, `rejected`, `replaced` |
| `notes` | Short explanation of any ambiguity or decision. | `Partiful image is a person avatar; replaced with official company logo.` |

## Icon type definitions

| Icon type | Meaning | Map display rule |
| --- | --- | --- |
| `official_logo` | Logo from the host's official site, official brand assets, verified social profile, or trusted organization page. | Show on map. |
| `partiful_logo` | Logo extracted from the Partiful event page and visually appears to be an organization logo. | Show if confidence is medium/high. |
| `favicon` | Browser/site favicon from the host's official domain. | Show only when readable at small size. |
| `person_avatar` | A headshot, selfie, personal profile photo, or human portrait. | Do not show on map. Replace if the host is an organization. |
| `tech_week_default` | Tech Week default host/profile image. | Do not show on map. Replace with the actual host logo when possible. |
| `event_artwork` | Event poster, flyer, generated art, venue photo, or composite image. | Do not show as host logo. |
| `unknown` | Image cannot be confidently classified. | Hide until reviewed. |

## Filtering rules

### Always hide from map

- `current_icon_type = person_avatar`
- `current_icon_type = tech_week_default`
- `current_icon_type = event_artwork`
- `confidence = low`
- `needs_manual_review = true`
- images that are unreadable below 32px
- images that are mostly text and lose meaning at marker size

### Prefer for map display

- `official_logo`
- simple symbol-only logos
- high-contrast logos
- square or transparent-background assets
- logos that remain recognizable at 32px to 48px

### Accept with caution

- Partiful logos that clearly represent an organization
- favicons if no better official logo exists
- wordmarks only if short and readable

## Replacement search strategy

Use this order when replacing poor icons:

1. Official website brand/media/press kit
2. Official website header logo or favicon
3. Official LinkedIn/company profile image
4. Official GitHub organization avatar
5. Crunchbase / Wellfound / reputable company database
6. Manual fallback icon only if no official logo can be found

Recommended search query patterns:

| Host type | Query pattern |
| --- | --- |
| Startup/company | `{host_name} logo svg` |
| VC/fund | `{host_name} capital logo` |
| Community/org | `{host_name} organization logo` |
| University/lab | `{host_name} lab logo` |
| Ambiguous host | `{host_name} SF Tech Week company` |

## Processing rules

Final map-ready icons should be processed into a consistent visual system:

- square canvas, recommended `256 x 256`
- transparent background preferred
- centered logo mark
- no extra text if the symbol alone is recognizable
- preserve brand color when useful
- add a subtle white or neutral circular backing in the UI, not inside the source image
- export PNG for map rendering stability

## Neighborhood map usage

Each neighborhood should display only a small number of top host logos.

Recommended default:

- low zoom: show neighborhood polygon + heat color only
- medium zoom: show top 5 to 8 displayable host logos per neighborhood
- high zoom: show event-level host markers or expanded host clusters

Suggested host ranking inside each neighborhood:

```text
host_map_score =
  total_public_guest_count
  + event_count * 25
  + featured_event_count * 50
```

If guest count is missing, fall back to event count.

## Map display eligibility

A host logo can appear on the map only when:

```text
displayable_on_map = true
needs_logo_replacement = false
needs_manual_review = false
confidence in high or medium
processed_icon_file is present
```

## Manual review checklist

Before approving a logo:

- Does the image represent the organization, not a person?
- Is it not the Tech Week default logo?
- Is the source credible?
- Is it readable at 32px?
- Does the host name match the organization?
- Is the logo suitable for a public-facing visualization?

## Output files

Recommended files for this workflow:

```text
analysis/host-analysis/logo-quality-workflow.md
analysis/host-analysis/logo-quality-manifest-template.csv
analysis/host-analysis/logo-quality-manifest.csv
data/00-ready-to-use-data/neighborhood-host-logo-summary.json
```

