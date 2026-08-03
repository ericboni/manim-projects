"""
loaders.py — STABLE public API. This is the ONLY module a video's
data_prep.py should import from; everything under sources/ is
implementation detail that can change without breaking videos, as long as
these function signatures stay stable.
"""

from pathlib import Path

import pandas as pd

from nba_manim.config import PATHS
from nba_manim.data import transforms
from nba_manim.data.sources import bref_source
from nba_manim.players.registry import resolve_player


def get_salary_history(player: str, use_cache: bool = True) -> pd.DataFrame:
    """
    Cleaned per-season salary history for one player, looked up by name
    via players.registry.resolve_player(). Cached to
    data/cache/<player_id>_salaries.parquet so repeated calls across a
    video's data_prep.py runs don't re-scrape bref.
    """
    resolved = resolve_player(player)
    if resolved is None:
        raise ValueError(f"Could not resolve player: {player!r} — check registry.csv")

    player_id = resolved["player_id"]
    cache_path = Path(PATHS["cache"]) / f"{player_id}_salaries.parquet"

    if use_cache and cache_path.exists():
        return pd.read_parquet(cache_path)

    raw = bref_source.get_salary_history(resolved["bref_id"])
    if raw.empty:
        return raw

    cleaned = transforms.clean_salary_table(raw)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_parquet(cache_path)
    return cleaned
