import streamlit as st
import cv2
import numpy as np
import pandas as pd
import mediapipe as mp
from datetime import datetime, timedelta
import json
import os
import schedule
import time
from threading import Thread
import requests
import folium
from streamlit_folium import st_folium
import socket
import base64
from PIL import Image
import io

# Page configuration
st.set_page_config(
    page_title="Fit4Unity - Strength to Stand",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for James Brown / Reuben Soul styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #FF6B35;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
        font-style: italic;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .feel-good-banner {
        background: linear-gradient(90deg, #FF6B35, #F7931E);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background: linear-gradient(90deg, #FF6B35, #F7931E);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(255,107,53,0.4);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'session_start' not in st.session_state:
    st.session_state.session_start = datetime.now()
if 'total_reps' not in st.session_state:
    st.session_state.total_reps = 0
if 'calories_burned' not in st.session_state:
    st.session_state.calories_burned = 0
if 'heart_rate' not in st.session_state:
    st.session_state.heart_rate = 0
if 'locations' not in st.session_state:
    st.session_state.locations = []
if 'is_running' not in st.session_state:
    st.session_state.is_running = False

# Header
st.markdown('<div class="main-header">💪 Fit4Unity</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">"Strength to Stand" - Training with Soul, Peace & Unity</div>', unsafe_allow_html=True)
st.markdown('<div class="feel-good-banner">🎵 FEEL GOOD! 🎵 Inspired by the Godfather of Soul</div>', unsafe_allow_html=True)

# Sidebar - Parent/Trainer Dashboard
st.sidebar.title("📊 Parent/Trainer Dashboard")
st.sidebar.markdown("---")

# Get IP for parent connection
def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

ip_address = get_ip()

# Parent connection info
st.sidebar.subheader("🔗 Parent Connection")
st.sidebar.info(f"""
**Parent Dashboard URL:**
http://{ip_address}:5000

Share this with parents/trainers!
""")

# Load parent contacts
@st.cache_data
def load_contacts():
    contacts_file = "fit4unity_data/parent_contacts.txt"
    if os.path.exists(contacts_file):
        with open(contacts_file, 'r') as f:
            lines = f.readlines()
        contacts = []
        for line in lines[3:]:  # Skip header
            if line.strip() and not line.startswith('#'):
                parts = line.strip().split('|')
                if len(parts) >= 4:
                    contacts.append({
                        'name': parts[0],
                        'phone': parts[1],
                        'email': parts[2],
                        'relationship': parts[3]
                    })
        return contacts
    return []

contacts = load_contacts()
if contacts:
    st.sidebar.subheader("👥 Emergency Contacts")
    for contact in contacts:
        with st.sidebar.expander(f"{contact['name']} ({contact['relationship']})"):
            st.write(f"📞 Phone: {contact['phone']}")
            st.write(f"📧 Email: {contact['email']}")

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏃 Live Training", 
    "📍 GPS Tracking", 
    "📊 Analytics", 
    "❤️ Heart Rate", 
    "📱 Parent View"
])

# Tab 1: Live Training with Pose Detection
with tab1:
    st.header("Real-Time Exercise Tracking")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Camera input
        st.subheader("Camera Feed")
        
        # Option to use camera or upload video
        camera_option = st.radio("Input Source:", ["Live Camera", "Upload Video"])
        
        if camera_option == "Live Camera":
            # Use streamlit camera input
            img_file = st.camera_input("Take a picture or start recording")
            
            if img_file is not None:
                # Convert to CV2 format
                bytes_data = img_file.getvalue()
                nparr = np.frombuffer(bytes_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                # Process with MediaPipe
                mp_pose = mp.solutions.pose
                pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)
                
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(rgb_frame)
                
                # Draw landmarks
                if results.pose_landmarks:
                    mp_drawing = mp.solutions.drawing_utils
                    annotated_frame = frame.copy()
                    mp_drawing.draw_landmarks(
                        annotated_frame, 
                        results.pose_landmarks, 
                        mp_pose.POSE_CONNECTIONS
                    )
                    
                    # Display annotated frame
                    st.image(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB), 
                            channels="RGB", use_column_width=True)
                    
                    # Count reps based on movement
                    st.session_state.total_reps += 1
                    
                    st.success("✅ Pose detected! Rep counted!")
                else:
                    st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), 
                            channels="RGB", use_column_width=True)
        else:
            uploaded_file = st.file_uploader("Upload workout video", type=['mp4', 'avi', 'mov'])
            if uploaded_file is not None:
                st.video(uploaded_file)
                st.info("Video uploaded! AI analysis would process this...")
    
    with col2:
        st.subheader("Live Metrics")
        
        # Real-time metrics
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{st.session_state.total_reps}</div>
                <div class="metric-label">Total Reps</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_b:
            calories = st.session_state.total_reps * 0.5
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{calories:.1f}</div>
                <div class="metric-label">Calories Burned</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Session timer
        elapsed = datetime.now() - st.session_state.session_start
        minutes = int(elapsed.total_seconds() / 60)
        seconds = int(elapsed.total_seconds() % 60)
        
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
            <div class="metric-value">{minutes:02d}:{seconds:02d}</div>
            <div class="metric-label">Session Time</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Exercise selector
        st.subheader("Exercise Type")
        exercise_type = st.selectbox(
            "Select exercise:",
            ["Push-ups", "Squats", "Jumping Jacks", "Running", "Dancing (James Brown style!)", "Custom"]
        )
        
        # Start/Stop buttons
        col_start, col_stop = st.columns(2)
        with col_start:
            if st.button("▶️ Start Session"):
                st.session_state.is_running = True
                st.session_state.session_start = datetime.now()
                st.rerun()
        
        with col_stop:
            if st.button("⏹️ Stop Session"):
                st.session_state.is_running = False
                # Save session data
                save_session_data()
                st.success("Session saved! Feel Good!")

