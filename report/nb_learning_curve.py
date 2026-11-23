"""Naive Bayes learning curve: training vs. validation log-loss as the training set grows.

Uses the same cleaning, split, TF-IDF settings and model as notebooks/baselines/naive_bayes.ipynb.
Usage: python nb_learning_curve.py <modeling_data.csv> <output.png>
"""
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import log_loss
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB


def clean_narrative(text):
    text = str(text).lower()

    # Remove CFPB redaction placeholders such as XXXX, XX, etc.
    text = re.sub(r'\bx{2,}\b', ' ', text)

    # Remove standalone numeric placeholders
    text = re.sub(r'\b0{2,}\b', ' ', text)

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


data_path, out_path = sys.argv[1], sys.argv[2]

df = pd.read_csv(data_path, usecols=["Product", "Consumer complaint narrative"])
df["clean_narrative"] = df["Consumer complaint narrative"].apply(clean_narrative)
df = df[df["clean_narrative"].str.strip() != ""].copy()

X_train, X_test, y_train, y_test = train_test_split(
    df["clean_narrative"], df["Product"], test_size=0.20, random_state=42, stratify=df["Product"]
)

# Hold out 20% of the training set for validation; the test set is not used here
X_fit, X_val, y_fit, y_val = train_test_split(
    X_train, y_train, test_size=0.20, random_state=42, stratify=y_train
)

sizes, train_loss, val_loss = [], [], []
for fraction in [0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0]:
    if fraction < 1:
        X_sub, _, y_sub, _ = train_test_split(
            X_fit, y_fit, train_size=fraction, random_state=42, stratify=y_fit
        )
    else:
        X_sub, y_sub = X_fit, y_fit

    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000, min_df=5)
    X_sub_tfidf = vectorizer.fit_transform(X_sub)
    X_val_tfidf = vectorizer.transform(X_val)

    nb_model = MultinomialNB().fit(X_sub_tfidf, y_sub)
    sizes.append(len(y_sub))
    train_loss.append(log_loss(y_sub, nb_model.predict_proba(X_sub_tfidf), labels=nb_model.classes_))
    val_loss.append(log_loss(y_val, nb_model.predict_proba(X_val_tfidf), labels=nb_model.classes_))
    print(f"{len(y_sub):>7,} training complaints: train log-loss {train_loss[-1]:.3f}, "
          f"validation log-loss {val_loss[-1]:.3f}")

plt.figure(figsize=(6, 3.6))
plt.plot(sizes, train_loss, marker="o", label="Training loss")
plt.plot(sizes, val_loss, marker="o", label="Validation loss")
plt.title("Naive Bayes Learning Curve")
plt.xlabel("Number of Training Complaints")
plt.ylabel("Log-Loss")
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(out_path, dpi=300, bbox_inches="tight")
print("saved", out_path)
