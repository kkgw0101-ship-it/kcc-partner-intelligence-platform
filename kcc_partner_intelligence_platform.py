"""
KCC Partner Intelligence Platform
External-facing Streamlit portal for customer promotion and partner enablement.

This app is separate from app_v6_share.py and intentionally excludes internal
CRM, margin, ImportYeti, purchasing, and account-map workflows.
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
SOFT = "#DCE6F2"
MUTED = "#9AA7BA"
PANEL = "#111B2D"
PANEL_2 = "#18243A"
LINE = "#2A3A56"
GOLD = "#D9A441"
BLUE = "#3B82F6"
GREEN = "#16A34A"
RED = "#DC2626"
KCC_BLUE = "#0E2372"
CALI_NAVY = "#10213D"
CALI_SAND = "#E8DDCB"

PAGE_ICON = os.path.join(APP_DIR, "favicon_kcc.png")
if not os.path.exists(PAGE_ICON):
    PAGE_ICON = "KCC"

st.set_page_config(
    page_title="CALI Partner Intelligence Desk | KCC Glass",
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
CALI_LOGO = image_b64("cali_logo.png")
HERO_IMAGE = image_b64("homecc_lvt_design_library_hero.png")
VIDEO_THUMB = image_b64("kcc_company_video_thumb.jpg")

KCC_HOME_URL = "https://www.kccglass.co.kr/eng/"
KCC_ESG_URL = "https://www.kccglass.co.kr/eng/esgManagement/about/report.do"
KCC_PRODUCT_URL = "https://www.kccglass.co.kr/eng/product/interiorFlooring.do"
HOMECC_DESIGN_LIBRARY_URL = "https://www.homecc.com/lvt/designlibrary.do"
CALI_VISIT_DATE = "July 7, 2026"
CALI_DEMO_TITLE = "CALI Partner Intelligence Desk"

MENU_ITEMS = [
    "Home",
    "CALI Care Model",
    "Design Library",
    "Market Pulse",
    "Flooring Demand",
    "Cost & Freight",
    "Product & Technology",
    "Meeting Brief",
]


st.markdown(
    f"""
<style>
[data-testid="stAppViewContainer"] {{ background:{NAVY}; color:{INK}; }}
[data-testid="stHeader"] {{ background:transparent; height:0; }}
#MainMenu, footer, [data-testid="stToolbar"] {{ visibility:hidden; }}
.block-container {{ padding:1rem 1.4rem 2.4rem; max-width:1440px; }}
* {{ letter-spacing:0; font-variant-numeric:tabular-nums; }}

