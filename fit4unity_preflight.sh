#!/bin/bash
# Fit4Unity Pre-Flight Check Script

echo "🎵 Fit4Unity Pre-Flight Check 🎵"
echo "================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PASS=0
WARN=0
FAIL=0

check_pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((PASS++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
    ((WARN++))
}

check_fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((FAIL++))
}

# Check Python
echo ""
echo "🔍 Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    check_pass "Python3 found: $PYTHON_VERSION"
else
    check_fail "Python3 not found"
fi

# Check pip
echo ""
echo "🔍 Checking pip..."
if command -v pip3 &> /dev/null; then
    check_pass "pip3 found"
else
    check_fail "pip3 not found"
fi

# Check required Python packages
echo ""
echo "🔍 Checking Python packages..."
PACKAGES="streamlit flask numpy pandas opencv-python mediapipe folium schedule requests"
for pkg in $PACKAGES; do
    if python3 -c "import $pkg" 2>/dev/null; then
        check_pass "Package $pkg installed"
    else
        check_warn "Package $pkg not installed (will be installed)"
    fi
done

# Check directory structure
echo ""
echo "🔍 Checking directory structure..."
if [ -d "fit4unity_data" ]; then
    check_pass "fit4unity_data directory exists"
else
    check_warn "fit4unity_data directory will be created"
fi

# Check key files
echo ""
echo "🔍 Checking key files..."
if [ -f "fit4unity_complete.py" ]; then
    check_pass "fit4unity_complete.py found"
else
    check_fail "fit4unity_complete.py not found"
fi

if [ -f "simple_flask_parent_server.py" ]; then
    check_pass "simple_flask_parent_server.py found"
else
    check_fail "simple_flask_parent_server.py not found"
fi

# Check network
echo ""
echo "🔍 Checking network..."
IP=$(ip route get 1 2>/dev/null | grep -oP 'src \K\S+' || echo "")
if [ -n "$IP" ]; then
    check_pass "Network interface found: $IP"
else
    check_warn "Could not detect IP address"
fi

# Check ports
echo ""
echo "🔍 Checking port availability..."
if ! netstat -tuln 2>/dev/null | grep -q ":8501"; then
    check_pass "Port 8501 (Streamlit) available"
else
    check_warn "Port 8501 may be in use"
fi

if ! netstat -tuln 2>/dev/null | grep -q ":5000"; then
    check_pass "Port 5000 (Flask) available"
else
    check_warn "Port 5000 may be in use"
fi

# Summary
echo ""
echo "================================"
echo "📊 Pre-Flight Check Summary"
echo "================================"
echo -e "${GREEN}✅ Passed: $PASS${NC}"
echo -e "${YELLOW}⚠️  Warnings: $WARN${NC}"
echo -e "${RED}❌ Failed: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "🎉 All critical checks passed!"
    echo "🚀 Ready to run: ./run_all.sh"
else
    echo "⚠️  Some critical checks failed."
    echo "🔧 Run: ./fit4unity_wizard.sh to fix issues"
fi
echo ""
echo "💪 Feel Good! 🎵"
