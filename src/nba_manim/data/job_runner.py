"""
job_runner.py — resumable batch scraping for long-running jobs. bref's
per-player salary history is the motivating case: thousands of players,
one HTTP request each, rate-limited to one every few seconds -> hours.

Progress is logged one row per item to a CSV (conventionally a video's
scrape_log.csv, checked into git as provenance — small and human-
readable). Re-running a job skips items already marked 'done' and retries
'failed' items up to max_retries before giving up on them permanently — a
single bad item (no salary table, a 404, a timeout) never takes down the
whole batch.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

import pandas as pd

LOG_COLUMNS = ["item", "status", "retries", "error"]


@dataclass
class ScrapeJob:
    items: Iterable[str]
    fetch_fn: Callable[[str], object]
    log_path: Path
    max_retries: int = 3

    def _load_log(self) -> pd.DataFrame:
        if self.log_path.exists():
            return pd.read_csv(self.log_path, dtype=str)
        return pd.DataFrame(columns=LOG_COLUMNS)

    def _save_log(self, log: pd.DataFrame) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        log.to_csv(self.log_path, index=False)

    def run(self) -> dict:
        """
        Runs the job, returns {item: result} for items fetched
        successfully THIS run. Results from a prior run are not
        re-returned here — only the log persists across runs; fetch_fn
        should cache its own results (e.g. via sources.base.cached_get)
        if you need those too.
        """
        log = self._load_log()
        results = {}

        for item in self.items:
            existing = log[log["item"] == item]
            retries = int(existing.iloc[0]["retries"]) if not existing.empty else 0
            status = existing.iloc[0]["status"] if not existing.empty else None

            if status == "done":
                continue
            if status == "failed" and retries >= self.max_retries:
                continue

            log = log[log["item"] != item]
            try:
                results[item] = self.fetch_fn(item)
                log = pd.concat([log, pd.DataFrame([{
                    "item": item, "status": "done", "retries": retries, "error": "",
                }])], ignore_index=True)
            except Exception as exc:
                log = pd.concat([log, pd.DataFrame([{
                    "item": item, "status": "failed", "retries": retries + 1, "error": str(exc),
                }])], ignore_index=True)
            self._save_log(log)

        return results
