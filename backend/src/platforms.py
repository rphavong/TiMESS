"""
platforms.py
-------------
Detects which platform(s), if any, a question is about, by matching
known product names and aliases. Deliberately simple keyword
matching, not an LLM classification call -- fast, free, and
deterministic. When it gets something wrong, you can just read the
alias list and fix it directly, which matters more here than
handling every possible phrasing perfectly.

ORDER MATTERS: more specific aliases are listed before their more
generic substrings (e.g. "xenium prime" before bare "xenium"), and
each match REMOVES that text from the working string before checking
less-specific groups -- otherwise "xenium" would also match inside
"xenium prime" and incorrectly tag both platforms for the same
mention.
"""

PLATFORM_ALIASES = [
    ("xenium-prime", ["xenium prime", "xenium analyzer"]),
    ("xenium-v1", ["xenium v1", "xenium analyzer", "xenium"]),
    ("visium-hd-3prime", ["visium hd 3'", "visium hd 3", "visium hd3'", "visium hd3", "visium hd3 prime", "visium hd 3 prime"]),
    ("visium-hd", ["visium hd"]),
    ("visium-cyt-protein", ["visium cyt protein", "visium protein", "visium cyt", "visium cytassist", "visium cytassist protein"]),
    ("universal-3prime", ["universal 3'", "universal 3 prime", "universal 3", "single cell 3'"]),
    ("universal-5prime", ["universal 5'", "universal 5 prime", "universal 5", "single cell 5'"]),
    ("flex", ["flex", "fixed rna profiling"]),
]


def detect_platforms(question: str) -> list[str]:
    """
    Returns the platform slugs (matching your docs_staging/ folder
    names) mentioned in the question, in match order. Returns [] if
    no known platform is mentioned -- callers should fall back to an
    unfiltered search across all platforms in that case.
    """
    q = question.lower()
    matched: list[str] = []

    for slug, aliases in PLATFORM_ALIASES:
        for alias in aliases:
            if alias in q:
                matched.append(slug)
                q = q.replace(alias, " ")
                break

    return matched