"""Style global et petits composants d'interface (mobile first)."""

from __future__ import annotations

import streamlit as st

CSS = """
<style>
:root {
  --c-bg1: #1b1035;
  --c-bg2: #2b1055;
  --c-accent: #ff5f9e;
  --c-accent2: #7b5cff;
  --c-ok: #3ddc97;
  --c-warn: #ffc857;
  --c-ko: #ff6b6b;
  --glass: rgba(255,255,255,0.08);
  --glass-b: rgba(255,255,255,0.18);
}

.stApp {
  background:
    radial-gradient(1200px 600px at 10% -10%, #4b1e8c 0%, transparent 55%),
    radial-gradient(900px 600px at 110% 10%, #ff5f9e33 0%, transparent 50%),
    linear-gradient(160deg, var(--c-bg1) 0%, var(--c-bg2) 60%, #120a26 100%);
  background-attachment: fixed;
  color: #f4f1ff;
}

#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 1.2rem; padding-bottom: 4rem; max-width: 720px;}

h1, h2, h3, h4, p, span, label, li {color: #f4f1ff !important;}

.cc-title {
  font-size: 2.1rem; font-weight: 800; letter-spacing: -0.5px;
  background: linear-gradient(90deg, #fff 0%, var(--c-accent) 60%, var(--c-accent2) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  margin-bottom: 0.1rem;
}
.cc-sub {opacity: .72; font-size: .95rem; margin-bottom: 1.1rem;}

.cc-card {
  background: var(--glass);
  border: 1px solid var(--glass-b);
  border-radius: 22px;
  padding: 1.1rem 1.2rem;
  backdrop-filter: blur(14px);
  box-shadow: 0 10px 40px rgba(0,0,0,.35);
  margin-bottom: .9rem;
}

.cc-hero {
  text-align: center;
  padding: 2.2rem 1rem;
  border-radius: 26px;
  border: 1px solid var(--glass-b);
  background: linear-gradient(145deg, rgba(255,95,158,.22), rgba(123,92,255,.22));
  box-shadow: 0 14px 50px rgba(0,0,0,.4);
  animation: pop .35s ease-out;
}
@keyframes pop {from {transform: scale(.94); opacity: 0;} to {transform: scale(1); opacity: 1;}}

.cc-name {font-size: 2.3rem; font-weight: 800; line-height: 1.15; margin: .4rem 0;}
.cc-hint {opacity: .8; font-style: italic; margin-top: .5rem;}

.cc-chip {
  display: inline-block; padding: .25rem .7rem; border-radius: 999px;
  font-size: .78rem; font-weight: 700; letter-spacing: .3px;
  border: 1px solid var(--glass-b); background: var(--glass);
}

.cc-score {
  display: flex; gap: .6rem;
}
.cc-team {
  flex: 1; text-align: center; padding: .7rem .4rem; border-radius: 18px;
  border: 1px solid var(--glass-b); background: var(--glass);
}
.cc-team.active {
  border-color: var(--c-accent);
  box-shadow: 0 0 0 2px rgba(255,95,158,.35), 0 8px 30px rgba(255,95,158,.25);
  background: linear-gradient(145deg, rgba(255,95,158,.25), rgba(123,92,255,.18));
}
.cc-team .n {font-size: .8rem; opacity: .8; text-transform: uppercase; letter-spacing: .6px;}
.cc-team .p {font-size: 1.9rem; font-weight: 800; line-height: 1;}

.cc-timer {
  height: 12px; border-radius: 999px; background: rgba(255,255,255,.12); overflow: hidden;
}
.cc-timer > div {height: 100%; border-radius: 999px; transition: width .4s linear;}

div.stButton > button {
  width: 100%;
  border-radius: 16px;
  padding: .8rem 1rem;
  font-weight: 700;
  font-size: 1rem;
  border: 1px solid var(--glass-b);
  background: var(--glass);
  color: #fff;
  transition: transform .12s ease, box-shadow .12s ease;
}
div.stButton > button:hover {transform: translateY(-2px); border-color: var(--c-accent); color: #fff;}
div.stButton > button:active {transform: translateY(0);}
div.stButton > button[kind="primary"] {
  background: linear-gradient(120deg, var(--c-accent), var(--c-accent2));
  border: none;
  box-shadow: 0 8px 26px rgba(255,95,158,.35);
}

div[data-testid="stMetricValue"] {color: #fff !important;}
section[data-testid="stSidebar"] {background: rgba(15,8,35,.85); backdrop-filter: blur(10px);}

.cc-log {font-size: .85rem; opacity: .85; margin: .15rem 0;}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def header(title: str, subtitle: str = "") -> None:
    st.markdown(f'<div class="cc-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="cc-sub">{subtitle}</div>', unsafe_allow_html=True)


def card(html: str) -> None:
    st.markdown(f'<div class="cc-card">{html}</div>', unsafe_allow_html=True)


def chip(text: str, color: str = "#ffffff") -> str:
    return (
        f'<span class="cc-chip" style="color:{color} !important;'
        f'border-color:{color}55;background:{color}1a">{text}</span>'
    )


def scoreboard(teams: list[dict], active_index: int | None) -> None:
    blocks = []
    for i, team in enumerate(teams):
        cls = "cc-team active" if i == active_index else "cc-team"
        blocks.append(
            f'<div class="{cls}"><div class="n">{team["emoji"]} {team["name"]}</div>'
            f'<div class="p">{team["score"]}</div></div>'
        )
    st.markdown(f'<div class="cc-score">{"".join(blocks)}</div>', unsafe_allow_html=True)


def timer_bar(remaining: float, total: float) -> None:
    ratio = max(0.0, min(1.0, remaining / total)) if total else 0.0
    color = "#3ddc97" if ratio > 0.5 else ("#ffc857" if ratio > 0.2 else "#ff6b6b")
    st.markdown(
        f'<div class="cc-timer"><div style="width:{ratio * 100:.1f}%;background:{color}"></div></div>'
        f'<div style="text-align:center;font-weight:800;font-size:1.6rem;margin-top:.35rem">'
        f"{int(max(0, remaining))} s</div>",
        unsafe_allow_html=True,
    )
