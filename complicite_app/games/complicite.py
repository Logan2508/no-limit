"""Jeu de la Complicité : 2 équipes de 2, on fait deviner sans se faire intercepter."""

from __future__ import annotations

import time

import streamlit as st

from .. import ui
from ..characters import (
    DIFFICULTY_COLORS,
    DIFFICULTY_LABELS,
    Character,
    draw,
    load_themes,
    pool,
)

KEY = "complicite"

TEAM_PRESETS = [
    {"name": "Les Rouges", "emoji": "🔴"},
    {"name": "Les Bleus", "emoji": "🔵"},
]


# --------------------------------------------------------------------------- state


def _state() -> dict:
    return st.session_state[KEY]


def reset() -> None:
    st.session_state.pop(KEY, None)


def _init_if_needed() -> None:
    if KEY not in st.session_state:
        st.session_state[KEY] = {"phase": "setup"}


def _start_game(settings: dict) -> None:
    st.session_state[KEY] = {
        "phase": "handoff",
        "settings": settings,
        "teams": [
            {
                "name": t["name"],
                "emoji": t["emoji"],
                "score": 0,
                "difficulty": settings["difficulty"],
                "streak": 0,
                "giver": 0,
                "players": t["players"],
            }
            for t in settings["teams"]
        ],
        "active": 0,
        "round": 1,
        "seen": set(),
        "character": None,
        "started_at": None,
        "history": [],
        "last": None,
    }


# ------------------------------------------------------------------------- helpers


def _active_team(s: dict) -> dict:
    return s["teams"][s["active"]]


def _giver_name(team: dict) -> str:
    return team["players"][team["giver"] % 2]


def _guesser_name(team: dict) -> str:
    return team["players"][(team["giver"] + 1) % 2]


def _adapt_difficulty(team: dict, success: bool, enabled: bool) -> None:
    if not enabled:
        return
    team["streak"] = max(1, team["streak"] + 1) if success else min(-1, team["streak"] - 1)
    if team["streak"] >= 2:
        team["difficulty"] = min(3, team["difficulty"] + 1)
        team["streak"] = 0
    elif team["streak"] <= -2:
        team["difficulty"] = max(1, team["difficulty"] - 1)
        team["streak"] = 0


def _resolve(outcome: str) -> None:
    """outcome ∈ {found, intercepted, missed}"""
    s = _state()
    team = _active_team(s)
    other = s["teams"][1 - s["active"]]
    char: Character = s["character"]
    pts = char.points
    if s.get("hint_used"):
        pts = max(1, pts - 1)

    if outcome == "found":
        team["score"] += pts
        msg = f"✅ {team['emoji']} {team['name']} marque +{pts} avec « {char.name} »"
    elif outcome == "intercepted":
        other["score"] += pts
        msg = f"🕵️ Interception ! {other['emoji']} {other['name']} vole +{pts} (« {char.name} »)"
    else:
        msg = f"⌛ Raté : c'était « {char.name} »"

    _adapt_difficulty(team, outcome == "found", s["settings"]["adaptive"])
    team["giver"] += 1
    s["history"].insert(0, msg)
    s["last"] = msg
    s["character"] = None
    s["started_at"] = None
    s["hint_used"] = False

    target = s["settings"]["target_score"]
    max_rounds = s["settings"]["max_rounds"]
    turns_done = s["round"] * 2 if s["active"] == 1 else s["round"] * 2 - 1
    reached = any(t["score"] >= target for t in s["teams"])
    # on termine un tour complet pour l'équité
    if reached and s["active"] == 1:
        s["phase"] = "over"
        return
    if s["active"] == 1:
        s["round"] += 1
        if s["round"] > max_rounds:
            s["phase"] = "over"
            return
    s["active"] = 1 - s["active"]
    s["phase"] = "handoff"
    _ = turns_done


# --------------------------------------------------------------------------- views


