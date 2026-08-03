# AI-Powered Resume Ranking & CONTEXTUAL Candidate Evaluation
# this is a Streamlit web application that allows recruiters and hiring managers to upload candidate resumes
# and a job description, and then evaluates the candidates based on various criteria.
# The application uses natural language processing (NLP) techniques, including semantic similarity, cross-encoder scoring,
# and rule-based eligibility checks, to rank candidates and provide explanations for the rankings.

# for frontend -
import streamlit as st

# to extract text from uploaded files (PDF, DOCX, TXT)
from modules.parser import extract_text

# to extract structured fields from the resume text using a large language model (LLM)
from modules.llm.extractor import extract_structured_fields

# to compute eligibility based on predefined rules
from modules.rule_engine import compute_eligibility

# to compute semantic similarity score using a bi-encoder model
from modules.semantic_engine import compute_bi_encoder_score

# to compute cross-encoder score for more accurate ranking
from modules.cross_encoder import compute_cross_encoder_score

# to generate explanations for the candidate evaluation using an LLM
from modules.llm.explainer import generate_explanation

# to build the dashboard results for each candidate
from modules.scorer import build_dashboard_results


# Page Configguration -
st.set_page_config(
    page_title="AI-Powered Resume Ranking & CONTEXTUAL Candidate Evaluation",
    page_icon="👽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Color Palette
COLORS = {
    "bg": "#0f172a",
    "card": "#1e293b",
    "card_border": "#334155",
    "text": "#e6e6e6",
    "text_muted": "#94a3b8",
    "strong": "#2dd4bf",
    "consider": "#f59e0b",
    "reject": "#ef4444",
    "accent": "#6366f1",
    "track": "#334155",
}


# Helper Functions for Tier Color and Emoji -
def tier_color(recommendation: str, final_score: float) -> tuple[str, str]:
    label = (recommendation or "").strip().lower()
    if "strong" in label or "excellent" in label or "recommend" in label:
        return COLORS["strong"], "🟢"
    if "consider" in label or "moderate" in label or "maybe" in label:
        return COLORS["consider"], "🟡"
    if "reject" in label or "not" in label or "poor" in label:
        return COLORS["reject"], "🔴"

    # if label text doesn't match anything known, use this coloring scheme.
    if final_score >= 70:
        return COLORS["strong"], "🟢"
    elif final_score >= 45:
        return COLORS["consider"], "🟡"
    else:
        return COLORS["reject"], "🔴"


# Session State - for storing results and uploader key to manage file uploads and results across reruns.
if "results" not in st.session_state:
    st.session_state.results = None
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0


# Custom CSS - button styles, card styles, and other UI elements to match the dark theme and color palette defined above.
st.markdown(
    f"""
<style>

# Global Styles
html, body, [class*="css"] {{
    background:{COLORS['bg']};
    color:{COLORS['text']};
}}

# this is a hack to remove the default Streamlit padding and make the app full-width
.block-container {{
    padding-top:1.2rem;
    padding-bottom:2rem;
}}


# Hide Streamlit default elements
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}

# Hero Section Styles
.hero {{
    padding: 2rem 2.4rem;
    border-radius: 20px ;
    background: linear-gradient(135deg, #4338ca 0%, #6366f1 50%, #0ea5e9 100%);
    box-shadow: 0 10px 30px rgba(67, 56, 202, 0.25);
    margin-bottom: 1.6rem;
    text-align:center;
}}

# Hero Section Text Styles
.hero h1 {{
    color:#ffffff;
    font-size:2rem;
    font-weight:800;
    margin-bottom:0.4rem;
}}
.hero p {{
    color:rgba(255,255,255,0.88);
    font-size:1rem;
    margin-bottom:0;
}}

div[data-testid="stMetric"] {{
    background:{COLORS['card']};
    border:1px solid {COLORS['card_border']};
    border-radius:20px;
    padding:1rem 1.2rem;
}}


# the following styles are for the cards that display candidate information, scores, and recommendations.
.card {{
    background:{COLORS['card']};
    border-radius:20px;
    padding:20px;
    border:1px solid {COLORS['card_border']};
    box-shadow:0 8px 30px rgba(0,0,0,.25);
    margin-bottom:18px;
}}

.section-title {{
    font-size:22px;
    font-weight:700;
    color:{COLORS['text']};
    margin-bottom:12px;
}}

.section-label {{
    font-size:12px;
    text-transform:uppercase;
    letter-spacing:0.06em;
    color:{COLORS['text_muted']};
    font-weight:600;
    margin-bottom:6px;
    margin-top:10px;
}}

.score-ring {{
    --pct: 0;
    --ring-color: {COLORS['track']};
    width: 132px;
    height: 132px;
    border-radius: 50%;
    background: conic-gradient(var(--ring-color) calc(var(--pct) * 1%), {COLORS['track']} 0);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
}}
.score-ring-inner {{
    width: 104px;
    height: 104px;
    border-radius: 50%;
    background-color: {COLORS['card']};
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}}
.score-ring-value {{
    font-size:26px;
    font-weight:700;
    color:{COLORS['text']};
    line-height:1;
}}
.score-ring-label {{
    font-size:11px;
    color:{COLORS['text_muted']};
    margin-top:2px;
}}

.rec-badge {{
    display:inline-block;
    padding:5px 14px;
    border-radius:999px;
    font-size:13px;
    font-weight:600;
    margin-top:8px;
}}


# chip styles for skills, green flags, and red flags in the candidate evaluation dashboard.
.chip {{
    display:inline-block;
    padding:0.3rem 0.75rem;
    margin:0.2rem 0.25rem 0.2rem 0;
    border-radius:999px;
    font-size:0.85rem;
    font-weight:600;
}}
.chip-skill {{
    background: rgba(99, 102, 241, 0.15);
    color:#a5b4fc;
    border:1px solid rgba(99, 102, 241, 0.35);
}}
.chip-green {{
    background: rgba(34, 197, 94, 0.13);
    color:#4ade80;
    border:1px solid rgba(34, 197, 94, 0.35);
}}
.chip-red {{
    background: rgba(248, 113, 113, 0.10);
    color:#f87171;
    border:1px solid rgba(248, 113, 113, 0.35);
}}


# candidate information styles for name, email, phone, degree, CGPA, and experience.
.candidate-name {{
    font-size:20px;
    font-weight:700;
    color:{COLORS['text']};
    margin-bottom:2px;
}}
.candidate-meta {{
    font-size:13px;
    color:{COLORS['text_muted']};
}}

.footer {{
    text-align:center;
    color:{COLORS['text_muted']};
    padding-top:40px;
}}

hr {{
    border:1px solid {COLORS['card_border']};
}}

</style>
""",
    unsafe_allow_html=True,
)


# Hero Header - the main title and description of the application, styled with a gradient background and centered text.
st.markdown(
    """
    <div class="hero">
        <h1>👽 AI-Powered Resume Ranking & CONTEXTUAL Candidate Evaluation</h1>
        <p>Organizational Level Contextualization and Ranking of candidate evaluation for recruiters and hiring managers.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# Spec cards - instead of a sidebar, the specifications of the models and weights used
# in the evaluation are displayed in a row of cards at the top of the application.
spec_cols = st.columns(5)
spec_items = [
    ("Bi-Encoder", "all-MiniLM-L6-v2"),
    ("Cross-Encoder", "stsb-roberta-base"),
    ("LLM", "Qwen 3.6 27B"),
    ("Weights", "Rule 30% · Semantic 30% · Cross 40%"),
    ("Status", "🟢 System Ready"),
]
for col, (label, value) in zip(spec_cols, spec_items):
    with col:
        st.markdown(
            f"""
            <div class="card" style="padding:14px 16px; margin-bottom:1rem;">
                <div class="section-label" style="margin-top:0;">{label}</div>
                <div style="font-size:14px; font-weight:600; color:{COLORS['text']};">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# Upload Section - two columns for uploading candidate resumes and the job description,
# with file uploaders and text area for pasting the job description.
left, right = st.columns(2)

with left:
    st.markdown("<div class='section-title'>📄 Candidate Resumes</div>",
                unsafe_allow_html=True)
    resume_files = st.file_uploader(
        "Upload one or more resumes",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        key=f"resume_upload_{st.session_state.uploader_key}",
    )

with right:
    st.markdown("<div class='section-title'>📝 Job Description</div>",
                unsafe_allow_html=True)
    jd_file = st.file_uploader(
        "Upload Job Description",
        type=["pdf", "docx", "txt"],
        key=f"jd_upload_{st.session_state.uploader_key}",
    )
    jd_text_input = st.text_area(
        "Or paste Job Description",
        height=200,
        placeholder="Paste job description here...",
        key=f"jd_paste_{st.session_state.uploader_key}",
    )

st.divider()

# Analyze Candidates Button - when clicked, triggers the processing pipeline to evaluate the uploaded resumes against
# the job description.
process = st.button("🚀 Analyze Candidates", type="primary",
                    use_container_width=True)

progress_placeholder = st.empty()
status_placeholder = st.empty()


# Processing Pipeline
if process:
    if not resume_files:
        st.error("Please upload at least one resume.")
    elif jd_file is None and jd_text_input.strip() == "":
        st.error("Please upload or paste a Job Description.")
    else:
        progress = progress_placeholder.progress(0)

        # ---- In Step 1: Job Description text (single JD, shared across all candidates) will be extracted and stored in `jd_text`. If the user uploaded a JD file, it will be read; otherwise, the pasted text will be used.
        try:
            status_placeholder.info("📄 Reading Job Description...")
            progress.progress(5)

            if jd_file is not None:
                jd_text = extract_text(jd_file, jd_file.name)
            else:
                jd_text = jd_text_input

# if there is an error reading the job description, it will be caught and displayed to the user, and the processing will stop.
        except Exception as e:
            progress_placeholder.empty()
            status_placeholder.empty()
            st.error("⚠️ Issue reading Job Description")
            with st.expander("Details", expanded=False):
                st.exception(e)
            st.stop()

        # the following loop iterates over each uploaded resume file, extracting text, structured fields, computing eligibility, semantic and cross-encoder scores, building the dashboard, and generating explanations. Any errors encountered during processing of a specific resume will be caught and displayed, allowing the processing of other resumes to continue.
        results = []
        n = len(resume_files)

        for i, resume_file in enumerate(resume_files):
            candidate_label = resume_file.name
            base_pct = int((i / n) * 90) + 5

            try:
                status_placeholder.info(f"📑 Parsing {candidate_label}...")
                progress.progress(min(base_pct + 5, 95))
                resume_text = extract_text(resume_file, resume_file.name)

                status_placeholder.info(
                    f"🤖 Extracting fields — {candidate_label}...")
                progress.progress(min(base_pct + 10, 95))

                """ LLM JSON output is non-deterministic — a malformed comma
                 on one attempt often succeeds on a retry. Bounded to 3
                 total attempts so a genuinely broken prompt/schema still
                 fails fast instead of hanging. """
                candidate = None
                last_extract_error = None
                for attempt in range(3):
                    try:
                        candidate = extract_structured_fields(resume_text)
                        break
                    except Exception as extract_err:
                        last_extract_error = extract_err
                        if attempt < 2:
                            status_placeholder.info(
                                f"🔁 Retrying extraction for {candidate_label} "
                                f"(attempt {attempt + 2}/3)..."
                            )
                if candidate is None:
                    raise last_extract_error

                status_placeholder.info(
                    f"📋 Running rule engine — {candidate_label}...")
                progress.progress(min(base_pct + 15, 95))
                rule_results = compute_eligibility(candidate)

                status_placeholder.info(
                    f"🧠 Semantic similarity — {candidate_label}...")
                progress.progress(min(base_pct + 20, 95))
                semantic_score = compute_bi_encoder_score(resume_text, jd_text)

                status_placeholder.info(
                    f"⚡ Cross-encoder scoring — {candidate_label}...")
                progress.progress(min(base_pct + 25, 95))
                cross_score = compute_cross_encoder_score(resume_text, jd_text)

                status_placeholder.info(
                    f"📊 Building dashboard — {candidate_label}...")
                dashboard = build_dashboard_results(
                    extracted_fields=candidate,
                    jd_text=jd_text,
                    rule_results=rule_results,
                    semantic_score=semantic_score,
                    cross_encoder_score=cross_score,
                )

                status_placeholder.info(
                    f"💡 Generating explanation — {candidate_label}...")
                explanation = generate_explanation(
                    jd_text, candidate, dashboard["final_score"]
                )
                # the results for each candidate are appended to the `results` list, which will be used later to display the ranked candidates in the dashboard.
                results.append(
                    {
                        "file_name": candidate_label,
                        "resume_text": resume_text,
                        "candidate": candidate,
                        "rule_results": rule_results,
                        "dashboard": dashboard,
                        "explanation": explanation,
                    }
                )

            except Exception as e:
                st.warning(f"⚠️ Issue in resume: {candidate_label}")
                with st.expander(f"Details — {candidate_label}", expanded=False):
                    st.exception(e)
                continue

        progress.progress(100)
        # if no candidates were successfully processed, an error message is displayed to the user. Otherwise, the results are sorted by final score and stored in the session state for display in the results dashboard.
        if not results:
            progress_placeholder.empty()
            status_placeholder.empty()
            st.error("No candidates could be processed.")
        else:
            results.sort(key=lambda r: r["dashboard"]
                         ["final_score"], reverse=True)
            st.session_state.results = results
            status_placeholder.success(
                f"✅ Processed {len(results)} candidate(s) successfully.")


# Results Dashboard - results are displayed in a ranked list, with each candidate's score, recommendation, and explanation.
# A summary of the cohort is also provided, showing the number of strong, consider, and reject candidates.
if st.session_state.results:
    results = st.session_state.results

    st.divider()

    scores = [r["dashboard"]["final_score"] for r in results]
    strong = sum(1 for r in results if tier_color(r["dashboard"].get(
        "recommendation", ""), r["dashboard"]["final_score"])[1] == "🟢")
    consider = sum(1 for r in results if tier_color(r["dashboard"].get(
        "recommendation", ""), r["dashboard"]["final_score"])[1] == "🟡")
    reject = len(results) - strong - consider

    st.markdown("<div class='section-title'>📊 Cohort Summary</div>",
                unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Candidates Evaluated", len(results))
    m2.metric("🟢 Strong", strong)
    m3.metric("🟡 Consider", consider)
    m4.metric("🔴 Reject", reject)

    st.divider()
    st.markdown("<div class='section-title'>🏆 Ranked Candidates</div>",
                unsafe_allow_html=True)

# Displaying each candidate's information, score, recommendation, and explanation in a card format.
# The candidates are ranked based on their final scores, and the color and emoji for each candidate are determined
# by their recommendation and score.
    for rank, r in enumerate(results, start=1):
        dashboard = r["dashboard"]
        candidate = r["candidate"]
        final_score = dashboard["final_score"]
        recommendation = dashboard.get("recommendation", "")
        color, emoji = tier_color(recommendation, final_score)

        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)

            column_ring, column_information, column_flags = st.columns([
                                                                       1, 1.4, 2.1])
            # this section displays the candidate's score in a circular ring format, along with their recommendation and rank.
            with column_ring:
                st.markdown(
                    f"""
                    <div class="score-ring" style="--pct:{final_score}; --ring-color:{color};">
                        <div class="score-ring-inner">
                            <div class="score-ring-value">{final_score:.0f}</div>
                            <div class="score-ring-label">/ 100</div>
                        </div>
                    </div>
                    <div style="text-align:center;">
                        <span class="rec-badge" style="background-color:{color}22; color:{color}; border:1px solid {color}55;">
                            {emoji} {recommendation or "Scored"}
                        </span>
                    </div>
                    <div style="text-align:center; margin-top:6px; color:{COLORS['text_muted']}; font-size:13px;">
                        Rank #{rank}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            # this section displays the candidate's name, email, phone number, degree, CGPA, experience, and skills. If any of these fields are missing, default values or placeholders are used.
            with column_information:
                name = candidate.get("name") or r["file_name"]
                email = candidate.get("email") or "—"
                phone = candidate.get("phone") or "—"
                degree = candidate.get("degree") or "Degree not found"
                cgpa = candidate.get("cgpa")
                exp = candidate.get("total_experience_years")

                st.markdown(
                    f"<div class='candidate-name'>{name}</div>", unsafe_allow_html=True)
                st.markdown(
                    f"<div class='candidate-meta'>{email} · {phone}</div>", unsafe_allow_html=True)
                st.markdown(
                    f"<div class='candidate-meta'>{degree}</div>", unsafe_allow_html=True)
                st.markdown(
                    f"<div class='candidate-meta'>CGPA: {cgpa if cgpa is not None else 'Not stated'} · "
                    f"Experience: {exp if exp is not None else 'Not stated'} yrs</div>",
                    unsafe_allow_html=True,
                )

                st.markdown("<div class='section-label'>Skills</div>",
                            unsafe_allow_html=True)
                skills = candidate.get("skills") or []
                if skills:
                    st.markdown(
                        "".join(
                            f"<span class='chip chip-skill'>{s}</span>" for s in skills),
                        unsafe_allow_html=True,
                    )
                else:
                    st.caption("No skills extracted")

            with column_flags:
                explanation = r["explanation"]
                # Handle both possible shapes: structured dict or plain text,
                # since generate_explanation's return type wasn't confirmed.
                if isinstance(explanation, dict):
                    green_flags = explanation.get("green_flags", [])
                    red_flags = explanation.get("red_flags", [])
                    rationale = explanation.get("overall_rationale", "")

                    gcol, rcol = st.columns(2)
                    with gcol:
                        with st.container(border=True):
                            st.markdown("**✅ Green Flags**")
                            if green_flags:
                                for flag in green_flags:
                                    st.markdown(
                                        f"<div class='chip chip-green' style='display:block; margin-bottom:4px;'>{flag}</div>",
                                        unsafe_allow_html=True,
                                    )
                            else:
                                st.caption("None identified")
                    with rcol:
                        with st.container(border=True):
                            st.markdown("**🚩 Red Flags**")
                            if red_flags:
                                for flag in red_flags:
                                    st.markdown(
                                        f"<div class='chip chip-red' style='display:block; margin-bottom:4px;'>{flag}</div>",
                                        unsafe_allow_html=True,
                                    )
                            else:
                                st.caption("None identified")

                else:
                    st.markdown(
                        "<div class='section-label'>AI Explanation</div>", unsafe_allow_html=True)
                    with st.container(border=True):
                        st.write(explanation)

            # --- Recruiter Summary — the final-verdict callout ------------
            # Distinct from the green/red flag chips above: this is the
            # one paragraph a recruiter reads if they read nothing else.
            if isinstance(explanation, dict):
                summary_text = (
                    explanation.get(
                        "overall_rationale")
                    or explanation.get("rationale")
                    or "No rationale generated."
                )
            else:
                summary_text = explanation or "No explanation generated."

            st.markdown(
                f"""
                <div style="
                    margin-top:16px;
                    padding:16px 20px;
                    border-radius:12px;
                    background:{color}14;
                    border-left:4px solid {color};
                ">
                    <div class="section-label" style="margin-top:0; color:{color};">
                        #{rank} · {recommendation or 'Scored'}
                        📋 Recruiter Summary — Rank
                    </div>
                    <div style="font-size:14.5px; line-height:1.55; color:{COLORS['text']};">
                        {summary_text}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    if st.button("🔄 Start New Evaluation", type="secondary"):
        st.session_state.results = None
        st.session_state.uploader_key += 1
        st.rerun()

else:
    st.info("🗂️Upload candidate resumes and a job description, then click **Analyze Candidates**.")


# Footer

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<div class='footer'>© 2026 Atharva Jivan Ayachit  . All Rights Reserved.</div>",
    unsafe_allow_html=True,
)
