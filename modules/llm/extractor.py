# this file defines the LLM-based resume information extractor,
# which is responsible for sending raw resume text to the LLM,
# receiving structured JSON output, and parsing it to return extracted candidate information.
# The module does not handle scoring, ranking, or recommendation logic.

"""
LLM-based resume information extractor.

Responsibility:
- Send resume text to the LLM.
- Receive structured JSON.
- Parse and return the extracted candidate information.

This module is ONLY responsible for extraction.
No scoring, ranking, or recommendation logic belongs here.
"""


import json
from typing import Any

from modules.llm.client import client, MODEL_NAME
from modules.llm.prompts import EXTRACTION_SYSTEM_PROMPT
from modules.llm.schema import CANDIDATE_SCHEMA


def extract_structured_fields(resume_text: str) -> dict[str, Any]:
    """
    Extract structured candidate information from resume text using an LLM.

    Args:
        resume_text: Raw resume text.

    Returns:
        Dictionary containing structured candidate information.
    """

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": EXTRACTION_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": f"""
                    Extract structured information from the following resume.

                    Return ONLY a valid JSON object.

                Resume:

                        {resume_text}   
                """,
            },
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content

    if raw is None:
        raise ValueError("LLM returned an empty response.")

    raw = raw.strip()

    # Remove markdown code fences if the model adds them.
    if raw.startswith("```"):
        raw = raw.removeprefix("```json")
        raw = raw.removeprefix("```")
        raw = raw.removesuffix("```")
        raw = raw.strip()

    # Extract JSON object if extra text exists
    start = raw.find("{")
    end = raw.rfind("}")

    if start != -1 and end != -1:
        raw = raw[start: end + 1]

    try:
        extracted_data = json.loads(raw)

    except json.JSONDecodeError as e:
        raise ValueError(
            f"LLM returned invalid JSON.\n\nError: {e}\n\nOutput:\n{raw}"
        )

    # Ensure all expected top-level keys exist.
    for key, default_value in CANDIDATE_SCHEMA.items():
        extracted_data.setdefault(key, default_value)

    return extracted_data
