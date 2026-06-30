"""
KCC Partner Intelligence Platform
External-facing Streamlit portal for customer promotion and partner enablement.

This file is intentionally separate from app_v6_share.py so the internal
intelligence platform can keep evolving without exposing internal workflows.
"""

from __future__ import annotations

import base64
import io
import json
import os
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st


APP_DIR = os.path.dirname(__file__)

NAVY = "#071328"
NAVY_2 = "#0D1C35"
INK = "#F7FAFC"
MUTED = "#9AA7BA"
PANEL = "#111B2D"
PANEL_2 = "#18243A"
LINE = "#2A3A56"
GOLD = "#D9A441"
BLUE = "#3B82F6"
GREEN = "#16A34A"
RED = "#DC2626"
SOFT = "#EAF0F7"
KCC_BLUE = "#0E2372"

PAGE_ICON = os.path.join(APP_DIR, "favicon_kcc.png")
if not os.path.exists(PAGE_ICON):
    PAGE_ICON = "KCC"

st.set_page_config(
    page_title="KCC Partner Intelligence Platform",
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_secret(name: str, default: str = "") -> str:
    try:
        return st.secrets.get(name, os.environ.get(name, default))
    except Exception:
        return os.environ.get(name, default)


def image_b64(file_name: str) -> str:
    path = os.path.join(APP_DIR, file_name)
    try:
        with open(path, "rb") as handle:
            return base64.b64encode(handle.read()).decode("utf-8")
    except Exception:
        return ""


FRED_API_KEY = get_secret("FRED_API_KEY", "")
KCC_LOGO_WHITE = image_b64("logo_white_t.png")
KCC_LOGO_NAVY = image_b64("logo_navy_t.png")
HERO_IMAGE = image_b64("homecc_lvt_design_library_hero.png")
VIDEO_THUMB = image_b64("kcc_company_video_thumb.jpg")

KCC_HOME_URL = "https://www.kccglass.co.kr/eng/"
KCC_ESG_URL = "https://www.kccglass.co.kr/eng/esgManagement/about/report.do"
KCC_PRODUCT_URL = "https://www.kccglass.co.kr/eng/product/interiorFlooring.do"
HOMECC_DESIGN_LIBRARY_URL = "https://www.homecc.com/lvt/designlibrary.do"


st.markdown(
    f"""
<style>
[data-testid="stAppViewContainer"] {{ background:{NAVY}; color:{INK}; }}
[data-testid="stHeader"] {{ background:transparent; height:0; }}
#MainMenu, footer, [data-testid="stToolbar"] {{ visibility:hidden; }}
.block-container {{ padding:1rem 1.4rem 2.4rem; max-width:1440px; }}
* {{ letter-spacing:0; font-variant-numeric:tabular-nums; }}

[data-testid="stSidebar"] {{ background:#08111F; border-right:1px solid {LINE}; }}
[data-testid="stSidebar"] * {{ color:{INK}; }}
[data-testid="stSidebar"] a {{ color:{SOFT} !important; text-decoration:none; }}
[data-testid="stSidebar"] .stDownloadButton button {{
  background:{GOLD} !important; color:#101827 !important; border:0 !important;
  border-radius:7px !important; font-weight:900 !important;
}}
.side-logo {{ width:116px; background:{KCC_BLUE}; border-radius:7px; padding:8px 10px; margin:6px 0 10px; }}
.side-title {{ font-size:15px; font-weight:900; line-height:1.25; margin-bottom:6px; }}
.side-copy {{ color:{MUTED}; font-size:12px; line-height:1.55; margin-bottom:14px; }}
.side-link {{ display:block; padding:8px 10px; border:1px solid {LINE}; border-radius:7px; margin:6px 0; background:rgba(255,255,255,.03); font-size:12px; font-weight:800; }}
.side-note {{ color:{MUTED}; font-size:11px; line-height:1.55; margin-top:12px; }}

.ticker {{ height:34px; overflow:hidden; border:1px solid {LINE}; border-radius:8px; background:#060C17; display:flex; align-items:center; margin-bottom:12px; }}
.ticker-track {{ display:flex; width:max-content; animation:tickerFlow 44s linear infinite; }}
.ticker-set {{ display:flex; flex-shrink:0; min-width:max-content; }}
.ticker-item {{ display:inline-flex; align-items:center; gap:8px; padding:0 24px; white-space:nowrap; color:{SOFT}; font-size:12px; font-weight:900; }}
.ticker-label {{ color:{MUTED}; text-transform:uppercase; }}
.up {{ color:#4ADE80; }}
.down {{ color:#FB7185; }}
@keyframes tickerFlow {{ from {{ transform:translateX(0); }} to {{ transform:translateX(-50%); }} }}

.hero {{
  min-height:570px; border-radius:14px; overflow:hidden; position:relative; margin-bottom:14px;
  border:1px solid {LINE}; box-shadow:0 26px 80px rgba(0,0,0,.30);
  background:
    linear-gradient(90deg, rgba(7,19,40,.96) 0%, rgba(7,19,40,.80) 43%, rgba(7,19,40,.24) 100%),
    url("data:image/png;base64,{HERO_IMAGE}"),
    url("data:image/jpeg;base64,{VIDEO_THUMB}");
  background-size:cover; background-position:center;
}}
.hero-inner {{ position:absolute; inset:0; padding:54px 58px; display:flex; flex-direction:column; justify-content:space-between; }}
.logo-row {{ display:flex; align-items:center; gap:16px; margin-bottom:28px; }}
.hero-logo {{ height:42px; width:auto; background:{KCC_BLUE}; border-radius:7px; padding:8px 12px; }}
.eyebrow {{ color:{GOLD}; font-size:12px; font-weight:900; text-transform:uppercase; letter-spacing:2px; }}
.h1 {{ color:#fff; font-size:50px; line-height:1.05; font-weight:900; max-width:820px; margin:12px 0 14px; }}
.hero-copy {{ color:#DDE6F3; font-size:16px; line-height:1.65; max-width:760px; }}
.hero-pills {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:20px; }}
.pill {{ display:inline-flex; align-items:center; border:1px solid rgba(217,164,65,.55); background:rgba(8,17,31,.72); color:#fff; border-radius:999px; padding:8px 12px; font-size:12px; font-weight:900; }}
.hero-grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; max-width:920px; }}
.hero-metric {{ min-height:108px; border:1px solid rgba(255,255,255,.14); border-radius:8px; padding:13px; background:rgba(8,17,31,.76); backdrop-filter:blur(8px); }}
.metric-k {{ color:{MUTED}; font-size:10px; font-weight:900; text-transform:uppercase; }}
.metric-v {{ color:{INK}; font-size:24px; font-weight:900; margin-top:7px; }}
.metric-c {{ color:{MUTED}; font-size:11px; line-height:1.45; margin-top:5px; }}

.section-title {{ display:flex; align-items:baseline; justify-content:space-between; gap:12px; margin:22px 0 10px; }}
.section-title h2 {{ color:{INK}; font-size:22px; margin:0; }}
.section-title span {{ color:{MUTED}; font-size:11px; font-weight:800; text-transform:uppercase; }}
.grid4 {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; }}
.grid3 {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; }}
.grid2 {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
.card {{ background:{PANEL}; border:1px solid {LINE}; border-radius:8px; padding:15px; min-height:120px; }}
.card.gold {{ border-left:4px solid {GOLD}; }}
.card.blue {{ border-left:4px solid {BLUE}; }}
.card.green {{ border-left:4px solid {GREEN}; }}
.card.red {{ border-left:4px solid {RED}; }}
.card-title {{ color:{INK}; font-size:15px; font-weight:900; margin-bottom:7px; }}
.card-copy {{ color:{MUTED}; font-size:12px; line-height:1.55; }}
.card-value {{ color:{INK}; font-size:27px; font-weight:900; margin-top:8px; }}
.panel {{ background:{PANEL}; border:1px solid {LINE}; border-radius:8px; overflow:hidden; margin-bottom:12px; }}
.panel-head {{ display:flex; justify-content:space-between; gap:12px; align-items:center; padding:12px 14px; border-bottom:1px solid {LINE}; background:{PANEL_2}; }}
.panel-title {{ color:{INK}; font-size:13px; font-weight:900; }}
.panel-meta {{ color:{MUTED}; font-size:10px; font-weight:800; text-transform:uppercase; }}
.panel-body {{ padding:14px; }}
.brief {{ color:#DCE6F2; font-size:13px; line-height:1.65; background:{PANEL_2}; border:1px solid {LINE}; border-left:4px solid {GOLD}; border-radius:8px; padding:13px 14px; margin-bottom:12px; }}
.link-button {{ display:inline-flex; padding:9px 12px; background:{GOLD}; color:#101827 !important; border-radius:7px; text-decoration:none !important; font-size:12px; font-weight:900; margin-right:7px; margin-bottom:7px; }}
.link-button.secondary {{ background:{PANEL_2}; color:{INK} !important; border:1px solid {LINE}; }}
.product-band {{ min-height:250px; border:1px solid {LINE}; border-radius:8px; overflow:hidden; position:relative; background:url("data:image/png;base64,{HERO_IMAGE}"); background-size:cover; background-position:center; }}
.product-band::after {{ content:""; position:absolute; inset:0; background:linear-gradient(90deg,rgba(7,19,40,.92),rgba(7,19,40,.24)); }}
.product-band-content {{ position:absolute; z-index:1; inset:0; padding:26px; display:flex; flex-direction:column; justify-content:flex-end; max-width:680px; }}
.product-title {{ color:#fff; font-size:30px; font-weight:900; line-height:1.15; }}
.product-copy {{ color:#DDE6F3; font-size:14px; line-height:1.6; margin-top:9px; }}
.footer-note {{ margin-top:20px; color:{MUTED}; font-size:11px; line-height:1.55; border-top:1px solid {LINE}; padding-top:12px; }}

div[data-testid="stDataFrame"] {{ border:1px solid {LINE}; border-radius:8px; overflow:hidden; }}
.stButton button, .stDownloadButton button {{ border-radius:7px !important; font-weight:900 !important; }}

@media (max-width: 1050px) {{
  .grid4, .hero-grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }}
  .grid3, .grid2 {{ grid-template-columns:1fr; }}
  .h1 {{ font-size:36px; }}
}}
@media (max-width: 700px) {{
  .hero {{ min-height:780px; }}
  .hero-inner {{ padding:28px 24px; }}
  .hero-grid, .grid4 {{ grid-template-columns:1fr; }}
  .h1 {{ font-size:30px; }}
}}
</style>
""",
    unsafe_allow_html=True,
)


def fmt_num(value: float | int | None, unit: str = "", decimals: int = 1) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    if decimals == 0:
        base = f"{float(value):,.0f}"
    else:
        base = f"{float(value):,.{decimals}f}"
    return f"{base}{unit}"


def latest(frame: pd.DataFrame, col: str) -> float | None:
    if frame.empty or col not in frame:
        return None
    clean = pd.to_numeric(frame[col], errors="coerce").dropna()
    if clean.empty:
        return None
    return float(clean.iloc[-1])


def delta_pct(frame: pd.DataFrame, col: str, periods: int = 1) -> float | None:
    if frame.empty or col not in frame:
        return None
    clean = pd.to_numeric(frame[col], errors="coerce").dropna()
    if len(clean) <= periods or clean.iloc[-1 - periods] == 0:
        return None
    return float((clean.iloc[-1] - clean.iloc[-1 - periods]) / clean.iloc[-1 - periods] * 100)


def last_date(frame: pd.DataFrame) -> str:
    if frame.empty or "date" not in frame:
        return "waiting"
    return pd.to_datetime(frame["date"]).max().strftime("%Y-%m-%d")


@st.cache_data(ttl=21600)
def get_fred(series_id: str, label: str) -> pd.DataFrame:
    if not FRED_API_KEY:
        return pd.DataFrame(columns=["date", label])
    url = (
        "https://api.stlouisfed.org/fred/series/observations"
        f"?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json"
        "&observation_start=2020-01-01"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        rows = response.json().get("observations", [])
        frame = pd.DataFrame(rows)
        frame["date"] = pd.to_datetime(frame["date"])
        frame[label] = pd.to_numeric(frame["value"], errors="coerce")
        return frame[["date", label]].dropna()
    except Exception:
        return pd.DataFrame(columns=["date", label])


@st.cache_data
def load_freight() -> pd.DataFrame:
    path = os.path.join(APP_DIR, "freight_index_records.json")
    try:
        with open(path, "r", encoding="utf-8") as handle:
            rows = json.load(handle)
        frame = pd.DataFrame(rows)
        frame["date"] = pd.to_datetime(frame["date"])
        return frame
    except Exception:
        return pd.DataFrame(columns=["date", "SCFI", "CCFI"])


def line_chart(frame: pd.DataFrame, cols: list[str], title: str, height: int = 270) -> go.Figure:
    fig = go.Figure()
    for col in cols:
        if col in frame:
            fig.add_trace(
                go.Scatter(
                    x=frame["date"],
                    y=frame[col],
                    mode="lines",
                    name=col,
                    line=dict(width=2.5),
                    hovertemplate="%{x|%Y-%m-%d}<br>%{y:,.2f}<extra></extra>",
                )
            )
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color="#101827")),
        height=height,
        margin=dict(l=12, r=12, t=36, b=10),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(size=11)),
        xaxis=dict(showgrid=True, gridcolor="#EEF2F7", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#EEF2F7", zeroline=False),
    )
    return fig


