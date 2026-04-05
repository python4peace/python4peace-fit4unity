#!/bin/bash
cd ~/fit4unity
source venv/bin/activate
echo "🚀 Starting ReubenSoul4peaceunity..."
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