def _setup_view() -> None:
    themes = load_themes()
    ui.header("🤝 La Complicité", "2 équipes de 2. Fais deviner sans te faire intercepter.")

    with st.container():
        st.markdown("#### 👥 Les équipes")
        cols = st.columns(2)
        teams = []
        for i, col in enumerate(cols):
            with col:
                preset = TEAM_PRESETS[i]
                name = st.text_input("Équipe", preset["name"], key=f"cc_team_{i}")
                p1 = st.text_input("Joueur 1", f"Joueur {2 * i + 1}", key=f"cc_p{i}_1")
                p2 = st.text_input("Joueur 2", f"Joueur {2 * i + 2}", key=f"cc_p{i}_2")
                teams.append(
                    {"name": name or preset["name"], "emoji": preset["emoji"], "players": [p1, p2]}
                )

    st.markdown("#### 🎭 Thèmes")
    default_themes = [t for t in ("disney", "chanteurs") if t in themes]
    selected = st.multiselect(
        "Choisis un ou plusieurs univers",
        options=list(themes.keys()),
        default=default_themes,
        format_func=lambda t: f"{themes[t].emoji} {themes[t].label}",
        label_visibility="collapsed",
    )
    if selected:
        total = len(pool(selected, [1, 2, 3]))
        st.caption(f"{total} personnages disponibles dans la sélection.")

    st.markdown("#### 🎚️ Difficulté")
    diff = st.select_slider(
        "Niveau de départ",
        options=[1, 2, 3],
        value=2,
        format_func=lambda d: DIFFICULTY_LABELS[d],
        label_visibility="collapsed",
    )
    adaptive = st.toggle(
        "Difficulté adaptative", value=True, help="Monte après 2 réussites, redescend après 2 échecs."
    )

    st.markdown("#### ⚙️ Règles")
    c1, c2 = st.columns(2)
    duration = c1.number_input("Temps / tour (s)", 20, 180, 60, step=10)
    target = c2.number_input("Score cible", 5, 100, 15, step=1)
    max_rounds = st.number_input("Manches max", 3, 50, 12, step=1)
    allow_hint = st.toggle("Autoriser l'indice (−1 point)", value=True)

    st.write("")
    if st.button("🚀 Commencer la partie", type="primary", use_container_width=True):
        if not selected:
            st.error("Choisis au moins un thème !")
            return
        _start_game(
            {
                "teams": teams,
                "themes": selected,
                "difficulty": int(diff),
                "adaptive": adaptive,
                "duration": int(duration),
                "target_score": int(target),
                "max_rounds": int(max_rounds),
                "allow_hint": allow_hint,
            }
        )
        st.rerun()

    with st.expander("📖 Règles du jeu"):
        st.markdown(
            """
**But** : faire deviner un personnage à ton coéquipier **sans que l'équipe adverse comprenne**.

1. Le téléphone passe au **donneur d'indices** de l'équipe active, qui révèle le personnage (seul).
2. Il fait deviner comme il veut : allusions, souvenirs communs, private jokes… mais **interdit** de dire
   le nom, un mot de la même famille, ou d'épeler.
3. Son binôme a le temps imparti pour trouver → l'équipe marque les points du personnage
   (Facile = 1, Moyen = 2, Difficile = 3).
4. Si l'**équipe adverse** devine avant / comprend l'allusion, elle crie « Intercepté ! » et **vole les points**.
5. Les rôles tournent à chaque tour et la difficulté s'adapte au niveau de chaque équipe.
            """
        )


def _handoff_view() -> None:
    s = _state()
    team = _active_team(s)
    ui.header("🤝 La Complicité", f"Manche {s['round']} / {s['settings']['max_rounds']}")
    ui.scoreboard(s["teams"], s["active"])
    if s.get("last"):
        st.markdown(f'<div class="cc-card cc-log">{s["last"]}</div>', unsafe_allow_html=True)

    d = team["difficulty"]
    ui.card(
        f'<div style="text-align:center">'
        f'<div class="cc-sub" style="margin:0">Au tour de</div>'
        f'<div style="font-size:1.6rem;font-weight:800">{team["emoji"]} {team["name"]}</div>'
        f'<div style="margin:.7rem 0">📱 <b>{_giver_name(team)}</b> prend le téléphone<br>'
        f'🧠 <b>{_guesser_name(team)}</b> devine</div>'
        f'{ui.chip(DIFFICULTY_LABELS[d], DIFFICULTY_COLORS[d])}</div>'
    )

    if st.button("👀 Révéler le personnage", type="primary", use_container_width=True):
        char = draw(s["settings"]["themes"], team["difficulty"], s["seen"])
        if char is None:
            st.warning("Plus de personnages disponibles, la partie s'arrête !")
            s["phase"] = "over"
            st.rerun()
        s["character"] = char
        s["seen"].add(char.uid)
        s["started_at"] = time.time()
        s["hint_used"] = False
        s["phase"] = "playing"
        st.rerun()

    if st.button("🏁 Terminer la partie", use_container_width=True):
        s["phase"] = "over"
        st.rerun()