[data-testid="stSidebar"] {{
  background:linear-gradient(180deg,#0E2372 0%,#08111F 74%,#050A12 100%);
  border-right:1px solid rgba(217,164,65,.22);
}}
[data-testid="stSidebar"] * {{ color:{INK}; }}
[data-testid="stSidebar"] .stDownloadButton button {{
  background:{GOLD} !important; color:#101827 !important; border:0 !important;
  border-radius:7px !important; font-weight:900 !important;
}}
[data-testid="stSidebar"] [role="radiogroup"] label {{
  padding:8px 10px; border-radius:7px; margin:3px 0; border:1px solid transparent;
  font-weight:800;
}}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {{
  background:rgba(217,164,65,.12); border-color:rgba(217,164,65,.32);
}}
.side-logo {{ width:118px; background:{KCC_BLUE}; border-radius:7px; padding:8px 10px; margin:6px 0 12px; }}
.side-cali-logo {{ width:118px; background:rgba(255,255,255,.96); border-radius:7px; padding:8px 10px; margin:4px 0 8px; }}
.side-cali {{ display:inline-flex; align-items:center; justify-content:center; width:118px; height:45px; border-radius:7px; background:rgba(255,255,255,.94); color:{CALI_NAVY} !important; font-size:34px; font-family:Georgia,'Times New Roman',serif; margin:4px 0 8px; }}
.side-title {{ font-size:15px; font-weight:900; line-height:1.25; margin-bottom:6px; }}
.side-copy {{ color:#B8C3D6; font-size:12px; line-height:1.55; margin-bottom:15px; }}
.side-label {{ color:#AEB9CE; font-size:10px; font-weight:900; text-transform:uppercase; letter-spacing:.8px; margin:14px 0 6px; }}
.side-note {{ color:#B8C3D6; font-size:11px; line-height:1.55; margin-top:12px; }}

.ticker {{ height:34px; overflow:hidden; border:1px solid {LINE}; border-radius:8px; background:#060C17; display:flex; align-items:center; margin-bottom:12px; }}
.ticker-track {{ display:flex; width:max-content; animation:tickerFlow 44s linear infinite; }}
.ticker-set {{ display:flex; flex-shrink:0; min-width:max-content; }}
.ticker-item {{ display:inline-flex; align-items:center; gap:8px; padding:0 24px; white-space:nowrap; color:{SOFT}; font-size:12px; font-weight:900; }}
.ticker-label {{ color:{MUTED}; text-transform:uppercase; }}
.up {{ color:#4ADE80; }}
.down {{ color:#FB7185; }}
@keyframes tickerFlow {{ from {{ transform:translateX(0); }} to {{ transform:translateX(-50%); }} }}

.topbar {{
  display:flex; align-items:center; justify-content:space-between; gap:16px;
  background:{KCC_BLUE}; border-bottom:2px solid {GOLD}; border-radius:8px;
  padding:12px 18px; margin-bottom:12px; box-shadow:0 18px 50px rgba(0,0,0,.24);
}}
.topbar img {{ height:40px; width:auto; }}
.top-lockup {{ display:flex; align-items:center; gap:12px; }}
.top-cali-logo {{ height:38px; width:auto; border-radius:7px; background:rgba(255,255,255,.96); padding:7px 10px; }}
.top-cali {{ display:inline-flex; align-items:center; justify-content:center; min-width:92px; height:38px; border-radius:7px; background:rgba(255,255,255,.95); color:{CALI_NAVY}; font-size:28px; font-family:Georgia,'Times New Roman',serif; }}
.top-x {{ color:#DDE6F3; font-size:12px; font-weight:900; opacity:.75; }}
.top-meta {{ display:flex; gap:22px; align-items:center; text-align:right; }}
.top-k {{ color:#B8C3D6; font-size:9px; font-weight:900; text-transform:uppercase; }}
.top-v {{ color:#fff; font-size:13px; font-weight:900; }}

.hero {{
  min-height:570px; border-radius:14px; overflow:hidden; position:relative; margin-bottom:14px;
  border:1px solid {LINE}; box-shadow:0 26px 80px rgba(0,0,0,.30);
  background:#06101E;
}}
.hero::after {{ content:""; position:absolute; inset:0; z-index:1; background:
  linear-gradient(90deg,rgba(6,16,30,.96) 0%,rgba(6,16,30,.78) 44%,rgba(6,16,30,.22) 100%),
  linear-gradient(0deg,rgba(6,16,30,.72) 0%,rgba(6,16,30,.10) 42%,rgba(6,16,30,.20) 100%);
}}
.hero-slide {{ position:absolute; inset:0; opacity:0; background-size:cover; background-position:center; animation:caliHeroCycle 18s infinite; transform:scale(1.03); }}
.hero-slide.one {{ background-image:url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=2200&q=80"); animation-delay:0s; }}
.hero-slide.two {{ background-image:url("https://images.unsplash.com/photo-1556911220-bff31c812dba?auto=format&fit=crop&w=2200&q=80"); animation-delay:6s; }}
.hero-slide.three {{ background-image:url("data:image/png;base64,{HERO_IMAGE}"); animation-delay:12s; }}
@keyframes caliHeroCycle {{
  0% {{ opacity:0; transform:scale(1.03); }}
  8% {{ opacity:1; }}
  33% {{ opacity:1; transform:scale(1.08); }}
  41% {{ opacity:0; }}
  100% {{ opacity:0; }}
}}
.hero-inner {{ position:absolute; inset:0; z-index:2; padding:54px 58px; display:flex; flex-direction:column; justify-content:space-between; }}
.hero-logo {{ height:38px; width:auto; background:{KCC_BLUE}; border-radius:7px; padding:8px 12px; }}
.cali-lockup {{ display:flex; align-items:center; gap:13px; margin-bottom:28px; flex-wrap:wrap; }}
.cali-hero-logo {{ height:56px; width:auto; max-width:190px; padding:9px 14px; border-radius:8px; background:rgba(255,255,255,.94); box-shadow:0 14px 40px rgba(0,0,0,.22); object-fit:contain; }}
.partner-x {{ color:{CALI_SAND}; font-size:16px; font-weight:900; text-transform:uppercase; opacity:.82; }}
.hero-progress {{ display:flex; gap:12px; max-width:720px; margin-top:16px; }}
.hero-progress span {{ display:block; height:5px; flex:1; border-radius:99px; background:rgba(255,255,255,.34); overflow:hidden; }}
.hero-progress span::after {{ content:""; display:block; height:100%; background:{GOLD}; opacity:.72; animation:progressPulse 18s linear infinite; transform-origin:left; }}
.hero-progress span:nth-child(2)::after {{ animation-delay:6s; }}
.hero-progress span:nth-child(3)::after {{ animation-delay:12s; }}
@keyframes progressPulse {{ 0% {{ transform:scaleX(0); }} 28% {{ transform:scaleX(1); }} 33%,100% {{ transform:scaleX(0); }} }}
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
.panel {{ background:{PANEL}; border:1px solid {LINE}; border-radius:8px; overflow:hidden; margin-bottom:12px; }}
.panel-head {{ display:flex; justify-content:space-between; gap:12px; align-items:center; padding:12px 14px; border-bottom:1px solid {LINE}; background:{PANEL_2}; }}
.panel-title {{ color:{INK}; font-size:13px; font-weight:900; }}
.panel-meta {{ color:{MUTED}; font-size:10px; font-weight:800; text-transform:uppercase; }}
.panel-body {{ padding:14px; }}
.brief {{ color:#DCE6F2; font-size:13px; line-height:1.65; background:{PANEL_2}; border:1px solid {LINE}; border-left:4px solid {GOLD}; border-radius:8px; padding:13px 14px; margin-bottom:12px; }}
.link-button {{ display:inline-flex; padding:9px 12px; background:{GOLD}; color:#101827 !important; border-radius:7px; text-decoration:none !important; font-size:12px; font-weight:900; margin-right:7px; margin-bottom:7px; }}
.link-button.secondary {{ background:{PANEL_2}; color:{INK} !important; border:1px solid {LINE}; }}
.product-band {{ min-height:270px; border:1px solid {LINE}; border-radius:8px; overflow:hidden; position:relative; background:url("data:image/png;base64,{HERO_IMAGE}"); background-size:cover; background-position:center; margin-bottom:12px; }}
.product-band::after {{ content:""; position:absolute; inset:0; background:linear-gradient(90deg,rgba(7,19,40,.92),rgba(7,19,40,.24)); }}
.product-band-content {{ position:absolute; z-index:1; inset:0; padding:26px; display:flex; flex-direction:column; justify-content:flex-end; max-width:720px; }}
.product-title {{ color:#fff; font-size:30px; font-weight:900; line-height:1.15; }}
.product-copy {{ color:#DDE6F3; font-size:14px; line-height:1.6; margin-top:9px; }}
.footer-note {{ margin-top:20px; color:{MUTED}; font-size:11px; line-height:1.55; border-top:1px solid {LINE}; padding-top:12px; }}

.dark-table-wrap {{ border:1px solid {LINE}; border-radius:8px; overflow:hidden; background:{PANEL}; margin-bottom:12px; }}
.dark-table {{ width:100%; border-collapse:collapse; font-size:13px; color:{SOFT}; }}
.dark-table th {{ background:{PANEL_2}; color:{MUTED}; text-align:left; padding:12px 13px; font-size:11px; text-transform:uppercase; border-bottom:1px solid {LINE}; }}
.dark-table td {{ padding:12px 13px; border-bottom:1px solid {LINE}; vertical-align:top; }}
.dark-table tr:last-child td {{ border-bottom:0; }}
.dark-table tbody tr:nth-child(even) {{ background:rgba(255,255,255,.025); }}

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
  .top-meta {{ display:none; }}
}}
</style>
""",
    unsafe_allow_html=True,
)


def fmt_num(value: float | int | None, unit: str = "", decimals: int = 1) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    base = f"{float(value):,.0f}" if decimals == 0 else f"{float(value):,.{decimals}f}"
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


def line_chart(frame: pd.DataFrame, cols: list[str], title: str, height: int = 285) -> go.Figure:
    fig = go.Figure()
    colors = ["#7AA7FF", "#D9A441", "#4ADE80", "#FB7185", "#38BDF8"]
    for idx, col in enumerate(cols):
        if col in frame:
            fig.add_trace(
                go.Scatter(
                    x=frame["date"],
                    y=frame[col],
                    mode="lines",
                    name=col,
                    line=dict(width=2.5, color=colors[idx % len(colors)]),
                    hovertemplate="%{x|%Y-%m-%d}<br>%{y:,.2f}<extra></extra>",
                )
            )
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color=INK)),
        height=height,
        margin=dict(l=12, r=12, t=38, b=10),
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        hovermode="x unified",
        font=dict(color=SOFT),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(size=11, color=SOFT)),
        xaxis=dict(showgrid=True, gridcolor=LINE, zeroline=False, color=MUTED),
        yaxis=dict(showgrid=True, gridcolor=LINE, zeroline=False, color=MUTED),
    )
    return fig


def render_dark_table(frame: pd.DataFrame, max_rows: int | None = None) -> None:
    shown = frame.head(max_rows) if max_rows else frame
    header = "".join(f"<th>{col}</th>" for col in shown.columns)
    body_rows = []
    for _, row in shown.iterrows():
        cells = "".join(f"<td>{'' if pd.isna(value) else value}</td>" for value in row)
        body_rows.append(f"<tr>{cells}</tr>")
    st.markdown(
        f"""
<div class="dark-table-wrap">
  <table class="dark-table">
    <thead><tr>{header}</tr></thead>
    <tbody>{''.join(body_rows)}</tbody>
  </table>
</div>
""",
        unsafe_allow_html=True,
    )


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
    output.write(f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii"))
    return output.getvalue()


def create_partner_brief_pdf(snapshot: dict[str, str], rows: pd.DataFrame) -> bytes:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ModuleNotFoundError:
        return simple_pdf_bytes(
            [CALI_DEMO_TITLE, f"Prepared for CALI visit on {CALI_VISIT_DATE}"]
            + [f"- {key}: {value}" for key, value in snapshot.items()]
        )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=14 * mm, leftMargin=14 * mm, topMargin=14 * mm, bottomMargin=14 * mm)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(CALI_DEMO_TITLE, styles["Title"]),
        Spacer(1, 8),
        Paragraph(f"Prepared for CALI visit on {CALI_VISIT_DATE}", styles["Normal"]),
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
    story.append(Paragraph("Disclaimer: Market data is for reference and partner discussion, not as a binding forecast or quotation.", styles["Italic"]))
    doc.build(story)
    return buffer.getvalue()


fred = {
    "housing": get_fred("HOUST", "Housing Starts"),
    "mortgage": get_fred("MORTGAGE30US", "30Y Mortgage"),
    "cpi": get_fred("CPIAUCSL", "CPI"),
    "fedfunds": get_fred("FEDFUNDS", "Fed Funds"),
    "new_home_sales": get_fred("HSN1F", "New Home Sales"),
    "permits": get_fred("PERMIT", "Building Permits"),
    "completions": get_fred("COMPUTSA", "Housing Completions"),
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
        ["Design Library", "Send partners directly to the HomeCC LVT design library so they can review current design directions."],
        ["Follow-up", "Share the brief link before a call so the buyer has a reason to re-open the conversation without another attachment."],
    ],
    columns=["Area", "Partner Use"],
)

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

logo_white_html = f'<img src="data:image/png;base64,{KCC_LOGO_WHITE}" alt="KCC Glass">' if KCC_LOGO_WHITE else "<strong>KCC GLASS</strong>"
hero_logo_html = f'<img class="hero-logo" src="data:image/png;base64,{KCC_LOGO_WHITE}" alt="KCC Glass">' if KCC_LOGO_WHITE else "<strong>KCC GLASS</strong>"
sidebar_logo_html = f'<img class="side-logo" src="data:image/png;base64,{KCC_LOGO_WHITE}" alt="KCC Glass">' if KCC_LOGO_WHITE else "<strong>KCC GLASS</strong>"
cali_hero_logo_html = f'<img class="cali-hero-logo" src="data:image/png;base64,{CALI_LOGO}" alt="CALI">' if CALI_LOGO else '<div class="cali-logo-word">CALI</div>'
cali_top_logo_html = f'<img class="top-cali-logo" src="data:image/png;base64,{CALI_LOGO}" alt="CALI">' if CALI_LOGO else '<span class="top-cali">CALI</span>'
cali_side_logo_html = f'<img class="side-cali-logo" src="data:image/png;base64,{CALI_LOGO}" alt="CALI">' if CALI_LOGO else '<div class="side-cali">CALI</div>'

with st.sidebar:
    st.markdown(
        f"""
{sidebar_logo_html}
{cali_side_logo_html}
<div class="side-title">CALI Partner Intelligence Desk</div>
<div class="side-copy">July 7 visit demo: how KCC can support CALI with market signals, design access, and account-care rhythm.</div>
<div class="side-label">Workspace</div>
""",
        unsafe_allow_html=True,
    )
    view = st.radio("Workspace", MENU_ITEMS, label_visibility="collapsed")
    st.markdown('<div class="side-label">Downloads</div>', unsafe_allow_html=True)
    st.download_button(
        "Download CALI Brief",
        data=create_partner_brief_pdf(snapshot, partner_rows),
        file_name=f"KCC_CALI_Visit_Brief_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        width="stretch",
    )
    st.markdown(
        f"""
<div class="side-note">
FRED API: {"connected" if FRED_API_KEY else "waiting"}<br>
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
    ("DESIGN", "HomeCC LVT library", "up"),
]
ticker_html = "".join(
    f'<span class="ticker-item"><span class="ticker-label">{label}</span><span class="{cls}">{value}</span></span>'
    for label, value, cls in ticker_items
)
st.markdown(f'<div class="ticker"><div class="ticker-track"><div class="ticker-set">{ticker_html}</div><div class="ticker-set">{ticker_html}</div></div></div>', unsafe_allow_html=True)
st.markdown(
    f"""
<div class="topbar">
  <div class="top-lockup">{cali_top_logo_html}<span class="top-x">x</span>{logo_white_html}</div>
  <div class="top-meta">
    <div><div class="top-k">Workspace</div><div class="top-v">{view}</div></div>
    <div><div class="top-k">Data</div><div class="top-v">FRED + Freight</div></div>
    <div><div class="top-k">Updated</div><div class="top-v">{datetime.now().strftime('%Y-%m-%d %H:%M')}</div></div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)


def render_home() -> None:
    st.markdown(
        f"""
<div class="hero">
  <div class="hero-slide one"></div>
  <div class="hero-slide two"></div>
  <div class="hero-slide three"></div>
  <div class="hero-inner">
    <div>
      <div class="cali-lockup">
        {cali_hero_logo_html}
        <div class="partner-x">x</div>
        {hero_logo_html}
      </div>
      <div class="eyebrow">California lifestyle partner demo / July 7</div>
      <div class="h1">Carefree homes meet market-ready support.</div>
      <div class="hero-copy">
        A CALI-facing demo with the coastal, natural, design-forward energy of California:
        surf-to-showroom inspiration, HomeCC LVT design access, market signals, freight timing,
        and a repeatable account-care rhythm from KCC.
      </div>
      <div class="hero-pills">
        <span class="pill">California lifestyle</span>
        <span class="pill">CALI care model</span>
        <span class="pill">HomeCC LVT Design Library</span>
        <span class="pill">FRED live indicators</span>
        <span class="pill">Freight watch</span>
        <span class="pill">KCC technology & ESG</span>
      </div>
      <div class="hero-progress"><span></span><span></span><span></span></div>
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
    section_title("What CALI Can See", "customer-care demo")
    st.markdown(
        """
<div class="grid4">
  <div class="card gold"><div class="card-title">Managed account view</div><div class="card-copy">Show CALI that KCC can organize market, product, design, and follow-up information in one dedicated workspace.</div></div>
  <div class="card blue"><div class="card-title">Design-first conversation</div><div class="card-copy">Move quickly from market context to the HomeCC LVT Design Library so CALI can review current design directions.</div></div>
  <div class="card green"><div class="card-title">Sales support layer</div><div class="card-copy">Help CALI explain timing, freight, demand, product confidence, and ESG to its own customer base.</div></div>
  <div class="card red"><div class="card-title">External-safe demo</div><div class="card-copy">No internal margin, customer list, CRM, ImportYeti, or sensitive purchasing workflow is exposed in this version.</div></div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_cali_care_model() -> None:
    section_title("CALI Care Model", "how KCC can manage the account")
    st.markdown(
        """
<div class="brief">
This screen is the core message for the July 7 visit: KCC is not only presenting products.
We can provide CALI with a repeatable support rhythm that connects market signals, design access,
freight timing, product documentation, California lifestyle positioning, and follow-up actions.
</div>
""",
        unsafe_allow_html=True,
    )
    care_rows = pd.DataFrame(
        [
            ["Lifestyle fit", "California coast, natural interiors, and carefree home positioning", "Connect KCC LVT design support with CALI's brand world before discussing specs."],
            ["Market watch", "Housing, mortgage, CPI, FX, oil, and freight signals", "Use as neutral context for timing, replenishment, and promotion discussion."],
            ["Design access", "HomeCC LVT Design Library", "Let CALI check current KCC LVT design directions without waiting for separate files."],
            ["Product confidence", "KCC quality, technology, ESG, and documentation links", "Support CALI's dealer, builder, and commercial conversations."],
            ["Follow-up rhythm", "Monthly or pre-order update desk", "Turn one meeting into an ongoing account-care habit."],
            ["Custom expansion", "CALI-specific version can be prepared later", "Add approved SKUs, sample status, launch notes, and agreed next actions."],
        ],
        columns=["Care Area", "What KCC Provides", "How CALI Can Use It"],
    )
    render_dark_table(care_rows)
    st.markdown(
        f"""
<a class="link-button" href="{HOMECC_DESIGN_LIBRARY_URL}" target="_blank" rel="noopener noreferrer">Open HomeCC LVT Design Library</a>
<a class="link-button secondary" href="{KCC_ESG_URL}" target="_blank" rel="noopener noreferrer">Open ESG Resources</a>
""",
        unsafe_allow_html=True,
    )


def render_market_pulse() -> None:
    section_title("Market Pulse", "FRED public indicators")
    render_dark_table(market_table)
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


def render_flooring_demand() -> None:
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
    c1, c2 = st.columns(2)
    with c1:
        panel("New and Existing Home Sales", "FRED HSN1F / EXHOSLUSM495S")
        sales_frame = fred["new_home_sales"].merge(fred["existing_sales"], on="date", how="outer").sort_values("date")
        st.plotly_chart(line_chart(sales_frame.tail(60), ["New Home Sales", "Existing Home Sales"], "Home Sales Direction"), width="stretch", config={"displayModeBar": False})
        close_panel()
    with c2:
        panel("Building Materials Retail", "FRED MRTSSM4441USN")
        st.plotly_chart(line_chart(fred["building_retail"].tail(60), ["Building Materials Retail"], "Building Materials and Garden Retail Sales"), width="stretch", config={"displayModeBar": False})
        close_panel()


def render_cost_freight() -> None:
    section_title("Cost & Freight Watch", "external-safe pressure signals")
    render_dark_table(cost_table)
    c1, c2 = st.columns(2)
    with c1:
        panel("Freight Direction", "SCFI / CCFI local records")
        st.plotly_chart(line_chart(freight.tail(90), ["SCFI", "CCFI"], "Container Freight Index Direction"), width="stretch", config={"displayModeBar": False})
        close_panel()
    with c2:
        panel("Energy and Material Mood", "FRED WTI / Brent / PPI")
        oil_frame = fred["wti"].merge(fred["brent"], on="date", how="outer").sort_values("date")
        st.plotly_chart(line_chart(oil_frame.tail(120), ["WTI", "Brent"], "Oil Benchmarks"), width="stretch", config={"displayModeBar": False})
        close_panel()


def render_product_technology() -> None:
    section_title("Product & Technology", "KCC confidence layer")
    st.markdown(
        f"""
<div class="product-band">
  <div class="product-band-content">
    <div class="eyebrow">LVT, design library, quality, and manufacturing credibility</div>
    <div class="product-title">Let partners see new KCC LVT designs without waiting for another file.</div>
    <div class="product-copy">
      Use the HomeCC LVT Design Library as the visual entry point. Partners can check current design directions first,
      then use this platform for market context, freight timing, ESG, and follow-up.
    </div>
  </div>
</div>
<div class="grid4">
  <div class="card gold"><div class="card-title">Manufacturing confidence</div><div class="card-copy">Use KCC's scale and quality language to reduce perceived supplier risk.</div></div>
  <div class="card blue"><div class="card-title">Design library access</div><div class="card-copy">Send partners directly to HomeCC's LVT design library so they can review new designs in one place.</div></div>
  <div class="card green"><div class="card-title">Technical support</div><div class="card-copy">Keep product, specification, sample, and documentation requests inside a repeatable partner support flow.</div></div>
  <div class="card red"><div class="card-title">ESG credibility</div><div class="card-copy">Use public ESG resources when commercial accounts ask for vendor governance references.</div></div>
</div>
<br>
<a class="link-button" href="{KCC_HOME_URL}" target="_blank" rel="noopener noreferrer">Open KCC Glass</a>
<a class="link-button" href="{HOMECC_DESIGN_LIBRARY_URL}" target="_blank" rel="noopener noreferrer">Open LVT Design Library</a>
<a class="link-button secondary" href="{KCC_PRODUCT_URL}" target="_blank" rel="noopener noreferrer">Product Reference</a>
<a class="link-button secondary" href="{KCC_ESG_URL}" target="_blank" rel="noopener noreferrer">ESG Reports</a>
""",
        unsafe_allow_html=True,
    )


def render_design_library() -> None:
    section_title("Design Library Hub", "first visual stop for CALI")
    st.markdown(
        f"""
<div class="brief">
For the CALI visit, this should be the fastest visual moment: open the HomeCC LVT Design Library,
review current KCC LVT designs, then use the market and freight screens to explain timing and support.
</div>
<a class="link-button" href="{HOMECC_DESIGN_LIBRARY_URL}" target="_blank" rel="noopener noreferrer">View New LVT Designs</a>
""",
        unsafe_allow_html=True,
    )
    design_rows = pd.DataFrame(
        [
            ["Live design review", "Open the HomeCC library during the visit and let CALI react to current LVT visuals."],
            ["Dealer wall planning", "Shortlist designs that are easiest to show in dealer displays, sample boards, and showroom updates."],
            ["Builder / multi-family", "Match practical wood and neutral visuals with demand signals from starts, permits, and completions."],
            ["Retail refresh", "Use new design visuals as a reason for a structured follow-up after the visit."],
            ["Next conversation", "Ask CALI which designs should be sampled, localized, or prepared for a launch set."],
        ],
        columns=["Design Use Case", "How Partners Can Use It"],
    )
    render_dark_table(design_rows)


def render_partner_kit() -> None:
    section_title("CALI Meeting Brief", "talk track and follow-up")
    left, right = st.columns([1.05, 0.95])
    with left:
        panel("Suggested Outreach Copy", "email / LinkedIn")
        st.markdown(
            """
<div class="brief">
We prepared this desk as a short example of how KCC can support CALI after today's visit:
market signals, freight timing, HomeCC LVT design access, product confidence, ESG resources,
and follow-up questions in one place. The goal is to make collaboration easier after the meeting.
</div>
""",
            unsafe_allow_html=True,
        )
        close_panel()
    with right:
        panel("CALI Follow-up Prompts", "meeting openers")
        prompts = pd.DataFrame(
            [
                ["Market", "Which demand signal matters most for CALI's customer base right now?"],
                ["Freight", "Which port or lane is most sensitive for CALI's replenishment plan?"],
                ["Design", "Which HomeCC LVT designs should we review or sample first?"],
                ["Support", "Would ESG or technical documentation help with CALI's builder/commercial accounts?"],
            ],
            columns=["Topic", "Question"],
        )
        render_dark_table(prompts)
        close_panel()
    section_title("Download Center", "shareable assets")
    st.download_button(
        "Download CALI Visit Brief PDF",
        data=create_partner_brief_pdf(snapshot, partner_rows),
        file_name=f"KCC_CALI_Visit_Brief_{datetime.now().strftime('%Y%m%d')}.pdf",
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


if view == "Home":
    render_home()
elif view == "CALI Care Model":
    render_cali_care_model()
elif view == "Market Pulse":
    render_market_pulse()
elif view == "Flooring Demand":
    render_flooring_demand()
elif view == "Cost & Freight":
    render_cost_freight()
elif view == "Product & Technology":
    render_product_technology()
elif view == "Design Library":
    render_design_library()
elif view == "Meeting Brief":
    render_partner_kit()

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
