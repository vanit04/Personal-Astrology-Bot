# -----------------------------------------------
# README.md
# -----------------------------------------------


# 🔮 Personal Astrology Web App (Thai + Chinese + Western + AI)


A full-featured astrology web application that analyzes personal birth charts using Thai, Chinese, and Western astrology systems. It integrates a free AI model (Flan‑T5) to generate interpretations and allows users to export results as PDF reports.


---


## 🌟 Features
- Streamlit web-based GUI
- Hybrid astrology system (Thai, Chinese, Western)
- AI-assisted interpretations (via Hugging Face API)
- PDF report export
- Ready for Streamlit Cloud deployment


---


## 🧩 Installation
```bash
pip install -r requirements.txt
```


## 🚀 Run locally
```bash
streamlit run personal_astrology_webapp.py
```


After running, open:
- Local: http://localhost:8501
- Network (LAN): http://<your-ip>:8501


---


## ☁️ Deploy on Streamlit Cloud


### 1. Create a GitHub repository
Upload these files to your repository:
```
personal_astrology_webapp.py
requirements.txt
README.md
```


### 2. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
- Log in with your GitHub account.
- Click **“New app”** → Select your repo → Choose `personal_astrology_webapp.py` → **Deploy.**


### 3. Done!
You’ll get a permanent public link such as:
```
https://your-app-name.streamlit.app
```


---


## 📦 Optional: Run via Windows Batch
Create a file named `run_astrology_bot.bat` in the same folder:
```bat
@echo off
echo Launching Personal Astrology Web App...
python -m streamlit run personal_astrology_webapp.py
pause
```


Double‑click it to open the app instantly.


---


## 📘 Notes
- Free AI model: Google Flan‑T5 via HuggingFace Inference API.
- For advanced accuracy, consider installing local astrology data libraries or planetary ephemerides.


---


**Author:** ChatGPT (OpenAI)
**License:** MIT
