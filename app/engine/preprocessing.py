from __future__ import annotations

import re
import unicodedata


LEET_TRANSLATION = str.maketrans(
    {
        "0": "o",
        "1": "i",
        "3": "e",
        "4": "a",
        "5": "s",
        "6": "g",
        "7": "t",
        "8": "b",
        "9": "g",
        "@": "a",
        "$": "s",
        "!": "i",
    }
)


def _strip_zero_width(text: str) -> str:
    return re.sub(r"[\u200B-\u200D\uFEFF]", "", text)


def _collapse_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _collapse_repeated_chars(text: str) -> str:
    # contoh:
    # toloool -> tolol
    # gobloooook -> goblok
    return re.sub(r"(.)\1{2,}", r"\1", text)


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = _strip_zero_width(text)
    text = text.lower()
    text = _collapse_spaces(text)
    return text


def normalize_obfuscation(text: str) -> str:
    text = normalize_text(text)
    text = text.translate(LEET_TRANSLATION)

    # ubah pemisah aneh jadi spasi
    text = re.sub(r"[^a-z\s]", " ", text)

    # rapikan huruf berulang
    text = _collapse_repeated_chars(text)

    # rapikan spasi
    text = _collapse_spaces(text)
    return text


def build_text_variants(text: str) -> dict[str, str]:
    raw_lower = normalize_text(text)
    normalized_text = normalize_obfuscation(text)

    # compact untuk bantu pencarian bentuk yang dipisah-pisah
    compact_text = re.sub(r"\s+", "", normalized_text)

    return {
        "raw_lower": raw_lower,
        "normalized_text": normalized_text,
        "compact_text": compact_text,
    }