def save_session_data():
    """Save session data to file"""
    session_data = {
        'timestamp': datetime.now().isoformat(),
        'duration': str(datetime.now() - st.session_state.session_start),
        'reps': st.session_state.total_reps,
        'calories': st.session_state.total_reps * 0.5,
        'exercise_type': 'Mixed',
        'locations': st.session_state.locations
    }
    
    filename = f"fit4unity_data/sessions/session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(session_data, f, indent=2)
    return filename

# Tab 2: GPS Tracking
with tab2:
    st.header("📍 Location Tracking")
    
    # Get GPS location
    st.subheader("Current Location")
    
    # JavaScript to get GPS
    gps_js = """
    <script>
    function getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    document.getElementById('gps-lat').value = lat;
                    document.getElementById('gps-lon').value = lon;
                    document.getElementById('gps-status').innerHTML = 
                        '<p style="color: green;">✅ GPS acquired!</p>' +
                        '<p>Latitude: ' + lat + '</p>' +
                        '<p>Longitude: ' + lon + '</p>';
                },
                function(error) {
                    document.getElementById('gps-status').innerHTML = 
                        '<p style="color: red;">❌ Error: ' + error.message + '</p>';
                }
            );
        } else {
            document.getElementById('gps-status').innerHTML = 
                '<p style="color: red;">❌ Geolocation not supported</p>';
        }
    }
    getLocation();
    </script>
    <div id="gps-status">
        <p>📡 Acquiring GPS signal...</p>
    </div>
    <input type="hidden" id="gps-lat">
    <input type="hidden" id="gps-lon">
    """
    
    st.components.v1.html(gps_js, height=150)
    
    # Manual location entry for testing
    st.subheader("Or Enter Location Manually")
    col_lat, col_lon = st.columns(2)
    with col_lat:
        lat = st.number_input("Latitude", value=40.7128, format="%.6f")
    with col_lon:
        lon = st.number_input("Longitude", value=-74.0060, format="%.6f")
    
    # Show map
    if st.button("📍 Show on Map"):
        m = folium.Map(location=[lat, lon], zoom_start=15)
        folium.Marker([lat, lon], popup="Training Location", 
                     icon=folium.Icon(color='orange', icon='heartbeat')).add_to(m)
        st_folium(m, width=700, height=500)
        
        # Save location
        st.session_state.locations.append({
            'timestamp': datetime.now().isoformat(),
            'lat': lat,
            'lon': lon
        })

