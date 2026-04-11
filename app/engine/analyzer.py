from __future__ import annotations

from app.engine.dfa import classify_result, run_dfa
from app.engine.preprocessing import build_text_variants
from app.engine.regex_rules import detect_categories


def _ordered_symbols(match_info: dict[str, object]) -> list[str]:
    has_k = bool(match_info["has_k"])
    has_s = bool(match_info["has_s"])
    has_a = bool(match_info["has_a"])
    has_p = bool(match_info["has_p"])
    has_u = bool(match_info["has_u"])
    positions: dict[str, int | None] = match_info["positions"]  # type: ignore[assignment]

    symbols: list[str] = []

    # inti dulu: K dan S
    if has_k and has_s:
        pos_k = positions.get("K")
        pos_s = positions.get("S")

        if pos_s is not None and pos_k is not None and pos_s < pos_k:
            symbols.extend(["S", "K"])
        else:
            symbols.extend(["K", "S"])
    elif has_k:
        symbols.append("K")
    elif has_s:
        symbols.append("S")

    # fitur tambahan
    if has_p:
        symbols.append("P")
    if has_a:
        symbols.append("A")
    if has_u:
        symbols.append("U")

    if not symbols:
        symbols = ["N"]

    return symbols


def analyze_message(text: str) -> dict[str, object]:
    variants = build_text_variants(text)
    match_info = detect_categories(variants)

    symbols = _ordered_symbols(match_info)
    trace, final_state = run_dfa(symbols)
    label, strike_points = classify_result(symbols, final_state)

    return {
        "raw_text": text,
        "normalized_text": variants["normalized_text"],
        "symbols": symbols,
        "trace": trace,
        "final_state": final_state,
        "label": label,
        "strike_points": strike_points,
        "matched_keywords": match_info["matched_keywords"],
    }