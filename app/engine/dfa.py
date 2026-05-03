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


STATE_CLASSIFICATION: dict[str, tuple[str, int]] = {
    "q0": ("Aman", 0),
    "q1": ("Waspada", 0),
    "q2": ("Aman", 0),
    "q3": ("Indikasi Bullying", 1),
    "q4": ("Indikasi Bullying", 1),
    "qF": ("Indikasi Bullying Berat", 3),
}


def run_dfa(symbols: list[str]) -> tuple[list[str], str]:
    state = "q0"
    trace = [state]

    for symbol in symbols:
        state = TRANSITIONS.get(state, {}).get(symbol, state)
        trace.append(state)

    return trace, state


def classify_result(symbols: list[str], final_state: str) -> tuple[str, int]:
    # Tanpa state tambahan, simbol A yang tidak membawa DFA ke qF
    # tetap diperlakukan sebagai ancaman mandiri / belum lengkap.
    if "A" in symbols and final_state in {"q0", "q1", "q2"}:
        return "Waspada", 0

    return STATE_CLASSIFICATION.get(final_state, ("Aman", 0))
