# 🤖 AI Powered Resume Ranking Contextual Candidate Evaluation

<p align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Web_App-FF4B4B?style=for-the-badge&logo=streamlit)
![LLM](https://img.shields.io/badge/Groq-LLM-orange?style=for-the-badge)
![Sentence Transformers](https://img.shields.io/badge/SentenceTransformers-MiniLM-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-success?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

</p>

---

## 📌 Overview

 
"""assets/IMAGES/Streamlit APP.png 
"""

**AI Powered Resume Ranking Contextual Candidate Evaluation** is an enterprise-inspired Applicant Tracking System (ATS) that intelligently evaluates resumes against job descriptions using a hybrid AI pipeline.

Unlike traditional ATS solutions that rely solely on keyword matching, this project combines:

- 🤖 Large Language Models (LLMs)
- 📖 Semantic Search (Bi-Encoder)
- 🎯 Cross-Encoder Re-ranking
- 📏 Deterministic Rule Engine
- 📊 Weighted ATS Scoring
- 💡 AI Recruiter Explanation

The goal is to automate the first stage of recruitment while keeping candidate evaluation transparent, explainable, and reproducible.

---

# ✨ Features

- 📄 Upload multiple PDF/DOCX resumes
- 📝 Upload or paste Job Description
- 🤖 LLM-based Resume Information Extraction
- 📊 Automatic Candidate Ranking
- 📈 ATS Score Generation
- 🎯 Cross Encoder Re-ranking
- 🧠 Semantic Similarity Matching
- ✅ Deterministic Rule Engine
- 💬 AI Recruiter Explanation
- 🟢 Green Flags & 🔴 Red Flags
- 📋 Candidate Summary Dashboard
- 👨‍💻 Developer Pipeline Viewer
- ⚡ Modern Streamlit Interface

---

# 🏗️ System Architecture

```assets/IMAGES/System Architecture.png
```

---

# 🚀 Tech Stack

## Frontend

- Streamlit

## Backend

- Python

## AI / ML

- Groq API
- GPT-OSS / Qwen (Configurable)
- Sentence Transformers
- MiniLM Bi-Encoder
- Cross Encoder

## NLP

- Semantic Search
- Contextual Ranking

## Document Processing

- pdfplumber
- python-docx

---

# 📂 Project Structure

```text
AI_Powered_Resume_Ranking_Contextual_Candidate_Evaluation/

│
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── .env
│
├── modules/
│   ├── parser.py
│   ├── semantic_engine.py
│   ├── cross_encoder.py
│   ├── scorer.py
│   ├── rule_engine.py
│   │
│   └── llm/
│       ├── client.py
│       ├── extractor.py
│       ├── explainer.py
│       ├── prompts.py
│       └── schema.py
│
├── dev_tools.py
│
└── assets/
```

---

# ⚙️ End-to-End Pipeline

### Step 1

Upload Resume(s)

↓

### Step 2

Upload Job Description

↓

### Step 3

Resume Parsing

↓

### Step 4

LLM extracts structured candidate information

↓

### Step 5

Rule Engine checks

- CGPA
- Experience

↓

### Step 6

Semantic Search computes similarity

↓

### Step 7

Cross Encoder computes contextual relevance

↓

### Step 8

Weighted ATS Score is calculated

↓

### Step 9

LLM generates recruiter explanation

↓

### Step 10

Recruiter Dashboard displays ranked candidates

---

# 📊 ATS Score Formula

The final ATS score is calculated using weighted scoring.

| Component           | Weight |
|---------------------|--------|
| Rule Engine         | 30%    |
| Semantic Similarity | 30%    |
| Cross Encoder       | 40%    |

```
Final Score =
(Rule × 0.30)
+
(Semantic × 0.30)
+
(Cross Encoder × 0.40)
```

---

# 🧠 AI Components

## Resume Extraction

Uses an LLM to convert unstructured resumes into structured JSON.

Extracted information includes:

- Personal Information
- Education
- Experience
- Projects
- Skills
- Certifications
- Languages
- Professional Summary

---

## Rule Engine

Deterministic checks for:

- Minimum CGPA
- Minimum Experience

Future support:

- Degree
- Notice Period
- Location
- Salary
- Certifications

---

## Semantic Search

Bi-Encoder computes semantic similarity between:

```
Resume

⇄

Job Description
```

---

## Cross Encoder

Performs contextual comparison by jointly processing:

```
(Job Description, Resume)
```

Produces a highly accurate relevance score.

---

## AI Explanation

The LLM **does not calculate scores**.

Instead, it explains:

- Green Flags
- Red Flags
- Matching Skills
- Missing Skills
- Recommendation
- Overall Rationale

---

# 📸 Screenshots

Add screenshots here.

```
assets/screenshots/home.png

assets/screenshots/mulitple resumes against one jd.png

assets/screenshots/Parsing.png

assets/screenshots/candidate summary.png



```

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/atharva-2011/AI_Powered_Resume_Ranking_Contextual_Candidate_Evaluation.git

cd AI_Powered_Resume_Ranking_Contextual_Candidate_Evaluation
```

Always Create virtual environment for a new project

```bash
python -m venv venv
```

Activate environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
assets/IMAGES/Requirements.png
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file.

```
assets/IMAGES/System Config

env
GROQ_API_KEY=YOUR_API_KEY

GROQ_MODEL=openai/gpt-oss-120b
```

---

# ▶️ Run

```bash
streamlit run app.py
```

---

# 🌟 Future Enhancements

- Resume Batch Processing
- Recruiter Authentication
- Candidate Database
- PostgreSQL Integration
- FAISS Vector Database
- PDF Report Generation
- Recruiter Analytics
- REST API
- Docker Support
- Cloud Deployment
- OCR Support
- Resume History

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository

2. Create a feature branch

3. Commit your changes

4. Push your branch

5. Open a Pull Request

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**Atharva Jivan Ayachit**

📧 Email: your-atharvaayachit646@gmail.com

💻 GitHub: https://github.com/atharva-2011

---

## ⭐ If you found this project useful, consider giving it a Star!