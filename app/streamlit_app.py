"""Griev.AI.ance - Complaint Router (Streamlit demo).

Routes a consumer complaint narrative to one of 11 CFPB product categories, estimates the
chance it closes with monetary relief, and shows which words drove the product prediction.

Run from the repository root:
    python -m streamlit run app/streamlit_app.py

Needs the saved models created by the notebooks:
    models/product_logreg.joblib  <- notebooks/baselines/log_regression.ipynb
    models/relief_logreg.joblib   <- notebooks/relief/monetary_relief.ipynb
"""
import json
import re
from pathlib import Path

import altair as alt
import joblib
import numpy as np
import pandas as pd
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parent.parent
PRODUCT_MODEL_PATH = REPO_ROOT / "models" / "product_logreg.joblib"
RELIEF_MODEL_PATH = REPO_ROOT / "models" / "relief_logreg.joblib"
RELIEF_METRICS_PATH = REPO_ROOT / "results" / "metrics" / "relief_text.json"
MODEL_SOURCES = {
    PRODUCT_MODEL_PATH: "notebooks/baselines/log_regression.ipynb",
    RELIEF_MODEL_PATH: "notebooks/relief/monetary_relief.ipynb",
}

SHORT_LABELS = {
    "Checking or savings account": "Checking/Savings",
    "Credit card": "Credit Card",
    "Credit reporting or other personal consumer reports": "Credit Reporting",
    "Debt collection": "Debt Collection",
    "Debt or credit management": "Debt/Credit Mgmt",
    "Money transfer, virtual currency, or money service": "Money Transfer",
    "Mortgage": "Mortgage",
    "Payday loan, title loan, personal loan, or advance loan": "Payday/Personal Loan",
    "Prepaid card": "Prepaid Card",
    "Student loan": "Student Loan",
    "Vehicle loan or lease": "Vehicle Loan",
}

SAMPLE_COMPLAINTS = {
    "Credit report: account I don't recognize": (
        "I pulled my credit report and found a collection account that I do not recognize. I never opened "
        "this account. I disputed it with the credit bureau twice, and both times they said it was verified "
        "without doing any real investigation. This inaccurate information dropped my score by 80 points and "
        "I was denied an apartment. Please remove it from my report."
    ),
    "Debt collection: calls about a paid bill": (
        "A debt collector calls me five or six times a day about a medical bill that I already paid in full "
        "on XX/XX/2026. I sent them proof of payment and asked them to validate the debt, but they never sent "
        "a validation letter. They also called my job and told my supervisor that I owe money. I want these "
        "calls to stop."
    ),
    "Mortgage: loan modification and foreclosure": (
        "I applied for a loan modification with my mortgage servicer after I lost my job. They told me my "
        "application was complete, then said they lost my documents three times. While the modification was "
        "still under review they charged late fees and started foreclosure. My escrow payment also went up by "
        "{$350.00} a month with no explanation."
    ),
    "Money transfer: Zelle scam": (
        "Someone called pretending to be from my bank's fraud department and told me to send {$1,500.00} "
        "through Zelle to protect my account. The money went to a stranger. I reported the scam to my bank the "
        "same day, but they refused to reimburse me because they said I authorized the payment. I never would "
        "have sent it if they had not impersonated the bank."
    ),
    "Student loan: servicer transfer": (
        "My federal student loans were transferred to a new servicer and my income-driven repayment plan was "
        "not carried over. They put my loans in forbearance without asking me, the interest was capitalized, "
        "and my monthly payment tripled. Every representative gives me a different count of my qualifying "
        "payments for Public Service Loan Forgiveness."
    ),
}
WRITE_YOUR_OWN = "Write your own"

# --- Canonical text cleaning (copied verbatim from notebooks/01_data_cleaning.ipynb) ---
AMOUNT_PATTERN = re.compile(r"\{\$?[\d,]*(?:\.\d*)?\}")
DATE_PATTERN = re.compile(r"\b(?:x{2}|\d{1,2})/(?:x{2}|\d{1,2})/(?:x{2,4}|\d{2,4}|year>?)")
REDACTION_PATTERN = re.compile(r"\bx{2,}\b")
SYMBOL_PATTERN = re.compile(r"[{}<>/\\]")
WHITESPACE_PATTERN = re.compile(r"\s+")


def clean_narrative(text):
    text = str(text).lower()
    text = AMOUNT_PATTERN.sub(" dollaramount ", text)
    text = DATE_PATTERN.sub(" ", text)
    text = REDACTION_PATTERN.sub(" ", text)
    text = SYMBOL_PATTERN.sub(" ", text)
    text = WHITESPACE_PATTERN.sub(" ", text).strip()
    return text


@st.cache_resource
def load_models():
    product_model = joblib.load(PRODUCT_MODEL_PATH)
    relief_model = joblib.load(RELIEF_MODEL_PATH)
    vocabulary = product_model.named_steps["tfidf"].get_feature_names_out()
    return product_model, relief_model, vocabulary


def load_relief_settings():
    """Decision threshold and base rate for the relief model (from its metrics JSON when available)."""
    try:
        metrics = json.loads(RELIEF_METRICS_PATH.read_text())
        return float(metrics["threshold"]), float(metrics["prevalence"])
    except (OSError, KeyError, ValueError):
        return 0.5, 0.05


