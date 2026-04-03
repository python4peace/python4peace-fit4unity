from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Store live training data
live_data = {
    'status': 'idle',
    'heart_rate': 0,
    'reps': 0,
    'calories': 0,
    'session_time': '00:00',
    'location': None,
    'last_update': None
}

@app.route('/')
def parent_dashboard():
    """Main parent dashboard"""
    html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Fit4Unity - Parent Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #FF6B35;
            margin: 0;
            font-size: 2.5rem;
        }
        .header p {
            color: #666;
            font-style: italic;
        }
        .status-badge {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
            margin: 10px 0;
        }
        .status-active {
            background: #4CAF50;
            color: white;
        }
        .status-idle {
            background: #FFC107;
            color: black;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
        }
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.9;
            margin-top: 5px;
        }
        .map-container {
            background: #f5f5f5;
            border-radius: 15px;
            height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 20px 0;
        }
        .alert-box {
            background: #FFF3CD;
            border: 2px solid #FFC107;
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 0.9rem;
        }
        .update-time {
            text-align: center;
            color: #999;
            font-size: 0.8rem;
            margin-top: 10px;
        }
        .feel-good {
            background: linear-gradient(90deg, #FF6B35, #F7931E);
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            font-size: 1.2rem;
            font-weight: bold;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💪 Fit4Unity</h1>
            <p>Parent/Trainer Dashboard</p>
            <p><em>"Strength to Stand" - Reuben's Journey</em></p>
        </div>
        
        <div class="feel-good">🎵 FEEL GOOD! 🎵</div>
        
        <div style="text-align: center;">
            <span id="status-badge" class="status-badge status-idle">⏸️ No Active Session</span>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div id="heart-rate" class="metric-value">--</div>
                <div class="metric-label">❤️ Heart Rate (BPM)</div>
            </div>
            <div class="metric-card">
                <div id="reps" class="metric-value">--</div>
                <div class="metric-label">🏃 Total Reps</div>
            </div>
            <div class="metric-card">
                <div id="calories" class="metric-value">--</div>
                <div class="metric-label">🔥 Calories Burned</div>
            </div>
            <div class="metric-card">
                <div id="session-time" class="metric-value">--</div>
                <div class="metric-label">⏱️ Session Time</div>
            </div>
        </div>
        
        <div class="map-container">
            <div id="location-info">
                <p>📍 Location tracking will appear here</p>
                <p><small>Last known location: <span id="location-text">Not available</span></small></p>
            </div>
        </div>
        
        <div id="alert-box" class="alert-box" style="display: none;">
            <strong>⚠️ Alert:</strong> <span id="alert-message"></span>
        </div>
        
        <div class="update-time">
            Last update: <span id="last-update">Never</span>
        </div>
        
        <div class="footer">
            <p>Real-time training monitoring for peace of mind</p>
            <p>Fit4Unity - Training with Soul, Peace & Unity</p>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 2 seconds
        setInterval(fetchData, 2000);
        
        function fetchData() {
            fetch('/api/live-data')
                .then(response => response.json())
                .then(data => {
                    updateDashboard(data);
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                });
        }
        
        function updateDashboard(data) {
            // Update status
            const statusBadge = document.getElementById('status-badge');
            if (data.status === 'active') {
                statusBadge.className = 'status-badge status-active';
                statusBadge.textContent = '▶️ Training in Progress';
            } else {
                statusBadge.className = 'status-badge status-idle';
                statusBadge.textContent = '⏸️ No Active Session';
            }
            
            // Update metrics
            document.getElementById('heart-rate').textContent = data.heart_rate || '--';
            document.getElementById('reps').textContent = data.reps || '--';
            document.getElementById('calories').textContent = data.calories ? data.calories.toFixed(1) : '--';
            document.getElementById('session-time').textContent = data.session_time || '--';
            
            // Update location
            if (data.location) {
                document.getElementById('location-text').textContent = 
                    `Lat: ${data.location.lat.toFixed(4)}, Lon: ${data.location.lon.toFixed(4)}`;
            }
            
            // Update last update time
            if (data.last_update) {
                const updateTime = new Date(data.last_update);
                document.getElementById('last-update').textContent = updateTime.toLocaleTimeString();
            }
        }
        
        // Initial fetch
        fetchData();
    </script>
</body>
</html>
    '''
    return html

@app.route('/api/live-data', methods=['GET'])
def get_live_data():
    """API endpoint for live training data"""
    return jsonify(live_data)

@app.route('/api/update', methods=['POST'])
def update_data():
    """Update live training data from the main app"""
    data = request.json
    live_data.update(data)
    live_data['last_update'] = datetime.now().isoformat()
    return jsonify({'status': 'success'})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Get saved session history"""
    sessions = []
    sessions_dir = 'fit4unity_data/sessions'
    if os.path.exists(sessions_dir):
        for f in os.listdir(sessions_dir):
            if f.endswith('.json'):
                try:
                    with open(f'{sessions_dir}/{f}', 'r') as file:
                        sessions.append(json.load(file))
                except:
                    pass
    return jsonify(sessions)

if __name__ == '__main__':
    print("🎵 Fit4Unity Parent Server Starting...")
    print(f"📱 Parent dashboard available at: http://0.0.0.0:5000")
    print(f"🔗 API endpoint: http://0.0.0.0:5000/api/live-data")
    print("🛑 Press Ctrl+C to stop")
    app.run(host='0.0.0.0', port=5000, debug=False)