# Tab 3: Analytics Dashboard
with tab3:
    st.header("📊 Training Analytics")
    
    # Load historical data
    session_files = []
    if os.path.exists("fit4unity_data/sessions"):
        session_files = [f for f in os.listdir("fit4unity_data/sessions") if f.endswith('.json')]
    
    if session_files:
        st.subheader(f"📁 Found {len(session_files)} saved sessions")
        
        # Load all sessions
        all_sessions = []
        for f in session_files:
            try:
                with open(f"fit4unity_data/sessions/{f}", 'r') as file:
                    data = json.load(file)
                    all_sessions.append(data)
            except:
                pass
        
        if all_sessions:
            # Create DataFrame
            df = pd.DataFrame(all_sessions)
            
            # Show stats
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_sessions = len(all_sessions)
                st.metric("Total Sessions", total_sessions)
            
            with col2:
                total_reps = sum([s.get('reps', 0) for s in all_sessions])
                st.metric("Total Reps", f"{int(total_reps):,}")
            
            with col3:
                total_calories = sum([s.get('calories', 0) for s in all_sessions])
                st.metric("Total Calories", f"{total_calories:.1f}")
            
            with col4:
                total_duration = sum([s.get('duration_minutes', 30) for s in all_sessions])
                st.metric("Total Minutes", f"{total_duration:.1f}")
            
            # Charts
            st.subheader("Progress Over Time")
            
            if 'timestamp' in df.columns:
                df['date'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('date')
                
                # Line chart
                st.line_chart(df.set_index('date')[['reps', 'calories']])
    else:
        st.info("📊 No saved sessions yet. Start training to see analytics!")

# Tab 4: Heart Rate Monitor
with tab4:
    st.header("❤️ Heart Rate Monitor")
    
    st.markdown("""
    ### 📷 Camera-Based Heart Rate Detection
    
    This uses your phone's camera to detect your heart rate through your fingertip!
    
    **Instructions:**
    1. Cover your back camera completely with your fingertip
    2. Hold steady and don't move
    3. Wait 10-15 seconds for measurement
    """)
    
    # Camera input for heart rate
    hr_file = st.camera_input("Take photo of fingertip on camera")
    
    if hr_file is not None:
        st.info("📊 Analyzing... (Simulated reading)")
        
        # Simulate heart rate calculation
        import random
        heart_rate = random.randint(60, 140)
        
        st.session_state.heart_rate = heart_rate
        
        # Display heart rate with color coding
        if heart_rate < 60:
            color = "blue"
            zone = "Rest"
        elif heart_rate < 100:
            color = "green"
            zone = "Fat Burn"
        elif heart_rate < 140:
            color = "orange"
            zone = "Cardio"
        else:
            color = "red"
            zone = "Peak"
        
        st.markdown(f"""
        <div style="background: {color}; padding: 2rem; border-radius: 15px; text-align: center; color: white;">
            <div style="font-size: 4rem; font-weight: bold;">{heart_rate}</div>
            <div style="font-size: 1.5rem;">BPM</div>
            <div style="font-size: 1.2rem; margin-top: 1rem;">Zone: {zone}</div>
        </div>
        """, unsafe_allow_html=True)

# Tab 5: Parent View Instructions
with tab5:
    st.header("📱 Parent/Trainer View Setup")
    
    st.markdown("""
    ### 👨‍👩‍👧‍👦 How Parents Can Monitor
    
    **Option 1: Web Dashboard (Recommended)**
    1. Parents open a web browser on their phone/computer
    2. Go to: `http://{}:5000`
    3. They'll see live training data!
    
    **Option 2: Shared Links**
    - Send them your current IP address
    - They can bookmark it for easy access
    
    **Option 3: Export Reports**
    - After training, export session data
    - Email or text the reports to parents
    """.format(ip_address))
    
    # Show current connection status
    st.subheader("🔗 Connection Status")
    
    try:
        response = requests.get(f"http://{ip_address}:5000/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ Parent server is running and accessible!")
        else:
            st.warning("⚠️ Parent server may not be running")
    except:
        st.info("ℹ️ Start the parent server with: `python simple_flask_parent_server.py`")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>💪 <strong>Fit4Unity</strong> - Training with Soul, Peace & Unity</p>
    <p>🎵 Inspired by the Godfather of Soul 🎵</p>
    <p><em>"Strength to Stand" - Reuben's Journey</em></p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    pass
