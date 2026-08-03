"""
data/ — data retrieval and shaping layer.

loaders.py    -> stable public API, this is what videos/*/data_prep.py imports
sources/      -> per-source implementation (nba_api, bref, spotrac) — fragile,
                 isolated, not imported directly outside this package
transforms.py -> source-agnostic pandas cleaning shared across loaders
raw_cache/    -> gitignored raw HTTP responses (debug/re-parse without re-fetching)
cache/        -> gitignored final processed data, namespaced per video slug
"""