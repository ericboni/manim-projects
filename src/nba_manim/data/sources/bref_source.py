"""
bref_source.py — Basketball-Reference scraping. Functions here return raw
tables as pandas.read_html gives them; cleaning (dollar parsing, season
normalization, Career-row filtering) belongs in transforms.py/loaders.py,
not here — keep this module a thin, source-specific fetch layer.
"""

import io

import pandas as pd

from nba_manim.data.sources.base import cached_get

BASE_URL = "https://www.basketball-reference.com"


def get_salary_history(bref_id: str) -> pd.DataFrame:
    """
    Raw per-season salary table from a player's bref page (table id
    'all_salaries'), tagged with bref_id. Returns an empty DataFrame if
    the player has no salary table (e.g. never signed an NBA contract) —
    callers should treat an empty result as "no data," not an error.
    """
    url = f"{BASE_URL}/players/{bref_id[0]}/{bref_id}.html"
    html = cached_get(url, cache_key=f"bref_salary_{bref_id}")

    try:
        tables = pd.read_html(io.StringIO(html), attrs={"id": "all_salaries"}, flavor="lxml")
    except ValueError:
        return pd.DataFrame()

    df = tables[0]
    df["bref_id"] = bref_id
    return df
