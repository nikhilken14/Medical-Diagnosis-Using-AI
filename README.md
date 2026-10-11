# MediCareAI — website-style screening demo

A Streamlit frontend in light teal styling, a home page with five service cards, a four-step guide, a dark footer, and a dedicated screening workspace.

## Run locally (Python 3.11 or 3.12 recommended)

Extract the ZIP and open a terminal in the `medical-website` directory.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Then:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed in the terminal (normally http://localhost:8501).

## What's included

- `app.py`: home, screening, health info and about pages.
- `screenings.py`: feature contracts, model loading and prediction.
- `assets/style.css`: responsive website styling; no external image/font dependency.
- `.streamlit/config.toml`: light theme and app settings.
- `model/`, `datasets/`, `jupyter notebook/`: original project assets.
- `verify.py`: interaction checks for navigation, required fields, all five predictions and clearing.

Forms start empty. Use **Load sample data** for a labeled training-record demo. **Clear inputs** removes the current form values and result. Submit all fields to get a classification, inspect the submitted values, and download TXT or JSON summaries. No account or external API is required.

## Model compatibility and input fixes

The supplied pickles originate from multiple scikit-learn versions: 1.0.2, 1.2.2 and 1.5.2. They were smoke-tested here with scikit-learn 1.8.0 and every model successfully produced a prediction. Version warnings are expected; successful loading does not guarantee full compatibility or clinical correctness. For future production work, retrain and export all models with one pinned environment and retain fitted preprocessing alongside each estimator. The original models have not been retrained or silently rescaled.

Changes verified against the training notebooks and datasets:

- Lung survey inputs use **No = 1 / Yes = 2**, rather than the old UI's 0/1.
- Thyroid sex uses **Male = 0 / Female = 1**.
- Heart `thal` accepts dataset codes 0–3; the old UI used incorrect descriptions and omitted code 3. Major-vessel codes 0–4 are supported.
- Decimal precision is supported for BMI, pedigree, laboratory values and acoustic features.
- Named model features are passed in their original training order.

The saved diabetes and Parkinson's SVCs do not provide calibrated probabilities. No confidence percentage or unsupported accuracy claim is displayed. Numerical bounds are input controls, not medically validated normal ranges. Thyroid laboratory units are not documented in the source project, so no unit conversion is assumed.

## Limitations and privacy

This is an educational ML demonstration, not a clinical diagnosis, medical advice, or an all-clear. Models have not been clinically validated. Positive and negative classifications describe the model output only. The interface contains no simulated sign-in, invented users, contact details or treatment recommendations.

Inputs are sent to the Streamlit server and retained in the active session. The app does not write them to a database or local project files. Hosting infrastructure may have separate logging policies. Downloaded reports contain entered data. Do not use real patient data on a public demo without an appropriate privacy design.

Only the bundled trusted pickle files are loaded. Never replace them with untrusted pickles; deserialization can execute code.

## Validation

```bash
python verify.py
```

Validated here using Streamlit's AppTest: home and navigation rendered; all five forms rejected missing data; all five original models predicted using sample records; clearing removed inputs and results. This verifies application behavior, not diagnostic accuracy. CSS includes narrow-screen layout adjustments; exact browser rendering can vary.
