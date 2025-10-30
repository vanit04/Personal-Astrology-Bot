# Personal Astrology Web App (Thai + OpenRouter)

## คำอธิบาย (ภาษาไทย)
ระบบเว็บแอปสำหรับทำนายดวงชะตาเฉพาะบุคคล โดยผสมหลักโหราศาสตร์ไทย จีน และสากล ผู้ใช้สามารถระบุปี พ.ศ. ที่ต้องการทำนายได้ ผลลัพธ์แสดงเป็นภาษาไทยและสามารถดาวน์โหลดเป็น PDF ได้

### การติดตั้ง
1. ติดตั้ง Python 3.8+ และ Git
2. แตกไฟล์โปรเจกต์
3. ติดตั้ง dependencies:
```bash
pip install -r requirements.txt
```

4. สมัครและรับ API Key จาก OpenRouter: https://openrouter.ai
5. ตั้งค่า environment variable (Linux/macOS):
```bash
export OPENROUTER_API_KEY="sk-xxxx"
```
หรือบน Windows (PowerShell):
```powershell
setx OPENROUTER_API_KEY "sk-xxxx"
```

6. รันแอป:
```bash
streamlit run personal_astrology_webapp.py
```

## README (English)
This Streamlit web app predicts personal astrology by combining Thai, Chinese (BaZi-like), and Western astrology. The user can input a Thai Buddhist year (พ.ศ.) to predict for. AI interpretation is performed via OpenRouter (GPT-3.5). Output is in Thai with PDF export.

### Install
1. Install Python 3.8+ and Git
2. Unzip project
3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Get OpenRouter API key: https://openrouter.ai
5. Set environment variable:
```bash
export OPENROUTER_API_KEY="sk-xxxx"
```

6. Run:
```bash
streamlit run personal_astrology_webapp.py
```

---
