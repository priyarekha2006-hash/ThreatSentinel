HIGH_RISK_ACTIONS = {
    "send_email",
    "upload_file",
    "delete_file",
    "run_shell_command",
    "transfer_money",
    "share_credentials",
    "external_api_write",
}

MEDIUM_RISK_ACTIONS = {
    "read_private_file",
    "access_database",
    "browser_submit",
}


def assess_risk(
    user_goal: str,
    untrusted_content: str,
    proposed_action: str,
    findings: dict,
) -> dict:
    """
    Assess risk using detector findings and the proposed action.

    Returns:
        risk_score
        decision
        explanation
        reasons
        goal_overlap
    """

    user_goal = user_goal or ""
    untrusted_content = untrusted_content or ""

    score = int(findings.get("score", 0))
    reasons = []

    # 1. Consider detector findings.
    if findings.get("suspicious"):
        reasons.append(
            "Suspicious instruction patterns were detected."
        )

    # 2. Consider the proposed tool action.
    action = (proposed_action or "none").strip().lower()

    if action in HIGH_RISK_ACTIONS:
        score += 35

        reasons.append(
            f"The proposed action '{action}' is classified as high risk."
        )

    elif action in MEDIUM_RISK_ACTIONS:
        score += 18

        reasons.append(
            f"The proposed action '{action}' may expose sensitive resources."
        )

    # 3. Estimate goal drift using keyword overlap.
    # This is a rough heuristic, not semantic understanding.
    def get_keywords(text: str) -> set[str]:
        import re

        return {
            word.lower()
            for word in re.findall(r"\b[a-zA-Z]{5,}\b", text)
        }

    goal_words = get_keywords(user_goal)
    content_words = get_keywords(untrusted_content)

    if goal_words:
        overlap = (
            len(goal_words & content_words) / len(goal_words)
        )
    else:
        overlap = 0.0

    if (
        goal_words
        and len(content_words) > 8
        and overlap < 0.15
    ):
        score += 10

        reasons.append(
            "Possible goal drift: the untrusted content has little "
            "keyword overlap with the user's original goal."
        )

    # 4. Keep the score within 0–100.
    score = max(0, min(score, 100))

    # 5. Make a recommendation.
    if score >= 65:
        decision = "BLOCK"

        explanation = (
            "High risk detected. Stop the proposed action "
            "and review the evidence."
        )

    elif score >= 30:
        decision = "QUARANTINE"

        explanation = (
            "Elevated or uncertain risk. Hold the proposed action "
            "for human review."
        )

    else:
        decision = "ALLOW"

        explanation = (
            "Low detected risk. The current rules recommend allowing "
            "this input."
        )

    if not reasons:
        reasons.append(
            "No suspicious pattern or high-risk action was detected."
        )

    return {
        "risk_score": score,
        "decision": decision,
        "explanation": explanation,
        "reasons": reasons,
        "proposed_action": action,
        "goal_overlap": round(overlap, 2),
        "thresholds": {
            "ALLOW": "0-29",
            "QUARANTINE": "30-64",
            "BLOCK": "65-100",
        },
    }