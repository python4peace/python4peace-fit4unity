#!/bin/bash
# ==============================
# Fit4Unity Bulletproof Wizard + GitHub/Render Deployment
# ==============================

PROJECT_DIR=~/fit4unity
VENV_DIR="$PROJECT_DIR/venv"
APP_FILE="$PROJECT_DIR/app.py"
REQUIREMENTS="$PROJECT_DIR/requirements.txt"
PORT=8501
GIT_REMOTE="git@github.com:python4peace/python4peace-fit4unity.git"
BRANCH="main"

# ------------------------------
# Pre-flight check
# ------------------------------
preflight_check() {
    clear
    echo "🔍 Running Pre-Flight Check..."
    echo "============================"

    # Python version
    PYVER=$(python3 -V 2>&1)
    echo "Python Version: $PYVER"

    # Virtual env
    if [ ! -d "$VENV_DIR" ]; then
        echo "⚠️ Virtual environment not found."
    else
        echo "✅ Virtual environment exists."
    fi

    # requirements.txt
    if [ -f "$REQUIREMENTS" ]; then
        echo "✅ requirements.txt found."
    else
        echo "⚠️ requirements.txt NOT found!"
    fi

    # Streamlit process
    EXISTING_PID=$(lsof -ti:$PORT)
    if [ ! -z "$EXISTING_PID" ]; then
        echo "⚠️ Streamlit already running on port $PORT (PID $EXISTING_PID)"
    else
        echo "✅ No Streamlit process detected."
    fi

    echo "Pre-Flight Check complete."
    read -p "Press Enter to continue..."
}

# ------------------------------
# Install packages
# ------------------------------
install_packages() {
    echo "📦 Installing Python packages..."
    python3 -m pip install --upgrade pip
    if [ -f "$REQUIREMENTS" ]; then
        pip install -r "$REQUIREMENTS"
    else
        echo "⚠️ requirements.txt not found. Installing default packages..."
        pip install streamlit flask numpy pandas opencv-python mediapipe folium schedule requests scipy av fpdf googletrans gtts
    fi
    echo "✅ Packages installed."
    read -p "Press Enter to continue..."
}

# ------------------------------
# Full setup & repair
# ------------------------------
full_setup() {
    echo "🔧 Running Full Setup & Repair..."
    mkdir -p "$PROJECT_DIR"/fit4unity_data/{exports,logs,sessions}

    # Virtual env
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
    fi
    source "$VENV_DIR/bin/activate"

    install_packages
    preflight_check
    echo "✅ Full setup & repair complete."
    read -p "Press Enter to continue..."
}

# ------------------------------
# Reset data
# ------------------------------
reset_data() {
    echo "⚠️  This will delete all Fit4Unity data!"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        rm -rf "$PROJECT_DIR"/fit4unity_data/*
        echo "✅ Data reset complete!"
    else
        echo "❌ Cancelled."
    fi
    read -p "Press Enter to continue..."
}

# ------------------------------
# Launch App
# ------------------------------
launch_app() {
    echo "🚀 Launching Fit4Unity App..."
    cd "$PROJECT_DIR" || { echo "Folder not found!"; exit 1; }
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
    else
        python3 -m venv "$VENV_DIR"
        source "$VENV_DIR/bin/activate"
    fi

    python3 -m pip install --upgrade pip
    install_packages

    EXISTING_PID=$(lsof -ti:$PORT)
    if [ ! -z "$EXISTING_PID" ]; then
        echo "Stopping existing Streamlit (PID $EXISTING_PID)..."
        kill -9 $EXISTING_PID
    fi

    nohup streamlit run "$APP_FILE" --server.port $PORT > streamlit_log.txt 2>&1 &
    echo "✅ Streamlit started!"
    echo "🌐 Visit: http://localhost:$PORT"
    echo "🔍 Check logs: streamlit_log.txt"
    read -p "Press Enter to continue..."
}

# ------------------------------
# Push to GitHub & Deploy to Render
# ------------------------------
deploy_github_render() {
    cd "$PROJECT_DIR" || { echo "Folder not found!"; exit 1; }
    source "$VENV_DIR/bin/activate"

    echo "📦 Running full setup before deployment..."
    full_setup

    echo "📝 Adding, committing, and pushing changes to GitHub..."
    git add .
    git commit -m "Auto update from wizard $(date +"%Y-%m-%d %H:%M:%S")"
    git push $GIT_REMOTE $BRANCH

    if command -v render >/dev/null 2>&1; then
        echo "🚀 Deploying to Render..."
        render deploy
        echo "✅ Render deployment complete!"
    else
        echo "⚠️ Render CLI not found. Skipping deployment."
    fi

    echo "✅ GitHub push & Render deployment done!"
    read -p "Press Enter to continue..."
}

# ------------------------------
# Wizard Menu
# ------------------------------
while true; do
    clear
    echo "🎵 Fit4Unity Wizard + GitHub/Render 🎵"
    echo "==============================="
    echo "1) Pre-Flight Check"
    echo "2) Install Missing Python Packages"
    echo "3) Full Setup & Repair"
    echo "4) Reset All Fit4Unity Data"
    echo "5) Check & Launch App (manual)"
    echo "6) Exit"
    echo "7) Launch App Automatically (bulletproof!)"
    echo "8) Push to GitHub & Deploy to Render"
    echo ""
    read -p "Enter choice [1-8]: " choice

    case $choice in
        1) preflight_check ;;
        2) install_packages ;;
        3) full_setup ;;
        4) reset_data ;;
        5) launch_app ;;
        6) echo "👋 Goodbye! Feel Good! 🎵"; exit 0 ;;
        7) launch_app ;;
        8) deploy_github_render ;;
        *) echo "Invalid option. Press Enter to continue..."; read ;;
    esac
done
