# -*- coding: utf-8 -*-
"""Personal Astrology Web App - Pro
Features:
- Thai UI
- User specifies target year (พ.ศ.)
- AI (OpenRouter) generates
  * per-system analyses (Thai, Chinese, Western)
  * month-by-month forecasts for the whole year
  * synthesized annual summary combining the three systems
- PDF export
"""

import streamlit as st
import datetime, json, os, requests
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

try:
    import swisseph as swe
    HAS_SWISS = True
except Exception:
    HAS_SWISS = False

def to_julian_day(dt: datetime.datetime) -> float:
    utc = dt.astimezone(datetime.timezone.utc)
    y, m = utc.year, utc.month
    d = utc.day + utc.hour/24 + utc.minute/1440 + utc.second/86400
    if m <= 2:
        y -= 1
        m += 12
    A = y // 100
    B = 2 - A + (A // 4)
    return int(365.25*(y+4716)) + int(30.6001*(m+1)) + d + B - 1524.5

def calc_western_planets(jd):
    if not HAS_SWISS:
        return {"Sun": round(jd % 360, 2), "Note": "pyswisseph not installed"}
    swe.set_ephe_path('.')
    planets = ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto']
    result = {}
    for i, p in enumerate(planets):
        try:
            lon = swe.calc_ut(jd, i)[0][0]
        except Exception:
            lon = None
        result[p] = round(lon,2) if lon is not None else None
    return result

def chinese_zodiac(year: int):
    animals = ['หนู','วัว','เสือ','กระต่าย','มังกร','งู','ม้า','แพะ','ลิง','ไก่','สุนัข','หมู']
    elements = ['ไม้','ไฟ','ดิน','ทอง','น้ำ']
    elem = elements[((year - 4) % 10)//2]
    animal = animals[(year - 4) % 12]
    return f"{elem} {animal}"

def thai_lunar(day: int):
    tithi = ((day - 1) % 30) + 1
    phase = 'ข้างขึ้น' if tithi <= 15 else 'ข้างแรม'
    return {"ดิถี": tithi, "สถานะ": phase}

def ai_interpretation_openrouter(prompt: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "[AI Error] OPENROUTER_API_KEY ไม่ได้ตั้งค่า. กรุณาตั้ง environment หรือ Streamlit secrets."
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {"model":"openai/gpt-3.5-turbo", "messages":[{"role":"user","content":prompt}], "temperature":0.6, "max_tokens":1500}
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return content.strip()
    except Exception as e:
        return f"[AI Error] {e}"

def generate_pdf(name, birth_dt_str, lat, lon, zodiac, thai_info, western, target_year_p, ai_text):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    x_margin = 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(x_margin, height-50, f"รายงานดวงชะตาส่วนบุคคล: {name}")

    c.setFont("Helvetica", 11)
    c.drawString(x_margin, height-80, f"เกิด: {birth_dt_str}  (ละติจูด: {lat}, ลองจิจูด: {lon})")
    c.drawString(x_margin, height-100, f"ปี พ.ศ. ที่ทำนาย: {target_year_p}")
    c.drawString(x_margin, height-120, f"ปีนักษัตร: {zodiac}   |   ไทย (ดิถี): {thai_info}")

    c.drawString(x_margin, height-150, "ตำแหน่งดาว (approx):")
    y = height-170
    for k, v in western.items():
        line = f"{k}: {v}"
        c.drawString(x_margin+10, y, line[:100])
        y -= 14
        if y < 80:
            c.showPage()
            y = height-80

    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_margin, y-10, "คำทำนาย (AI):")
    text_obj = c.beginText(x_margin+10, y-30)
    text_obj.setFont("Helvetica", 11)
    for line in ai_text.split("\n"):
        text_obj.textLine(line)
        if text_obj.getY() < 50:
            c.drawText(text_obj)
            c.showPage()
            text_obj = c.beginText(x_margin+10, height-80)
            text_obj.setFont("Helvetica", 11)
    c.drawText(text_obj)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# Streamlit UI (Thai)
st.set_page_config(page_title="ระบบทำนายดวงชะตา (Pro)", layout="wide")
st.title("🔮 ระบบทำนายดวงชะตาเฉพาะบุคคล (Pro)")
st.markdown("ระบบวิเคราะห์ด้วย 3 ศาสตร์: ไทย, จีน, สากล — ทำนายแบบละเอียดรายเดือนและสรุปรายปี")

with st.form("form"):
    name = st.text_input("ชื่อ-นามสกุล", value="วณิช อิงคะวณิช")
    birth_date = st.date_input("วันเกิด", value=datetime.date(1973,1,7))
    birth_time = st.time_input("เวลาเกิด", value=datetime.time(6,11))
    lat = st.number_input("ละติจูด", value=13.752555, format="%.6f")
    lon = st.number_input("ลองจิจูด", value=100.494066, format="%.6f")
    target_year_p = st.number_input("ปี พ.ศ. ที่ต้องการทำนาย", min_value=2400, max_value=3000, value=2569)
    submitted = st.form_submit_button("วิเคราะห์และสร้างรายงาน PDF")

if submitted:
    target_year_ad = int(target_year_p) - 543
    tz = datetime.timezone(datetime.timedelta(hours=7))
    birth_dt = datetime.datetime.combine(birth_date, birth_time, tzinfo=tz)
    birth_dt_str = birth_dt.strftime("%Y-%m-%d %H:%M:%S %Z")
    jd = to_julian_day(birth_dt)
    western = calc_western_planets(jd)
    zodiac = chinese_zodiac(birth_date.year)
    thai_info = thai_lunar(birth_date.day)

    # Build detailed prompt asking per-system analysis + monthly forecasts
    prompt = f"""
คุณเป็นหมอดูผู้เชี่ยวชาญ 3 ระบบ:
1. โหราศาสตร์ไทย (ดวงดาว, ราหู–เกตุ, ดิถี, เดือนจันทรคติ)
2. โหราศาสตร์จีน (ปีนักษัตร, ธาตุ, ฮวงจุ้ย, ปีชง, ดวง 4 เสา)
3. โหราศาสตร์สากล (Western Astrology: Sun/Moon/Ascendant, Transits)

ข้อมูลพื้นดวง:
- ชื่อ: {name}
- วันเกิด: {birth_date} เวลา {birth_time} (เขตเวลา UTC+7)
- พิกัด: {lat}, {lon}
- ปี พ.ศ. ที่ต้องการทำนาย: {target_year_p} (ค.ศ. {target_year_ad})

จงทำนายอย่างละเอียดโดย:
1. วิเคราะห์พื้นดวงของแต่ละศาสตร์แยกกัน (ไทย, จีน, สากล)
2. ทำนายทุกเดือน (มกราคม–ธันวาคม {target_year_p})
   - ระบุเหตุการณ์เด่น
   - วิเคราะห์ด้านการงาน การเงิน ความรัก สุขภาพ และโชคลาภ
   - ให้คำแนะนำเฉพาะเดือนนั้น
3. สรุปผลรวมจากทั้ง 3 ศาสตร์:
   - จุดที่ตรงกันและต่างกัน
   - แนวโน้มชีวิตโดยรวม
   - คำแนะนำเสริมดวงแบบรวมศาสตร์

เขียนผลทำนายเป็นภาษาไทยทั้งหมด
ใช้ภาษาชัดเจน อ่านง่าย มีหัวข้อและจัดรูปแบบสวยงาม
"""

    st.subheader("🔭 ข้อมูลที่คำนวณได้ (สรุป)")
    st.json({"Western": western, "Chinese": zodiac, "Thai": thai_info, "ปี พ.ศ. ที่ทำนาย": target_year_p})

    st.subheader("🤖 กำลังส่งคำขอไปยัง OpenRouter เพื่อสร้างคำทำนาย (โปรดรอ)")
    with st.spinner("กำลังสร้างคำทำนายด้วย AI..."):
        ai_text = ai_interpretation_openrouter(prompt)

    st.subheader("📜 ผลการทำนาย (AI)")
    st.write(ai_text)

    pdf_buf = generate_pdf(name, birth_dt_str, lat, lon, zodiac, thai_info, western, target_year_p, ai_text)
    st.download_button("📄 ดาวน์โหลดรายงาน PDF (ภาษาไทย)", data=pdf_buf, file_name=f"ดวง_{name.replace(' ','_')}_{target_year_p}.pdf", mime="application/pdf")
