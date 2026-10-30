import re
from typing import Any


# Each rule contains:
# rule ID, regex pattern, weight, and explanation.
RULES = [
    {
        "id": "instruction_override",
        "pattern": (
            r"\b(ignore|disregard|forget|override)\b"
            r".{0,50}\b(previous|prior|all|system|developer)\b"
            r".{0,30}\b(instructions?|rules?|prompts?)\b"
        ),
        "weight": 30,
        "description": "Possible attempt to override existing instructions.",
    },
    {
        "id": "secret_extraction",
        "pattern": (
            r"\b(reveal|print|show|leak|expose|dump)\b"
            r".{0,40}\b(system prompt|hidden prompt|secret|password|"
            r"api key|credentials?)\b"
        ),
        "weight": 35,
        "description": "Possible attempt to extract secrets or hidden instructions.",
    },
    {
        "id": "data_exfiltration",
        "pattern": (
            r"\b(send|email|upload|forward|transfer|exfiltrate)\b"
            r".{0,50}\b(private|personal|confidential|customer|user|"
            r"secret|data|file|credentials?)\b"
        ),
        "weight": 35,
        "description": "Possible attempt to transfer sensitive data.",
    },
    {
        "id": "safety_bypass",
        "pattern": (
            r"\b(bypass|disable|evade|turn off)\b"
            r".{0,30}\b(safety|security|filter|guard|policy|protection)\b"
        ),
        "weight": 25,
        "description": "Possible attempt to bypass safety controls.",
    },
    {
        "id": "role_hijack",
        "pattern": (
            r"\b(you are now|act as|pretend to be)\b"
            r".{0,40}\b(unrestricted|admin|attacker|developer|system)\b"
        ),
        "weight": 20,
        "description": "Possible attempt to change the agent's authority.",
    },
    {
        "id": "hidden_instruction",
        "pattern": (
            r"\b(do not tell the user|secretly|without asking|"
            r"without permission)\b"
        ),
        "weight": 20,
        "description": "Possible instruction to conceal an action or bypass consent.",
    },
]


def scan_text(text: str) -> dict[str, Any]:
    """
    Scan untrusted text for suspicious patterns.

    Returns:
        score: heuristic score from 0 to 100
        suspicious: whether any rule matched
        matches: evidence for each detected rule
        summary: short explanation
    """

    if not isinstance(text, str):
        text = ""

    matches = []
    score = 0

    for rule in RULES:
        match = re.search(
            rule["pattern"],
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )

        if match:
            score += rule["weight"]

            matches.append({
                "rule_id": rule["id"],
                "evidence": match.group(0)[:200],
                "weight": rule["weight"],
                "description": rule["description"],
            })

    # Additional signal when suspicious terms are repeated.
    suspicious_terms = re.findall(
        r"\b(ignore|override|reveal|secretly|bypass)\b",
        text,
        flags=re.IGNORECASE,
    )

    if len(suspicious_terms) >= 3:
        score += 10

        matches.append({
            "rule_id": "repeated_suspicious_language",
            "evidence": "Multiple suspicious terms detected.",
            "weight": 10,
            "description": "Repeated instruction-related terms need review.",
        })

    score = min(score, 100)

    return {
        "score": score,
        "suspicious": len(matches) > 0,
        "matches": matches,
        "summary": (
            f"Detected {len(matches)} suspicious signal(s)."
            if matches
            else "No known suspicious patterns matched."
        ),
    }