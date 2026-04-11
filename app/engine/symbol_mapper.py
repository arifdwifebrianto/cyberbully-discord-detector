from __future__ import annotations

from app.engine.regex_rules import A_PATTERN, K_PATTERN, P_PATTERN, S_PATTERN, first_match_position


def map_features_to_symbols(text: str, features: dict[str, object]) -> list[str]:
    has_k = bool(features["has_k"])
    has_s = bool(features["has_s"])
    has_a = bool(features["has_a"])
    has_p = bool(features["has_p"])
    has_u = bool(features["has_u"])

    symbols: list[str] = []

    k_pos = first_match_position(K_PATTERN, text)
    s_pos = first_match_position(S_PATTERN, text)

    if has_k and has_s:
        if s_pos is not None and k_pos is not None and s_pos < k_pos:
            symbols.extend(["S", "K"])
        else:
            symbols.extend(["K", "S"])
    elif has_k:
        symbols.append("K")
    elif has_s:
        symbols.append("S")

    extra_symbols: list[tuple[int, str]] = []

    if has_p:
        pos = first_match_position(P_PATTERN, text)
        extra_symbols.append((pos if pos is not None else 10_000, "P"))
    if has_a:
        pos = first_match_position(A_PATTERN, text)
        extra_symbols.append((pos if pos is not None else 10_001, "A"))
    if has_u:
        extra_symbols.append((99_999, "U"))

    for _, symbol in sorted(extra_symbols, key=lambda item: item[0]):
        symbols.append(symbol)

    if not symbols:
        symbols = ["N"]

    return symbols
