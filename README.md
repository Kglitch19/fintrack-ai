# FinTrack — Personal Finance Tracker with AI Insights

A full-stack web application that helps users take control of their finances by logging transactions, visualising spending patterns, and leveraging a machine learning model to automatically categorise expenses.

---

## The Problem

Most people have no clear picture of where their money goes. FinTrack solves this by giving users a single place to log income and expenses, see meaningful summaries, and get AI-driven insight into their biggest spending categories — without relying on any third-party chart libraries.

---

## Features

- **User authentication** — Secure signup and login with password hashing and validation rules
- **Transaction management** — Add, edit, and delete income and expense records
- **Custom data visualisations** — Charts and summaries built from scratch (no Chart.js or external libraries)
- **AI-powered categorisation** — A Naive Bayes classifier predicts the category of a transaction from its description, then surfaces the user's highest expense category on the analysis page
- **Profile management** — Optional profile picture upload, stored per user

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript (custom charts) |
| Backend | Python 3, Flask, Jinja2 |
| Database | SQLite |
| Machine Learning | scikit-learn (Naive Bayes + CountVectorizer) |
| Data processing | pandas |

---

## How It Works — The ML Pipeline

1. Transaction descriptions (e.g. *"Uber ride"*, *"Netflix subscription"*) are vectorised using `CountVectorizer`
2. A Naive Bayes classifier trained on labelled financial data predicts the expense category
3. The app aggregates predictions and highlights the user's top spending category on the analysis dashboard
4. The pre-trained model (`model.pkl`) is included — no training step required to run the app

---

## Getting Started

### Prerequisites
- Python 3.10+
- pip (bundled with Python)

### 1. Clone the repository
```bash
git clone https://github.com/Kglitch19/FinTrack.git
cd FinTrack
```

### 2. Create and activate a virtual environment

**Windows**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app

**Windows**
```powershell
python app/app.py
```

**macOS / Linux**
```bash
python3 app/app.py
```

### 5. Open in your browser
```
http://127.0.0.1:5000
```

> The SQLite database (`fintrack.db`) and pre-trained model (`model.pkl`) are included — no additional setup required.

---

## Project Structure

```
FinTrack/
├── app/
│   ├── static/          # CSS, JS, images
│   ├── templates/       # Jinja2 HTML templates
│   ├── app.py           # Main Flask application
│   ├── train_model.py   # ML training script
│   └── load_data.py     # Data loading utilities
├── data/
│   └── financial_data.csv
├── fintrack.db          # SQLite database
├── model.pkl            # Pre-trained Naive Bayes model
└── requirements.txt
```

---

## Known Limitations & Planned Improvements

- ML accuracy is constrained by training set size — expanding the dataset and adding rule-based filters for common terms (e.g. *"rent"*, *"salary"*) would improve classification
- Visualisations could be enhanced with interactivity such as filters and drill-down views
- Security improvements such as MFA and at-rest database encryption are planned for any future public deployment

---

## Notes

- This project was built for academic purposes
- Debug mode is enabled by default — disable before any production deployment
- Replace the placeholder `secret_key` in `app.py` with a strong value before deploying publicly
