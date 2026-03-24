#!/bin/bash
# Fit4Unity Quick Start - One command to check and launch

echo "🎵 Fit4Unity Quick Start 🎵"
echo "============================"

# Run pre-flight check
./fit4unity_preflight.sh

# Check if pre-flight passed
if [ $? -eq 0 ]; then
    echo ""
    read -p "🚀 Launch Fit4Unity now? (y/n): " launch
    if [ "$launch" = "y" ]; then
        ./run_all.sh
    fi
else
    echo ""
    echo "⚠️  Issues found. Run ./fit4unity_wizard.sh to fix."
fi