def section_title(title: str, meta: str) -> None:
    st.markdown(
        f'<div class="section-title"><h2>{title}</h2><span>{meta}</span></div>',
        unsafe_allow_html=True,
    )


def panel(title: str, meta: str = "") -> None:
    st.markdown(
        f'<div class="panel"><div class="panel-head"><div class="panel-title">{title}</div><div class="panel-meta">{meta}</div></div><div class="panel-body">',
        unsafe_allow_html=True,
    )


def close_panel() -> None:
    st.markdown("</div></div>", unsafe_allow_html=True)


def create_partner_brief_pdf(snapshot: dict[str, str], rows: pd.DataFrame) -> bytes:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ModuleNotFoundError:
        return simple_pdf_bytes(
            [
                "KCC Partner Intelligence Platform",
                f"Prepared {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "Market reference brief for flooring partners.",
            ]
            + [f"- {key}: {value}" for key, value in snapshot.items()]
        )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=14 * mm, leftMargin=14 * mm, topMargin=14 * mm, bottomMargin=14 * mm)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("KCC Partner Intelligence Platform", styles["Title"]),
        Spacer(1, 8),
        Paragraph(f"Market reference brief prepared {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph("Current Snapshot", styles["Heading2"]),
    ]
    snapshot_rows = [["Signal", "Read"]] + [[key, value] for key, value in snapshot.items()]
    table = Table(snapshot_rows, colWidths=[52 * mm, 116 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#071328")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#DDE4EE")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
            ]
        )
    )
    story.extend([table, Spacer(1, 14), Paragraph("Partner Use", styles["Heading2"])])
    partner_rows = [["Area", "How to use this with customers"]] + rows[["Area", "Partner Use"]].values.tolist()
    partner_table = Table(partner_rows, colWidths=[42 * mm, 126 * mm])
    partner_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0E2372")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#DDE4EE")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.extend([partner_table, Spacer(1, 12)])
    story.append(
        Paragraph(
            "Disclaimer: This brief is for market reference and partner discussion. Indicators are based on public data sources and selected external-safe monitoring records.",
            styles["Italic"],
        )
    )
    doc.build(story)
    return buffer.getvalue()


