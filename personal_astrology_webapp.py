# -*- coding: utf-8 -*-
"""Personal Astrology Web App (ภาษาไทย) - OpenRouter + PDF Export
รองรับการระบุปี พ.ศ. ที่ต้องการทำนาย และแสดงผลเป็นภาษาไทย
"""

import streamlit as st
import datetime
import json
import os
import requests
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
        return {"Sun": jd % 360, "Note": "pyswisseph not installed"}
    swe.set_ephe_path('.')
    planets = ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto']
    result = {}
    for i, p in enumerate(planets):
        try:
            lon = swe.calc_ut(jd, i)[0][0]
        except Exception:
            lon = None
        result[p] = lon
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


def ai_interpretation(prompt: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "[AI Error] OPENROUTER_API_KEY ไม่ได้ตั้งค่า. กรุณาตั้งใน environment หรือ Streamlit secrets."

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 800
    }
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return content.strip()
    except Exception as e:
        return f"[AI Error] {e}"


def generate_pdf(name, dt, lat, lon, western, zodiac, thai, target_year_p, ai_text):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height-50, f"รายงานดวงชะตาส่วนบุคคล สำหรับ {name}")

    c.setFont("Helvetica", 11)
    c.drawString(50, height-80, f"เกิด: {dt}  (ละติจูด: {lat}, ลองจิจูด: {lon})")
    c.drawString(50, height-100, f"ปี พ.ศ. ที่ทำนาย: {target_year_p}")

    c.drawString(50, height-130, f"ปีนักษัตร: {zodiac}")
    c.drawString(50, height-150, f"ไทย (ดิถี): {thai}")

    c.drawString(50, height-180, "ตำแหน่งดาว (approx):")
    y = height-200
    for k, v in western.items():
        line = f"{k}: {v}"
        c.drawString(60, y, line[:100])
        y -= 14
        if y < 80:
            c.showPage()
            y = height-80

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y-10, "การตีความจาก AI:")
    text_obj = c.beginText(60, y-30)
    text_obj.setFont("Helvetica", 11)
    for line in ai_text.split("\n"):
        text_obj.textLine(line)
        if text_obj.getY() < 50:
            c.drawText(text_obj)
            c.showPage()
            text_obj = c.beginText(60, height-80)
            text_obj.setFont("Helvetica", 11)
    c.drawText(text_obj)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


st.set_page_config(page_title="ระบบทำนายดวงส่วนบุคคล", layout="wide")
st.title("🔮 ระบบทำนายดวงส่วนบุคคล (ไทย + จีน + สากล)")
st.markdown("กรุณากรอกข้อมูลพื้นดวง และเลือกปี พ.ศ. ที่ต้องการให้ทำนาย (เช่น 2569)")

with st.form("birth_form"):
    name = st.text_input("ชื่อ-นามสกุล", value="วณิช อิงคะวณิช")
    birth_date = st.date_input("วันเกิด", value=datetime.date(1973,1,7))
    birth_time = st.time_input("เวลาเกิด (ชั่วโมง:นาที)", value=datetime.time(6,11))
    lat = st.number_input("ละติจูด", value=13.752555, format="%.6f")
    lon = st.number_input("ลองจิจูด", value=100.494066, format="%.6f")
    target_year_p = st.number_input("ปี พ.ศ. ที่ต้องการทำนาย", min_value=2400, max_value=3000, value=2569)
    submitted = st.form_submit_button("วิเคราะห์และสร้างรายงาน PDF")

if submitted:
    # Convert พ.ศ. to ค.ศ.
    target_year_ad = int(target_year_p) - 543
    tz = datetime.timezone(datetime.timedelta(hours=7))
    dt = datetime.datetime.combine(birth_date, birth_time, tzinfo=tz)
    jd = to_julian_day(dt)

    western = calc_western_planets(jd)
    zodiac = chinese_zodiac(birth_date.year)
    thai = thai_lunar(birth_date.day)

    # Build Thai prompt for AI with target พ.ศ.
    prompt = f\"\"\"คุณเป็นหมอดูที่ใช้หลักโหราศาสตร์ไทย จีน และสากล ให้ทำนายโดยใช้ข้อมูลต่อไปนี้ (ภาษาไทย):
- ชื่อ: {name}
- เกิด: {birth_date} เวลา {birth_time} (Bangkok, UTC+7)
- ละติจูด/ลองจิจูด: {lat}, {lon}
- ปี พ.ศ. ที่ต้องการทำนาย: {target_year_p} (คือ ค.ศ. {target_year_ad})
- ข้อมูลพื้นดวงโดยย่อ: ปีนักษัตร: {zodiac} ; ไทย: {thai} ; ตำแหน่งดาวโดยคร่าว: {western}

โปรดให้ผลทำนายดังนี้ (เรียงเป็นหัวข้อ):
1) สรุปภาพรวมของปี {target_year_p}
2) การงาน การเงิน ความรัก สุขภาพ และโชคลาภ
3) เหตุการณ์สำคัญรายเดือน (ถ้าเป็นไปได้ ให้แยกรายเดือน)
4) คำแนะนำในการรับมือ / เสริมดวง (แบบที่สามารถทำได้จริง)
ตอบเป็นภาษาไทย ใช้น้ำเสียงเป็นทางการและให้คำแนะนำที่ชัดเจนและเป็นประโยชน์
\"\"\"

    st.subheader("🔭 ข้อมูลที่คำนวณได้")
    st.json({"Western": western, "Chinese": zodiac, "Thai": thai, "ปี พ.ศ. ที่ทำนาย": target_year_p})

    st.subheader("🤖 ผลการตีความโดย AI (OpenRouter)")
    with st.spinner("กำลังติดต่อ OpenRouter เพื่อสร้างคำทำนาย..."):
        ai_text = ai_interpretation(prompt)
    st.write(ai_text or "ไม่มีการตีความจาก AI")

    pdf_buf = generate_pdf(name, dt, lat, lon, western, zodiac, thai, target_year_p, ai_text)
    st.download_button(
        label="📄 ดาวน์โหลดรายงาน PDF (ภาษาไทย)" ,
        data=pdf_buf,
        file_name=f"รายงานดวง_{name.replace(' ','_')}_{target_year_p}.pdf",
        mime="application/pdf"
    )
