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

    # Aman
    if symbols == ["N"] or final_state == "q0":
        return "Aman", 0

    # Jika belum ada kombinasi sasaran + kata kasar,
    # maka jangan pernah naik ke bullying / berat.
    # Tetap Waspada saja.
    if not (has_k and has_s):
        return "Waspada", 0

    # Berat hanya jika konteks bullying sudah lengkap
    # dan diperkuat ancaman / ulangan / final qF
    if final_state == "qF" or has_a or has_u:
        return "Indikasi Bullying Berat", 3

    # Jika sudah ada sasaran + kata kasar tapi belum berat
    return "Indikasi Bullying", 1