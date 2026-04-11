from __future__ import annotations

import re
from pathlib import Path
from typing import Pattern


BASE_DIR = Path(__file__).resolve().parents[2]
DICT_DIR = BASE_DIR / "data" / "dictionaries"


DEFAULT_KATA_KASAR = {
    "bodoh",
    "tolol",
    "goblok",
    "bego",
    "idiot",
    "dungu",
    "bloon",
    "bebal",
    "brengsek",
    "bangsat",
    "anjing",
    "anjir",
    "anjay",
}

DEFAULT_KATA_KASAR_ALIASES = {
    "gblk",
    "tll",
    "bgst",
    "brngsk",
    "njing",
}

DEFAULT_SASARAN = {
    "kamu",
    "kau",
    "lu",
    "lo",
    "loe",
    "elu",
    "dia",
    "kalian",
}

DEFAULT_ANCAMAN = {
    "hajar",
    "pukul",
    "tampar",
    "tonjok",
    "gebuk",
    "bacok",
    "bunuh",
    "habisi",
    "habisin",
}

DEFAULT_PENGUAT = {
    "banget",
    "parah",
    "sangat",
    "sekali",
    "beneran",
}


LEET_EQUIV: dict[str, str] = {
    "a": r"[a4@]+",
    "b": r"[b8]+",
    "e": r"[e3]+",
    "g": r"[g69]+",
    "i": r"[i1!l|]+",
    "l": r"[l1i!|]+",
    "o": r"[o0]+",
    "s": r"[s5$]+",
    "t": r"[t7+]+",
    "z": r"[z2]+",
}

INNER_SEP = r"[\W_]{0,2}"


def _load_wordlist(filename: str, defaults: set[str]) -> list[str]:
    path = DICT_DIR / filename
    words = set(defaults)

    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            item = line.strip().lower()
            if item and not item.startswith("#"):
                words.add(item)

    return sorted(words)


KATA_KASAR = _load_wordlist("kata_kasar.txt", DEFAULT_KATA_KASAR)
SASARAN = _load_wordlist("sasaran.txt", DEFAULT_SASARAN)
ANCAMAN = _load_wordlist("ancaman.txt", DEFAULT_ANCAMAN)
PENGUAT = _load_wordlist("penguat.txt", DEFAULT_PENGUAT)

ALL_KATA_KASAR = sorted(set(KATA_KASAR) | DEFAULT_KATA_KASAR_ALIASES)


def _char_pattern(ch: str) -> str:
    return LEET_EQUIV.get(ch, re.escape(ch) + "+")


def make_obfuscated_word_pattern(word: str) -> Pattern[str]:
    """
    Contoh:
    goblok -> bisa menangkap:
    goblok, g0bl0k, g-o-b-l-o-k, g*o*b*l*o*k, gobloook
    """
    parts = [_char_pattern(ch) for ch in word.lower()]
    joined = INNER_SEP.join(parts)
    pattern = rf"(?<!\w){joined}(?!\w)"
    return re.compile(pattern, re.IGNORECASE)


def make_exact_word_pattern(word: str) -> Pattern[str]:
    return re.compile(rf"\b{re.escape(word.lower())}\b", re.IGNORECASE)


KATA_KASAR_PATTERNS: list[tuple[str, Pattern[str]]] = [
    (word, make_obfuscated_word_pattern(word)) for word in ALL_KATA_KASAR
]

ANCAMAN_PATTERNS: list[tuple[str, Pattern[str]]] = [
    (word, make_obfuscated_word_pattern(word)) for word in ANCAMAN
]

PENGUAT_PATTERNS: list[tuple[str, Pattern[str]]] = [
    (word, make_exact_word_pattern(word)) for word in PENGUAT
]

SASARAN_PATTERNS: list[tuple[str, Pattern[str]]] = [
    (word, make_exact_word_pattern(word)) for word in SASARAN
]

