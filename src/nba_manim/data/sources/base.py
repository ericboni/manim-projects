"""
sources/base.py — shared HTTP fetch layer. Every source module should
route requests through cached_get() instead of calling requests directly:
it fixes bref's missing-charset mojibake, strips HTML-comment-wrapped
tables, rate-limits per domain, and caches raw responses to disk so
re-running a notebook or a job doesn't re-hit the network.
"""

import time
from pathlib import Path
from urllib.parse import urlparse

import requests

from nba_manim.config import DataConfig, PATHS

_last_request_at: dict[str, float] = {}


def _rate_limit(domain: str) -> None:
    domain = domain.removeprefix("www.")
    min_interval = DataConfig.RATE_LIMITS.get(domain, DataConfig.DEFAULT_RATE_LIMIT)
    last = _last_request_at.get(domain)
    if last is not None:
        elapsed = time.monotonic() - last
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
    _last_request_at[domain] = time.monotonic()


def cached_get(url: str, cache_key: str, params: dict | None = None, headers: dict | None = None) -> str:
    """
    Fetch `url` and return decoded, HTML-comment-stripped text.

    Raw responses are cached to PATHS["raw_cache"]/<cache_key>.html — pass
    a stable, filesystem-safe key (e.g. a bref_id) so repeated calls across
    notebook restarts or job resumes don't re-hit the network. Delete the
    cached file manually to force a re-fetch.
    """
    cache_path = Path(PATHS["raw_cache"]) / f"{cache_key}.html"
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")

    _rate_limit(urlparse(url).netloc)

    resp = requests.get(
        url,
        params=params,
        headers=headers or {"User-Agent": DataConfig.USER_AGENT},
        timeout=DataConfig.REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding  # bref sends no charset header -> mojibake otherwise
    html = resp.text.replace("<!--", "").replace("-->", "")

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(html, encoding="utf-8")
    return html
