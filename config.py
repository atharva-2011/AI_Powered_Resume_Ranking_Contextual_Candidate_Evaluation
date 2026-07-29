# THIS IS CONFIG FILE FOR THE EMBEDDING MODELS USED IN THE APPLICATION

BI_ENCODER_MODEL = "all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL = "cross-encoder/stsb-roberta-base"


# These weights are used to combine the scores from different scoring methods
# (rule-based, bi-encoder, and cross-encoder) into a final score.
# The weights should sum to 1.0.
WEIGHTS = {
    "rule": 0.30,
    "bi_encoder": 0.30,
    "cross_encoder": 0.40
}
