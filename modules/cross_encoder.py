# this file defines the Cross-Encoder reranking engine,
# which computes a fine-grained relevance score between a Job Description (JD) and a Resume.
# Unlike the Bi-Encoder, both texts are processed together, allowing the transformer to attend jointly across both inputs.
# This produces a more accurate relevance score but is slower than the Bi-Encoder.

"""
Cross-Encoder reranking engine.

Purpose:
- Compute a fine-grained relevance score between a Job Description (JD)
  and a Resume.
- Unlike the Bi-Encoder, both texts are processed together, allowing
  the transformer to attend jointly across both inputs.
- This produces a more accurate relevance score but is slower than
  the Bi-Encoder.

Pipeline:

        Resume
           │
           ▼
   [JD, Resume]
           │
           ▼
     Cross Encoder
           │
           ▼
    Relevance Score
           │
           ▼
         0 - 100
"""

from sentence_transformers import CrossEncoder

from config import CROSS_ENCODER_MODEL

# Lazy-loaded Cross Encoder model
_model: CrossEncoder | None = None


def get_model() -> CrossEncoder:
    """
    Load the Cross Encoder model only once.
    """

    global _model

    if _model is None:
        _model = CrossEncoder(CROSS_ENCODER_MODEL)

    return _model


def normalize_score(score: float) -> float:
    """
    Normalize the raw model score to the range [0, 100].
    """

    score = max(0.0, min(1.0, score))

    return round(score * 100, 2)


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
