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

# Initial prep only with 2000. To explore consistency of salary data before.
# players/Notes.md philosophy of only pulling what a video actually needs.
MIN_DEBUT_YEAR = 1999


def _target_player_ids() -> list[str]:
    players = all_players()
    players = players.assign(From=pd.to_numeric(players["From"], errors="coerce"))
    return players.loc[players["From"] >= MIN_DEBUT_YEAR, "bref_id"].tolist()


def _append_combined(new_rows: pd.DataFrame, out_path: Path) -> None:
    """
    Merges one player's rows into the video-level combined parquet,
    replacing any prior rows for the same bref_id — safe to call again on
    a retry. Written via a temp file + replace so a crash mid-write never
    leaves out_path truncated/corrupt; the previous good version survives.

    out_path and scrape_log.csv are a pair — a player marked 'done' in the
    log is never re-fetched, so don't delete out_path without also
    clearing the log entries you want re-collected into it.
    """
    if new_rows.empty:
        return
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        existing = pd.read_parquet(out_path)
        existing = existing[~existing["bref_id"].isin(new_rows["bref_id"].unique())]
        combined = pd.concat([existing, new_rows], ignore_index=True)
    else:
        combined = new_rows
    tmp_path = out_path.with_suffix(".tmp")
    combined.to_parquet(tmp_path)
    tmp_path.replace(out_path)


def main() -> None:
    video_dir = Path(__file__).parent
    player_ids = _target_player_ids()
    print(f"{len(player_ids)} players debuted {MIN_DEBUT_YEAR}+, running scrape job...")

    out_path = Path(PATHS["cache"]) / VIDEO_SLUG / "all_salaries.parquet"

    def fetch(player_id: str) -> int:
        """
        Runs one player through the pipeline; the row count is returned
        purely so ScrapeJob's log has something readable per item. The
        per-player parquet cache in loaders.py is the durable source, but
        each successful fetch also folds straight into out_path so the
        video-level table stays complete as the job runs, not just at the
        very end.
        """
        df = get_salary_history_by_id(player_id)
        _append_combined(df, out_path)
        return len(df)

    job = ScrapeJob(
        items=player_ids,
        fetch_fn=fetch,
        log_path=video_dir / "scrape_log.csv",
    )
    job.run()

    combined = pd.read_parquet(out_path) if out_path.exists() else pd.DataFrame()
    scraped_ids = set(combined["bref_id"].unique()) if not combined.empty else set()
    missing = len(player_ids) - len(scraped_ids)
    if missing:
        print(f"{missing} players have no cached salary data (no salary table on bref, or permanently failed — see scrape_log.csv)")

    print(f"Saved {len(combined)} rows across {len(scraped_ids)} players -> {out_path}")


if __name__ == "__main__":
    main()
