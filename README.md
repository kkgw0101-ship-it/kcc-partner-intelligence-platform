# CALI Partner Intelligence Desk

External-facing Streamlit demo prepared for the CALI visit on July 7, 2026.

The app demonstrates how KCC can support CALI with California-lifestyle positioning, market signals, freight timing, HomeCC LVT design access, product confidence, ESG resources, and follow-up rhythm in one customer-care workspace.

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

## External Sharing Scope

This repo is designed to exclude internal CRM files, ImportYeti data, customer maps, margin tools, internal purchase workflows, `.env`, and Streamlit secrets.

## Design Library

Primary LVT design reference:

```text
https://www.homecc.com/lvt/designlibrary.do
```
