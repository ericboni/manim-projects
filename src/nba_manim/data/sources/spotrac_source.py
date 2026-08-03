"""
spotrac_source.py — intentionally NOT implemented.

Spotrac's detailed contract/cap data sits behind a paid tier; scraping
paywalled/ToS-restricted content is a legal judgment call, not just a
technical one. See data/NOTES.md before changing this. Current approach:
hand-enter the specific figures a video needs directly in that video's
data_prep.py, with a comment citing the source URL.
"""


def get_contract_details(*args, **kwargs):
    raise NotImplementedError(
        "Spotrac scraping is intentionally not automated — see data/NOTES.md. "
        "Hand-enter the figures this video needs in its data_prep.py instead."
    )
