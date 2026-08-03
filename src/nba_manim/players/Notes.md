# Player registry — notes

## What this is
A small, hand-maintained lookup table (`registry.csv`) mapping an internal
`player_id` to each external source's ID for that player. It is NOT a stats
or salary database — those get pulled fresh per-video via
`nba_manim.data.loaders` and cached under `data/cache/<video_slug>/`.

## Growing the registry
Add players as videos need them — same philosophy as TEAM_COLORS in
theme.py. Don't try to pre-populate every player in league history.

When adding a row:
1. `player_id` = lowercase_snake_case, stable forever once created (this is
   the join key for headshots and any cross-video reference — do not rename
   it later even if you spot a typo in `full_name`).
2. `nba_api_id` — look up via nba_api's `players` static index
   (`nba_api.stats.static.players.find_players_by_full_name(...)`).
3. `bref_slug` — the URL slug from the player's Basketball-Reference page
   (e.g. basketball-reference.com/players/j/jamesle01.html -> jamesle01).
4. `spotrac_slug` — the URL slug from their Spotrac contract page.
5. `aliases` — pipe-separated nicknames/shorthand you're likely to type in
   a script (helps resolve_player() match "LBJ", "Steph", etc.)

## Headshots — LICENSING CAUTION
Official NBA/team headshots are copyrighted. Before using any headshot
image in a rendered video:
- Prefer nba_api's official stats.nba.com headshot endpoint only if your
  use falls under fair use for commentary/education — this is a legal
  judgment call, not a technical one, and rules differ by jurisdiction
  and monetization status. When unsure, don't use the image.
- Consider commissioning or drawing simple original illustrations/avatars
  instead of using licensed photography — this sidesteps the issue
  entirely and can become a recognizable channel style.
- Never bulk-scrape and redistribute headshot images outside this repo.

This file is a placeholder for that decision — resolve it before you
ship a video that displays player photos.