def bar_chart(data, value, label, value_format):
    return (
        alt.Chart(data)
        .mark_bar(color="#2a78d6", cornerRadiusEnd=4)
        .encode(
            x=alt.X(f"{value}:Q", title=None, axis=alt.Axis(format=value_format)),
            y=alt.Y(f"{label}:N", sort="-x", title=None),
            tooltip=[alt.Tooltip(f"{label}:N"), alt.Tooltip(f"{value}:Q", format=value_format)],
        )
        .properties(height=alt.Step(30))
    )


# --- Page ---
st.set_page_config(page_title="Griev.AI.ance - Complaint Router", layout="centered")
st.title("Griev.AI.ance — Complaint Router")
st.write(
    "Paste a consumer complaint narrative (or start from a sample) to see which CFPB product category it "
    "would be routed to, how likely it is to end with monetary relief, and which words drove the decision."
)

missing = [path for path in MODEL_SOURCES if not path.exists()]
if missing:
    st.error(
        "Model file not found:\n\n"
        + "\n".join(f"- `{p.relative_to(REPO_ROOT).as_posix()}`: run `{MODEL_SOURCES[p]}` to create it." for p in missing)
    )
    st.stop()

product_model, relief_model, vocabulary = load_models()
relief_threshold, relief_base_rate = load_relief_settings()

sample = st.selectbox("Sample complaint", [*SAMPLE_COMPLAINTS, WRITE_YOUR_OWN])
narrative = st.text_area(
    "Complaint narrative",
    value=SAMPLE_COMPLAINTS.get(sample, ""),
    height=200,
    placeholder="Describe what happened, in your own words...",
)

if st.button("Route complaint", type="primary"):
    cleaned = clean_narrative(narrative)
    if not cleaned:
        st.warning("Please enter a complaint narrative first.")
        st.stop()

    # Product prediction
    tfidf = product_model.named_steps["tfidf"]
    clf = product_model.named_steps["clf"]
    x = tfidf.transform([cleaned])
    proba = clf.predict_proba(x)[0]
    ranked = np.argsort(proba)[::-1]
    predicted_index = ranked[0]
    predicted = clf.classes_[predicted_index]

    if x.nnz == 0:
        st.warning("None of these words are in the model's vocabulary, so the prediction is close to a guess.")

    st.subheader("Predicted product")
    st.success(f"**{predicted}**")
    top3 = pd.DataFrame(
        {
            "product": [SHORT_LABELS.get(c, c) for c in clf.classes_[ranked[:3]]],
            "probability": proba[ranked[:3]],
        }
    )
    st.altair_chart(bar_chart(top3, "probability", "product", ".0%"), width="stretch")

    # Monetary relief
    st.subheader("Monetary relief")
    positive_column = list(relief_model.classes_).index(1)
    relief_proba = relief_model.predict_proba([cleaned])[0, positive_column]
    class_weighted = getattr(relief_model[-1], "class_weight", None) == "balanced"
    left, right = st.columns(2)
    left.metric("Relief score" if class_weighted else "Relief probability", f"{relief_proba:.1%}")
    right.metric("Flag", "Likely" if relief_proba >= relief_threshold else "Unlikely")
    weighting_note = (
        "The model was trained with balanced class weights, so scores run well above true probabilities "
        "(a 50% score does not mean a 50% chance). "
        if class_weighted
        else ""
    )
    st.caption(
        f"Monetary relief is rare: only {relief_base_rate:.1%} of closed complaints in the training data ended "
        f"with monetary relief. A complaint is flagged as likely when its score is at least {relief_threshold:.2f}, "
        f"the threshold chosen on cross-validation. {weighting_note}Treat the score as a ranking signal, "
        "not a promise of compensation."
    )

    # Word contributions for the predicted product: tfidf value x coefficient
    contributions = x.data * clf.coef_[predicted_index, x.indices]
    order = np.argsort(contributions)[::-1][:10]
    top_words = pd.DataFrame({"word": vocabulary[x.indices[order]], "contribution": contributions[order]})
    top_words = top_words[top_words["contribution"] > 0]

    st.subheader("Top contributing words")
    st.caption(
        f"Contribution = TF-IDF weight of the word in this complaint x the model's coefficient for "
        f"{SHORT_LABELS.get(predicted, predicted)}. Longer bars pushed the complaint harder toward this product."
    )
    if top_words.empty:
        st.info("No individual word pushed strongly toward this product.")
    else:
        st.altair_chart(bar_chart(top_words, "contribution", "word", ".2f"), width="stretch")

    with st.expander("Cleaned text (what the models see)"):
        st.code(cleaned, language=None, wrap_lines=True)

st.divider()
st.caption(
    "Models: TF-IDF (1-2 grams) + Logistic Regression trained on CFPB complaints received Aug 2023 - Jul 2026. "
    "There is no live-complaints feed: the CFPB stopped publishing new complaint narratives on Aug 14, 2026. "
    "CSC 4850 class project; not legal or financial advice."
)
