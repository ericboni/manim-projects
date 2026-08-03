# nba-manim — project context

NBA data visualization videos built with Manim. This file exists so Claude
Code has context without re-deriving decisions already made — read it
before making structural changes.

## What this is

A YouTube channel exploring NBA data/history through Manim animations.
Content mixes salary/contract history, trades, and stats analysis.
Currently one active video in progress: `videos/001_paycut_history/`.

## Architecture — the core rule

**`src/nba_manim/data/loaders.py` is the ONLY module a video's
`data_prep.py` should import from.** Everything under `data/sources/`
(nba_api, bref, spotrac wrappers) is implementation detail that can change
without breaking videos, as long as `loaders.py`'s function signatures
stay stable. Do not import from `nba_manim.data.sources` directly inside
`videos/`.

Same philosophy elsewhere: `nba_manim/__init__.py` and `data/__init__.py`
are intentionally thin (theme/config constants only) — they don't proxy
every function in the package. Import from the actual submodule
(`nba_manim.players.registry`, `nba_manim.data.loaders`, etc.) rather than
expecting everything at the top level.

## Folder structure

```
src/nba_manim/
├── theme.py          # Colors, Fonts, Sizes, TEAM_COLORS (all 30 teams), team_colors()
├── config.py         # CourtDimensions, PATHS, RenderDefaults, DataConfig
├── players/
│   ├── registry.csv      # player_id -> names/aliases/nba_api_id/bref_slug/spotrac_slug
│   └── registry.py       # resolve_player(), get_player_by_id(), headshot_path()
│                          # Fuzzy-matches names/aliases; refuses to guess below confidence
│                          # threshold rather than silently misattributing data.
├── data/
│   ├── loaders.py         # STABLE public API — see rule above
│   ├── transforms.py      # parse_dollar_to_int, clean_salary_table, normalize_season
│   ├── job_runner.py      # ScrapeJob — resumable, CSV-logged batch scraping (see below)
│   ├── sources/
│   │   ├── base.py            # cached_get() — encoding fix, HTML-comment strip,
│   │   │                      # per-domain rate limiting, raw response caching
│   │   ├── nba_api_source.py  # wraps official nba_api package — working, tested
│   │   ├── bref_source.py     # scraping via pandas.read_html — working
│   │   └── spotrac_source.py  # INTENTIONALLY STUBBED — see ToS note below
│   ├── raw_cache/          # gitignored — raw HTML/JSON per source
│   └── cache/               # gitignored — processed parquet, namespaced per video slug
└── components/            # NOT YET BUILT — CourtMobject, ShotChart, etc. go here
                            # once a second video needs to reuse a visual.
                            # Don't pre-build reusable components before a
                            # second use case is real — YAGNI applies here.

videos/
└── 00N_slug_name/          # sequential numbering, NOT year-prefixed
    ├── README.md               # scope, status, what's explicitly cut
    ├── script.md               # voiceover beats tagged to scene filenames
    ├── data_prep.py             # pulls/cleans this video's data via loaders.py only
    ├── scrape_log.csv           # if using ScrapeJob — CHECK THIS INTO GIT (small,
    │                            # human-readable, doubles as provenance documentation)
    ├── scene_NN_name.py         # one file per script beat
    └── render.sh                # exact manim commands, preview + final quality
```

## Known gotchas (already solved once — don't re-solve)

1. **Mojibake ("Ã³" instead of "ó")** — `requests` defaults to Latin-1 when
   a server (bref) doesn't send a charset header. Fixed centrally in
   `sources/base.py`'s `cached_get()` via `resp.encoding = resp.apparent_encoding`.
   If you bypass `cached_get()` and call `requests` directly, you WILL hit
   this again — route everything through `cached_get()`.

2. **bref wraps tables in HTML comments** — many secondary tables
   (salaries, advanced stats) render fine in a browser via JS but are
   invisible to `pd.read_html` on the raw source, because they sit inside
   `<!-- -->`. Also fixed centrally in `cached_get()` (strips comment
   markers unconditionally — harmless on pages that don't do this).

3. **bref salary tables end with a "Career" totals row** — not a real
   season, will corrupt any year-over-year diff if left in. Filtered out
   in `transforms.clean_salary_table()` by checking for NaN `Lg`
   (more stable than matching the string "Career").

4. **Mid-season trades create duplicate season rows** — a traded player
   has two rows for the same season (one per team). Decide explicitly per
   analysis whether to sum them or keep separate — don't let a naive
   groupby silently pick one.

5. **`pd.read_html` needs `lxml` or `html5lib` installed** — not bundled
   with pandas. `pip install lxml` if you hit
   `ImportError: Import lxml failed`.

## Data source policy

- **nba_api**: preferred whenever data exists here — structured JSON, far
  less fragile than scraping. Already rate-limited via `DataConfig`.
- **Basketball-Reference**: scraped for what nba_api doesn't cover
  (historical data, salary history). Expect this to break occasionally
  when bref changes their HTML — fix belongs in `bref_source.py` only.
- **Spotrac**: intentionally NOT automated. Their detailed contract/cap
  data sits behind a paid tier; scraping paywalled/ToS-restricted content
  is a legal judgment call, not just a technical one. Current approach:
  hand-enter the specific figures a video needs directly in that video's
  `data_prep.py`, with a comment citing the source URL. See
  `data/NOTES.md` before automating this.
- **Player headshots**: licensing unresolved — see `players/NOTES.md`.
  Don't assume it's fine to display official photos without checking.

## Long-running scrapes (8h+ jobs)

Use `data/job_runner.py`'s `ScrapeJob` — logs status per item to a CSV,
resumable across crashes/restarts, retries failures up to `max_retries`
then stops (won't loop forever on a permanently broken item). Run as a
background script, not a notebook cell, for anything multi-hour — notebooks
don't survive the machine sleeping or a disconnect.

## Open items / inconsistencies not yet resolved

- `videos/001_paycut_history/` currently only has an exploration notebook —
  the scraping loop and cleaning logic worked out there haven't been
  formalized into `data_prep.py` yet.
- No `.gitignore` yet — needs `raw_cache/`, `cache/`, `__pycache__/`,
  `*.egg-info`.
- `components/` is empty — first real Manim visual work hasn't started.
- `pyproject.toml` dependencies are unpinned — fine for now, revisit once
  the setup is stable (a breaking release mid-project would be worse).

## Setup

```bash
pip install -r requirements.txt   # editable install of nba_manim + deps
```

Then `from nba_manim.players import resolve_player` etc. works from any
notebook or script, regardless of location — no sys.path hacks needed.