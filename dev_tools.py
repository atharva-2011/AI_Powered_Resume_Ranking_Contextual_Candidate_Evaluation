"""
Developer Tools — Pipeline Internals Viewer
=============================================

This file is NOT part of the recruiter-facing dashboard (app.py). It's kept
separate on purpose: the main app should stay clean for recruiters, this
file is for anyone (interviewer, future you, a contributor) who wants to
see exactly what each pipeline stage produced for a given candidate.

When publishing this project, point people here with something like:
    "See dev_tools.py if you want to inspect full pipeline internals —
    raw extracted JSON, rule-engine checks, and stage-by-stage scores."

USAGE
-----
This isn't wired up as its own running app (deliberately — two live apps
sharing state needs real infra: shared DB/file/cache between processes,
which is more complexity than this feature is worth). Instead, it's a
plain function you can call from anywhere you already have a `results`
list in memory — e.g. drop this one line back into app.py temporarily:

    from dev_tools import render_developer_tools
    render_developer_tools(r["file_name"], dashboard, r["rule_results"], candidate)

Or, for offline inspection without Streamlit at all, use `print_pipeline_report()`
below to dump the same information to your terminal/notebook from a saved
results object (e.g. if you pickle/json-dump `results` after a run).
"""

import json

import streamlit as st


def render_developer_tools(candidate_label: str, dashboard: dict, rule_results: dict, candidate: dict) -> None:
    """Streamlit rendering of one candidate's full pipeline internals.

    Call this inside an app that already has `results` in memory (see
    module docstring). Shows the same six metrics plus raw JSON that used
    to live in app.py's per-candidate expander.
    """
    st.markdown(f"### 🛠️ Pipeline Internals — {candidate_label}")

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Semantic Score", f"{dashboard.get('semantic_score', 0):.2f}")
        st.metric("Cross Encoder", f"{dashboard.get('cross_encoder_score', 0):.2f}")
        st.metric("Rule Score", f"{dashboard.get('rule_score', 0):.2f}")
    with c2:
        st.metric("Final ATS Score", f"{dashboard.get('final_score', 0):.2f}")
        st.metric("Confidence", f"{dashboard.get('confidence', 0):.2f}%")
        st.write("**Recommendation:**", dashboard.get("recommendation", "—"))

    st.markdown("**Rule Engine Output**")
    st.json(rule_results)

    st.markdown("**Extracted Candidate JSON**")
    st.json(candidate)


def print_pipeline_report(candidate_label: str, dashboard: dict, rule_results: dict, candidate: dict) -> None:
    """Plain-terminal version of the same report — no Streamlit needed.
    Useful for a quick `python -c` check or a notebook cell."""
    print(f"\n{'=' * 60}")
    print(f"PIPELINE INTERNALS — {candidate_label}")
    print(f"{'=' * 60}")
    print(f"Semantic Score      : {dashboard.get('semantic_score', 0):.2f}")
    print(f"Cross Encoder Score : {dashboard.get('cross_encoder_score', 0):.2f}")
    print(f"Rule Engine Score   : {dashboard.get('rule_score', 0):.2f}")
    print(f"Final ATS Score     : {dashboard.get('final_score', 0):.2f}")
    print(f"Confidence          : {dashboard.get('confidence', 0):.2f}%")
    print(f"Recommendation      : {dashboard.get('recommendation', '—')}")
    print("\n--- Rule Engine Output ---")
    print(json.dumps(rule_results, indent=2, default=str))
    print("\n--- Extracted Candidate JSON ---")
    print(json.dumps(candidate, indent=2, default=str))
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    # Minimal smoke test with fake data, so this file can be sanity-checked
    # on its own without needing a real pipeline run.
    fake_dashboard = {
        "semantic_score": 71.9,
        "cross_encoder_score": 56.9,
        "rule_score": 0.0,
        "final_score": 44.3,
        "confidence": 82.0,
        "recommendation": "Consider",
    }
    fake_rule_results = {"cgpa_threshold": False, "experience_threshold": None}
    fake_candidate = {"name": "Sample Candidate", "skills": ["Python", "SQL"]}

    print_pipeline_report("sample_resume.pdf", fake_dashboard, fake_rule_results, fake_candidate)
