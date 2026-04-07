
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import cv2
import numpy as np
import pandas as pd
import mediapipe as mp
from datetime import datetime
import folium
import streamlit as st
import sqlite3
import speech_recognition as sr
from fpdf import FPDF
from gtts import gTTS
from streamlit_folium import st_folium

st.set_page_config(page_title="ReubenSoul4peaceunity", page_icon="💪", layout="wide")

st.markdown("""
<style>
:root {
    --bg1: #07111f;
    --bg2: #0d2233;
    --bg3: #102f46;
    --accent1: #00d2a8;
    --accent2: #7cdbff;
    --accent3: #a78bfa;
    --text: #f5f7fb;
}

html, body, [class*="css"] {
    background: radial-gradient(circle at top, var(--bg3), var(--bg2) 45%, var(--bg1));
    color: var(--text);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.hero {
    padding: 28px 24px;
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(0,210,168,0.16), rgba(124,219,255,0.10), rgba(167,139,250,0.12));
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 20px 60px rgba(0,0,0,0.28);
}

.big-title {
    font-size: clamp(2.2rem, 5vw, 4.3rem);
    text-align: center;
    font-weight: 900;
    background: linear-gradient(90deg, var(--accent1), var(--accent2), var(--accent3));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 28px rgba(0,210,168,0.22);
    margin-bottom: 0.25rem;
}

.sub-title {
    text-align: center;
    font-size: 1.05rem;
    color: rgba(245,247,251,0.82);
    margin-bottom: 0.75rem;
}

.badges {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 16px;
}
.badge {
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    color: #fff;
    font-size: 0.92rem;
}

.stButton>button, .stDownloadButton>button {
    background: linear-gradient(90deg, var(--accent1), #0080ff) !important;
    color: white !important;
    border-radius: 14px !important;
    height: 3.2em !important;
    width: 100% !important;
    border: 0 !important;
    font-weight: 800 !important;
    box-shadow: 0 10px 28px rgba(0, 210, 168, 0.25) !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
}

.card {
    padding: 18px 18px;
    border-radius: 18px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0 14px 34px rgba(0,0,0,0.22);
}

.promo {
    padding: 22px;
    border-radius: 22px;
    background: linear-gradient(135deg, rgba(0,210,168,0.15), rgba(0,128,255,0.16));
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 16px 42px rgba(0,0,0,0.22);
    text-align: center;
}

.promo-link {
    display: inline-block;
    margin-top: 14px;
    padding: 13px 22px;
    border-radius: 999px;
    text-decoration: none;
    font-weight: 800;
    color: white !important;
    background: linear-gradient(90deg, #00d2a8, #0080ff);
    box-shadow: 0 8px 24px rgba(0, 210, 168, 0.30);
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="big-title">🌍 ReubenSoul Peace Unity4 GREAT Health</div>
  <div class="sub-title">Building Health, Peace, and Unity Through Technology</div>
  <div class="badges">
    <div class="badge">💪 Fitness</div>
    <div class="badge">📍 GPS</div>
    <div class="badge">🏥 Care Portal</div>
    <div class="badge">🔐 Secure Records</div>
    <div class="badge">🎙️ Voice Support</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.title("🌍 ReubenSoul4peaceunity")
st.markdown(
    """
    ### Welcome to Your Health & Safety Platform
    Track fitness, manage care records, and share a polished client portal experience in one beautiful app.
    """
)
st.info("🔒 Your data is stored locally in the app database unless you deploy it with your own backend.")

if "reps" not in st.session_state:
    st.session_state.reps = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.now()

menu = st.sidebar.selectbox("Navigation", ["🏋️ Fitness Training", "🏥 Care Portal", "✨ Client Portal"])

if menu == "🏋️ Fitness Training":
    st.markdown('<div class="card"><div style="font-size:2rem;text-align:center;color:#00d2a8;font-weight:900;">💪 ReubenSoul4peaceunity</div><div style="text-align:center;color:#c8d5e0;">Health • Strength • Peace • Unity</div></div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["🏃 Live Training", "📍 GPS", "📊 Analytics"])

    with tab1:
        st.header("Live Training")
        img = st.camera_input("Capture Exercise")
        if img is not None:
            bytes_data = img.getvalue()
            nparr = np.frombuffer(bytes_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is not None:
                with mp.solutions.pose.Pose() as pose:
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = pose.process(rgb)
                    if results.pose_landmarks:
                        st.session_state.reps += 1
                        st.success("Rep counted!")
                    st.image(rgb, channels="RGB", use_container_width=True)
            else:
                st.error("Could not decode the camera image.")

        col1, col2, col3 = st.columns(3)
        col1.metric("Reps", st.session_state.reps)
        col2.metric("Calories", round(st.session_state.reps * 0.5, 2))
        col3.metric("Session Minutes", round((datetime.now() - st.session_state.start_time).seconds / 60, 1))

    with tab2:
        st.header("Location Tracking")
        lat = st.number_input("Latitude", value=34.05)
        lon = st.number_input("Longitude", value=-118.25)
        if st.button("Show Map"):
            m = folium.Map(location=[lat, lon], zoom_start=12, control_scale=True)
            folium.Marker([lat, lon], tooltip="Current Location").add_to(m)
            st_folium(m, width=700, height=500, returned_objects=[])

    with tab3:
        st.header("Analytics")
        df = pd.DataFrame({"Reps": [st.session_state.reps], "Calories": [st.session_state.reps * 0.5]})
        st.bar_chart(df)
        st.dataframe(df, use_container_width=True)

elif menu == "🏥 Care Portal":
    class ElderlyCarePortal:
        def __init__(self):
            self.db_name = "care_center.db"
            self.recognizer = sr.Recognizer()
            self.init_db()

        def init_db(self):
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS residents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    dob TEXT,
                    medical_info TEXT,
                    medications TEXT,
                    allergies TEXT,
                    emergency_contact TEXT,
                    language TEXT
                )
            """)
            conn.commit()
            conn.close()

        def speak(self, text, lang="en"):
            try:
                filename = "temp_voice.mp3"
                gTTS(text=text, lang=lang).save(filename)
                if os.name == "nt":
                    os.system(f'start "" "{filename}"')
                else:
                    os.system(f'xdg-open "{filename}" >/dev/null 2>&1 &')
            except Exception:
                pass

        def listen(self, lang_code, key_suffix=""):
            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source, timeout=5)
                    return self.recognizer.recognize_google(audio, language=lang_code)
            except Exception:
                return st.text_input(f"🎤 Voice not available. Type here instead: {key_suffix}", key=f"text_{key_suffix}")

        def add_resident_session(self):
            st.header("🆕 New Admission / Nueva Admisión")
            lang_choice = st.selectbox("Select Language / Seleccione Idioma", ["English", "Spanish"])
            lang_code = "es-ES" if lang_choice == "Spanish" else "en-US"
            name = st.text_input("Resident Full Name / Nombre", key="name")
            dob = self.listen(lang_code, "dob")
            med_info = self.listen(lang_code, "med")
            medications = self.listen(lang_code, "meds")
            allergies = self.listen(lang_code, "allergies")
            contact = self.listen(lang_code, "contact")

            col1, col2 = st.columns(2)
            with col1:
                save_clicked = st.button("Save Resident")
            with col2:
                pdf_clicked = st.button("Generate PDF")

            if save_clicked:
                conn = sqlite3.connect(self.db_name)
                c = conn.cursor()
                c.execute("""
                    INSERT INTO residents
                    (name, dob, medical_info, medications, allergies, emergency_contact, language)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (name, dob, med_info, medications, allergies, contact, lang_code))
                conn.commit()
                conn.close()
                st.success(f"{name} saved successfully!")

            if pdf_clicked:
                self.export_pdf(name, dob, med_info, medications, allergies, contact)

        def search_records_session(self):
            st.header("🔍 Search Resident Records")
            query = st.text_input("Enter Resident Name / Ingrese Nombre")
            if st.button("Search"):
                conn = sqlite3.connect(self.db_name)
                c = conn.cursor()
                c.execute("SELECT * FROM residents WHERE name LIKE ?", ('%' + query + '%',))
                results = c.fetchall()
                conn.close()

                if results:
                    for r in results:
                        st.markdown(f'<div class="card">', unsafe_allow_html=True)
                        st.write(f"**ID:** {r[0]}")
                        st.write(f"**Name:** {r[1]} | **DOB:** {r[2]}")
                        st.write(f"**Medical:** {r[3]}")
                        st.write(f"**Medications:** {r[4]}")
                        st.write(f"**Allergies:** {r[5]}")
                        st.write(f"**Emergency Contact:** {r[6]}")
                        if st.button(f"Read summary aloud for {r[1]}", key=f"read_{r[0]}"):
                            summary = f"Resident {r[1]}. Conditions: {r[3]}. Medications: {r[4]}."
                            self.speak(summary, lang=(r[7] or "en")[:2])
                        st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.warning("No records found matching that name.")

        def export_pdf(self, name, dob, medical, meds, allergies, contact):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, txt="Elderly Care Admission Record", ln=True, align="C")
            pdf.set_font("Arial", size=12)
            fields = {
                "Name": name,
                "DOB": dob,
                "Medical Conditions": medical,
                "Medications": meds,
                "Allergies": allergies,
                "Emergency Contact": contact,
            }
            for key, value in fields.items():
                pdf.ln(8)
                pdf.multi_cell(0, 10, txt=f"{key}: {value}")
            safe_name = "".join(c for c in (name or "resident") if c.isalnum() or c in (" ", "_")).strip().replace(" ", "_")
            filename = f"{safe_name}_intake.pdf"
            pdf.output(filename)
            st.success(f"PDF exported: {filename}")

        def run_portal(self):
            portal_menu = st.sidebar.radio("Care Portal Menu", ["🆕 New Admission", "🔍 Search Records"])
            if portal_menu == "🆕 New Admission":
                self.add_resident_session()
            else:
                self.search_records_session()

    ElderlyCarePortal().run_portal()

else:
    st.markdown("""
    <div class="promo">
        <div style="font-size:1.6rem;font-weight:900;color:#eaf7ff;">✨ Client Portal</div>
        <div style="margin-top:8px;color:#d8e8f5;">A premium, polished experience for your customers.</div>
        <a class="promo-link" href="https://your-link-here.com" target="_blank">🚀 Open Secure Client Portal</a>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("<center><b>ReubenSoul4peaceunity</b><br>Building Health, Peace, and Unity Through Technology</center>", unsafe_allow_html=True)

