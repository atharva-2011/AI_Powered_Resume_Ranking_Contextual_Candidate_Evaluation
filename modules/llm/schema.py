# this file defines a schema for candidate information, including personal details,
# professional summary, education, experience, projects, skills, certifications, achievements, languages, and overall profile.
# The schema is represented as a dictionary with string keys and values of any type.

from typing import Any


CANDIDATE_SCHEMA: dict[str, Any] = {

    "personal_information": {
        "full_name": "",

        "email": "",

        "phone": "",

        "location": "",

        "linkedin": "",

        "github": "",

        "portfolio": ""
    },

    "professional_summary": "",

    "education": [
        {

            "degree": "",

            "specialization": "",

            "institute": "",

            "cgpa": None,

            "graduation_year": ""

        }],

    "experience": [
        {

            "company": "",

            "role": "",

            "duration": "",

            "responsibilities": [],

            "technologies": [],

            "achievements": [],

            "domain": ""

        }],

    "projects": [
        {

            "name": "",

            "domain": "",

            "description": "",

            "problem": "",

            "solution": "",

            "skills_used": [],

            "technologies": [],

            "impact": ""

        }],

    "skills": {

        "technical": [],

        "tools": [],

        "frameworks": [],

        "databases": [],

        "cloud": [],

        "soft_skills": []

    },

    "certifications": [
        {
            "name": "",
            "issuer": "",
            "year": ""
        }
    ],

    "achievements": [],

    "languages": [
        {
            "language": "",
            "proficiency": ""
        }
    ],

    "overall_profile": {

        "total_experience": None,

        "current_role": "",

        "current_company": "",

        "highest_education": "",

        "strongest_domains": []

    }
}
