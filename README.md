# Personal Astrology Web App (OpenRouter + PDF Export)

This Streamlit app computes basic astrological information (Thai / Chinese / Western),
queries **OpenRouter API** for AI-based interpretation, and exports a PDF report.

## 🔧 Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Get a free API key from [OpenRouter.ai](https://openrouter.ai/docs/api-reference/authentication)

3. Set your API key as environment variable (or in Streamlit Cloud secrets):
   ```bash
   export OPENROUTER_API_KEY="sk-xxxx"
   ```

4. Run the app locally:
   ```bash
   streamlit run personal_astrology_webapp.py
   ```

## ☁️ Deploy to Streamlit Cloud
1. Push this project to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app → select your repo
4. In **Settings → Secrets**, add:
   ```
   OPENROUTER_API_KEY = "sk-xxxx"
   ```
5. Deploy and open the app!

## 📜 License
MIT License — Free to modify and deploy.
