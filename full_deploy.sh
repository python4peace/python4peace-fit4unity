#!/bin/bash
# ================================================
# 💎 Smart One-Click Deployment Script (v3)
# ================================================

set -e

echo "🚀 Starting smart deployment workflow..."

# -------------------------
# 0️⃣ Python version check
# -------------------------
PYTHON_VER=$(python --version 2>&1 | awk '{print $2}')
REQ_VER="3.11"
if [[ "$PYTHON_VER" != $REQ_VER* ]]; then
    echo "⚠️ Warning: Python version is $PYTHON_VER, recommended is $REQ_VER.x"
fi
echo "✅ Python version check done ($PYTHON_VER)"

# -------------------------
# 1️⃣ Ensure virtual environment
# -------------------------
if [ -z "$VIRTUAL_ENV" ]; then
    echo "🔧 Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
else
    echo "✅ Virtual environment activated."
fi

# -------------------------
# 2️⃣ Upgrade pip & build tools
# -------------------------
pip install --upgrade pip setuptools wheel || echo "⚠️ Upgrade failed, retrying..."
pip install --upgrade pip setuptools wheel
echo "✅ pip, setuptools, wheel upgraded"

# -------------------------
# 3️⃣ Install dependencies with retry
# -------------------------
install_package() {
    pkg=$1
    attempts=0
    while [ $attempts -lt 3 ]; do
        pip install --no-cache-dir "$pkg" && break
        attempts=$((attempts+1))
        echo "⚠️ Retry $attempts for $pkg..."
        sleep 2
    done
    if [ $attempts -eq 3 ]; then
        echo "❌ Failed to install $pkg after 3 attempts"
        exit 1
    fi
}

echo "🔧 Installing project dependencies..."
for pkg in $(cat requirements.txt); do
    install_package "$pkg"
done
echo "✅ Dependencies installed"

# -------------------------
# 4️⃣ Pre-flight module checks
# -------------------------
declare -a modules=("speech_recognition" "gtts" "fpdf" "googletrans" "streamlit")
for module in "${modules[@]}"; do
    if ! python -c "import $module" &> /dev/null; then
        echo "⚠️ Module '$module' missing, installing..."
        install_package "$module"
    else
        echo "✅ Module '$module' OK"
    fi
done

# -------------------------
# 5️⃣ Windows Firewall (optional)
# -------------------------
if [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "cygwin"* ]]; then
    echo "🔐 Setting Windows Firewall rules..."
    powershell -Command "
    \$pythonPath = '$((which python | sed 's|/c|C:\\|;s|/|\\|g'))'
    New-NetFirewallRule -DisplayName 'Allow Python Streamlit' -Direction Inbound -Program \$pythonPath -Action Allow -Profile Domain,Private,Public -Description 'Allow Streamlit apps'
    New-NetFirewallRule -DisplayName 'Allow Python Streamlit Outbound' -Direction Outbound -Program \$pythonPath -Action Allow -Profile Domain,Private,Public -Description 'Allow Streamlit outbound'
    "
    echo "✅ Windows Firewall rules applied"
fi

# -------------------------
# 6️⃣ Launch Streamlit locally
# -------------------------
echo "🌐 Launching Streamlit locally..."
nohup streamlit run app.py &> streamlit_log.txt &
echo "⏳ Waiting for Streamlit to start..."
sleep 5

# -------------------------
# Open in browser automatically
# -------------------------
URL="http://localhost:8501"
echo "🌐 Opening Streamlit app in your browser: $URL"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open $URL
elif [[ "$OSTYPE" == "darwin"* ]]; then
    open $URL
elif [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "cygwin"* ]]; then
    start $URL
fi

# -------------------------
# 7️⃣ Commit & push to GitHub
# -------------------------
git checkout main
git add .
git commit -m "${1:-'Auto-update app'}"
git push origin main
echo "✅ Code pushed to GitHub"

# -------------------------
# 8️⃣ Trigger Render deployment
# -------------------------
echo "🌍 Triggering Render deployment..."
curl -X POST "https://api.render.com/deploy/srv-d793mctactks73cvcr3g?key=E0U"
echo "✅ Render deploy triggered"

# -------------------------
# 9️⃣ Finished
# -------------------------
echo "🎉 Smart deployment completed!"
echo "✅ Streamlit should be running and open in your browser now."
echo "✅ Render deployment is in progress."
