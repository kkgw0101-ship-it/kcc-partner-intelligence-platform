# CALI Partner Intelligence Desk

External-facing Streamlit demo prepared for the CALI visit on July 7, 2026.

The app demonstrates why KCC Glass is a credible LVT partner for CALI, using interactive storytelling rather than uploading the brochure PDF directly.

Meeting focus:

- Hero trust numbers: 6,000,000m2 annual capacity, $1.3B sales, 1,300 artworks / print rolls
- Clickable KCC Glass milestone timeline from 1958 to 2024
- Technology proof: Egis annealing, R11 non-slip, 13dB acoustic performance
- OEM spec finder for Plank / Tile, Dryback / Looselay, thickness, wear layer, and size options
- Hero motion background: `cali_wave_hero.gif` is included. If you later add `cali_wave_hero.mp4`, the app will use the MP4 first.

## Main App

```text
kcc_partner_intelligence_platform.py
```

## Streamlit Secrets

Add this in Streamlit Cloud app settings:

```toml
FRED_API_KEY = "YOUR_FRED_API_KEY"
```

The app can still open without the key, but live FRED charts will wait for the API key.

## Included Files

- `kcc_partner_intelligence_platform.py`
- `requirements.txt`
- `cali_logo.png`
- `freight_index_records.json`
- `logo_white_t.png`
- `logo_navy_t.png`
- `favicon_kcc.png`
- `homecc_lvt_design_library_hero.png`
- `kcc_company_video_thumb.jpg`
- `cali_wave_hero.gif`
- Optional: `cali_wave_hero.mp4`

## External Sharing Scope

This repo is designed to exclude internal CRM files, ImportYeti data, customer maps, margin tools, internal purchase workflows, `.env`, and Streamlit secrets.

## Design Library

Primary LVT design reference:

```text
https://www.homecc.com/lvt/designlibrary.do
```
