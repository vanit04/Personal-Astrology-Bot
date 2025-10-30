# Personal Astrology Web App - Pro (Thai UI, OpenRouter)

## คำอธิบาย (ภาษาไทย)
เวอร์ชัน Pro: ระบบทำนายดวงชะตาส่วนบุคคลแบบละเอียดโดยใช้ 3 ศาสตร์ (ไทย, จีน, สากล) และ AI (OpenRouter) เพื่อสร้างการวิเคราะห์เชิงเหตุผลและการทำนายรายเดือนตลอดปีที่ผู้ใช้เลือก

### การติดตั้ง
1. ติดตั้ง Python 3.8+ และ Git
2. แตกไฟล์โปรเจกต์
3. ติดตั้ง dependencies:
```
pip install -r requirements.txt
```

4. สมัครและรับ API Key จาก OpenRouter: https://openrouter.ai
5. ตั้งค่า environment variable (Linux/macOS):
```
export OPENROUTER_API_KEY="sk-xxxx"
```
หรือบน Windows (PowerShell):
```
setx OPENROUTER_API_KEY "sk-xxxx"
```

6. รันแอป:
```
streamlit run personal_astrology_webapp_pro.py
```

## README (English)
This Pro Streamlit app generates detailed personal astrology forecasts using Thai, Chinese, and Western astrology. The user specifies a Thai Buddhist year (พ.ศ.) to forecast. AI interpretation and synthesis is performed via OpenRouter (GPT-3.5). Output is in Thai and can be exported to PDF.
