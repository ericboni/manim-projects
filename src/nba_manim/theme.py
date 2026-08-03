"""
theme.py — single source of truth for visual style across every video.

Import from here in every scene/component instead of hardcoding hex values.
If you rebrand (new palette, new font), you change it in exactly one place.

Usage:
    from nba_manim.theme import Colors, Fonts, Sizes, TEAM_COLORS
    Text("Clutch Time", color=Colors.PRIMARY, font=Fonts.HEADING)
"""

from manim import ManimColor


# ---------------------------------------------------------------------------
# Core brand palette — used for anything NOT team-specific
# ---------------------------------------------------------------------------
class Colors:
    # Backgrounds
    BG_DARK = ManimColor("#0E1117")
    BG_PANEL = ManimColor("#161B22")

    # Text
    TEXT_PRIMARY = ManimColor("#F5F5F5")
    TEXT_SECONDARY = ManimColor("#9CA3AF")
    TEXT_MUTED = ManimColor("#6B7280")

    # Brand accents (pick something that isn't a real team's colors,
    # so your "voice" is visually distinct from any team you're covering)
    PRIMARY = ManimColor("#F5A623")     # amber — headline highlights
    SECONDARY = ManimColor("#2DD4BF")   # teal — secondary highlights

    # Semantic stat colors — keep these CONSISTENT across every video
    POSITIVE = ManimColor("#22C55E")    # made shots, positive delta, wins
    NEGATIVE = ManimColor("#EF4444")    # missed shots, negative delta, losses
    NEUTRAL = ManimColor("#EAB308")     # league average / baseline

    # Court rendering
    COURT_LINE = ManimColor("#D1D5DB")
    COURT_WOOD = ManimColor("#C9975B")
    COURT_PAINT = ManimColor("#1E293B")

    # Shot chart intensity scale (cold -> hot), used for hexbin/heatmap fills
    HEAT_SCALE = ["#1E3A8A", "#2563EB", "#F5A623", "#EF4444"]


# ---------------------------------------------------------------------------
# Team colors — extend as you cover more teams. Keys are standard 3-letter
# team abbreviations (matches nba_api / stats.nba.com codes) so lookups are
# consistent with whatever you pull from data/loaders.py
# ---------------------------------------------------------------------------
TEAM_COLORS: dict[str, dict[str, ManimColor]] = {
    # Atlantic
    "BOS": {"primary": ManimColor("#007A33"), "secondary": ManimColor("#BA9653")},
    "BKN": {"primary": ManimColor("#000000"), "secondary": ManimColor("#FFFFFF")},
    "NYK": {"primary": ManimColor("#006BB6"), "secondary": ManimColor("#F58426")},
    "PHI": {"primary": ManimColor("#006BB6"), "secondary": ManimColor("#ED174C")},
    "TOR": {"primary": ManimColor("#CE1141"), "secondary": ManimColor("#000000")},

    # Central
    "CHI": {"primary": ManimColor("#CE1141"), "secondary": ManimColor("#000000")},
    "CLE": {"primary": ManimColor("#6F263D"), "secondary": ManimColor("#FFB81C")},
    "DET": {"primary": ManimColor("#C8102E"), "secondary": ManimColor("#1D42BA")},
    "IND": {"primary": ManimColor("#002D62"), "secondary": ManimColor("#FDBB30")},
    "MIL": {"primary": ManimColor("#00471B"), "secondary": ManimColor("#EEE1C6")},

    # Southeast
    "ATL": {"primary": ManimColor("#E03A3E"), "secondary": ManimColor("#C1D32F")},
    "CHA": {"primary": ManimColor("#1D1160"), "secondary": ManimColor("#00788C")},
    "MIA": {"primary": ManimColor("#98002E"), "secondary": ManimColor("#F9A01B")},
    "ORL": {"primary": ManimColor("#0077C0"), "secondary": ManimColor("#C4CED4")},
    "WAS": {"primary": ManimColor("#002B5C"), "secondary": ManimColor("#E31837")},

    # Northwest
    "DEN": {"primary": ManimColor("#0E2240"), "secondary": ManimColor("#FEC524")},
    "MIN": {"primary": ManimColor("#0C2340"), "secondary": ManimColor("#236192")},
    "OKC": {"primary": ManimColor("#007AC1"), "secondary": ManimColor("#EF3B24")},
    "POR": {"primary": ManimColor("#E03A3E"), "secondary": ManimColor("#000000")},
    "UTA": {"primary": ManimColor("#002B5C"), "secondary": ManimColor("#F9A01B")},

    # Pacific
    "GSW": {"primary": ManimColor("#1D428A"), "secondary": ManimColor("#FFC72C")},
    "LAC": {"primary": ManimColor("#C8102E"), "secondary": ManimColor("#1D428A")},
    "LAL": {"primary": ManimColor("#552583"), "secondary": ManimColor("#FDB927")},
    "PHX": {"primary": ManimColor("#1D1160"), "secondary": ManimColor("#E56020")},
    "SAC": {"primary": ManimColor("#5A2D81"), "secondary": ManimColor("#63727A")},

    # Southwest
    "DAL": {"primary": ManimColor("#00538C"), "secondary": ManimColor("#002B5E")},
    "HOU": {"primary": ManimColor("#CE1141"), "secondary": ManimColor("#000000")},
    "MEM": {"primary": ManimColor("#5D76A9"), "secondary": ManimColor("#12173F")},
    "NOP": {"primary": ManimColor("#0C2340"), "secondary": ManimColor("#E31837")},
    "SAS": {"primary": ManimColor("#C4CED4"), "secondary": ManimColor("#000000")},
}

DEFAULT_TEAM_COLORS = {"primary": ManimColor("#4B5563"), "secondary": ManimColor("#9CA3AF")}


def team_colors(abbr: str) -> dict[str, ManimColor]:
    """Safe lookup with a sane fallback for teams not yet added above."""
    return TEAM_COLORS.get(abbr.upper(), DEFAULT_TEAM_COLORS)


# ---------------------------------------------------------------------------
# Fonts — must be installed on the render machine (system fonts or assets/fonts)
# ---------------------------------------------------------------------------
class Fonts:
    HEADING = "Inter Bold"
    BODY = "Inter"
    MONO = "JetBrains Mono"   # for stat tickers / numeric tables


# ---------------------------------------------------------------------------
# Sizing — keep title/label/tick sizes consistent so every video "feels" the
# same even when built months apart
# ---------------------------------------------------------------------------
class Sizes:
    TITLE = 56
    SUBTITLE = 32
    LABEL = 24
    TICK = 18
    STROKE_WIDTH_THIN = 1.5
    STROKE_WIDTH_MED = 3
    STROKE_WIDTH_THICK = 5