MENTION_PATTERN = re.compile(r"<@!?\d+>")


def _find_category_matches(
    text: str,
    patterns: list[tuple[str, Pattern[str]]],
) -> tuple[list[str], list[str], int | None]:
    """
    Return:
    - display_hits: kata yang benar-benar tertangkap di teks
    - canonical_hits: bentuk dasar / canonical dari kata yang cocok
    - first_pos: posisi match pertama
    """
    display_hits: list[str] = []
    canonical_hits: list[str] = []
    first_pos: int | None = None

    for canonical, pattern in patterns:
        for match in pattern.finditer(text):
            display_hits.append(match.group(0))
            canonical_hits.append(canonical)
            if first_pos is None or match.start() < first_pos:
                first_pos = match.start()

    display_hits = list(dict.fromkeys(display_hits))
    canonical_hits = list(dict.fromkeys(canonical_hits))
    return display_hits, canonical_hits, first_pos


def _count_insult_tokens(normalized_text: str) -> int:
    tokens = normalized_text.split()
    base_set = set(ALL_KATA_KASAR)
    return sum(1 for token in tokens if token in base_set)


def detect_categories(variants: dict[str, str]) -> dict[str, object]:
    raw_text = variants["raw_lower"]
    normalized_text = variants["normalized_text"]

    kata_display_raw, kata_canon_raw, kata_pos_raw = _find_category_matches(raw_text, KATA_KASAR_PATTERNS)
    kata_display_norm, kata_canon_norm, kata_pos_norm = _find_category_matches(normalized_text, KATA_KASAR_PATTERNS)

    anc_display_raw, anc_canon_raw, anc_pos_raw = _find_category_matches(raw_text, ANCAMAN_PATTERNS)
    anc_display_norm, anc_canon_norm, anc_pos_norm = _find_category_matches(normalized_text, ANCAMAN_PATTERNS)

    peng_display, peng_canon, peng_pos = _find_category_matches(normalized_text, PENGUAT_PATTERNS)
    sas_display, sas_canon, sas_pos = _find_category_matches(normalized_text, SASARAN_PATTERNS)

    mention_hits = MENTION_PATTERN.findall(raw_text)
    if mention_hits:
        sas_display.extend(mention_hits)
        sas_display = list(dict.fromkeys(sas_display))
        mention_pos = MENTION_PATTERN.search(raw_text).start()
        if sas_pos is None or mention_pos < sas_pos:
            sas_pos = mention_pos

    kata_display_hits = list(dict.fromkeys(kata_display_raw + kata_display_norm))
    anc_display_hits = list(dict.fromkeys(anc_display_raw + anc_display_norm))

    kata_canonical_hits = list(dict.fromkeys(kata_canon_raw + kata_canon_norm))
    anc_canonical_hits = list(dict.fromkeys(anc_canon_raw + anc_canon_norm))

    kata_pos = kata_pos_raw if kata_pos_raw is not None else kata_pos_norm
    anc_pos = anc_pos_raw if anc_pos_raw is not None else anc_pos_norm

    # Ulangan hanya jika:
    # - ada 2 kata kasar atau lebih dalam teks normal
    # - atau ada 2 canonical kata kasar berbeda
    insult_token_count = _count_insult_tokens(normalized_text)
    has_u = insult_token_count >= 2 or len(kata_canonical_hits) >= 2

    matched_keywords = list(
        dict.fromkeys(kata_display_hits + anc_display_hits + peng_display + sas_display)
    )

    return {
        "has_k": bool(kata_display_hits),
        "has_s": bool(sas_display),
        "has_a": bool(anc_display_hits),
        "has_p": bool(peng_display),
        "has_u": has_u,
        "matched_keywords": matched_keywords,
        "positions": {
            "K": kata_pos,
            "S": sas_pos,
            "A": anc_pos,
            "P": peng_pos,
            "U": kata_pos if has_u else None,
        },
    }