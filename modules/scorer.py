# This file defines the Cross-Encoder reranking engine,
# which computes a fine-grained relevance score between a Job Description (JD) and a Resume.
# Unlike the Bi-Encoder, both texts are processed together, allowing the transformer to attend jointly across both inputs.
# This produces a more accurate relevance score but is slower than the Bi-Encoder.

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

from config import WEIGHTS
from sentence_transformers import CrossEncoder

from config import CROSS_ENCODER_MODEL

# Lazy-loaded Cross Encoder model
_model: CrossEncoder | None = None


# this function loads the Cross Encoder model only once and returns it for use in scoring.
def get_model() -> CrossEncoder:
    """
    Load the Cross Encoder model only once.
    """

    global _model

    if _model is None:
        _model = CrossEncoder(CROSS_ENCODER_MODEL)

    return _model


# this function normalizes the raw model score to the range [0, 100] for consistency in scoring.
def normalize_score(score: float) -> float:
    """
    Normalize the raw model score to the range [0, 100].
    """

    score = max(0.0, min(1.0, score))

    return round(score * 100, 2)

# this function computes the contextual relevance score between a Job Description and Resume using the Cross Encoder model.


def compute_cross_encoder_score(
    jd_text: str,
    resume_text: str,
) -> float:
    """
    Compute contextual relevance score between
    a Job Description and Resume.

    Args:
        jd_text:
            Job Description text.

        resume_text:
            Resume text.

    Returns:
        float:
            Relevance score between 0 and 100.
    """

    model = get_model()

    raw_score = float(
        model.predict(
            [
                (jd_text, resume_text),
            ]
        )[0]
    )

    return normalize_score(raw_score)


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


# this function generates green flags based on the candidate's skills and passed rule checks, indicating strengths and areas of alignment with the job description.


def generate_green_flags(
    extracted_fields: dict,
    jd_text: str,
    rule_results: dict,
) -> list[str]:

    flags = []

    skills = extracted_fields.get("skills", [])

    for skill in skills:
        if skill.lower() in jd_text.lower():
            flags.append(f"Strong in {skill}")

    for check in rule_results.get("checks", []):
        if check.get("passed"):
            flags.append(check["rule"])

    return list(dict.fromkeys(flags))


# this function generates red flags based on missing skills and failed rule checks, indicating weaknesses or areas of concern in relation to the job description.


def generate_red_flags(
    extracted_fields: dict,
    jd_text: str,
    rule_results: dict,
) -> list[str]:

    flags = []

    skills = extracted_fields.get("skills", [])

    jd_lower = jd_text.lower()

    for word in jd_lower.split():

        if len(word) < 3:
            continue

        if word not in [s.lower() for s in skills]:

            if word.isalpha():
                flags.append(f"Missing skill: {word}")

    for check in rule_results.get("checks", []):

        if not check.get("passed"):
            flags.append(check["reason"])

    return list(dict.fromkeys(flags))


# this function builds a comprehensive dashboard result dictionary containing all relevant scoring information, recommendations, and flags for display in a Streamlit interface.
def build_dashboard_results(
    extracted_fields: dict,
    jd_text: str,
    rule_results: dict,
    semantic_score: float,
    cross_encoder_score: float,
) -> dict:
    """
    Returns everything required by Streamlit.
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
