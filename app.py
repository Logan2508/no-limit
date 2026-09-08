"""Point d'entrée Streamlit : « Complicité & Co », la boîte à jeux de soirée."""

from __future__ import annotations

import streamlit as st

from complicite_app import ui
from complicite_app.characters import load_themes
from complicite_app.games import get_games

st.set_page_config(
    page_title="Complicité & Co",
    page_icon="🤝",
    layout="centered",
    initial_sidebar_state="collapsed",
)

ui.inject_css()

if "route" not in st.session_state:
    st.session_state.route = "home"

games = {g.id: g for g in get_games()}


def _home() -> None:
    ui.header("No Limit", "Elouan j'espère t'as bien la rage.")
    for game in games.values():
        state = "" if game.available else ' style="opacity:.45"'
        ui.card(
            f"<div{state}>"
            f'<div style="font-size:1.25rem;font-weight:800">{game.emoji} {game.name}</div>'
            f'<div class="cc-sub" style="margin:.25rem 0 .5rem">{game.tagline}</div>'
            f"{ui.chip(game.players)}"
            f'{"" if game.available else " " + ui.chip("Bientôt", "#ffc857")}'
            f"</div>"
        )
        if game.available:
            if st.button(
                f"Jouer à {game.name}",
                key=f"go_{game.id}",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.route = game.id
                st.rerun()

    themes = load_themes()
    total = sum(len(t.characters) for t in themes.values())
    st.caption(f"📚 Base de données : {total} personnages sur {len(themes)} thèmes.")


def _game_page(game_id: str) -> None:
    if st.button("← Retour aux jeux", key="back_home"):
        st.session_state.route = "home"
        st.rerun()
    games[game_id].render()


route = st.session_state.route
if route in games and games[route].available:
    _game_page(route)
else:
    _home()
