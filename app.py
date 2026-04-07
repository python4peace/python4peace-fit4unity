#!/usr/bin/env python3
# -*- coding: utf-8 -*-

### 1. Streamlit: Health, Fitness, Elderly Care
import os
import sqlite3
import cv2
import numpy as np
import pandas as pd
import mediapipe as mp
import folium
import streamlit as st
from folium.plugins import MeasureControl
from streamlit_folium import st_folium
import speech_recognition as sr
from fpdf import FPDF
from gtts import gTTS

### 2. Flask: Family SafeLink check‑in
import threading
from datetime import datetime
from flask import Flask, request, render_template_string, jsonify
from cryptography.fernet import Fernet

### 3. Shared state
FERNET_KEY_STR = os.environ.get("FERNET_KEY", "")
if not FERNET_KEY_STR:
    raise RuntimeError("Set FERNET_KEY in environment")
cipher_suite = Fernet(FERNET_KEY_STR.encode())

users_db = {
    "child_01": {
        "name": "Alex",
        "medical_encrypted": cipher_suite.encrypt(
            b"Allergic to Penicillin. Blood Type O+."
        ),
        "contact": "+15550199",
        "allowed": True,
    },
    "elder_01": {
        "name": "Grandma",
        "medical_encrypted": cipher_suite.encrypt(
            b"Diabetic. Insulin dependent."
        ),
        "contact": "+15550188",
        "allowed": True,
    },
}

# ---------------------------------------------------------
# 1. FAMILY SAFELINK FLASK SERVER (SafeCheck URLs)
# ---------------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>Family Safety Check‑In</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family:sans-serif; text-align:center; padding:20px; background:#f9f9f9; }
    button { display:block; width:100%; padding:16px; margin:10px 0;
             font-size:16px; border:none; border-radius:8px; cursor:pointer; }
    .safe { background:#28a745; color:white; }
    .help { background:#dc3545; color:white; }
    #status { margin-top:20px; color:#666; font-size:14px; }
  </style>
</head>
<body>
  <h2>Hi {{ name }}, are you safe?</h2>
  <p>This page will <b>only</b> share your location if you tap a button.</p>
  <button class="safe" onclick="shareLocation('safe')">Share my location</button>
  <button class="safe" onclick="sendUpdate('safe')">I'm OK</button>
  <button class="help" onclick="sendUpdate('emergency')">I need help</button>
  <p id="status">Waiting for action...</p>

  <script>
    function postData(status, lat, lon, accuracy) {
      const statusEl = document.getElementById("status");
      statusEl.innerText = "Sending...";
      fetch("/report/{{ user_id }}", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          status, lat, lon, accuracy,
          timestamp: new Date().toISOString()
        })
      }).then(r => r.json()).then(() => {
        statusEl.innerText = "Location shared.";
      }).catch(() => {
        statusEl.innerText = "Network error.";
      });
    }

    function shareLocation() {
      const status = document.getElementById("status");
      if (!navigator.geolocation) {
        status.innerText = "Location not supported.";
        return;
      }
      status.innerText = "Requesting permission...";
      navigator.geolocation.getCurrentPosition(
        pos => postData(
          "safe",
          pos.coords.latitude,
          pos.coords.longitude,
          pos.coords.accuracy
        ),
        () => status.innerText = "Location permission denied.",
        { enableHighAccuracy: true, timeout: 10000 }
      );
    }

    function sendUpdate(status) {
      const statusEl = document.getElementById("status");
      if (!navigator.geolocation) {
        postData(status, null, null, null);
        statusEl.innerText = "Status sent (no location).";
        return;
      }
      navigator.geolocation.getCurrentPosition(
        pos => postData(
          status,
          pos.coords.latitude,
          pos.coords.longitude,
          pos.coords.accuracy
        ),
        () => {
          postData(status, null, null, null);
          statusEl.innerText = "Status sent (no location).";
        },
        { enableHighAccuracy: true, timeout: 10000 }
      );
    }
  </script>
