#!/bin/bash
# Fit4Unity Setup Wizard

while true; do
    clear
    echo "🎵 Fit4Unity Setup Wizard 🎵"
    echo "============================"
    echo ""
    echo "Select an option:"
    echo ""
    echo "1) Run Pre-Flight Check"
    echo "2) Install Missing Python Packages"
    echo "3) Full Setup & Repair (Recommended)"
    echo "4) Reset All Fit4Unity Data"
    echo "5) Check & Launch App"
    echo "6) Exit"
    echo ""
    read -p "Enter choice [1-6]: " choice

    case $choice in
        1)
            ./fit4unity_preflight.sh
            echo ""
            read -p "Press Enter to continue..."
            ;;
        2)
            echo "📦 Installing Python packages..."
            pip3 install streamlit flask numpy pandas opencv-python mediapipe folium schedule requests scipy av
            echo "✅ Installation complete!"
            read -p "Press Enter to continue..."
            ;;
        3)
            echo "🔧 Running full setup..."
            mkdir -p fit4unity_data/{exports,logs,sessions}
            touch fit4unta/parent_contacts.txt
            pip3 install streamlit flask numpy pandas opencv-python mediapipe folium schedule requests scipy av
            ./fit4unity_preflight.sh
            echo "✅ Full setup complete!"
            read -p "Press Enter to continue..."
            ;;
        4)
            echo "⚠️  This will delete all Fit4Unity data!"
            read -p "Are you sure? (yes/no): " confirm
            if [ "$confirm" = "yes" ]; then
                rm -rf fit4unity_data/*
                echo "✅ Data reset complete!"
            else
                echo "❌ Cancelled."
            fi
            read -p "Press Enter to continue..."
            ;;
        5)
            ./fit4unity_preflight.sh
            echo ""
            read -p "Launch Fit4Unity now? (y/n): " launch
            if [ "$launch" = "y" ]; then
                ./run_all.sh
            fi
            ;;
        6)
            echo "👋 Goodbye! Feel Good! 🎵"
            exit 0
            ;;
        *)
            echo "Invalid option. Press Enter to continue..."
            read
            ;;
    esac
done
