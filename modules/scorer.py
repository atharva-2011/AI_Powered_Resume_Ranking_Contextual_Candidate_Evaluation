
"""
Cross-Encoder reranking engine.

Goal:
- Compute a fine-grained relevance score between a Job Description (JD)
  and a Resume.
- Unlike the Bi-Encoder, both texts are processed together, allowing
  the transformer to attend jointly across both inputs.
- This produces a more accurate relevance score but is slower than
  the Bi-Encoder.
"""

from typing import Any
from config import WEIGHTS
from modules.cross_encoder import compute_cross_encoder_score



# this function calculates the rule engine score based on the number of passed checks in the rule results.
def calculate_rule_score(rule_results: dict) -> float:
    """
    Calculates rule engine score based on passed checks.
    """

    checks = rule_results.get("checks", [])

    if not checks:
        return 0.0

    passed = sum(
        1 for check in checks
        if check.get("passed", False)
    )

    return round((passed / len(checks)) * 100, 2)

# this function calculates the final weighted ATS score based on the individual scores from the rule engine, semantic scoring, and cross-encoder scoring.


def calculate_final_score(
    rule_score: float,
    semantic_score: float,
    cross_encoder_score: float,
) -> float:
    """
    Calculates weighted ATS score.
    """

    final_score = (
        rule_score * WEIGHTS["rule"]
        + semantic_score * WEIGHTS["bi_encoder"]
        + cross_encoder_score * WEIGHTS["cross_encoder"]
    )

    return round(final_score, 2)

# this function converts the final ATS score into a recruiter-friendly recommendation based on predefined thresholds.


def get_recommendation(score: float) -> str:
    """
    Converts ATS score into recruiter recommendation.
    """

    if score >= 85:
        return "Highly Recommended"

    elif score >= 70:
        return "Recommended"

    elif score >= 50:
        return "Consider"

    return "Not Recommended"


# this function calculates the confidence level of the final score based on the agreement between the individual scoring methods (rule engine, semantic scoring, and cross-encoder scoring).
def get_confidence(
    rule_score: float,
    semantic_score: float,
    cross_encoder_score: float,
) -> float:
    """
    Confidence based on agreement between all scoring methods.
    """

    scores = [
        rule_score,
        semantic_score,
        cross_encoder_score,
    ]

    spread = max(scores) - min(scores)

    confidence = max(60, 100 - spread)

    return round(confidence, 2)


def extract_skill_list(skills_data: Any) -> list[str]:
    """Helper to extract a flat list of skill strings from dict or list."""
    if isinstance(skills_data, list):
        return [str(s).strip() for s in skills_data if str(s).strip()]
    elif isinstance(skills_data, dict):
        flat: list[str] = []
        for val in skills_data.values():
            if isinstance(val, list):
                flat.extend([str(s).strip() for s in val if str(s).strip()])
            elif isinstance(val, str) and val.strip():
                flat.append(val.strip())
        return list(dict.fromkeys(flat))
    return []


# this function generates green flags based on the candidate's skills and passed rule checks, indicating strengths and areas of alignment with the job description.
def generate_green_flags(
    extracted_fields: dict,
    jd_text: str,
    rule_results: dict,
) -> list[str]:

    flags = []
    skills = extract_skill_list(extracted_fields.get("skills", []))
    jd_lower = jd_text.lower()

    for skill in skills:
        if skill.lower() in jd_lower:
            flags.append(f"Strong in {skill}")

    for check in rule_results.get("checks", []):
        if check.get("passed"):
            reason = check.get("reason") or check.get("rule", "Passed rule check")
            flags.append(f"Meets requirement: {reason}")

    return list(dict.fromkeys(flags))


# this function generates red flags based on missing skills and failed rule checks, indicating weaknesses or areas of concern in relation to the job description.
def generate_red_flags(
    extracted_fields: dict,
    jd_text: str,
    rule_results: dict,
) -> list[str]:

    flags = []

    for check in rule_results.get("checks", []):
        if check.get("passed") is False:
            reason = check.get("reason") or f"Failed {check.get('rule', 'rule')} check"
            flags.append(reason)

    return list(dict.fromkeys(flags))



# this function builds a comprehensive dashboard result dictionary containing all relevant scoring information, recommendations, and flags for display in the web interface.
def build_dashboard_results(
    extracted_fields: dict,
    jd_text: str,
    rule_results: dict,
    semantic_score: float,
    cross_encoder_score: float,
) -> dict:
    """
    Returns candidate dashboard results dictionary.
    """


    rule_score = calculate_rule_score(rule_results)

    final_score = calculate_final_score(
        rule_score,
        semantic_score,
        cross_encoder_score,
    )

    return {
        "rule_score": rule_score,
        "semantic_score": round(semantic_score, 2),
        "cross_encoder_score": round(cross_encoder_score, 2),
        "final_score": final_score,
        "recommendation": get_recommendation(final_score),
        "confidence": get_confidence(
            rule_score,
            semantic_score,
            cross_encoder_score,
        ),
        "green_flags": generate_green_flags(
            extracted_fields,
            jd_text,
            rule_results,
        ),
        "red_flags": generate_red_flags(
            extracted_fields,
            jd_text,
            rule_results,
        ),
    }
