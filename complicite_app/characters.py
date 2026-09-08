"""Chargement et tirage des personnages par thème et difficulté."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

THEMES_DIR = Path(__file__).parent / "data" / "themes"

DIFFICULTY_LABELS = {1: "Facile", 2: "Moyen", 3: "Difficile"}
DIFFICULTY_POINTS = {1: 1, 2: 2, 3: 3}
DIFFICULTY_COLORS = {1: "#3ddc97", 2: "#ffc857", 3: "#ff6b6b"}


@dataclass(frozen=True)
class Character:
    name: str
    difficulty: int
    theme_id: str
    theme_label: str
    theme_emoji: str
    hint: str | None = None

    @property
    def uid(self) -> str:
        return f"{self.theme_id}::{self.name}"

    @property
    def points(self) -> int:
        return DIFFICULTY_POINTS[self.difficulty]


@dataclass(frozen=True)
class Theme:
    id: str
    label: str
    emoji: str
    description: str
    characters: tuple[Character, ...]

    def count_by_difficulty(self) -> dict[int, int]:
        return {d: sum(1 for c in self.characters if c.difficulty == d) for d in (1, 2, 3)}


@lru_cache(maxsize=1)
def load_themes() -> dict[str, Theme]:
    themes: dict[str, Theme] = {}
    for path in sorted(THEMES_DIR.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        chars = tuple(
            Character(
                name=c["name"],
                difficulty=int(c.get("difficulty", 1)),
                theme_id=raw["id"],
                theme_label=raw["label"],
                theme_emoji=raw.get("emoji", "🎲"),
                hint=c.get("hint"),
            )
            for c in raw["characters"]
        )
        themes[raw["id"]] = Theme(
            id=raw["id"],
            label=raw["label"],
            emoji=raw.get("emoji", "🎲"),
            description=raw.get("description", ""),
            characters=chars,
        )
    return themes


def pool(theme_ids: list[str], difficulties: list[int]) -> list[Character]:
    themes = load_themes()
    return [
        c
        for tid in theme_ids
        if tid in themes
        for c in themes[tid].characters
        if c.difficulty in difficulties
    ]


def draw(
    theme_ids: list[str],
    difficulty: int,
    already_seen: set[str],
    rng: random.Random | None = None,
) -> Character | None:
    """Tire un personnage non encore vu, en élargissant la difficulté si besoin."""
    rng = rng or random
    # ordre de repli : difficulté cible, puis les plus proches
    order = sorted((1, 2, 3), key=lambda d: (abs(d - difficulty), d))
    for d in order:
        candidates = [c for c in pool(theme_ids, [d]) if c.uid not in already_seen]
        if candidates:
            return rng.choice(candidates)
    return None
