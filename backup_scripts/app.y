import streamlit as st
import cv2
import numpy as np
import pandas as pd
import mediapipe as mp
from datetime import datetime
import folium
from streamlit_folium import st_folium

# ✅ Import Elderly Care Portal
from elderly_portal import run_portal

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
# FITNESS APP
# ==============================
if menu == "🏋️ Fitness Training":
    st.markdown('<div class="main-header">💪 ReubenSoul4peaceunity</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Health • Strength • Peace • Unity</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "🏃 Live Training",
        "📍 GPS",
        "📊 Analytics"
    ])

    # ===== TAB 1: TRAINING =====
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

    # ===== TAB 2: GPS =====
    with tab2:
        st.header("Location Tracking")
        lat = st.number_input("Latitude", value=34.05)
        lon = st.number_input("Longitude", value=-118.25)
        if st.button("Show Map"):
            m = folium.Map(location=[lat, lon], zoom_start=12)
            folium.Marker([lat, lon]).add_to(m)
            st_folium(m)

    # ===== TAB 3: ANALYTICS =====
    with tab3:
        st.header("Analytics")
        data = {
            "Reps": [st.session_state.reps],
            "Calories": [st.session_state.reps * 0.5]
        }
        df = pd.DataFrame(data)
        st.bar_chart(df)

# ==============================
# CARE PORTAL
# ==============================
elif menu == "🏥 Care Portal":
    run_portal()

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
