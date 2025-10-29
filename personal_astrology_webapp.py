"""Personal Astrology Web App (OpenRouter + PDF Export)
Streamlit app that computes basic Western/Chinese/Thai astrological cues,
asks OpenRouter API for interpretation, and exports PDF.
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
    animals = ['Rat','Ox','Tiger','Rabbit','Dragon','Snake','Horse','Goat','Monkey','Rooster','Dog','Pig']
    elements = ['Wood','Fire','Earth','Metal','Water']
    elem = elements[((year - 4) % 10)//2]
    animal = animals[(year - 4) % 12]
    return f"{elem} {animal}"


def thai_lunar(day: int):
    tithi = ((day - 1) % 30) + 1
    phase = 'Waxing' if tithi <= 15 else 'Waning'
    return {"tithi": tithi, "phase": phase}


def ai_interpretation(prompt: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "[AI Error] OPENROUTER_API_KEY not set. Please set in environment or Streamlit secrets."

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 500
    }
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return content.strip()
    except Exception as e:
        return f"[AI Error] {e}"


def generate_pdf(name, dt, lat, lon, western, zodiac, thai, ai_text):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height-50, f"Astrological Report for {name}")

    c.setFont("Helvetica", 11)
    c.drawString(50, height-80, f"Born: {dt}  (Lat: {lat}, Lon: {lon})")

    c.drawString(50, height-110, f"Chinese Zodiac: {zodiac}")
    c.drawString(50, height-130, f"Thai Lunar: {thai}")

    c.drawString(50, height-160, "Western Planets:")
    y = height-180
    for k, v in western.items():
        line = f"{k}: {v}"
        c.drawString(60, y, line[:90])
        y -= 14
        if y < 80:
            c.showPage()
            y = height-80

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y-10, "AI Interpretation:")
    text_obj = c.beginText(60, y-30)
    text_obj.setFont("Helvetica", 11)
    for line in ai_text.split("\\n"):
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


def main():
    st.set_page_config(page_title="Personal Astrology Web App", layout="wide")
    st.title("🔮 Personal Astrology Web App (OpenRouter + PDF Export)")
    st.markdown("Analyze your birth chart (Thai / Chinese / Western) and get AI-assisted interpretation via OpenRouter API.")

    with st.form("birth_form"):
        name = st.text_input("Name", value="วณิช อิงคะวณิช")
        birth_date = st.date_input("Birth Date", value=datetime.date(1973,1,7))
        birth_time = st.time_input("Birth Time", value=datetime.time(6,11))
        lat = st.number_input("Latitude", value=13.752555, format="%.6f")
        lon = st.number_input("Longitude", value=100.494066, format="%.6f")
        submitted = st.form_submit_button("Analyze & Generate Report")

    if submitted:
        tz = datetime.timezone(datetime.timedelta(hours=7))
        dt = datetime.datetime.combine(birth_date, birth_time, tzinfo=tz)
        jd = to_julian_day(dt)

        western = calc_western_planets(jd)
        zodiac = chinese_zodiac(birth_date.year)
        thai = thai_lunar(birth_date.day)

        summary = (
            f"Name: {name}\\nBorn: {dt}\\nLat/Lon: {lat},{lon}\\n"
            f"Western: {json.dumps(western)}\\nChinese: {zodiac}\\nThai: {thai}\\n"
            "Please summarize key personality traits, strengths, weaknesses, and provide a concise outlook for years 2025 and 2026."
        )

        st.subheader("🔭 Computed Astrological Data")
        st.json({"Western": western, "Chinese": zodiac, "Thai": thai})

        st.subheader("🤖 AI Interpretation (OpenRouter)")
        with st.spinner("Generating interpretation via OpenRouter..."):
            ai_text = ai_interpretation(summary)
        st.write(ai_text or "No interpretation generated.")

        pdf_buf = generate_pdf(name, dt, lat, lon, western, zodiac, thai, ai_text)
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_buf,
            file_name=f"Astrology_Report_{name.replace(' ','_')}.pdf",
            mime="application/pdf"
        )


if __name__ == '__main__':
    main()
