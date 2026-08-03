"""
transforms.py — pandas cleaning/reshaping shared across multiple loaders.

Anything here should be source-agnostic: "normalize a season string,"
"convert a salary string like '$52.6M' to a float," "standardize team
abbreviations." If a transform only ever applies to one source's raw
format, it belongs inside that source module instead.
"""

import re

import pandas as pd


def parse_dollar_string(value: str) -> float:
    """'$52.6M' -> 52_600_000.0, '$8,000,000' -> 8_000_000.0"""
    if pd.isna(value):
        return float("nan")
    s = str(value).strip().replace("$", "").replace(",", "")
    multiplier = 1
    if s.upper().endswith("M"):
        multiplier = 1_000_000
        s = s[:-1]
    elif s.upper().endswith("K"):
        multiplier = 1_000
        s = s[:-1]
    return float(s) * multiplier


def parse_dollar_to_int(value: str) -> "pd.Int64Dtype | int":
    """
    Same as parse_dollar_string but returns a whole-dollar integer
    (nullable Int64-compatible) instead of a float. Salaries don't have
    cents, so int is the honest type — avoids float rounding noise when
    these numbers get summed/diffed later.
    """
    parsed = parse_dollar_string(value)
    if pd.isna(parsed):
        return pd.NA
    return int(round(parsed))


def clean_salary_table(df: pd.DataFrame, salary_col: str = "Salary") -> pd.DataFrame:
    """
    Cleans a bref-style salary history table:
      1. Drops the trailing 'Career' totals row bref appends — it's a
         lifetime sum, not a season, and will wreck any year-over-year
         diff (a "pay cut") if left in.
      2. Converts the salary column from '$8,533,333' text to a nullable
         Int64 column.

    Row-dropping is done by NaN league ('Lg') rather than matching the
    string 'Career', since bref's row layout is a more stable signal than
    English text that could theoretically vary.
    """
    cleaned = df[df["Lg"].notna()].copy()
    cleaned[salary_col] = cleaned[salary_col].apply(parse_dollar_to_int).astype("Int64")
    return cleaned.reset_index(drop=True)


def normalize_season(season: str) -> str:
    """Accepts '2025-26', '2025-2026', or '2026' -> canonical '2025-26'."""
    season = season.strip()
    if re.fullmatch(r"\d{4}", season):
        year = int(season)
        return f"{year - 1}-{str(year)[-2:]}"
    match = re.fullmatch(r"(\d{4})-(\d{2,4})", season)
    if match:
        start = match.group(1)
        end = match.group(2)[-2:]
        return f"{start}-{end}"
    raise ValueError(f"Unrecognized season format: {season}")