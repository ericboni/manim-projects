"""
nba_api_source.py — thin wrapper around the official nba_api package.

Minimal by design: no video currently pulls live stats through here
(video 001 is bref-only, salary history). Add functions as a stats-driven
video actually needs them — don't pre-build career-stats/game-log
wrappers ahead of a real use case.
"""

from nba_api.stats.static import players


def find_nba_api_id(full_name: str) -> int | None:
    """
    Look up a player's nba_api player ID by exact full name, using
    nba_api's local static index (no network call, no rate limiting
    needed). Returns None if there's no exact match — nba_api's own fuzzy
    matching is unreliable for common names, so this deliberately doesn't
    fuzzy-match; use players.registry.resolve_player() for that instead.
    """
    matches = players.find_players_by_full_name(full_name)
    exact = [p for p in matches if p["full_name"].lower() == full_name.strip().lower()]
    if len(exact) == 1:
        return exact[0]["id"]
    return None
