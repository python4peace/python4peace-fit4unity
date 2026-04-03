import streamlit as st
import sqlite3
import os
from fpdf import FPDF
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS

def run_portal():
    st.header("🏥 Elderly Care Portal")
    st.write("Bilingual voice/text admissions and resident record management.")

    portal = ElderlyCarePortal()

    menu = st.radio(
        "Select Option",
        ["🆕 New Admission", "🔍 Search Records"]
    )

    if menu == "🆕 New Admission":
        portal.add_resident_session()
    elif menu == "🔍 Search Records":
        portal.search_records_session()


class ElderlyCarePortal:
    def __init__(self):
        self.db_name = "care_center.db"
        self.translator = Translator()
        self.recognizer = sr.Recognizer()
        self.init_db()

    def init_db(self):
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
        try:
            tts = gTTS(text=text, lang=lang)
            tts.save("temp_voice.mp3")
            os.system("start temp_voice.mp3" if os.name == "nt" else "afplay temp_voice.mp3")
        except Exception as e:
            st.error(f"Audio Error: {e}")

    def listen(self, lang_code):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            st.info("Listening... / Escuchando...")
            try:
                audio = self.recognizer.listen(source, timeout=7)
                return self.recognizer.recognize_google(audio, language=lang_code)
            except:
                st.warning("Could not understand voice. Please type your answer.")
                return st.text_input("Type answer:")

    def add_resident_session(self):
        st.subheader("🆕 New Admission / Nueva Admisión")
        lang_choice = st.selectbox("Select Language / Seleccione idioma", ["English", "Spanish"])
        lang_code = 'es-ES' if lang_choice == 'Spanish' else 'en-US'

        name = st.text_input("Resident Full Name / Nombre")
        dob = st.text_input("Date of Birth (YYYY-MM-DD) / Fecha de nacimiento")
        med_info = st.text_area("Medical Conditions / Condiciones médicas")
        medications = st.text_area("Medications / Medicamentos")
        allergies = st.text_area("Allergies / Alergias")
        contact = st.text_input("Emergency Contact / Contacto de emergencia")

        if st.button("Save Resident / Guardar"):
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO residents (name, dob, medical_info, medications, allergies, emergency_contact, language)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, dob, med_info, medications, allergies, contact, lang_code))
            conn.commit()
            conn.close()
            st.success(f"{name} saved successfully!")

            if st.checkbox("Generate PDF / Generar PDF"):
                self.export_pdf(name, dob, med_info, medications, allergies, contact)

    def search_records_session(self):
        st.subheader("🔍 Search Resident Records")
        query = st.text_input("Enter Resident Name / Ingrese nombre del residente")
        if st.button("Search / Buscar"):
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM residents WHERE name LIKE ?", ('%' + query + '%',))
            results = cursor.fetchall()
            conn.close()
            if results:
                for r in results:
                    st.write(f"**ID:** {r[0]} | **Name:** {r[1]} | **DOB:** {r[2]}")
                    st.write(f"Medical: {r[3]} | Meds: {r[4]} | Allergies: {r[5]}")
                    st.write(f"Contact: {r[6]}")
                    if st.checkbox(f"Read summary aloud / Leer resumen: {r[1]}"):
                        summary = f"Resident {r[1]}. Conditions: {r[3]}. Medications: {r[4]}."
                        self.speak(summary, lang=r[7][:2])
            else:
                st.warning("No records found matching that name / No se encontraron registros.")

    def export_pdf(self, name, dob, medical, meds, allergies, contact):
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
