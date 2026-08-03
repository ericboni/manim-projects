"""
nba_manim — shared components, theme, and data utilities for NBA data
visualization videos built with Manim.

This __init__.py re-exports the handful of names every video's scene files
need constantly, so imports stay short:

    from nba_manim import Colors, Fonts, Sizes, team_colors
    from nba_manim import CourtDimensions, PATHS

Anything used less often (specific components, data loaders, geometry
helpers) should be imported from its actual submodule instead of routed
through here — keep this file small on purpose. If it starts accumulating
every class in the package, that's a sign to stop and just import from
submodules directly in videos/.
"""

from nba_manim.theme import (
    Colors,
    Fonts,
    Sizes,
    TEAM_COLORS,
    team_colors,
)
from nba_manim.config import (
    CourtDimensions,
    PATHS,
    RenderDefaults,
    DataConfig,
)

__version__ = "0.1.0"

__all__ = [
    "Colors",
    "Fonts",
    "Sizes",
    "TEAM_COLORS",
    "team_colors",
    "CourtDimensions",
    "PATHS",
    "RenderDefaults",
    "DataConfig",
]