def simple_pdf_bytes(lines: list[str]) -> bytes:
    escaped = [line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") for line in lines]
    stream_lines = ["BT", "/F1 16 Tf", "72 790 Td", f"({escaped[0]}) Tj", "/F1 10 Tf"]
    for line in escaped[1:]:
        stream_lines.append("0 -18 Td")
        stream_lines.append(f"({line}) Tj")
    stream_lines.append("ET")
    stream = "\n".join(stream_lines).encode("latin-1", errors="replace")
    objects = [
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n",
        b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
        b"5 0 obj << /Length " + str(len(stream)).encode("ascii") + b" >> stream\n" + stream + b"\nendstream endobj\n",
    ]
    output = io.BytesIO()
    output.write(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(output.tell())
        output.write(obj)
    xref = output.tell()
    output.write(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.write(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.write(
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii")
    )
    return output.getvalue()


fred = {
    "housing": get_fred("HOUST", "Housing Starts"),
    "mortgage": get_fred("MORTGAGE30US", "30Y Mortgage"),
    "cpi": get_fred("CPIAUCSL", "CPI"),
    "fedfunds": get_fred("FEDFUNDS", "Fed Funds"),
    "new_home_sales": get_fred("HSN1F", "New Home Sales"),
    "permits": get_fred("PERMIT", "Building Permits"),
    "completions": get_fred("COMPUTSA", "Housing Completions"),
    "months_supply": get_fred("MSACSR", "New Home Supply"),
    "existing_sales": get_fred("EXHOSLUSM495S", "Existing Home Sales"),
    "building_retail": get_fred("MRTSSM4441USN", "Building Materials Retail"),
    "lumber_ppi": get_fred("WPU081", "Lumber PPI"),
    "building_ppi": get_fred("PCU44414441", "Building Materials PPI"),
    "wti": get_fred("DCOILWTICO", "WTI"),
    "brent": get_fred("DCOILBRENTEU", "Brent"),
    "fx": get_fred("DEXKOUS", "USD/KRW"),
}
freight = load_freight()

housing_now = latest(fred["housing"], "Housing Starts")
housing_delta = delta_pct(fred["housing"], "Housing Starts")
mortgage_now = latest(fred["mortgage"], "30Y Mortgage")
mortgage_delta = delta_pct(fred["mortgage"], "30Y Mortgage", periods=4)
cpi_now = latest(fred["cpi"], "CPI")
fed_now = latest(fred["fedfunds"], "Fed Funds")
fx_now = latest(fred["fx"], "USD/KRW")
fx_delta = delta_pct(fred["fx"], "USD/KRW", periods=20)
wti_now = latest(fred["wti"], "WTI")
wti_delta = delta_pct(fred["wti"], "WTI", periods=20)
scfi_now = latest(freight, "SCFI")
scfi_delta = delta_pct(freight, "SCFI", periods=4)

snapshot = {
    "Housing Starts": f"{fmt_num(housing_now, 'K', 0)} ({fmt_num(housing_delta, '%', 1)} MoM)",
    "30Y Mortgage": f"{fmt_num(mortgage_now, '%', 2)} ({fmt_num(mortgage_delta, '%', 1)} 4W)",
    "USD/KRW": f"{fmt_num(fx_now, '', 0)} ({fmt_num(fx_delta, '%', 1)} 20D)",
    "WTI Oil": f"{fmt_num(wti_now, '$/bbl', 1)} ({fmt_num(wti_delta, '%', 1)} 20D)",
    "SCFI Freight": f"{fmt_num(scfi_now, '', 0)} ({fmt_num(scfi_delta, '%', 1)} 4W)",
}

partner_rows = pd.DataFrame(
    [
        ["Market Timing", "Use public macro and housing indicators to support launch timing, quote cadence, and demand discussion."],
        ["Freight Watch", "Use freight direction as a neutral reason to discuss shipment timing and replenishment planning earlier."],
        ["Product Confidence", "Use KCC manufacturing, quality, design, and ESG materials as credibility layers in builder and dealer conversations."],
        ["Design Support", "Use neutral, wood-forward LVT trend language to help sales teams connect products to current interior preferences."],
        ["Follow-up", "Share the brief link before a call so the buyer has a reason to re-open the conversation without another attachment."],
    ],
    columns=["Area", "Partner Use"],
)

logo_white_html = f'<img class="hero-logo" src="data:image/png;base64,{KCC_LOGO_WHITE}" alt="KCC Glass">' if KCC_LOGO_WHITE else "<strong>KCC GLASS</strong>"
logo_navy_html = f'<img class="side-logo" src="data:image/png;base64,{KCC_LOGO_WHITE}" alt="KCC Glass">' if KCC_LOGO_WHITE else "<strong>KCC GLASS</strong>"

with st.sidebar:
    st.markdown(
        f"""
{logo_navy_html}
<div class="side-title">Partner Intelligence Platform</div>
<div class="side-copy">External-safe market desk for flooring partners, distributors, builders, and retail accounts.</div>
<a class="side-link" href="#market-pulse">Market Pulse</a>
<a class="side-link" href="#flooring-demand">Flooring Demand</a>
<a class="side-link" href="#cost-freight">Cost & Freight</a>
<a class="side-link" href="#product-technology">Product & Technology</a>
<a class="side-link" href="#design-library">Design Library</a>
<a class="side-link" href="#partner-kit">Partner Kit</a>
""",
        unsafe_allow_html=True,
    )
    st.download_button(
        "Download Partner Brief",
        data=create_partner_brief_pdf(snapshot, partner_rows),
        file_name=f"KCC_Partner_Market_Brief_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        width="stretch",
    )
    st.markdown(
        f"""
<div class="side-note">
Data mode: FRED public indicators + external-safe freight records.<br>
Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} KST
</div>
""",
        unsafe_allow_html=True,
    )


ticker_items = [
    ("HOUSING", snapshot["Housing Starts"], "up" if (housing_delta or 0) >= 0 else "down"),
    ("MORTGAGE", snapshot["30Y Mortgage"], "down" if (mortgage_delta or 0) >= 0 else "up"),
    ("USD/KRW", snapshot["USD/KRW"], "up" if (fx_delta or 0) >= 0 else "down"),
    ("WTI", snapshot["WTI Oil"], "up" if (wti_delta or 0) >= 0 else "down"),
    ("SCFI", snapshot["SCFI Freight"], "up" if (scfi_delta or 0) >= 0 else "down"),
    ("KCC", "Quality + design + supply confidence", "up"),
]
ticker_html = "".join(
    f'<span class="ticker-item"><span class="ticker-label">{label}</span><span class="{cls}">{value}</span></span>'
    for label, value, cls in ticker_items
)
st.markdown(
    f'<div class="ticker"><div class="ticker-track"><div class="ticker-set">{ticker_html}</div><div class="ticker-set">{ticker_html}</div></div></div>',
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="hero">
  <div class="hero-inner">
    <div>
      <div class="logo-row">{logo_white_html}</div>
      <div class="eyebrow">Market intelligence for flooring partners</div>
      <div class="h1">A useful market desk buyers will open again.</div>
      <div class="hero-copy">
        Public market indicators, freight direction, flooring demand signals, KCC product confidence,
        design context, and partner-ready talking points in one external-safe platform.
      </div>
      <div class="hero-pills">
        <span class="pill">FRED live indicators</span>
        <span class="pill">Freight watch</span>
        <span class="pill">HomeCC LVT Design Library</span>
        <span class="pill">KCC technology & ESG</span>
      </div>
    </div>
    <div class="hero-grid">
      <div class="hero-metric"><div class="metric-k">Housing Starts</div><div class="metric-v">{fmt_num(housing_now, 'K', 0)}</div><div class="metric-c">MoM {fmt_num(housing_delta, '%', 1)} / FRED HOUST</div></div>
      <div class="hero-metric"><div class="metric-k">30Y Mortgage</div><div class="metric-v">{fmt_num(mortgage_now, '%', 2)}</div><div class="metric-c">4W {fmt_num(mortgage_delta, '%', 1)} / rate-sensitive demand</div></div>
      <div class="hero-metric"><div class="metric-k">USD/KRW</div><div class="metric-v">{fmt_num(fx_now, '', 0)}</div><div class="metric-c">20D {fmt_num(fx_delta, '%', 1)} / quote timing watch</div></div>
      <div class="hero-metric"><div class="metric-k">SCFI</div><div class="metric-v">{fmt_num(scfi_now, '', 0)}</div><div class="metric-c">4W {fmt_num(scfi_delta, '%', 1)} / freight direction</div></div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

section_title("Why Partners Use This", "supplier utility")
st.markdown(
    """
<div class="grid4">
  <div class="card gold"><div class="card-title">Better first impression</div><div class="card-copy">Instead of sending another attachment, share a live workspace that helps partners read the market and prepare customer conversations.</div></div>
  <div class="card blue"><div class="card-title">Natural repeat exposure</div><div class="card-copy">Weekly indicators, freight direction, and product resources create a reason to revisit the KCC page before buying cycles.</div></div>
  <div class="card green"><div class="card-title">Sales enablement</div><div class="card-copy">Partners can reuse market logic, design positioning, ESG links, and product confidence points in their own dealer or builder calls.</div></div>
  <div class="card red"><div class="card-title">External-safe by design</div><div class="card-copy">No internal margin, customer list, CRM, ImportYeti, or sensitive purchasing workflow is exposed in this version.</div></div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown('<div id="market-pulse"></div>', unsafe_allow_html=True)
section_title("Market Pulse", "FRED public indicators")
market_table = pd.DataFrame(
    [
        ["Housing Starts", fmt_num(housing_now, "K", 0), fmt_num(housing_delta, "%", 1), last_date(fred["housing"]), "Flooring demand backdrop"],
        ["New Home Sales", fmt_num(latest(fred["new_home_sales"], "New Home Sales"), "K", 0), fmt_num(delta_pct(fred["new_home_sales"], "New Home Sales"), "%", 1), last_date(fred["new_home_sales"]), "New construction sales signal"],
        ["Building Permits", fmt_num(latest(fred["permits"], "Building Permits"), "K", 0), fmt_num(delta_pct(fred["permits"], "Building Permits"), "%", 1), last_date(fred["permits"]), "Forward construction signal"],
        ["30Y Mortgage", fmt_num(mortgage_now, "%", 2), fmt_num(mortgage_delta, "%", 1), last_date(fred["mortgage"]), "Affordability and remodeling sentiment"],
        ["CPI", fmt_num(cpi_now, "", 2), fmt_num(delta_pct(fred["cpi"], "CPI"), "%", 1), last_date(fred["cpi"]), "Consumer price pressure"],
        ["Fed Funds", fmt_num(fed_now, "%", 2), fmt_num(delta_pct(fred["fedfunds"], "Fed Funds"), "%", 1), last_date(fred["fedfunds"]), "Rate environment"],
    ],
    columns=["Indicator", "Latest", "Change", "As of", "Partner Meaning"],
)
st.dataframe(market_table, hide_index=True, width="stretch")

c1, c2 = st.columns(2)
with c1:
    panel("Housing Starts vs Building Permits", "FRED HOUST / PERMIT")
    demand_frame = fred["housing"].merge(fred["permits"], on="date", how="outer").sort_values("date")
    if demand_frame.dropna(how="all", subset=["Housing Starts", "Building Permits"]).empty:
        st.info("Add FRED_API_KEY in Streamlit Secrets to activate live FRED charts.")
    else:
        st.plotly_chart(line_chart(demand_frame.tail(60), ["Housing Starts", "Building Permits"], "U.S. Housing Starts and Building Permits"), width="stretch", config={"displayModeBar": False})
    close_panel()
with c2:
    panel("Rates and Inflation", "FRED MORTGAGE30US / CPIAUCSL")
    rate_frame = fred["mortgage"].merge(fred["cpi"], on="date", how="outer").sort_values("date")
    if rate_frame.dropna(how="all", subset=["30Y Mortgage", "CPI"]).empty:
        st.info("Add FRED_API_KEY in Streamlit Secrets to activate live FRED charts.")
    else:
        st.plotly_chart(line_chart(rate_frame.tail(100), ["30Y Mortgage", "CPI"], "Mortgage Rate and CPI"), width="stretch", config={"displayModeBar": False})
    close_panel()

st.markdown('<div id="flooring-demand"></div>', unsafe_allow_html=True)
section_title("Flooring Demand Signals", "how buyers can use the data")
st.markdown(
    """
<div class="grid3">
  <div class="card gold"><div class="card-title">Builder / multi-family</div><div class="card-copy">When starts, permits, and completions stabilize, partners can frame LVT as a practical, repeatable specification for project-driven demand.</div></div>
  <div class="card blue"><div class="card-title">Retail replacement</div><div class="card-copy">When mortgage rates remain high, replacement and repair demand can matter more than move-driven new-home demand.</div></div>
  <div class="card green"><div class="card-title">Dealer planning</div><div class="card-copy">Use market direction to talk about assortment discipline, sample readiness, and replenishment timing without making a hard forecast.</div></div>
</div>
""",
    unsafe_allow_html=True,
)

c3, c4 = st.columns(2)
with c3:
    panel("New and Existing Home Sales", "FRED HSN1F / EXHOSLUSM495S")
    sales_frame = fred["new_home_sales"].merge(fred["existing_sales"], on="date", how="outer").sort_values("date")
    st.plotly_chart(line_chart(sales_frame.tail(60), ["New Home Sales", "Existing Home Sales"], "Home Sales Direction"), width="stretch", config={"displayModeBar": False})
    close_panel()
with c4:
    panel("Building Materials Retail", "FRED MRTSSM4441USN")
    st.plotly_chart(line_chart(fred["building_retail"].tail(60), ["Building Materials Retail"], "Building Materials and Garden Retail Sales"), width="stretch", config={"displayModeBar": False})
    close_panel()

st.markdown('<div id="cost-freight"></div>', unsafe_allow_html=True)
section_title("Cost & Freight Watch", "external-safe pressure signals")
cost_table = pd.DataFrame(
    [
        ["USD/KRW", fmt_num(fx_now, "", 0), fmt_num(fx_delta, "%", 1), "Use a clear quote-validity window when FX moves quickly."],
        ["WTI Oil", fmt_num(wti_now, "$/bbl", 1), fmt_num(wti_delta, "%", 1), "Oil direction can affect resin, logistics, and cost sentiment."],
        ["Brent Oil", fmt_num(latest(fred["brent"], "Brent"), "$/bbl", 1), fmt_num(delta_pct(fred["brent"], "Brent", 20), "%", 1), "Use with WTI as a broad energy-cost reference."],
        ["SCFI", fmt_num(scfi_now, "", 0), fmt_num(scfi_delta, "%", 1), "Rising freight supports earlier replenishment and booking conversations."],
        ["Lumber PPI", fmt_num(latest(fred["lumber_ppi"], "Lumber PPI"), "", 1), fmt_num(delta_pct(fred["lumber_ppi"], "Lumber PPI"), "%", 1), "A useful proxy for building-material cost mood."],
        ["Building Materials PPI", fmt_num(latest(fred["building_ppi"], "Building Materials PPI"), "", 1), fmt_num(delta_pct(fred["building_ppi"], "Building Materials PPI"), "%", 1), "Supports discussion of broader construction-material inflation."],
    ],
    columns=["Signal", "Latest", "Change", "Partner Use"],
)
st.dataframe(cost_table, hide_index=True, width="stretch")

c5, c6 = st.columns(2)
with c5:
    panel("Freight Direction", "SCFI / CCFI local records")
    st.plotly_chart(line_chart(freight.tail(90), ["SCFI", "CCFI"], "Container Freight Index Direction"), width="stretch", config={"displayModeBar": False})
    close_panel()
with c6:
    panel("Energy and Material Mood", "FRED WTI / Brent / PPI")
    oil_frame = fred["wti"].merge(fred["brent"], on="date", how="outer").sort_values("date")
    st.plotly_chart(line_chart(oil_frame.tail(120), ["WTI", "Brent"], "Oil Benchmarks"), width="stretch", config={"displayModeBar": False})
    close_panel()

st.markdown('<div id="product-technology"></div>', unsafe_allow_html=True)
section_title("Product & Technology", "KCC confidence layer")
st.markdown(
    f"""
<div class="product-band">
  <div class="product-band-content">
    <div class="eyebrow">LVT, design library, quality, and manufacturing credibility</div>
    <div class="product-title">Let partners see new KCC LVT designs without waiting for another file.</div>
    <div class="product-copy">
      Use the HomeCC LVT Design Library as the visual entry point: partners can check current design
      directions first, then use this platform for market context, freight timing, ESG, and follow-up.
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)
st.markdown(
    f"""
<br>
<div class="grid4">
  <div class="card gold"><div class="card-title">Manufacturing confidence</div><div class="card-copy">Use KCC's scale and quality language to reduce perceived supplier risk.</div></div>
  <div class="card blue"><div class="card-title">Design library access</div><div class="card-copy">Send partners directly to HomeCC's LVT design library so they can review new designs and visual directions in one place.</div></div>
  <div class="card green"><div class="card-title">Technical support</div><div class="card-copy">Keep product, specification, sample, and documentation requests inside a repeatable partner support flow.</div></div>
  <div class="card red"><div class="card-title">ESG credibility</div><div class="card-copy">Use public ESG resources when commercial accounts ask for vendor governance and responsible supply-chain references.</div></div>
</div>
<br>
<a class="link-button" href="{KCC_HOME_URL}" target="_blank" rel="noopener noreferrer">Open KCC Glass</a>
<a class="link-button" href="{HOMECC_DESIGN_LIBRARY_URL}" target="_blank" rel="noopener noreferrer">Open LVT Design Library</a>
<a class="link-button secondary" href="{KCC_PRODUCT_URL}" target="_blank" rel="noopener noreferrer">Product Reference</a>
<a class="link-button secondary" href="{KCC_ESG_URL}" target="_blank" rel="noopener noreferrer">ESG Reports</a>
""",
    unsafe_allow_html=True,
)

st.markdown('<div id="design-library"></div>', unsafe_allow_html=True)
section_title("Design Library Hub", "HomeCC LVT designlibrary.do")
st.markdown(
    f"""
<div class="brief">
The HomeCC LVT Design Library should be the main visual destination for partners. Use this platform to create
the reason to click: market timing, demand signals, freight context, and then a direct path to current KCC LVT designs.
</div>
<a class="link-button" href="{HOMECC_DESIGN_LIBRARY_URL}" target="_blank" rel="noopener noreferrer">View New LVT Designs</a>
""",
    unsafe_allow_html=True,
)
design_rows = pd.DataFrame(
    [
        ["New design check", "Open the HomeCC library first and use it as the visual source of truth for current LVT designs."],
        ["Dealer wall planning", "Shortlist designs that are easiest to show in dealer displays, sample boards, and showroom updates."],
        ["Builder / multi-family", "Match practical wood and neutral visuals with demand signals from starts, permits, and completions."],
        ["Retail refresh", "Use new design visuals as a reason to follow up after the market brief, not as another attachment."],
        ["Next conversation", "Ask the partner which designs should be sampled, localized, or prepared for a launch set."],
    ],
    columns=["Design Use Case", "How Partners Can Use It"],
)
st.dataframe(design_rows, hide_index=True, width="stretch")

st.markdown('<div id="partner-kit"></div>', unsafe_allow_html=True)
section_title("Partner Kit", "copy, links, and follow-up")
left, right = st.columns([1.05, 0.95])
with left:
    panel("Suggested Outreach Copy", "email / LinkedIn")
    st.markdown(
        """
<div class="brief">
We built a small market desk for flooring partners so your team can check housing demand, mortgage rates,
freight direction, cost sentiment, and KCC product/ESG resources in one place. It is not a brochure or a static file;
it is meant to be a practical reference before pricing, replenishment, and assortment conversations.
</div>
""",
        unsafe_allow_html=True,
    )
    close_panel()
with right:
    panel("Partner Follow-up Prompts", "meeting openers")
    prompts = pd.DataFrame(
        [
            ["Market", "Which demand signal matters most for your customer base right now?"],
            ["Freight", "Which port or lane is most sensitive for your replenishment plan?"],
            ["Product", "Which LVT visuals are easiest for your sales team to show first?"],
            ["Support", "Would ESG or technical documentation help with builder/commercial accounts?"],
        ],
        columns=["Topic", "Question"],
    )
    st.dataframe(prompts, hide_index=True, width="stretch")
    close_panel()

section_title("Download Center", "shareable assets")
st.download_button(
    "Download Market Brief PDF",
    data=create_partner_brief_pdf(snapshot, partner_rows),
    file_name=f"KCC_Partner_Market_Brief_{datetime.now().strftime('%Y%m%d')}.pdf",
    mime="application/pdf",
    width="stretch",
)
st.download_button(
    "Download Indicator Snapshot CSV",
    data=cost_table.to_csv(index=False).encode("utf-8-sig"),
    file_name=f"KCC_Partner_Indicator_Snapshot_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv",
    width="stretch",
)

st.markdown(
    """
<div class="footer-note">
External sharing note: this partner platform intentionally excludes internal margins, CRM/account maps,
ImportYeti analysis, customer impact scoring, internal purchase workflows, and confidential sales actions.
Market data is provided for reference and partner discussion, not as a binding forecast or quotation.
</div>
""",
    unsafe_allow_html=True,
)

