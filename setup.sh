#!/bin/bash

echo "🚀 ReubenSoul4peaceunity FULL AUTO SETUP STARTING..."

# =============================
# GO TO PROJECT FOLDER
# =============================
cd ~/fit4unity || {
    echo "❌ Folder ~/fit4unity not found!"
    exit 1
}

# =============================
# UPDATE SYSTEM
# =============================
echo "🔄 Updating system..."
sudo apt update -y && sudo apt upgrade -y

# =============================
# INSTALL SYSTEM DEPENDENCIES
# =============================
echo "📦 Installing system packages..."
sudo apt install -y python3 python3-pip python3-venv \
    build-essential libgl1 libglib2.0-0

# =============================
# CREATE VIRTUAL ENVIRONMENT
# =============================
echo "🐍 Setting up virtual environment..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate venv
source venv/bin/activate

# =============================
# CREATE SAFE REQUIREMENTS
# =============================
echo "📄 Creating requirements.txt..."

cat > requirements.txt << EOF
streamlit==1.32.0
numpy
pandas
opencv-python-headless
mediapipe
folium
streamlit-folium
fpdf
googletrans==4.0.0-rc1
gTTS
EOF

# =============================
# INSTALL PYTHON PACKAGES
# =============================
echo "⬇️ Installing Python packages..."

pip install --upgrade pip
pip install -r requirements.txt

# =============================
# CREATE DATA FOLDERS
# =============================
echo "📁 Creating folders..."

mkdir -p fit4unity_data/exports
mkdir -p fit4unity_data/logs
mkdir -p fit4unity_data/sessions

# =============================
# CREATE START SCRIPT
# =============================
echo "⚙️ Creating start.sh..."

cat > start.sh << 'EOF'
#!/bin/bash
cd ~/fit4unity
source venv/bin/activate
echo "🚀 Starting ReubenSoul4peaceunity..."
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
EOF

chmod +x start.sh

# =============================
# KILL OLD STREAMLIT
# =============================
echo "🛑 Stopping old Streamlit if running..."
pkill -f streamlit || true

# =============================
# RUN APP
# =============================
echo "🌐 Launching app..."
./start.sh &

sleep 5

# =============================
# CHECK IF RUNNING
# =============================
if curl -s http://localhost:8501 > /dev/null; then
    echo ""
    echo "✅ SUCCESS!"
    echo "👉 Open your app here:"
    echo "http://localhost:8501"
else
    echo "⚠️ App may still be starting..."
    echo "👉 Check logs or wait a few seconds"
fi

echo "🎉 Setup Complete!"
