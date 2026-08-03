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


def get_salary_history_by_id(player_id: str, use_cache: bool = True) -> pd.DataFrame:
    """
    Cleaned per-season salary history for one player, keyed directly by
    player_id (bref_id) — skips name resolution entirely. Use this over
    get_salary_history() for bulk jobs iterating a known list of IDs,
    where resolve_player()'s fuzzy/collision-prone name matching is
    neither needed nor safe (two players can share a full_name).
    Cached to data/cache/<player_id>_salaries.parquet.
    """
    cache_path = Path(PATHS["cache"]) / f"{player_id}_salaries.parquet"
    if use_cache and cache_path.exists():
        return pd.read_parquet(cache_path)

    raw = bref_source.get_salary_history(player_id)
    if raw.empty:
        return raw

    cleaned = transforms.clean_salary_table(raw)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_parquet(cache_path)
    return cleaned


def get_salary_history(player: str, use_cache: bool = True) -> pd.DataFrame:
    """
    Cleaned per-season salary history for one player, looked up by name
    via players.registry.resolve_player(). For bulk work over a list of
    known bref_ids, use get_salary_history_by_id() instead.
    """
    resolved = resolve_player(player)
    if resolved is None:
        raise ValueError(f"Could not resolve player: {player!r} — check registry.csv")
    return get_salary_history_by_id(resolved["player_id"], use_cache=use_cache)
