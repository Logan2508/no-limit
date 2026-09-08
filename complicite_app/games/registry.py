"""Registre des jeux disponibles dans l'application."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True)
class GameSpec:
    id: str
    name: str
    emoji: str
    tagline: str
    players: str
    render: Callable[[], None] | None = None
    available: bool = True
    reset: Callable[[], None] | None = field(default=None)


def get_games() -> list[GameSpec]:
    from . import complicite

    return [
        GameSpec(
            id="complicite",
            name="La Complicité",
            emoji="🤝",
            tagline="Fais deviner un personnage à ton binôme sans que l'autre équipe comprenne.",
            players="4 joueurs (2 équipes de 2)",
            render=complicite.render,
            reset=complicite.reset,
        ),
        GameSpec(
            id="undercover",
            name="L'Intrus",
            emoji="🕵️",
            tagline="Tout le monde a le même mot… sauf un.",
            players="3 à 8 joueurs",
            available=False,
        ),
        GameSpec(
            id="mime",
            name="Time's Up",
            emoji="⏱️",
            tagline="Trois manches, un paquet de cartes, zéro dignité.",
            players="4+ joueurs",
            available=False,
        ),
    ]
