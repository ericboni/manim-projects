"""
data_prep.py — video 001 (paycut_history).

Scrapes salary history for every NBA player who debuted in MIN_DEBUT_YEAR
or later from Basketball-Reference, via nba_manim.data.loaders and
nba_manim.data.job_runner — the only nba_manim.data modules this file
imports from (never nba_manim.data.sources directly, per CLAUDE.md).

This is a long-running job (thousands of players, rate-limited to one
request every 8s -> multiple hours) — run it as a background script, not
a notebook cell, so it survives disconnects:

    python videos/001_Paycut_history/data_prep.py

Safe to interrupt and re-run: ScrapeJob skips players already logged
'done' in scrape_log.csv (checked into git as provenance), and retries
'failed' ones up to job_runner's max_retries before giving up on them
permanently. loaders.py's own per-player parquet cache means a player is
never re-scraped once fetched, even if the log is cleared.
"""

from pathlib import Path

import pandas as pd

from nba_manim.config import PATHS
from nba_manim.data.job_runner import ScrapeJob
from nba_manim.data.loaders import get_salary_history_by_id
from nba_manim.players import all_players

VIDEO_SLUG = "001_paycut_history"

# Salary data on bref gets sparse/unreliable before the 2000s — see
# players/Notes.md philosophy of only pulling what a video actually needs.
MIN_DEBUT_YEAR = 2000


def _target_player_ids() -> list[str]:
    players = all_players()
    players = players.assign(From=pd.to_numeric(players["From"], errors="coerce"))
    return players.loc[players["From"] >= MIN_DEBUT_YEAR, "bref_id"].tolist()


def _fetch(player_id: str) -> int:
    """
    Runs one player through the pipeline; returns the row count purely so
    ScrapeJob's log has something readable per item. The actual data
    lands in loaders.py's per-player parquet cache, not in this return
    value — see _combine_all() below for how it's collected back up.
    """
    return len(get_salary_history_by_id(player_id))


def _combine_all(player_ids: list[str]) -> pd.DataFrame:
    """Gathers every player's cached salary history into one video-level table."""
    frames = []
    for player_id in player_ids:
        cache_path = Path(PATHS["cache"]) / f"{player_id}_salaries.parquet"
        if cache_path.exists():
            frames.append(pd.read_parquet(cache_path))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def main() -> None:
    video_dir = Path(__file__).parent
    player_ids = _target_player_ids()
    print(f"{len(player_ids)} players debuted {MIN_DEBUT_YEAR}+, running scrape job...")

    job = ScrapeJob(
        items=player_ids,
        fetch_fn=_fetch,
        log_path=video_dir / "scrape_log.csv",
    )
    job.run()

    combined = _combine_all(player_ids)
    missing = len(player_ids) - combined["bref_id"].nunique() if not combined.empty else len(player_ids)
    if missing:
        print(f"{missing} players have no cached salary data (no salary table on bref, or permanently failed — see scrape_log.csv)")

    out_path = Path(PATHS["cache"]) / VIDEO_SLUG / "all_salaries.parquet"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(out_path)
    print(f"Saved {len(combined)} rows across {combined['bref_id'].nunique() if not combined.empty else 0} players -> {out_path}")


if __name__ == "__main__":
    main()
