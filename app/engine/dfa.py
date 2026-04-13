from __future__ import annotations


TRANSITIONS: dict[str, dict[str, str]] = {
    "q0": {
        "N": "q0",
        "K": "q1",
        "S": "q2",
    },
    "q1": {
        "S": "q3",
    },
    "q2": {
        "K": "q3",
    },
    "q3": {
        "P": "q4",
        "A": "qF",
        "U": "qF",
    },
    "q4": {
        "K": "qF",
        "A": "qF",
        "P": "qF",
        "U": "qF",
    },
    "qF": {},
}


def run_dfa(symbols: list[str]) -> tuple[list[str], str]:
    state = "q0"
    trace = [state]

    for symbol in symbols:
        state = TRANSITIONS.get(state, {}).get(symbol, state)
        trace.append(state)

    return trace, state


def classify_result(symbols: list[str], final_state: str) -> tuple[str, int]:
    symbol_set = set(symbols)

    has_k = "K" in symbol_set
    has_s = "S" in symbol_set
    has_a = "A" in symbol_set
    has_u = "U" in symbol_set
    has_p = "P" in symbol_set

    # 1) Aman murni
    if symbols == ["N"] or final_state == "q0":
        return "Aman", 0

    # 2) Kalau hanya ada sasaran / penguat tanpa kata kasar dan tanpa ancaman,
    #    harus tetap Aman
    if has_s and not has_k and not has_a:
        return "Aman", 0

    # 3) Kalau hanya ada penguat tanpa unsur lain, juga Aman
    if has_p and not has_k and not has_s and not has_a:
        return "Aman", 0

    # 4) Waspada:
    #    - ada kata kasar tanpa sasaran
    #    - ada ancaman tanpa sasaran+kata kasar lengkap
    if has_k and not has_s:
        return "Waspada", 0

    if has_a and not (has_k and has_s):
        return "Waspada", 0

    # 5) Kalau sudah ada pasangan sasaran + kata kasar,
    #    baru bisa masuk bullying / bullying berat
    if has_k and has_s:
        if final_state == "qF" or has_a or has_u:
            return "Indikasi Bullying Berat", 3
        return "Indikasi Bullying", 1

    # fallback aman
    return "Aman", 0