def _render_timer(s: dict) -> None:
    duration = s["settings"]["duration"]

    def _body() -> None:
        remaining = duration - (time.time() - s["started_at"])
        ui.timer_bar(remaining, duration)
        if remaining <= 0 and s["phase"] == "playing":
            _resolve("missed")
            st.rerun(scope="app")

    if hasattr(st, "fragment"):
        st.fragment(_body, run_every=1)()
    else:  # pragma: no cover - vieilles versions de Streamlit
        _body()


def _playing_view() -> None:
    s = _state()
    team = _active_team(s)
    char: Character = s["character"]
    d = char.difficulty

    ui.scoreboard(s["teams"], s["active"])
    _render_timer(s)

    hint_html = ""
    if s.get("hint_used") and char.hint:
        hint_html = f'<div class="cc-hint">💡 {char.hint}</div>'
    pts_label = f"{DIFFICULTY_LABELS[d]} · {char.points} pt" + ("s" if char.points > 1 else "")
    theme_chip = ui.chip(f"{char.theme_emoji} {char.theme_label}")
    diff_chip = ui.chip(pts_label, DIFFICULTY_COLORS[d])
    st.markdown(
        f'<div class="cc-hero">'
        f"{theme_chip} {diff_chip}"
        f'<div class="cc-name">{char.name}</div>'
        f'<div class="cc-sub" style="margin:0">{_giver_name(team)} fait deviner à {_guesser_name(team)}</div>'
        f"{hint_html}</div>",
        unsafe_allow_html=True,
    )

    st.write("")
    if st.button("✅ Trouvé !", type="primary", use_container_width=True):
        _resolve("found")
        st.rerun()

    c1, c2 = st.columns(2)
    if c1.button("🕵️ Intercepté", use_container_width=True):
        _resolve("intercepted")
        st.rerun()
    if c2.button("⏭️ Passer", use_container_width=True):
        _resolve("missed")
        st.rerun()

    if s["settings"]["allow_hint"] and char.hint and not s.get("hint_used"):
        if st.button("💡 Indice (−1 point)", use_container_width=True):
            s["hint_used"] = True
            st.rerun()


def _over_view() -> None:
    s = _state()
    teams = s["teams"]
    ui.header("🏆 Fin de partie", f"{s['round']} manche(s) jouée(s)")
    ui.scoreboard(teams, None)
    st.write("")

    best = max(t["score"] for t in teams)
    winners = [t for t in teams if t["score"] == best]
    if len(winners) == 1:
        st.balloons()
        ui.card(
            f'<div style="text-align:center;font-size:1.5rem;font-weight:800">'
            f'{winners[0]["emoji"]} {winners[0]["name"]} gagne !</div>'
        )
    else:
        ui.card('<div style="text-align:center;font-size:1.4rem;font-weight:800">Égalité parfaite 🤝</div>')

    with st.expander("📜 Historique", expanded=False):
        for line in s["history"]:
            st.markdown(f'<div class="cc-log">{line}</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    if c1.button("🔁 Rejouer", type="primary", use_container_width=True):
        _start_game(s["settings"])
        st.rerun()
    if c2.button("⚙️ Nouveaux réglages", use_container_width=True):
        reset()
        st.rerun()


def render() -> None:
    _init_if_needed()
    phase = _state()["phase"]
    if phase == "setup":
        _setup_view()
    elif phase == "handoff":
        _handoff_view()
    elif phase == "playing":
        _playing_view()
    else:
        _over_view()
