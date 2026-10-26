# ComplaintRouter (Griev.AI.ance)

Machine learning system for classifying and analyzing consumer financial complaints from the
CFPB Consumer Complaint Database (CSC 4850 course project).

Given the free-text narrative of a complaint, ComplaintRouter:

1. **Routes it to a financial product** (11 classes, e.g. credit reporting, debt collection,
   mortgage). Primary metric: macro-F1.
2. **Predicts whether it will close with monetary relief**, a rare outcome (about 5% of
   complaints). Metrics: ROC-AUC and PR-AUC.

It also studies truncated SVD (latent semantic analysis) of the TF-IDF features, k-means complaint
themes, and model explainability, and ships a small Streamlit demo.

## Data

On **August 14, 2026 the CFPB stopped publishing complaint narratives**; the current bulk file and
API no longer contain them. `notebooks/00_download_data.ipynb` therefore downloads the official
CFPB bulk file **as archived by the Internet Archive on August 15, 2026** (1.4 GB), the last public
snapshot with narratives. Raw and processed data are gitignored.

The modeling sample uses complaints received from **August 2023** (the CFPB's last product
taxonomy revision) through **August 2026**, deduplicated on cleaned text, with a capped number of
complaints per product (162,500 in total) and a fixed 80/20 train/test split stored in the data.

## Setup

```bash
pip install -r requirements.txt
```

Run notebooks from Jupyter, or headless with:

```bash
python -m nbconvert --to notebook --execute --inplace notebooks/01_data_cleaning.ipynb
```

## Run order

| Step | Notebook | Output |
|---|---|---|
| 0 | `notebooks/00_download_data.ipynb` | `data/raw/complaints_2026-08-15_archive.csv.zip` |
| 1 | `notebooks/01_data_cleaning.ipynb` | `data/processed/complaint_router_modeling_data.csv` |
| 2 | `notebooks/02_eda.ipynb` | EDA figures |
| 3 | `notebooks/baselines/` — `naive_bayes`, `log_regression`, `linear_svm` | metrics, confusion matrices, `models/product_logreg.joblib` |
| 4 | `notebooks/models/` — `knn`, `random_forest`, `gradient_boosting`, `mlp` | metrics, confusion matrices |
| 5 | `notebooks/relief/monetary_relief.ipynb` | relief metrics, ROC/PR curves, `models/relief_logreg.joblib` |
| 6 | `notebooks/03_dimensionality_reduction_clustering.ipynb` | SVD curve, 2-D plots, k-means themes |
| 7 | `notebooks/04_explainability_error_analysis.ipynb` | top terms, error analysis, leakage check |
| 8 | `notebooks/model_comparison.ipynb` | comparison table and figures |

Every modeling notebook is self-contained: it reads the processed CSV, uses the shared `split`
column, tunes hyperparameters with 3-fold stratified cross-validation on the training set only,
and writes its test metrics to `results/metrics/<model>.json` and figures to `figures/`.

## Demo

After running the logistic regression and monetary relief notebooks:

```bash
python -m streamlit run app/streamlit_app.py
```

## Results

All scores are on the fixed 32,500-complaint test set; hyperparameters were tuned with 3-fold
stratified cross-validation on the training set only.

### Product routing (11 classes)

| Model | Features | Test macro-F1 | Test accuracy |
|---|---|---|---|
| **Linear SVM** (C=0.25, balanced) | TF-IDF 1–2 grams (100k) | **0.784** | **0.806** |
| Logistic Regression (C=4) — used by the demo | TF-IDF 1–2 grams (100k) | 0.776 | 0.798 |
| MLP (256 hidden units) | TF-IDF → SVD-300 | 0.747 | 0.777 |
| Gradient Boosting (HistGB) | TF-IDF → SVD-300 | 0.734 | 0.765 |
| Multinomial Naive Bayes (α=0.03) | TF-IDF 1–2 grams (100k) | 0.723 | 0.749 |
| Complement Naive Bayes (α=0.01) | TF-IDF 1–2 grams (100k) | 0.721 | 0.759 |
| k-Nearest Neighbors (k=35, distance) | TF-IDF → SVD-300 | 0.709 | 0.751 |
| Random Forest (300 trees, depth 30) | TF-IDF → SVD-300 | 0.707 | 0.749 |
| Naive Bayes, team's original setup | TF-IDF 5k unigrams | 0.695 | 0.728 |

- Linear models on the full sparse TF-IDF beat every nonlinear model trained on 300 SVD components.
- The hardest product is *Debt or credit management* (F1 ≈ 0.50). The most frequent confusions are
  Debt collection ↔ Credit reporting and Money transfer ↔ Checking/savings, often genuine label
  ambiguity (the consumer chooses the product when filing).
- The strongest features are largely company names (Equifax, MOHELA, Zelle, Capital One, ...).
- Prediction confidence is informative: predictions above 0.9 (46% of complaints) are 94.9% accurate,
  so low-confidence complaints could be sent to a human reviewer.
- 5.6% of test narratives share their opening with a training narrative (template letters), but
  removing them changes macro-F1 only from 0.776 to 0.771.

### Monetary relief (binary, 5.6% positive)

| Model (Logistic Regression unless noted) | Test ROC-AUC | Test PR-AUC | F1 at CV-chosen threshold |
|---|---|---|---|
| Prevalence baseline | 0.500 | 0.056 | 0.107 |
| Product only | 0.819 | 0.160 | 0.261 |
| Text only (used by the demo) | 0.902 | 0.357 | 0.409 |
| Text + product | 0.904 | 0.365 | 0.416 |
| **Text + product + company** | **0.915** | **0.393** | **0.433** |
| Linear SVM, text + product + company | 0.914 | 0.387 | 0.434 |

- Narrative text lifts PR-AUC to about 6–7× the base rate. Company identity adds the most beyond text,
  because relief rates differ sharply by company (about 0% at the credit bureaus, 35% at American Express).

### Dimensionality reduction and clustering

- Truncated SVD (LSA) compresses 100k TF-IDF features well but not losslessly: a linear SVM keeps
  88% of its full-TF-IDF macro-F1 with 100 components, 94% with 300 and 96% with 500 (0.749 vs 0.782).
  This explains why the nonlinear models trained on SVD-300 trail the sparse linear models.
- K-means (k = 25) on L2-normalized SVD-100 features finds coherent complaint themes such as
  credit-report disputes, debt-validation demands, unauthorized transactions, merchant refunds, gift
  cards, and two clusters made almost entirely of the January 2025 Cash App and Zelle template
  campaigns. Clusters follow issues as well as products (ARI 0.19, NMI 0.36 against product labels).
- Monetary relief rates differ strongly by theme: 33% for gift cards and 20% for merchant disputes,
  versus under 1% for credit reporting, debt collection and template campaigns.

## Repository layout

```
app/                 Streamlit demo
data/raw/            downloaded CFPB data (gitignored)
data/processed/      modeling dataset (gitignored)
figures/             saved plots
models/              trained pipelines (gitignored)
notebooks/           analysis and modeling notebooks
results/metrics/     per-model test metrics (JSON)
```
