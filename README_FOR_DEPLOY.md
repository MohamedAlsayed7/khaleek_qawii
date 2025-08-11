# Khaleek Qawi — Streamlit demo (English UI)

This package contains a simple Streamlit app (app.py) and sample data for quick testing
and deployment to Streamlit Cloud (share.streamlit.io).

## Run locally
1. Create a Python virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate    # macOS / Linux
   venv\\Scripts\\activate     # Windows (PowerShell / CMD)
   ```
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```
4. Open the local URL printed by Streamlit (usually http://localhost:8501).

## Deploy to Streamlit Cloud
1. Push this repository to GitHub.
2. Go to https://share.streamlit.io/ and log in with GitHub.
3. Click **New app**, select your repo and branch.
4. Set **Main file path** to `app.py` and deploy.