</body>
</html>
"""

SAFE_APP = Flask(__name__)


@SAFE_APP.route("/checkin/<user_id>")
def checkin(user_id):
    user = users_db.get(user_id)
    if not user or not user.get("allowed"):
        return "Invalid or disabled link", 404
    return render_template_string(HTML_TEMPLATE, name=user["name"], user_id=user_id)


@SAFE_APP.route("/report/<user_id>", methods=["POST"])
def report(user_id):
    user = users_db.get(user_id)
    if not user:
        return jsonify({"status": "error"}), 404

    data = request.get_json(force=True)
    lat = data.get("lat")
    lon = data.get("lon")
    status = data.get("status")

    if lat and lon:
        maps_link = f"https://www.google.com/maps?q={lat},{lon}"
    else:
        maps_link = None

    now = datetime.now().isoformat()
    print(f"[{now}] SafeLink {user['name']} | status={status} | maps={maps_link}")

    if status == "emergency":
        med_info = cipher_suite.decrypt(user["medical_encrypted"]).decode()
        print(f"[EMERGENCY] {user['name']} | MED: {med_info}")

    return jsonify({"status": "received", "maps": maps_link})


def run_flask():
    SAFE_APP.run(host="0.0.0.0", port=5000, debug=False)


# Start Flask in a background thread
threading.Thread(target=run_flask, daemon=True).start()

# ---------------------------------------------------------
# 2. STREAMLIT APP (Health, Fitness, Elderly Care)
# ---------------------------------------------------------
st.set_page_config(page_title="ReubenSoul4peaceunity", page_icon="💪", layout="wide")

st.title("🌍 ReubenSoul4peaceunity")
st.markdown(
    """
