# This module contains all the deterministic rule engine for resume screening.

import re
from typing import Any

DEFAULT_MIN_CGPA = 6.5
DEFAULT_MIN_EXPERIENCE = 0.0


# these functions are used to parse numeric values from strings, such as CGPA, percentages, and experience durations.
# They handle various formats and return float values or None if parsing fails.

def parse_numeric(value: Any) -> float | None:
    """
    This function converts values like:8,8.5,8/10,8.5/10,8.5 CGPA,82%,82 %,6 years into float.
    """

    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().lower()

    if not text:
        return None

    # Handle "8/10"
    if "/" in text:
        text = text.split("/")[0]

    # Keep only digits and decimal point
    text = re.sub(r"[^\d.]", "", text)

    if not text:
        return None

    try:
        return float(text)
    except ValueError:
        return None


# this function converts experience values into float.
def parse_experience(value: Any) -> float | None:
    """
    This function converts experience values into float. 
    Supports:2,2.5,2 years,2 yrs,2+ years,24 months,18 months,1 year 6 months,Fresher
    """

    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).lower().strip()

    if not text:
        return None

    if "fresher" in text:
        return 0.0

    years = re.search(r"(\d+(?:\.\d+)?)\s*(?:year|years|yr|yrs)", text)
    months = re.search(r"(\d+(?:\.\d+)?)\s*(?:month|months)", text)

    total = 0.0

    if years:
        total += float(years.group(1))

    if months:
        total += float(months.group(1)) / 12

    if total > 0:
        return round(total, 2)

    number = parse_numeric(text)

    return number


# RULES - The following functions implement deterministic rules for resume screening,
# such as checking CGPA and experience against minimum requirements.
# Each function returns a dictionary indicating whether the rule passed and the reason.


def check_cgpa(
    extracted: dict[str, Any],
    min_cgpa: float,
) -> dict[str, Any]:

    education = extracted.get("education", [])

    if not education:
        return {
            "rule": "cgpa",
            "passed": None,
            "reason": "Education details not found.",
        }

    highest = education[0] if isinstance(education, list) and len(education) > 0 else {}
    if not isinstance(highest, dict):
        highest = {}

    cgpa = parse_numeric(highest.get("cgpa"))

    # Fallback to percentage converted to ~10-point scale if cgpa is not directly present
    if cgpa is None and highest.get("percentage") is not None:
        pct = parse_numeric(highest.get("percentage"))
        if pct is not None:
            cgpa = round(pct / 9.5, 2) if pct > 10 else pct

    if cgpa is None:
        return {
            "rule": "cgpa",
            "passed": None,
            "reason": "CGPA not available.",
        }

    passed = cgpa >= min_cgpa

    return {
        "rule": "cgpa",
        "passed": passed,
        "reason": f"CGPA {cgpa:.2f} (Minimum Required: {min_cgpa})",
    }


def check_experience(
    extracted: dict[str, Any],
    min_experience: float,
) -> dict[str, Any]:

    profile = extracted.get("overall_profile", {})
    if not isinstance(profile, dict):
        profile = {}

    experience = (
        profile.get("total_experience")
        or profile.get("total_experience_years")
        or extracted.get("total_experience_years")
        or extracted.get("total_experience")
    )

    experience = parse_experience(experience)

    if experience is None:
        return {
            "rule": "experience",
            "passed": None,
            "reason": "Experience not available.",
        }

    passed = experience >= min_experience

    return {
        "rule": "experience",
        "passed": passed,
        "reason": (
            f"{experience:.2f} years "
            f"(Minimum Required: {min_experience})"
        ),
    }



# ENGINE - this is the main function that applies all deterministic rules and
# computes an overall eligibility score based on the results of individual checks.

# what we are doing here is applying all the deterministic rules and
# computing an overall eligibility score based on the results of individual checks.
# using formula logic: eligibility_score = (number of passed checks / total checks) * 100
# this score is then returned along with the individual check results for transparency and
# debugging purposes.

# this will help recruiters understand why a candidate was deemed eligible or not based on the rules applied.
def compute_eligibility(
    extracted: dict[str, Any],
    min_cgpa: float = DEFAULT_MIN_CGPA,
    min_experience: float = DEFAULT_MIN_EXPERIENCE,
) -> dict[str, Any]:
    """
    Apply deterministic business rules.

    Returns
    -------
    {
        "eligibility_score": float,
        "checks": [...]
    }
    """

    checks = [
        check_cgpa(extracted, min_cgpa),
        check_experience(extracted, min_experience),
    ]

    valid_checks = [
        check
        for check in checks
        if check["passed"] is not None
    ]

    if not valid_checks:
        score = 50.0
    else:
        passed = sum(
            check["passed"]
            for check in valid_checks
        )

        score = round(
            (passed / len(valid_checks)) * 100,
            2,
        )

    return {
        "eligibility_score": score,
        "checks": checks,
    }
