"""
config.py — non-visual configuration: filesystem paths, data-fetching
policy, and render defaults. Visual style (colors/fonts/sizes) lives in
theme.py instead — keep that split.
"""

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent.parent

PATHS = {
    # gitignored — see data/loaders.py and data/sources/base.py
    "raw_cache": PACKAGE_ROOT / "data" / "raw_cache",
    "cache": PACKAGE_ROOT / "data" / "cache",
    # licensing unresolved — see players/Notes.md before populating this
    "headshots": PROJECT_ROOT / "assets" / "headshots",
    "videos": PROJECT_ROOT / "videos",
}


class DataConfig:
    """Fetch policy for data/sources/base.py's cached_get()."""

    # Seconds between requests to the same domain. bref has no published
    # rate limit; 8s matches the pacing already used (and not rate-limited
    # by bref) in videos/001's exploration notebook — don't lower this
    # without a reason, scraping thousands of players at a faster rate
    # risks an IP ban.
    RATE_LIMITS = {
        "basketball-reference.com": 8.0,
    }
    DEFAULT_RATE_LIMIT = 2.0

    MAX_RETRIES = 3
    REQUEST_TIMEOUT = 15
    USER_AGENT = "Mozilla/5.0 (personal research script)"


class RenderDefaults:
    """Manim CLI flags for videos/*/render.sh — keep preview fast, final crisp."""

    PREVIEW_FLAGS = "-qm"   # medium quality, fast iteration
    FINAL_FLAGS = "-qh"     # high quality, final export
    FPS = 30


class CourtDimensions:
    """
    Standard NBA half/full-court measurements in feet, for a future
    CourtMobject (see components/ — not built yet, nothing consumes this
    today). Public dimensions, not derived from any scraped source.
    """

    LENGTH_FT = 94.0
    WIDTH_FT = 50.0
    KEY_WIDTH_FT = 16.0
    KEY_LENGTH_FT = 19.0
    FREE_THROW_CIRCLE_RADIUS_FT = 6.0
    THREE_POINT_ARC_RADIUS_FT = 23.75
    THREE_POINT_CORNER_FT = 22.0
    HOOP_CENTER_FROM_BASELINE_FT = 5.25
    BACKBOARD_WIDTH_FT = 6.0
