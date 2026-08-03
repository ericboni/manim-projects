"""
registry.py — resolves a player name (however it's typed in a script or a
video's data_prep.py) into the internal `player_id`, plus every external
source's ID for that player.

This is a LOOKUP HELPER, not a stats database. It holds no points/salary/
season data — that's fetched fresh per video via data/loaders.py. This
module only answers "who is this, and what ID do I use to go get their data
from nba_api / Basketball-Reference / Spotrac."

Usage:
    from nba_manim.players.registry import resolve_player, headshot_path

    player = resolve_player("LBJ")
    player["player_id"]     -> "lebron_james"
    player["nba_api_id"]    -> 2544
    player["bref_slug"]     -> "jamesle01"

    headshot_path("lebron_james")  -> Path to assets/headshots/lebron_james.png
"""

import difflib
from pathlib import Path
from functools import lru_cache

import pandas as pd

#from nba_manim.config import PATHS

REGISTRY_PATH = Path(__file__).parent / "registry.csv"

# Fuzzy-match threshold: below this, resolve_player() refuses to guess
# rather than silently returning the wrong player.
FUZZY_MATCH_CUTOFF = 0.75


@lru_cache(maxsize=1)
def _load_registry() -> pd.DataFrame:
    df = pd.read_csv(REGISTRY_PATH, dtype=str)
    #df["nba_api_id"] = pd.to_numeric(df["nba_api_id"], errors="coerce").astype("Int64")
    return df


def _build_lookup_index(df: pd.DataFrame) -> dict[str, str]:
    """Maps every known name/alias (lowercased) -> player_id."""
    index: dict[str, str] = {}
    for _, row in df.iterrows():
        names = [row["full_name"]]
        if pd.notna(row.get("aliases")):
            names += str(row["aliases"]).split("|")
        for name in names:
            index[name.strip().lower()] = row["player_id"]
    return index


def resolve_player(query: str) -> dict | None:
    """
    Resolve a free-text name to a registry row (as a dict).

    Tries exact match (case-insensitive, including aliases) first, then
    falls back to fuzzy matching against known names. Returns None if
    nothing clears the confidence threshold — callers should treat that as
    "needs a manual registry.csv entry," not silently skip the player.
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
    """Direct lookup when you already have the internal player_id."""
    df = _load_registry()
    match = df[df["player_id"] == player_id]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def headshot_path(player_id: str) -> Path:
    """
    Path to a player's headshot asset, keyed by player_id (not name), so
    a name correction in registry.csv never breaks the asset reference.
    Does not guarantee the file exists — see players/NOTES.md re: sourcing.
    """
    #return PATHS["headshots"] / f"{player_id}.png"
    pass

def all_players() -> pd.DataFrame:
    """Full registry table, e.g. for building a video's candidate list."""
    return _load_registry().copy()