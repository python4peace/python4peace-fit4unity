#!/bin/bash
# Fit4Unity - Run All Services
# This script starts both the Streamlit app and Flask parent server

echo "🎵 Fit4Unity - Strength to Stand 🎵"
echo "====================================="
echo ""

# Check if we're in the right directory
if [ ! -f "fit4unity_complete.py" ]; then
    echo "❌ Error: fit4unity_complete.py not found!"
    echo "Please run this script from the fit4unity directory."
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping Fit4Unity services..."
    kill $STREAMLIT_PID $FLASK_PID 2>/dev/null
    echo "✅ Services stopped. Feel Good!"
    exit 0
}

# Trap Ctrl+C
trap cleanup IN

echo "📱 Starting Fit4Unity services..."
echo ""

# Start Flask parent server in background
echo "🔵 Starting Parent Dashboard Server (Port 5000)..."
python simple_flask_parent_server.py &
FLASK_PID=$!

# Wait a moment for Flask to start
sleep 2

# Start Streamlit app
echo "🟢 Starting Main App (Port 8501)..."
streamlit run fit4unity_complete.py --server.port 8501 --server.address 0.0.0.0 &
STREAMLIT_PID=$!

echo ""
echo "✅ Both services started!"
echo ""
echo "📱 Access your apps at:"
echo "   • Main App:       http://localhost:8501"
echo "   • Parent Dashboard: http://localhost:5000"
echo ""
echo "🌐 For other devices on same WiFi:"
IP=$(ip route get 1 2>/dev/null | grep -oP 'src \K\S+' || echo "YOUR_PHONE_IP")
echo "   • Main App:       http://$IP:8501"
echo "   • Parent Dashboard: http://$IP:5000"
echo ""
echo "🛑 Press Ctrl+C to stop all services"
echo ""

# Wait for both processes
wait $STREAMLIT_PID $FLASK_PID
