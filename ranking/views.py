import logging
import traceback
from typing import Any

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from modules.parser import extract_text
from modules.llm.extractor import extract_structured_fields
from modules.rule_engine import compute_eligibility
from modules.semantic_engine import compute_bi_encoder_score
from modules.cross_encoder import compute_cross_encoder_score
from modules.llm.explainer import generate_explanation
from modules.scorer import build_dashboard_results

logger = logging.getLogger(__name__)


def home(request):
    """Renders the main animated SPA dashboard."""
    return render(request, "index.html")


def flatten_skills(raw_skills: Any) -> list[str]:
    """Helper to convert list or categorized dictionary of skills into a clean list."""
    if isinstance(raw_skills, list):
        return [str(s).strip() for s in raw_skills if str(s).strip()]
    elif isinstance(raw_skills, dict):
        result = []
        for val in raw_skills.values():
            if isinstance(val, list):
                result.extend([str(s).strip() for s in val if str(s).strip()])
            elif isinstance(val, str) and val.strip():
                result.append(val.strip())
        return list(dict.fromkeys(result))
    return []


@csrf_exempt
def analyze_candidates_api(request):
    """
    POST API to process uploaded resumes against a job description.
    Accepts:
      - 'resumes': multiple files (PDF, DOCX, TXT)
      - 'jd_file': optional file
      - 'jd_text': text string
    Returns JSON with ranked candidates, cohort metrics, and analytics.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed. Use POST."}, status=405)

    resumes = request.FILES.getlist("resumes")
    jd_file = request.FILES.get("jd_file")
    jd_text_input = request.POST.get("jd_text", "").strip()

    if not resumes:
        return JsonResponse({"error": "Please upload at least one candidate resume."}, status=400)

    if not jd_file and not jd_text_input:
        return JsonResponse({"error": "Please provide a Job Description (upload file or paste text)."}, status=400)

    # 1. Extract Job Description text
    try:
        if jd_file:
            jd_text = extract_text(jd_file, filename=jd_file.name)
        else:
            jd_text = jd_text_input
    except Exception as e:
        logger.error(f"Error reading job description: {e}")
        return JsonResponse({"error": f"Failed to parse Job Description: {str(e)}"}, status=400)

    # 2. Iterate through candidate resumes
    candidates_results = []
    errors = []

    for idx, resume_file in enumerate(resumes):
        file_name = resume_file.name
        try:
            resume_text = extract_text(resume_file, filename=file_name)

            # Structured extraction with up to 3 retries
            candidate_data = None
            last_err = None
            for attempt in range(3):
                try:
                    candidate_data = extract_structured_fields(resume_text)
                    break
                except Exception as extract_err:
                    last_err = extract_err

            if candidate_data is None:
                raise last_err or ValueError("Extraction failed.")

            # Rule engine
            rule_results = compute_eligibility(candidate_data)

            # Semantic similarity (Bi-Encoder)
            semantic_score = compute_bi_encoder_score(resume_text, jd_text)

            # Deep cross-encoder scoring
            cross_score = compute_cross_encoder_score(resume_text, jd_text)

            # Build dashboard metrics
            dashboard = build_dashboard_results(
                extracted_fields=candidate_data,
                jd_text=jd_text,
                rule_results=rule_results,
                semantic_score=semantic_score,
                cross_encoder_score=cross_score,
            )

            # Generate LLM explanation
            explanation = generate_explanation(
                jd_text=jd_text,
                extracted_fields=candidate_data,
                final_score=dashboard["final_score"],
            )

            # Resolve normalized display fields
            personal_info = candidate_data.get("personal_information") if isinstance(candidate_data.get("personal_information"), dict) else {}
            name = (
                candidate_data.get("name")
                or personal_info.get("full_name")
                or candidate_data.get("full_name")
                or file_name
            )
            email = personal_info.get("email") or candidate_data.get("email") or "—"
            phone = personal_info.get("phone") or candidate_data.get("phone") or "—"
            location = personal_info.get("location") or "—"
            linkedin = personal_info.get("linkedin") or ""
            github = personal_info.get("github") or ""
            portfolio = personal_info.get("portfolio") or ""

            education_list = candidate_data.get("education", [])
            primary_edu = education_list[0] if isinstance(education_list, list) and education_list and isinstance(education_list[0], dict) else {}
            degree = (
                primary_edu.get("degree")
                or candidate_data.get("degree")
                or candidate_data.get("overall_profile", {}).get("highest_education")
                or "Degree not specified"
            )
            institution = primary_edu.get("institution") or primary_edu.get("institute") or ""
            cgpa = primary_edu.get("cgpa") or primary_edu.get("percentage") or candidate_data.get("cgpa")

            profile_info = candidate_data.get("overall_profile") if isinstance(candidate_data.get("overall_profile"), dict) else {}
            experience_years = (
                profile_info.get("total_experience_years")
                or profile_info.get("total_experience")
                or candidate_data.get("total_experience_years")
                or candidate_data.get("total_experience")
            )

            all_skills = flatten_skills(candidate_data.get("skills"))

            # Explanation flags
            green_flags = []
            red_flags = []
            matching_skills = []
            missing_skills = []
            rationale = ""
            if isinstance(explanation, dict):
                green_flags = explanation.get("green_flags", [])
                red_flags = explanation.get("red_flags", [])
                matching_skills = explanation.get("matching_skills", [])
                missing_skills = explanation.get("missing_skills", [])
                rationale = explanation.get("overall_rationale") or explanation.get("rationale") or ""
            else:
                rationale = str(explanation)

            candidates_results.append({
                "id": idx + 1,
                "file_name": file_name,
                "name": name,
                "email": email,
                "phone": phone,
                "location": location,
                "socials": {
                    "linkedin": linkedin,
                    "github": github,
                    "portfolio": portfolio,
                },
                "degree": degree,
                "institution": institution,
                "cgpa": cgpa,
                "experience_years": experience_years,
                "skills": all_skills,
                "scores": {
                    "final_score": dashboard["final_score"],
                    "rule_score": dashboard["rule_score"],
                    "semantic_score": dashboard["semantic_score"],
                    "cross_encoder_score": dashboard["cross_encoder_score"],
                    "confidence": dashboard["confidence"],
                },
                "recommendation": dashboard.get("recommendation", "Scored"),
                "rule_checks": rule_results.get("checks", []),
                "explanation": {
                    "green_flags": green_flags,
                    "red_flags": red_flags,
                    "matching_skills": matching_skills,
                    "missing_skills": missing_skills,
                    "overall_rationale": rationale,
                    "raw": explanation,
                },
                "raw_candidate": candidate_data,
            })

        except Exception as cand_err:
            logger.error(f"Error processing {file_name}: {cand_err}\n{traceback.format_exc()}")
            errors.append({
                "file_name": file_name,
                "error": str(cand_err)
            })

    if not candidates_results:
        return JsonResponse({
            "error": "Failed to process candidate resumes.",
            "details": errors
        }, status=422)

    # Sort descending by final score
    candidates_results.sort(key=lambda c: c["scores"]["final_score"], reverse=True)

    # Assign ranks and tiers
    strong_count = 0
    consider_count = 0
    reject_count = 0

    for rank, cand in enumerate(candidates_results, start=1):
        cand["rank"] = rank
        score = cand["scores"]["final_score"]
        rec = cand["recommendation"].lower()
        if "strong" in rec or "recommend" in rec or score >= 70:
            cand["tier"] = "strong"
            cand["tier_label"] = "Highly Recommended" if score >= 85 else "Recommended"
            cand["tier_badge"] = "🟢"
            strong_count += 1
        elif "consider" in rec or score >= 50:
            cand["tier"] = "consider"
            cand["tier_label"] = "Consider"
            cand["tier_badge"] = "🟡"
            consider_count += 1
        else:
            cand["tier"] = "reject"
            cand["tier_label"] = "Not Recommended"
            cand["tier_badge"] = "🔴"
            reject_count += 1

    cohort_summary = {
        "total_evaluated": len(candidates_results),
        "strong": strong_count,
        "consider": consider_count,
        "reject": reject_count,
        "average_score": round(sum(c["scores"]["final_score"] for c in candidates_results) / len(candidates_results), 1),
        "top_score": candidates_results[0]["scores"]["final_score"] if candidates_results else 0,
    }

    return JsonResponse({
        "success": True,
        "cohort": cohort_summary,
        "candidates": candidates_results,
        "errors": errors,
    })
