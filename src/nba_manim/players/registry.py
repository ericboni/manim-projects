"""
registry.py — resolves a player name (however it's typed in a script or a
video's data_prep.py) into the bref player-index row for that player.

Backed directly by the raw Basketball-Reference player index
(registry.csv, ~5400 rows covering all of NBA history) — bref_id doubles
as the stable internal player_id, since bref never reassigns it. There is
currently no aliases/nba_api_id/spotrac_slug support; add those columns
here (and a lookup layer) once a video actually needs named-alias
resolution or a source keyed by a different ID.

Usage:
    from nba_manim.players.registry import resolve_player, headshot_path

    player = resolve_player("Kareem Abdul-Jabbar")
    player["player_id"]   -> "abdulka01"
    player["full_name"]   -> "Kareem Abdul-Jabbar"

    headshot_path("abdulka01")  -> Path to assets/headshots/abdulka01.png
"""

import difflib
from functools import lru_cache
from pathlib import Path

import pandas as pd

from nba_manim.config import PATHS

REGISTRY_PATH = Path(__file__).parent / "registry.csv"

# Fuzzy-match threshold: below this, resolve_player() refuses to guess
# rather than silently returning the wrong player.
FUZZY_MATCH_CUTOFF = 0.75


@lru_cache(maxsize=1)
def _load_registry() -> pd.DataFrame:
    df = pd.read_csv(REGISTRY_PATH, dtype=str)
    df["player_id"] = df["bref_id"]
    df["full_name"] = df["Player"].str.rstrip("*")  # bref marks Hall of Famers with a trailing '*'
    return df


def _build_lookup_index(df: pd.DataFrame) -> dict[str, str]:
    """
    Maps each lowercased full_name -> player_id. Names shared by multiple
    players across NBA history collide here (last row in registry.csv
    wins) — pass a bref_id directly to get_player_by_id() when you need a
    specific one of two same-named players.
    """
    return {
        name.strip().lower(): player_id
        for name, player_id in zip(df["full_name"], df["player_id"])
    }


def resolve_player(query: str) -> dict | None:
    """
    Resolve a free-text name to a registry row (as a dict).

    Tries an exact case-insensitive match on full_name first, then falls
    back to fuzzy matching. Returns None if nothing clears the confidence
    threshold — callers should treat that as "name doesn't match anything
    in the bref index," not silently skip the player.
    """
    df = _load_registry()
    index = _build_lookup_index(df)
    key = query.strip().lower()

    if key in index:
        player_id = index[key]
    else:
        matches = difflib.get_close_matches(
            key, index.keys(), n=1, cutoff=FUZZY_MATCH_CUTOFF
        )
        if not matches:
            return None
        player_id = index[matches[0]]

    row = df[df["player_id"] == player_id].iloc[0]
    return row.to_dict()


def get_player_by_id(player_id: str) -> dict | None:
    """Direct lookup by bref_id when you already have it."""
    df = _load_registry()
    match = df[df["player_id"] == player_id]
    if match.empty:
        return None
    return match.iloc[0].to_dict()

def get_player_by_bre_f_id(bref_id: str) -> dict | None:
    """Direct lookup by bref_id when you already have it."""
    df = _load_registry()
    match = df[df["bref_id"] == bref_id]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def headshot_path(player_id: str) -> Path:
    """
    Path to a player's headshot asset, keyed by bref_id (not name), so a
    name correction in registry.csv never breaks the asset reference.
    Does not guarantee the file exists — see players/Notes.md re:
    licensing before displaying any headshot in a rendered video.
    """
    return PATHS["headshots"] / f"{player_id}.png"


def all_players() -> pd.DataFrame:
    """Full bref player index, e.g. for building a video's candidate list."""
    return _load_registry().copy()