### Welcome to Your Health & Safety Platform
This system helps you:
✅ Track fitness and exercise  
✅ Monitor health progress  
✅ Manage care for loved ones  
✅ Store and review medical records safely
"""
)
st.info("🔒 Your data is stored securely and used only for health monitoring.")

if "reps" not in st.session_state:
    st.session_state.reps = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.now()

menu = st.sidebar.selectbox("Navigation", ["🏋️ Fitness Training", "🏥 Care Portal"])

# --- 2.1. FITNESS TRAINING MODULE ---
if menu == "🏋️ Fitness Training":
    st.markdown(
        '<div style="font-size:3rem;text-align:center;color:#00C9A7">💪 ReubenSoul4peaceunity</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="text-align:center;color:#666;">Health • Strength • Peace • Unity</div>',
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["🏃 Live Training", "📍 GPS", "📊 Analytics"])

    with tab1:
        st.header("Live Training")
        img = st.camera_input("Capture Exercise")
        if img is not None:
            bytes_data = img.getvalue()
            nparr = np.frombuffer(bytes_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is not None:
                mp_pose = mp.solutions.pose
                with mp_pose.Pose() as pose:
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = pose.process(rgb)
                    if results.pose_landmarks:
                        st.session_state.reps += 1
                        st.success("Rep counted!")
                    st.image(rgb, channels="RGB")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Reps", st.session_state.reps)
                    with col2:
                        st.metric("Calories", round(st.session_state.reps * 0.5, 1))

    with tab2:
        st.header("Location Tracking")
        lat = st.number_input("Latitude", value=34.05)
        lon = st.number_input("Longitude", value=-118.25)
        if st.button("Show Map"):
            m = folium.Map(location=[lat, lon], zoom_start=12, tiles="OpenStreetMap")
            folium.Marker([lat, lon]).add_child(folium.Tooltip("You are here")).add_to(m)
            MeasureControl().add_to(m)
            st_folium(m, width=700, height=500)

    with tab3:
        st.header("Analytics")
        df = pd.DataFrame(
            {"Reps": [st.session_state.reps], "Calories": [st.session_state.reps * 0.5]}
        )
        st.bar_chart(df)

# --- 2.2. ELDERLY CARE PORTAL ---
elif menu == "🏥 Care Portal":
    class ElderlyCarePortal:
        def __init__(self):
            self.db_name = "care_center.db"
            self.recognizer = sr.Recognizer()
            self.init_db()

        def init_db(self):
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute(
                """
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
                """
            )
            conn.commit()
            conn.close()

        def speak(self, text, lang="en"):
            try:
                tts = gTTS(text=text, lang=lang)
                filename = "temp_voice.mp3"
                tts.save(filename)
                if os.name == "nt":
                    os.system(f'start "" "{filename}"')
                else:
                    os.system(f'mpg321 "{filename}" >/dev/null 2>&1 &')
            except Exception as e:
                st.warning(f"Audio unavailable: {e}")

        def add_resident_session(self):
            st.header("🆕 New Admission / Nueva Admisión")
            lang_choice = st.selectbox("Select Language / Seleccione Idioma", ["English", "Spanish"])
            lang_code = "es-ES" if lang_choice == "Spanish" else "en-US"

            name = st.text_input("Resident Full Name / Nombre")
            dob = st.text_input("Date of Birth / Fecha de nacimiento")
            med_info = st.text_area("Medical Info / Información médica")
            medications = st.text_area("Medications / Medicamentos")
            allergies = st.text_area("Allergies / Alergias")
            contact = st.text_input("Emergency Contact / Contacto de emergencia")

            if st.button("Save Resident"):
                conn = sqlite3.connect(self.db_name)
                c = conn.cursor()
                c.execute(
                    """
                    INSERT INTO residents
                    (name, dob, medical_info, medications, allergies, emergency_contact, language)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (name, dob, med_info, medications, allergies, contact, lang_code),
                )
                conn.commit()
                conn.close()
                st.success(f"{name} saved successfully!")

                if st.button("Generate PDF"):
                    self.export_pdf(name, dob, med_info, medications, allergies, contact)

        def search_records_session(self):
            st.header("🔍 Search Resident Records")
            query = st.text_input("Enter Resident Name / Ingrese Nombre")
            if st.button("Search"):
                conn = sqlite3.connect(self.db_name)
                c = conn.cursor()
                c.execute("SELECT * FROM residents WHERE name LIKE ?", (f"%{query}%",))
                results = c.fetchall()
                conn.close()

                if results:
                    for r in results:
                        st.write(f"[ID:{r[0]}] Name: {r[1]} | DOB: {r[2]}")
                        st.write(f"Medical: {r[3]} | Medications: {r[4]} | Allergies: {r[5]}")
                        st.write(f"Emergency Contact: {r[6]}")
                        if st.button(f"Read summary aloud for {r[1]}", key=f"tts_{r[0]}"):
                            summary = f"Resident {r[1]}. Conditions: {r[3]}. Medications: {r[4]}."
                            self.speak(summary, lang="en" if r[7] == "en-US" else "es")
                else:
                    st.warning("No records found matching that name.")

        def export_pdf(self, name, dob, medical, meds, allergies, contact):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, txt="Elderly Care Admission Record", ln=True, align="C")
            pdf.set_font("Arial", size=12)
            for key, value in {
                "Name": name,
                "DOB": dob,
                "Medical Conditions": medical,
                "Medications": meds,
                "Allergies": allergies,
                "Emergency Contact": contact,
            }.items():
                pdf.ln(8)
                pdf.multi_cell(0, 10, txt=f"{key}: {value}")
            filename = f"{name.replace(' ', '_')}_intake.pdf"
            pdf.output(filename)
            st.success(f"PDF exported: {filename}")

        def run_portal(self):
            portal_menu = st.sidebar.radio("Care Portal Menu", ["🆕 New Admission", "🔍 Search Records"])
            if portal_menu == "🆕 New Admission":
                self.add_resident_session()
            else:
                self.search_records_session()

    ElderlyCarePortal().run_portal()

st.markdown("---")
st.markdown(
    "<center><b>ReubenSoul4peaceunity</b><br>Building Health, Peace, and Unity Through Technology</center>",
    unsafe_allow_html=True,
)
st.markdown(
    "<center>Flask check‑in URL example: <code>https://your-app.com/checkin/child_01</code></center>",
    unsafe_allow_html=True,
)
