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
PARTNER_NAVY = "#10213D"
PARTNER_SAND = "#E8DDCB"

PAGE_ICON = os.path.join(APP_DIR, "favicon_kcc.png")
if not os.path.exists(PAGE_ICON):
    PAGE_ICON = "KCC"

st.set_page_config(
    page_title="KCC Partner Intelligence Platform | KCC Glass",
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


def file_b64(file_name: str) -> str:
    path = os.path.join(APP_DIR, file_name)
    try:
        with open(path, "rb") as handle:
            return base64.b64encode(handle.read()).decode("utf-8")
    except Exception:
        return ""


FRED_API_KEY = get_secret("FRED_API_KEY", "")
KCC_LOGO_WHITE = image_b64("logo_white_t.png")
PARTNER_LOGO = ""
HERO_IMAGE = image_b64("homecc_lvt_design_library_hero.png")
HERO_VIDEO = file_b64("partner_hero.mp4")
VIDEO_THUMB = image_b64("kcc_company_video_thumb.jpg")

KCC_HOME_URL = "https://www.kccglass.co.kr/eng/"
KCC_ESG_URL = "https://www.kccglass.co.kr/eng/esgManagement/about/report.do"
KCC_PRODUCT_URL = "https://www.kccglass.co.kr/eng/product/interiorFlooring.do"
HOMECC_DESIGN_LIBRARY_URL = "https://www.homecc.com/lvt/designlibrary.do"
PARTNER_UPDATE_LABEL = "Continuously updated"
PLATFORM_TITLE = "KCC Partner Intelligence Platform"

MENU_ITEMS = [
    "Home",
    "Why KCC Glass",
    "Technology Proof",
    "OEM Spec Finder",
    "Design Library",
    "Market Pulse",
    "Meeting Brief",
]


st.markdown(
    f"""
<style>
[data-testid="stAppViewContainer"] {{ background:{NAVY}; color:{INK}; }}
[data-testid="stHeader"] {{ background:transparent; height:0; }}
#MainMenu, footer, [data-testid="stToolbar"] {{ visibility:hidden; }}
.block-container {{ padding:1rem 1.4rem 2.4rem; max-width:100%; width:100% !important; }}
* {{ letter-spacing:0; font-variant-numeric:tabular-nums; }}

[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapseButton"] {{
  display:none !important;
}}
[data-testid="stSidebar"] {{
  background:linear-gradient(180deg,#0E2372 0%,#08111F 74%,#050A12 100%);
  border-right:1px solid rgba(217,164,65,.22);
  transform:none !important;
  visibility:visible !important;
  min-width:252px !important;
  width:252px !important;
}}
[data-testid="stSidebar"][aria-expanded="false"] {{
  margin-left:0 !important;
}}
[data-testid="stMain"] {{
  margin-left:0 !important;
  width:100% !important;
  max-width:100% !important;
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
.side-partner-logo {{ width:118px; background:rgba(255,255,255,.96); border-radius:7px; padding:8px 10px; margin:4px 0 8px; }}
.side-partner {{ display:inline-flex; align-items:center; justify-content:center; width:118px; height:45px; border-radius:7px; background:rgba(255,255,255,.94); color:{PARTNER_NAVY} !important; font-size:34px; font-family:Georgia,'Times New Roman',serif; margin:4px 0 8px; }}
.partner-logo-word {{ display:inline-flex; align-items:center; justify-content:center; min-width:190px; height:82px; padding:0 18px; border-radius:9px; background:rgba(255,255,255,.94); color:{PARTNER_NAVY}; box-shadow:0 16px 44px rgba(0,0,0,.24); font-size:25px; line-height:1.05; font-weight:900; text-transform:uppercase; }}
.side-partner-word {{ display:inline-flex; align-items:center; justify-content:center; width:118px; min-height:48px; border-radius:7px; background:rgba(255,255,255,.94); color:{PARTNER_NAVY} !important; font-size:13px; line-height:1.05; font-weight:900; text-transform:uppercase; text-align:center; margin:4px 0 8px; }}
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
.top-partner-logo {{ height:38px; width:auto; border-radius:7px; background:rgba(255,255,255,.96); padding:7px 10px; }}
.top-partner-mark {{ display:inline-flex; align-items:center; justify-content:center; min-width:92px; height:38px; border-radius:7px; background:rgba(255,255,255,.95); color:{PARTNER_NAVY}; font-size:28px; font-family:Georgia,'Times New Roman',serif; }}
.top-partner-word {{ display:inline-flex; align-items:center; justify-content:center; min-width:112px; height:38px; border-radius:7px; background:rgba(255,255,255,.95); color:{PARTNER_NAVY}; font-size:11px; font-weight:900; text-transform:uppercase; }}
.top-x {{ color:#DDE6F3; font-size:12px; font-weight:900; opacity:.75; }}
.top-partner {{ display:flex; flex-direction:column; gap:3px; align-items:flex-start; }}
.top-partner-label {{ color:#C8D1E1; font-size:8px; font-weight:900; letter-spacing:.8px; text-transform:uppercase; }}
.top-partner img {{ height:22px; width:auto; background:{KCC_BLUE}; border-radius:5px; padding:4px 7px; }}
.top-meta {{ display:flex; gap:22px; align-items:center; text-align:right; }}
.top-k {{ color:#B8C3D6; font-size:9px; font-weight:900; text-transform:uppercase; }}
.top-v {{ color:#fff; font-size:13px; font-weight:900; }}

.hero {{
  min-height:610px; border-radius:14px; overflow:hidden; position:relative; margin-bottom:14px;
  border:1px solid {LINE}; box-shadow:0 26px 80px rgba(0,0,0,.30);
  background:#06101E;
}}
.hero::after {{ content:""; position:absolute; inset:0; z-index:1; background:
  linear-gradient(90deg,rgba(6,16,30,.96) 0%,rgba(6,16,30,.78) 44%,rgba(6,16,30,.22) 100%),
  linear-gradient(0deg,rgba(6,16,30,.72) 0%,rgba(6,16,30,.10) 42%,rgba(6,16,30,.20) 100%);
}}
.hero-video {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; opacity:.88; transform:scale(1.02); }}
.hero-wave-light {{ position:absolute; inset:0; opacity:.30; background:
  radial-gradient(circle at 77% 22%,rgba(104,215,255,.38),transparent 24%),
  linear-gradient(115deg,transparent 0%,rgba(232,221,203,.16) 46%,transparent 70%);
  animation:waveLight 9s ease-in-out infinite alternate;
}}
.hero-slide {{ position:absolute; inset:0; opacity:0; background-size:cover; background-position:center; animation:partnerHeroCycle 18s infinite; transform:scale(1.03); }}
.hero-slide.one {{ background-image:url("https://images.unsplash.com/photo-1600210491892-03d54c0aaf87?auto=format&fit=crop&w=2200&q=80"); animation-delay:0s; }}
.hero-slide.two {{ background-image:url("https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=2200&q=80"); animation-delay:6s; }}
.hero-slide.three {{ background-image:url("https://images.unsplash.com/photo-1600566752355-35792bedcfea?auto=format&fit=crop&w=2200&q=80"); animation-delay:12s; }}
@keyframes waveLight {{
  from {{ transform:translateX(-2%) scale(1.02); }}
  to {{ transform:translateX(2%) scale(1.06); }}
}}
@keyframes partnerHeroCycle {{
  0% {{ opacity:0; transform:scale(1.03); }}
  8% {{ opacity:1; }}
  33% {{ opacity:1; transform:scale(1.08); }}
  41% {{ opacity:0; }}
  100% {{ opacity:0; }}
}}
.hero-inner {{ position:absolute; inset:0; z-index:2; padding:54px 58px; display:flex; flex-direction:column; justify-content:space-between; }}
.hero-logo {{ height:24px; width:auto; background:{KCC_BLUE}; border-radius:5px; padding:4px 7px; }}
.partner-lockup {{ display:flex; align-items:flex-start; gap:18px; margin-bottom:28px; flex-wrap:wrap; }}
.partner-hero-logo {{ height:82px; width:auto; max-width:270px; padding:13px 18px; border-radius:9px; background:rgba(255,255,255,.94); box-shadow:0 16px 44px rgba(0,0,0,.24); object-fit:contain; }}
.partner-x {{ color:{PARTNER_SAND}; font-size:16px; font-weight:900; text-transform:uppercase; opacity:.82; }}
.strategic-partner {{ display:flex; flex-direction:column; gap:6px; margin-top:9px; }}
.strategic-partner-label {{ color:#CBD5E1; font-size:9px; font-weight:900; letter-spacing:1.1px; text-transform:uppercase; opacity:.86; }}
.hero-progress {{ display:flex; gap:12px; max-width:720px; margin-top:16px; }}
.hero-progress span {{ display:block; height:5px; flex:1; border-radius:99px; background:rgba(255,255,255,.34); overflow:hidden; }}
.hero-progress span::after {{ content:""; display:block; height:100%; background:{GOLD}; opacity:.72; animation:progressPulse 18s linear infinite; transform-origin:left; }}
.hero-progress span:nth-child(2)::after {{ animation-delay:6s; }}
.hero-progress span:nth-child(3)::after {{ animation-delay:12s; }}
@keyframes progressPulse {{ 0% {{ transform:scaleX(0); }} 28% {{ transform:scaleX(1); }} 33%,100% {{ transform:scaleX(0); }} }}
.eyebrow {{ color:{GOLD}; font-size:12px; font-weight:900; text-transform:uppercase; letter-spacing:2px; }}
.h1 {{ color:#fff; font-size:54px; line-height:1.05; font-weight:900; max-width:980px; margin:12px 0 14px; }}
.hero-copy {{ color:#DDE6F3; font-size:16px; line-height:1.65; max-width:900px; }}
.hero-pills {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:20px; }}
.pill {{ display:inline-flex; align-items:center; border:1px solid rgba(217,164,65,.55); background:rgba(8,17,31,.72); color:#fff; border-radius:999px; padding:8px 12px; font-size:12px; font-weight:900; }}
.hero-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; max-width:1080px; }}
.hero-metric {{ min-height:108px; border:1px solid rgba(255,255,255,.14); border-radius:8px; padding:13px; background:rgba(8,17,31,.76); backdrop-filter:blur(8px); }}
.metric-k {{ color:{MUTED}; font-size:10px; font-weight:900; text-transform:uppercase; }}
.metric-v {{ color:{INK}; font-size:34px; line-height:1; font-weight:900; margin-top:7px; }}
.metric-c {{ color:{MUTED}; font-size:11px; line-height:1.45; margin-top:5px; }}
.trust-number {{ color:#68D7FF; font-size:44px; line-height:1; font-weight:900; letter-spacing:0; }}
.trust-unit {{ color:{INK}; font-size:17px; font-weight:900; margin-left:4px; }}
.why-board {{ border:1px solid {LINE}; border-radius:10px; overflow:hidden; background:linear-gradient(135deg,#101B30 0%,#071328 58%,#0E2372 100%); box-shadow:0 22px 70px rgba(0,0,0,.24); margin-bottom:12px; }}
.why-board-head {{ display:flex; justify-content:space-between; gap:18px; align-items:flex-start; padding:18px 20px; border-bottom:1px solid rgba(255,255,255,.12); }}
.why-board-title {{ color:#fff; font-size:25px; line-height:1.15; font-weight:900; margin-bottom:8px; }}
.why-board-copy {{ color:#C8D4E6; font-size:13px; line-height:1.55; max-width:850px; }}
.source-chip {{ display:inline-flex; align-items:center; white-space:nowrap; border:1px solid rgba(217,164,65,.46); color:{GOLD}; background:rgba(217,164,65,.10); border-radius:999px; padding:8px 11px; font-size:10px; font-weight:900; text-transform:uppercase; }}
.profile-grid {{ display:grid; grid-template-columns:1.08fr .96fr .96fr; gap:12px; padding:14px; }}
.profile-card {{ min-height:292px; border:1px solid rgba(255,255,255,.13); border-radius:8px; background:rgba(8,17,31,.70); padding:16px; position:relative; overflow:hidden; }}
.profile-card::before {{ content:""; position:absolute; inset:0; background:linear-gradient(135deg,rgba(255,255,255,.05),transparent 48%); pointer-events:none; }}
.profile-label {{ color:{MUTED}; font-size:10px; font-weight:900; text-transform:uppercase; margin-bottom:7px; }}
.profile-number {{ color:#fff; font-size:43px; line-height:1; font-weight:900; }}
.profile-sub {{ color:#B9C6D8; font-size:12px; line-height:1.45; margin:7px 0 12px; }}
.profile-row {{ display:flex; gap:14px; align-items:center; margin-top:12px; }}
.capacity-ring {{ --p:86; width:154px; height:154px; flex:0 0 154px; border-radius:50%; background:conic-gradient({GOLD} calc(var(--p) * 1%), rgba(255,255,255,.10) 0); position:relative; box-shadow:inset 0 0 0 1px rgba(255,255,255,.10); }}
.capacity-ring::after {{ content:""; position:absolute; inset:14px; border-radius:50%; background:#0B172B; box-shadow:inset 0 0 28px rgba(0,0,0,.55); }}
.ring-center {{ position:absolute; z-index:1; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; color:#fff; font-weight:900; }}
.ring-center b {{ font-size:32px; line-height:1; }}
.ring-center span {{ color:{MUTED}; font-size:10px; text-transform:uppercase; margin-top:5px; }}
.factory-grid {{ display:grid; grid-template-columns:repeat(6,12px); gap:5px; }}
.factory-grid span {{ width:12px; height:12px; border-radius:2px; background:rgba(104,215,255,.22); border:1px solid rgba(104,215,255,.35); }}
.factory-grid span:nth-child(3n) {{ background:rgba(217,164,65,.50); border-color:rgba(217,164,65,.70); }}
.micro-caption {{ color:{MUTED}; font-size:10px; line-height:1.45; text-transform:uppercase; font-weight:800; margin-top:9px; }}
.revenue-bars {{ display:flex; align-items:end; gap:8px; height:118px; padding:10px 0 4px; border-bottom:1px solid rgba(255,255,255,.13); }}
.revenue-bars span {{ flex:1; min-width:18px; border-radius:5px 5px 0 0; background:linear-gradient(180deg,#68D7FF,#2563EB); box-shadow:0 -12px 28px rgba(59,130,246,.18); }}
.revenue-bars span:nth-child(1) {{ height:38%; opacity:.48; }}
.revenue-bars span:nth-child(2) {{ height:52%; opacity:.58; }}
.revenue-bars span:nth-child(3) {{ height:68%; opacity:.72; }}
.revenue-bars span:nth-child(4) {{ height:82%; opacity:.86; }}
.revenue-bars span:nth-child(5) {{ height:100%; }}
.scale-tags {{ display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:12px; }}
.scale-tag {{ border:1px solid rgba(255,255,255,.12); background:rgba(255,255,255,.045); border-radius:7px; padding:9px; color:#DDE6F3; font-size:11px; font-weight:900; }}
.art-mosaic {{ display:grid; grid-template-columns:repeat(10,1fr); gap:5px; margin:14px 0 13px; }}
.art-mosaic span {{ aspect-ratio:1; border-radius:3px; background:#B98952; opacity:.86; }}
.art-mosaic span:nth-child(3n) {{ background:#D7C6A5; }}
.art-mosaic span:nth-child(4n) {{ background:#5E7C89; }}
.art-mosaic span:nth-child(5n) {{ background:#805F4B; }}
.art-mosaic span:nth-child(7n) {{ background:#A5B3BD; }}
.design-meter {{ height:10px; border-radius:999px; overflow:hidden; background:rgba(255,255,255,.12); }}
.design-meter span {{ display:block; height:100%; width:87%; background:linear-gradient(90deg,{GOLD},#68D7FF); border-radius:999px; }}
.supply-story {{ display:grid; grid-template-columns:.9fr 1.1fr; gap:12px; margin:14px 0; }}
.supply-map {{ border:1px solid {LINE}; border-radius:8px; background:radial-gradient(circle at 72% 52%,rgba(104,215,255,.26),transparent 18%), radial-gradient(circle at 28% 44%,rgba(217,164,65,.24),transparent 16%), linear-gradient(135deg,{PANEL},#09172C); min-height:210px; position:relative; overflow:hidden; }}
.supply-map::before {{ content:""; position:absolute; left:16%; top:50%; width:58%; border-top:2px dashed rgba(217,164,65,.62); transform:rotate(9deg); }}
.map-dot {{ position:absolute; width:14px; height:14px; border-radius:50%; background:{GOLD}; box-shadow:0 0 0 7px rgba(217,164,65,.15); }}
.map-dot.kr {{ left:26%; top:42%; }}
.map-dot.id {{ left:73%; top:56%; background:#68D7FF; box-shadow:0 0 0 7px rgba(104,215,255,.15); }}
.map-label {{ position:absolute; color:#fff; font-size:11px; font-weight:900; background:rgba(8,17,31,.82); border:1px solid rgba(255,255,255,.14); border-radius:999px; padding:6px 9px; }}
.map-label.kr {{ left:19%; top:25%; }}
.map-label.id {{ right:10%; top:68%; }}
.supply-panel {{ border:1px solid {LINE}; border-radius:8px; background:{PANEL}; padding:15px; }}
.supply-kicker {{ color:{GOLD}; font-size:10px; text-transform:uppercase; font-weight:900; margin-bottom:8px; }}
.supply-title {{ color:#fff; font-size:22px; line-height:1.18; font-weight:900; margin-bottom:8px; }}
.supply-copy {{ color:{MUTED}; font-size:12px; line-height:1.6; }}
.timeline-strip {{ display:grid; grid-template-columns:repeat(8,minmax(0,1fr)); gap:8px; margin:12px 0; }}
.timeline-node {{ border:1px solid {LINE}; background:{PANEL}; border-radius:8px; padding:12px; min-height:96px; }}
.timeline-year {{ color:{GOLD}; font-size:20px; font-weight:900; margin-bottom:6px; }}
.timeline-copy {{ color:{MUTED}; font-size:11px; line-height:1.45; }}
.timeline-selected {{ border:1px solid rgba(217,164,65,.68); background:linear-gradient(135deg,rgba(217,164,65,.16),{PANEL}); }}
.proof-grid {{ display:grid; grid-template-columns:1.1fr .9fr; gap:10px; }}
.proof-visual {{ border:1px solid {LINE}; border-radius:8px; background:{PANEL}; padding:16px; }}
.bar-row {{ display:grid; grid-template-columns:150px 1fr 72px; gap:10px; align-items:center; margin:10px 0; }}
.bar-label {{ color:{SOFT}; font-size:12px; font-weight:900; }}
.bar-track {{ height:12px; border-radius:99px; background:#27364F; overflow:hidden; }}
.bar-fill {{ height:100%; border-radius:99px; background:{GOLD}; }}
.bar-fill.blue {{ background:#68D7FF; }}
.bar-value {{ color:{MUTED}; font-size:11px; text-align:right; }}
.tech-badge-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; }}
.tech-badge {{ border:1px solid {LINE}; border-radius:8px; padding:14px; background:{PANEL}; min-height:145px; }}
.tech-big {{ color:{GOLD}; font-size:38px; line-height:1; font-weight:900; margin:8px 0; }}
.spec-result {{ border:1px solid rgba(217,164,65,.48); border-left:4px solid {GOLD}; border-radius:8px; background:{PANEL_2}; padding:15px; margin-top:10px; }}
.spec-title {{ color:{INK}; font-size:18px; font-weight:900; margin-bottom:8px; }}
.spec-copy {{ color:{MUTED}; font-size:12px; line-height:1.6; }}

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
  .grid3, .grid2, .profile-grid, .supply-story {{ grid-template-columns:1fr; }}
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
            [PLATFORM_TITLE, f"Prepared as a continuously updated market, design, and supplier-confidence service"]
            + [f"- {key}: {value}" for key, value in snapshot.items()]
        )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=14 * mm, leftMargin=14 * mm, topMargin=14 * mm, bottomMargin=14 * mm)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(PLATFORM_TITLE, styles["Title"]),
        Spacer(1, 8),
        Paragraph(f"Prepared as a continuously updated market, design, and supplier-confidence service", styles["Normal"]),
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

milestones = [
    ("1958", "Founded KCC Corporation", "The manufacturing foundation behind KCC Glass."),
    ("1987", "Started glass business", "KCC entered glass as a core construction-material business."),
    ("1996", "Started flooring / film business", "Flooring and interior surface know-how became part of the platform."),
    ("2000", "Started automotive glass business", "Precision manufacturing capability expanded."),
    ("2010", "Started total interior business (HomeCC)", "Interior products and customer-facing solutions strengthened."),
    ("2017", "Started PHC pile business", "Construction-material portfolio expanded further."),
    ("2020", "Established KCC GLASS Corporation", "KCC Glass was launched through merger with Korea Autoglass Corporation."),
    ("2024", "Indonesia glass production plant completed", "A major overseas supply-stability message for global customers."),
]

oem_specs = {
    "Plank": {
        "Dryback": {
            "thickness": ["2.0", "2.5", "3.0"],
            "wear": {
                "2.0": ["0.15", "0.20", "0.30"],
                "2.5": ["0.15", "0.20", "0.30", "0.50"],
                "3.0": ["0.15", "0.20", "0.30", "0.50", "0.55"],
            },
            "gf": "N/A",
            "remark": "Glue Down",
        },
        "Looselay": {
            "thickness": ["4.5", "5.0"],
            "wear": {"4.5": ["0.50"], "5.0": ["0.50", "0.55", "0.70"]},
            "gf": "Included",
            "remark": "SENSELAY / anti-slip or acoustic option",
        },
        "sizes": [
            '7.24" x 37.4" / 184 x 950 mm',
            '7.25" x 48" / 184.15 x 1219.2 mm',
            '6" x 36" / 152.4 x 914.4 mm',
            '6" x 48" / 152.4 x 1219.2 mm',
            '7" x 48" / 177.8 x 1219.2 mm',
            '9" x 48" / 228.6 x 1219.2 mm',
            '9" x 60" / 228.6 x 1524 mm',
        ],
    },
    "Tile": {
        "Dryback": {
            "thickness": ["2.0", "2.5", "3.0"],
            "wear": {
                "2.0": ["0.15", "0.20", "0.30"],
                "2.5": ["0.15", "0.20", "0.30", "0.50"],
                "3.0": ["0.15", "0.20", "0.30", "0.50", "0.55"],
            },
            "gf": "N/A",
            "remark": "Glue Down",
        },
        "Looselay": {
            "thickness": ["4.5", "5.0"],
            "wear": {"4.5": ["0.50"], "5.0": ["0.50", "0.55", "0.70"]},
            "gf": "Included",
            "remark": "SENSELAY / anti-slip or acoustic option",
        },
        "sizes": [
            '18" x 18" / 457.2 x 457.2 mm',
            '18" x 36" / 457.2 x 914.4 mm',
            '23.6" x 23.6" / 600 x 600 mm',
        ],
    },
}

logo_white_html = f'<img src="data:image/png;base64,{KCC_LOGO_WHITE}" alt="KCC Glass">' if KCC_LOGO_WHITE else "<strong>KCC GLASS</strong>"
hero_logo_html = f'<img class="hero-logo" src="data:image/png;base64,{KCC_LOGO_WHITE}" alt="KCC Glass">' if KCC_LOGO_WHITE else "<strong>KCC GLASS</strong>"
sidebar_logo_html = f'<img class="side-logo" src="data:image/png;base64,{KCC_LOGO_WHITE}" alt="KCC Glass">' if KCC_LOGO_WHITE else "<strong>KCC GLASS</strong>"
partner_hero_logo_html = f'<img class="partner-hero-logo" src="data:image/png;base64,{PARTNER_LOGO}" alt="KCC Partner Intelligence">' if PARTNER_LOGO else '<div class="partner-logo-word">PARTNER<br>PORTAL</div>'
partner_top_logo_html = f'<img class="top-partner-logo" src="data:image/png;base64,{PARTNER_LOGO}" alt="KCC Partner Intelligence">' if PARTNER_LOGO else '<span class="top-partner-word">Partner Portal</span>'
partner_side_logo_html = f'<img class="side-partner-logo" src="data:image/png;base64,{PARTNER_LOGO}" alt="KCC Partner Intelligence">' if PARTNER_LOGO else '<div class="side-partner-word">Partner<br>Portal</div>'
hero_media_html = (
    f'<video class="hero-video" autoplay muted loop playsinline preload="auto"><source src="data:video/mp4;base64,{HERO_VIDEO}" type="video/mp4"></video><div class="hero-wave-light"></div>'
    if HERO_VIDEO
    else '<div class="hero-slide one"></div><div class="hero-slide two"></div><div class="hero-slide three"></div><div class="hero-wave-light"></div>'
)

with st.sidebar:
    st.markdown(
        f"""
{sidebar_logo_html}
{partner_side_logo_html}
<div class="side-title">KCC Partner Intelligence Platform</div>
<div class="side-copy">Partner service page: market signals, design access, freight timing, and KCC product confidence in one place.</div>
<div class="side-label">Workspace</div>
""",
        unsafe_allow_html=True,
    )
    view = st.radio("Workspace", MENU_ITEMS, label_visibility="collapsed")
    st.markdown('<div class="side-label">Downloads</div>', unsafe_allow_html=True)
    st.download_button(
        "Download Partner Brief",
        data=create_partner_brief_pdf(snapshot, partner_rows),
        file_name=f"KCC_Partner_Intelligence_Brief_{datetime.now().strftime('%Y%m%d')}.pdf",
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
  <div class="top-lockup">
    {partner_top_logo_html}
    <div class="top-partner"><span class="top-partner-label">Strategic flooring partner</span>{logo_white_html}</div>
  </div>
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
  {hero_media_html}
  <div class="hero-inner">
    <div>
      <div class="partner-lockup">
        {partner_hero_logo_html}
        <div class="strategic-partner">
          <div class="strategic-partner-label">Strategic flooring partner</div>
          {hero_logo_html}
        </div>
      </div>
      <div class="eyebrow">Partner intelligence service / continuously updated</div>
      <div class="h1">Market signals, design access, and supplier confidence in one page.</div>
      <div class="hero-copy">
        A general partner-facing page focused on trust: manufacturing scale, design capability,
        technical differentiation, OEM flexibility, and a repeatable account-care rhythm from KCC.
      </div>
      <div class="hero-pills">
        <span class="pill">6,000,000m2 annual capacity</span>
        <span class="pill">$1.3B sales scale</span>
        <span class="pill">1,300 artworks / print rolls</span>
        <span class="pill">OEM-ready specification desk</span>
      </div>
      <div class="hero-progress"><span></span><span></span><span></span></div>
    </div>
    <div class="hero-grid">
      <div class="hero-metric"><div class="metric-k">Annual production capacity</div><div><span class="trust-number">6,000,000</span><span class="trust-unit">m2</span></div><div class="metric-c">Brochure profile / OEM supply confidence</div></div>
      <div class="hero-metric"><div class="metric-k">Sales scale</div><div><span class="trust-number">$1.3B</span></div><div class="metric-c">Corporate scale for overseas buyers</div></div>
      <div class="hero-metric"><div class="metric-k">Artworks / print rolls</div><div><span class="trust-number">1,300</span></div><div class="metric-c">Design depth for partner assortment planning</div></div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    section_title("What Partners Can Use", "partner service")
    st.markdown(
        """
<div class="grid4">
  <div class="card gold"><div class="card-title">Managed account view</div><div class="card-copy">Show partners that KCC can organize market, product, design, and follow-up information in one dedicated workspace.</div></div>
  <div class="card blue"><div class="card-title">Design-first conversation</div><div class="card-copy">Move quickly from market context to the HomeCC LVT Design Library so partners can review current design directions.</div></div>
  <div class="card green"><div class="card-title">Sales support layer</div><div class="card-copy">Help partners explain timing, freight, demand, product confidence, and ESG to their own customer base.</div></div>
  <div class="card red"><div class="card-title">External-safe service</div><div class="card-copy">No internal margin, customer list, CRM, ImportYeti, or sensitive purchasing workflow is exposed in this version.</div></div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_partner_capability_profile() -> None:
    section_title("Why KCC Glass", "scale, history, and supply confidence")
    factory_cells = "".join("<span></span>" for _ in range(30))
    art_cells = "".join("<span></span>" for _ in range(80))
    st.markdown(
        f"""
<div class="why-board">
  <div class="why-board-head">
    <div>
      <div class="why-board-title">KCC Glass LVT Capability Profile</div>
      <div class="why-board-copy">
        A meeting-ready version of the brochure profile: manufacturing capacity, corporate scale,
        design depth, and overseas supply expansion presented as a confidence board for external partners.
      </div>
    </div>
    <div class="source-chip">Source: 2026 LVT Blue Brochure</div>
  </div>
  <div class="profile-grid">
    <div class="profile-card">
      <div class="profile-label">Annual Production Capacity</div>
      <div class="profile-number">6.0M m2</div>
      <div class="profile-sub">Scale signal for stable OEM discussions, repeat supply, and production planning.</div>
      <div class="profile-row">
        <div class="capacity-ring"><div class="ring-center"><b>6M</b><span>per year</span></div></div>
        <div>
          <div class="factory-grid">{factory_cells}</div>
          <div class="micro-caption">Each block represents production scale, not a separate factory line.</div>
        </div>
      </div>
    </div>
    <div class="profile-card">
      <div class="profile-label">Sales Scale</div>
      <div class="profile-number">$1.3B</div>
      <div class="profile-sub">Corporate scale helps partners read KCC as a long-term, lower-risk supplier.</div>
      <div class="revenue-bars"><span></span><span></span><span></span><span></span><span></span></div>
      <div class="scale-tags">
        <div class="scale-tag">Global customer credibility</div>
        <div class="scale-tag">Stable partner posture</div>
      </div>
    </div>
    <div class="profile-card">
      <div class="profile-label">Artworks / Print Rolls</div>
      <div class="profile-number">1,300</div>
      <div class="profile-sub">Design breadth for faster assortment planning, sampling, and localized launches.</div>
      <div class="art-mosaic">{art_cells}</div>
      <div class="design-meter"><span></span></div>
      <div class="micro-caption">Design solution library: wood, stone, neutral, and launch-ready surfaces.</div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
<div class="supply-story">
  <div class="supply-map">
    <div class="map-dot kr"></div><div class="map-label kr">Korea base</div>
    <div class="map-dot id"></div><div class="map-label id">Indonesia 2024</div>
  </div>
  <div class="supply-panel">
    <div class="supply-kicker">Overseas supply-stability message</div>
    <div class="supply-title">2024 Indonesia plant milestone gives the meeting a global supply story.</div>
    <div class="supply-copy">
      Instead of saying only "we can supply," this page gives partners a visible reason to believe KCC can support
      overseas growth: long material history, LVT capability, design depth, and an expanded production footprint.
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    section_title("Interactive Milestone Timeline", "click a year during partner follow-up")
    selected_year = st.radio(
        "Milestone",
        [year for year, _, _ in milestones],
        index=7,
        horizontal=True,
        label_visibility="collapsed",
    )
    selected = next(item for item in milestones if item[0] == selected_year)
    timeline_html = '<div class="timeline-strip">'
    for year, title, copy in milestones:
        cls = "timeline-node timeline-selected" if year == selected_year else "timeline-node"
        timeline_html += f'<div class="{cls}"><div class="timeline-year">{year}</div><div class="timeline-copy">{title}</div></div>'
    timeline_html += "</div>"
    st.markdown(timeline_html, unsafe_allow_html=True)
    st.markdown(
        f"""
<div class="brief">
<b>{selected[0]} - {selected[1]}</b><br>
{selected[2]}
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
<div class="grid4">
  <div class="card gold"><div class="card-title">Meeting angle</div><div class="card-copy">Open with scale first, then move to technology proof and OEM fit only after partners see KCC as a stable supplier.</div></div>
  <div class="card blue"><div class="card-title">Buyer takeaway</div><div class="card-copy">KCC is not just a quote source. It can support design, product performance, and account follow-up in one rhythm.</div></div>
  <div class="card green"><div class="card-title">Supply message</div><div class="card-copy">The 2024 Indonesia milestone creates a practical overseas-growth story without exposing internal operations.</div></div>
  <div class="card red"><div class="card-title">Next screen</div><div class="card-copy">Move to Technology Proof when partners ask why KCC LVT should be trusted inside real homes and commercial spaces.</div></div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
<a class="link-button" href="{HOMECC_DESIGN_LIBRARY_URL}" target="_blank" rel="noopener noreferrer">Open HomeCC LVT Design Library</a>
<a class="link-button secondary" href="{KCC_ESG_URL}" target="_blank" rel="noopener noreferrer">Open ESG Resources</a>
""",
        unsafe_allow_html=True,
    )


def render_technology_proof() -> None:
    section_title("Technology Proof", "Egis annealing / R11 / 13dB")
    st.markdown(
        """
<div class="brief">
Use this screen when the conversation moves from design to performance. It turns the static brochure charts into
partner-friendly proof points: dimensional stability, slip resistance, and acoustic comfort.
</div>
""",
        unsafe_allow_html=True,
    )
    temp = st.slider("Egis annealing dimensional stability test temperature", 0, 80, 60, 20)
    proprietary = max(8, int(22 + temp * 0.82))
    senselay = max(5, int(18 + temp * 0.24))
    st.markdown(
        f"""
<div class="proof-grid">
  <div class="proof-visual">
    <div class="card-title">Egis Annealing System - dimensional stability</div>
    <div class="card-copy">The closer to zero, the better the dimensional stability under temperature variation.</div>
    <div class="bar-row"><div class="bar-label">Proprietary 3T LVT</div><div class="bar-track"><div class="bar-fill" style="width:{proprietary}%"></div></div><div class="bar-value">{temp}C</div></div>
    <div class="bar-row"><div class="bar-label">SENSELAY</div><div class="bar-track"><div class="bar-fill blue" style="width:{senselay}%"></div></div><div class="bar-value">stable</div></div>
  </div>
  <div class="proof-visual">
    <div class="card-title">Partner interpretation</div>
    <div class="card-copy">Egis annealing helps reduce deformation risk caused by temperature and humidity changes. For partners, this is a confidence point for real homes, coastal climates, and repeat orders.</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
<br>
<div class="tech-badge-grid">
  <div class="tech-badge"><div class="metric-k">Non-slip rating</div><div class="tech-big">R11</div><div class="card-copy">DIN 51130:2014 ramp-test rating. Useful for commercial and safety-sensitive applications.</div></div>
  <div class="tech-badge"><div class="metric-k">Sound insulation</div><div class="tech-big">13dB</div><div class="card-copy">SENSELAY 5.0T acoustic layer helps reduce lightweight impact noise.</div></div>
  <div class="tech-badge"><div class="metric-k">Egis Comfort Tech</div><div class="tech-big">PVC integrated</div><div class="card-copy">Acoustic layer option adds cushioning and step comfort at the bottom of the product.</div></div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_oem_spec_finder() -> None:
    section_title("OEM Spec Finder", "Plank / Tile / Dryback / Looselay")
    st.markdown(
        """
<div class="brief">
Use this during the meeting when a partner asks, "Can this size or construction work?" Select the product type and installation style,
then check available thickness, wear layer, glass fiber, and size options.
</div>
""",
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        product_type = st.radio("Format", ["Plank", "Tile"], horizontal=True)
    with c2:
        install_type = st.radio("Construction", ["Dryback", "Looselay"], horizontal=True)
    spec = oem_specs[product_type][install_type]
    with c3:
        thickness = st.selectbox("Thickness (mm)", spec["thickness"])
    with c4:
        wear = st.selectbox("Wear layer (mm)", spec["wear"][thickness])
    size = st.selectbox("Available size", oem_specs[product_type]["sizes"])
    st.markdown(
        f"""
<div class="spec-result">
  <div class="spec-title">{product_type} / {install_type} / {thickness}mm / wear layer {wear}mm</div>
  <div class="spec-copy">
    <b>Available size:</b> {size}<br>
    <b>Glass fiber:</b> {spec["gf"]}<br>
    <b>Remark:</b> {spec["remark"]}<br>
    <b>Partner answer:</b> This combination can be discussed as an OEM starting point; final availability depends on order base and confirmed production review.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    render_dark_table(
        pd.DataFrame(
            [[product_type, install_type, thickness, wear, spec["gf"], spec["remark"], size]],
            columns=["Format", "Construction", "Thickness", "Wear Layer", "Glass Fiber", "Remark", "Size"],
        )
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
    section_title("Design Library Hub", "first visual stop for partners")
    st.markdown(
        f"""
<div class="brief">
For ongoing partner outreach, this should be the fastest visual moment: open the HomeCC LVT Design Library,
review current KCC LVT designs, then use the market and freight screens to explain timing and support.
</div>
<a class="link-button" href="{HOMECC_DESIGN_LIBRARY_URL}" target="_blank" rel="noopener noreferrer">View New LVT Designs</a>
""",
        unsafe_allow_html=True,
    )
    design_rows = pd.DataFrame(
        [
            ["Live design review", "Open the HomeCC library from the partner page and let partners react to current LVT visuals."],
            ["Dealer wall planning", "Shortlist designs that are easiest to show in dealer displays, sample boards, and showroom updates."],
            ["Builder / multi-family", "Match practical wood and neutral visuals with demand signals from starts, permits, and completions."],
            ["Retail refresh", "Use new design visuals as a reason for a structured follow-up after outreach."],
            ["Next conversation", "Ask each partner which designs should be sampled, localized, or prepared for a launch set."],
        ],
        columns=["Design Use Case", "How Partners Can Use It"],
    )
    render_dark_table(design_rows)


def render_partner_kit() -> None:
    section_title("Partner Outreach Brief", "talk track and follow-up")
    left, right = st.columns([1.05, 0.95])
    with left:
        panel("Suggested Outreach Copy", "email / LinkedIn")
        st.markdown(
            """
<div class="brief">
We prepared this desk as a short example of how KCC can support partners after initial outreach:
market signals, freight timing, HomeCC LVT design access, product confidence, ESG resources,
and follow-up questions in one place. The goal is to make collaboration easier after the first reply.
</div>
""",
            unsafe_allow_html=True,
        )
        close_panel()
    with right:
        panel("Partner Follow-up Prompts", "meeting openers")
        prompts = pd.DataFrame(
            [
                ["Market", "Which demand signal matters most for the partner's customer base right now?"],
                ["Freight", "Which port or lane is most sensitive for the partner's replenishment plan?"],
                ["Design", "Which HomeCC LVT designs should we review or sample first?"],
                ["Support", "Would ESG or technical documentation help with the partner's builder/commercial accounts?"],
            ],
            columns=["Topic", "Question"],
        )
        render_dark_table(prompts)
        close_panel()
    section_title("Download Center", "shareable assets")
    st.download_button(
        "Download Partner Brief PDF",
        data=create_partner_brief_pdf(snapshot, partner_rows),
        file_name=f"KCC_Partner_Intelligence_Brief_{datetime.now().strftime('%Y%m%d')}.pdf",
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
elif view == "Why KCC Glass":
    render_partner_capability_profile()
elif view == "Technology Proof":
    render_technology_proof()
elif view == "OEM Spec Finder":
    render_oem_spec_finder()
elif view == "Market Pulse":
    render_market_pulse()
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



