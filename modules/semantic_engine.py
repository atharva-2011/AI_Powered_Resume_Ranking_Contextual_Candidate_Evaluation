# this module is responsible for computing semantic similarity between a Job Description (JD) and a Resume using a Bi-Encoder model from Sentence Transformers.
# It provides functions to load the model, compute embeddings, and calculate cosine similarity scores.
# The computed score is normalized to a range of 0 to 100 for easier interpretation.

"""
Semantic similarity engine using a Bi-Encoder.

This module computes semantic similarity between a Job Description (JD)
and a Resume using Sentence Transformers.


This module is intentionally lightweight and fast.
Fine-grained ranking is handled by the Cross Encoder.
"""

from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer

from config import BI_ENCODER_MODEL

# this variable holds the lazy-loaded Bi-Encoder model instance.
_model: SentenceTransformer | None = None


# this function loads the Bi-Encoder model only once and returns it for use in computing embeddings.
def get_model() -> SentenceTransformer:
    """
    Load the bi-encoder model only once.
    """
    global _model

    if _model is None:
        _model = SentenceTransformer(BI_ENCODER_MODEL)

    return _model


# this function computes the cosine similarity between two vectors, which is used to measure the semantic similarity between the embeddings of the Job Description and Resume.


def cosine_similarity(
    vector_a: np.ndarray[Any, Any],
    vector_b: np.ndarray[Any, Any],
) -> float:
    """
    Compute cosine similarity between two vectors.
    """

    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)

    denominator = norm_a * norm_b

    if denominator == 0:
        return 0.0

    similarity = float(np.dot(vector_a, vector_b) / denominator)

    return similarity


# this function computes the semantic similarity score between a Job Description and Resume by encoding both texts into embeddings using the Bi-Encoder model and calculating their cosine similarity. The score is normalized to a range of 0 to 100 for easier interpretation.
def compute_bi_encoder_score(
    jd_text: str,
    resume_text: str,
) -> float:
    """
    Compute semantic similarity score.

    Args:
        jd_text:
            Job description text.

        resume_text:
            Resume text.

    Returns:
        Semantic similarity score between 0 and 100.
    """

    model = get_model()

    # SentenceTransformer currently has incomplete type hints.
    embeddings: Any = model.encode(  # pyright: ignore[reportUnknownMemberType]
        [jd_text, resume_text],
        convert_to_numpy=True,
    )

    similarity = cosine_similarity(
        embeddings[0],
        embeddings[1],
    )

    similarity = max(-1.0, min(1.0, similarity))

    score = round(
        ((similarity + 1.0) / 2.0) * 100.0,
        2,
    )

    return score
