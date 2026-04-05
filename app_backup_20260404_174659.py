#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==============================
# ReubenSoul4peaceunity App
# Combines Fitness Training + Elderly Care Portal
# ==============================

import os
import cv2
import numpy as np
import pandas as pd
import mediapipe as mp
from datetime import datetime
import folium
from streamlit_folium import st_folium
import streamlit as st
import sqlite3
import speech_recognition as sr
from fpdf import FPDF
from googletrans import Translator
from gtts import gTTS

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="ReubenSoul4peaceunity",
    page_icon="💪",
    layout="wide"
)

# ==============================
# CLEAN MODERN STYLE
# ==============================
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    font-weight: bold;
    color: #00C9A7;
    text-align: center;
}
.sub-header {
    text-align: center;
    color: #666;
}
.metric-card {
    background: linear-gradient(135deg, #00C9A7, #92FE9D);
    padding: 1rem;
    border-radius: 10px;
    color: black;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# SESSION STATE
# ==============================
if 'reps' not in st.session_state:
    st.session_state.reps = 0
if 'start_time' not in st.session_state:
    st.session_state.start_time = datetime.now()

# ==============================
# NAVIGATION
# ==============================
menu = st.sidebar.selectbox(
    "Navigation",
    ["🏋️ Fitness Training", "🏥 Care Portal"]
)

# ==============================
# FITNESS TRAINING MODULE
# ==============================
if menu == "🏋️ Fitness Training":

    st.markdown('<div class="main-header">💪 ReubenSoul4peaceunity</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Health • Strength • Peace • Unity</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "🏃 Live Training",
        "📍 GPS",
        "📊 Analytics"
    ])

    # --------------------------
    # TAB 1: LIVE TRAINING
    # --------------------------
    with tab1:
        st.header("Live Training")
        img = st.camera_input("Capture Exercise")
        if img:
            bytes_data = img.getvalue()
            nparr = np.frombuffer(bytes_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            mp_pose = mp.solutions.pose
            pose = mp_pose.Pose()

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)

            if results.pose_landmarks:
                st.session_state.reps += 1
                st.success("Rep counted!")

            st.image(rgb)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Reps", st.session_state.reps)
            with col2:
                calories = st.session_state.reps * 0.5
                st.metric("Calories", calories)

    # --------------------------
    # TAB 2: GPS
    # --------------------------
    with tab2:
        st.header("Location Tracking")
        lat = st.number_input("Latitude", value=34.05)
        lon = st.number_input("Longitude", value=-118.25)
        if st.button("Show Map"):
            m = folium.Map(location=[lat, lon], zoom_start=12)
            folium.Marker([lat, lon]).add_to(m)
            st_folium(m)

    # --------------------------
    # TAB 3: ANALYTICS
    # --------------------------
    with tab3:
        st.header("Analytics")
        data = {
            "Reps": [st.session_state.reps],
            "Calories": [st.session_state.reps * 0.5]
        }
        df = pd.DataFrame(data)
        st.bar_chart(df)

# ==============================
# ELDERLY CARE PORTAL MODULE
# ==============================
elif menu == "🏥 Care Portal":

    class ElderlyCarePortal:
        def __init__(self):
            self.db_name = "care_center.db"
            self.translator = Translator()
            self.recognizer = sr.Recognizer()
            self.init_db()

        def init_db(self):
            """Initializes SQLite database for persistent storage."""
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
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
            ''')
            conn.commit()
            conn.close()

        def speak(self, text, lang='en'):
            """Verbalizes text for the user."""
            try:
                tts = gTTS(text=text, lang=lang)
                tts.save("temp_voice.mp3")
                os.system("start temp_voice.mp3" if os.name == "nt" else "afplay temp_voice.mp3")
            except Exception as e:
                print(f"Audio Error: {e}")

        def listen(self, lang_code):
            """Captures voice input and transcribes it to text."""
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                print("Listening... / Escuchando...")
                try:
                    audio = self.recognizer.listen(source, timeout=7)
                    return self.recognizer.recognize_google(audio, language=lang_code)
                except:
                    print("Could not understand voice. Please type your answer.")
                    return input("Type answer: ")

        def add_resident_session(self):
            """Session to admit a new resident using voice or text."""
            st.header("🆕 New Admission / Nueva Admisión")
            lang_choice = st.selectbox("Select Language / Seleccione Idioma", ["English", "Spanish"])
            lang_code = 'es-ES' if lang_choice == 'Spanish' else 'en-US'

            name = st.text_input("Resident Full Name / Nombre")
            st.write("Speak Date of Birth (YYYY-MM-DD) / Diga la fecha de nacimiento:")
            dob = self.listen(lang_code)

            st.write("Speak Medical Conditions / Diga condiciones médicas:")
            med_info = self.listen(lang_code)
            st.write("Speak Medications / Diga medicamentos:")
            medications = self.listen(lang_code)
            st.write("Speak Allergies / Diga alergias:")
            allergies = self.listen(lang_code)
            st.write("Speak Emergency Contact / Diga contacto de emergencia:")
            contact = self.listen(lang_code)

            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO residents (name, dob, medical_info, medications, allergies, emergency_contact, language)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, dob, med_info, medications, allergies, contact, lang_code))
            conn.commit()
            conn.close()

            st.success(f"{name} saved successfully!")

            if st.button("Generate PDF"):
                self.export_pdf(name, dob, med_info, medications, allergies, contact)

        def search_records_session(self):
            """Session to search and verbally review existing records."""
            st.header("🔍 Search Resident Records")
            query = st.text_input("Enter Resident Name / Ingrese Nombre")
            if st.button("Search"):
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM residents WHERE name LIKE ?", ('%' + query + '%',))
                results = cursor.fetchall()
                conn.close()
                if results:
                    for r in results:
                        st.write(f"[ID: {r[0]}] Name: {r[1]} | DOB: {r[2]}")
                        st.write(f"Medical: {r[3]} | Medications: {r[4]} | Allergies: {r[5]}")
                        st.write(f"Emergency Contact: {r[6]}")
                        if st.button(f"Read summary aloud for {r[1]}"):
                            summary = f"Resident {r[1]}. Conditions: {r[3]}. Medications: {r[4]}."
                            self.speak(summary, lang=r[7][:2])
                else:
                    st.warning("No records found matching that name.")

        def export_pdf(self, name, dob, medical, meds, allergies, contact):
            """Generates a formal PDF document."""
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="Elderly Care Admission Record", ln=True, align='C')
            pdf.set_font("Arial", size=12)
            details = {
                "Name": name,
                "DOB": dob,
                "Medical Conditions": medical,
                "Medications": meds,
                "Allergies": allergies,
                "Emergency Contact": contact
            }
            for key, value in details.items():
                pdf.ln(8)
                pdf.multi_cell(0, 10, txt=f"{key}: {value}")
            filename = f"{name.replace(' ', '_')}_intake.pdf"
            pdf.output(filename)
            st.success(f"PDF exported: {filename}")

        def run_portal(self):
            st.sidebar.title("Care Portal Menu")
            portal_menu = st.sidebar.radio("Options", ["🆕 New Admission", "🔍 Search Records"])
            if portal_menu == "🆕 New Admission":
                self.add_resident_session()
            elif portal_menu == "🔍 Search Records":
                self.search_records_session()

    portal_app = ElderlyCarePortal()
    portal_app.run_portal()

# ==============================
# FOOTER
# ==============================
st.markdown("---")
st.markdown("""
<center>
<b>ReubenSoul4peaceunity</b><br>
Building Health, Peace, and Unity Through Technology
</center>
""", unsafe_allow_html=True)
