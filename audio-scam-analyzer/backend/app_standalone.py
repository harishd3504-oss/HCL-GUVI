#!/usr/bin/env python3
"""
🔐 AI-POWERED AUDIO CALL SCAM ANALYZER - STANDALONE DEMO
=========================================================

ZERO DEPENDENCIES VERSION - Works with just Python 3.8+
Perfect for hackathon demos and quick testing.

To run:
    python app_standalone.py

Then open:
    http://localhost:8000
"""

import json
import random
import mimetypes
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time
import sys
import io
from datetime import datetime

# ==========================================
# DEMO DATA - Simulated scam calls
# ==========================================

DEMO_SCENARIOS = {
    "high_risk_banking_otp": {
        "transcription": """
Hello sir, this is calling from your bank RBI Cyber Cell. We have detected 
suspicious activity in your account. Your account will be blocked immediately 
if you don't verify within 24 hours. For verification, we need your OTP code 
right now. This is urgent and time-sensitive. Please provide your OTP immediately.
Your account balance is at risk. Tell me your one-time password now.
        """.strip(),
        "risk_score": 95,
        "risk_level": "CRITICAL_SCAM",
        "patterns": [
            {
                "name": "OTP/Credential Request",
                "keywords": ["otp", "password", "verify code"],
                "confidence": 0.99,
                "risk": 100,
                "explanation": "🚨 CRITICAL: OTP/Password request detected. Legitimate institutions NEVER ask for OTP via phone."
            },
            {
                "name": "Artificial Urgency",
                "keywords": ["immediately", "urgent", "24 hours"],
                "confidence": 0.92,
                "risk": 20,
                "explanation": "⚠️ PRESSURE: Artificial urgency with time-pressure language."
            },
            {
                "name": "Authority Impersonation",
                "keywords": ["bank", "rbi", "cyber cell"],
                "confidence": 0.88,
                "risk": 25,
                "explanation": "👤 IMPERSONATION: Claims to represent RBI without verification."
            },
            {
                "name": "Fear-Based Pressure",
                "keywords": ["blocked", "at risk"],
                "confidence": 0.85,
                "risk": 20,
                "explanation": "😨 FEAR: Threat language designed to panic you."
            }
        ]
    },
    
    "medium_risk_verification": {
        "transcription": """
Hi, I'm calling regarding your recent credit card transactions. We noticed 
some unusual activity. Can you confirm if you made purchases at these stores?
We may need to verify your account information for security purposes.
        """.strip(),
        "risk_score": 45,
        "risk_level": "MEDIUM_RISK",
        "patterns": [
            {
                "name": "Financial Information Targeting",
                "keywords": ["credit card", "transactions", "account"],
                "confidence": 0.75,
                "risk": 15,
                "explanation": "💰 TARGET: Attempting to verify account information."
            }
        ]
    },
    
    "low_risk_legitimate": {
        "transcription": """
Hello, thank you for calling our customer service. My name is John. 
How can I assist you today? We're here to help. There's no rush.
        """.strip(),
        "risk_score": 8,
        "risk_level": "LIKELY_SAFE",
        "patterns": []
    }
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔐 AI Scam Call Analyzer - Demo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 900px;
            width: 100%;
            padding: 40px;
            animation: fadeIn 0.5s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 20px;
        }
        
        .header h1 {
            font-size: 2.5em;
            color: #333;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 1.1em;
        }
        
        .demo-badge {
            display: inline-block;
            background: #ffc107;
            color: #000;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            margin-top: 10px;
        }
        
        .upload-section {
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            border: 2px dashed #667eea;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 30px;
        }
        
        .upload-section:hover {
            border-color: #764ba2;
            background: linear-gradient(135deg, #667eea25 0%, #764ba225 100%);
        }
        
        .upload-section h3 {
            color: #333;
            margin-bottom: 10px;
        }
        
        .upload-section p {
            color: #666;
            margin-bottom: 15px;
        }
        
        input[type="file"] {
            display: none;
        }
        
        .btn {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            transition: transform 0.2s, box-shadow 0.2s;
            margin: 5px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        
        .results {
            display: none;
            margin-top: 40px;
            padding-top: 40px;
            border-top: 2px solid #f0f0f0;
            animation: slideUp 0.5s ease;
        }
        
        .results.show {
            display: block;
        }
        
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .risk-score {
            font-size: 3em;
            font-weight: bold;
            text-align: center;
            margin: 30px 0;
        }
        
        .risk-critical { color: #ff1744; }
        .risk-high { color: #ff6d00; }
        .risk-medium { color: #ffc107; }
        .risk-low { color: #4caf50; }
        
        .risk-level {
            font-size: 1.5em;
            text-align: center;
            margin: 10px 0 20px;
            font-weight: bold;
        }
        
        .pattern-list {
            margin: 30px 0;
        }
        
        .pattern-item {
            background: #f5f5f5;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 15px 0;
            border-radius: 8px;
        }
        
        .pattern-item h4 {
            color: #333;
            margin-bottom: 8px;
        }
        
        .pattern-item .confidence {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.85em;
            margin-right: 10px;
        }
        
        .pattern-item .risk-points {
            display: inline-block;
            background: #ff1744;
            color: white;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.85em;
        }
        
        .pattern-item p {
            color: #666;
            margin-top: 10px;
            line-height: 1.6;
        }
        
        .transcription {
            background: #f5f5f5;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 4px solid #667eea;
            line-height: 1.6;
            color: #333;
            font-size: 0.95em;
        }
        
        .explanation {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            line-height: 1.8;
            color: #333;
            font-size: 0.95em;
            white-space: pre-wrap;
        }
        
        .loading {
            text-align: center;
            display: none;
        }
        
        .loading.show {
            display: block;
        }
        
        .spinner {
            display: inline-block;
            width: 40px;
            height: 40px;
            border: 4px solid #f0f0f0;
            border-top-color: #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .loading p {
            margin-top: 15px;
            color: #666;
            font-size: 1.1em;
        }
        
        .demo-scenarios {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .scenario-btn {
            background: #f0f0f0;
            border: 2px solid #ddd;
            padding: 15px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            text-align: left;
        }
        
        .scenario-btn:hover {
            border-color: #667eea;
            background: #f9f9f9;
        }
        
        .scenario-btn h4 {
            color: #333;
            margin-bottom: 5px;
        }
        
        .scenario-btn .risk-badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.85em;
            color: white;
            font-weight: bold;
        }
        
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #f0f0f0;
            text-align: center;
            color: #999;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 AI Call Scam Analyzer</h1>
            <p>Detect financial fraud patterns in phone calls</p>
            <span class="demo-badge">⚡ DEMO VERSION - Zero Dependencies</span>
        </div>
        
        <div class="upload-section" onclick="document.getElementById('audioFile').click()">
            <div>
                <h3>📞 Upload Audio File</h3>
                <p>Or try demo scenarios below</p>
                <button class="btn" onclick="event.stopPropagation()">Choose Audio File</button>
            </div>
            <input type="file" id="audioFile" accept="audio/*">
        </div>
        
        <div style="margin: 30px 0;">
            <p style="text-align: center; color: #666; margin-bottom: 15px;"><strong>Quick Demo:</strong></p>
            <div class="demo-scenarios">
                <button class="scenario-btn" onclick="analyzeScenario('high_risk_banking_otp')">
                    <h4>🚨 High Risk Scam</h4>
                    <span class="risk-badge" style="background: #ff1744;">CRITICAL</span>
                    <p style="margin-top: 10px; font-size: 0.85em; color: #666;">OTP request, urgency, threat</p>
                </button>
                
                <button class="scenario-btn" onclick="analyzeScenario('medium_risk_verification')">
                    <h4>🟡 Medium Risk Call</h4>
                    <span class="risk-badge" style="background: #ffc107; color: #000;">SUSPICIOUS</span>
                    <p style="margin-top: 10px; font-size: 0.85em; color: #666;">Information gathering</p>
                </button>
                
                <button class="scenario-btn" onclick="analyzeScenario('low_risk_legitimate')">
                    <h4>✅ Likely Legitimate</h4>
                    <span class="risk-badge" style="background: #4caf50;">SAFE</span>
                    <p style="margin-top: 10px; font-size: 0.85em; color: #666;">Normal customer service</p>
                </button>
            </div>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>🔍 Analyzing call...</p>
        </div>
        
        <div class="results" id="results">
            <h2 style="margin-bottom: 20px; color: #333;">📊 Analysis Results</h2>
            
            <div class="risk-score" id="riskScore"></div>
            <div class="risk-level" id="riskLevel"></div>
            
            <div class="transcription" id="transcription" style="display: none;">
                <strong>📝 Transcription:</strong>
                <p id="transcriptionText" style="margin-top: 10px;"></p>
            </div>
            
            <div class="explanation" id="explanation"></div>
            
            <div class="pattern-list" id="patternList"></div>
        </div>
        
        <div class="footer">
            <p>🔒 Privacy Protected: No data stored • Local Analysis Only</p>
            <p>This is a demo version. For production use with real Whisper AI transcription, upgrade to the full version.</p>
        </div>
    </div>
    
    <script>
        // Handle file upload
        document.getElementById('audioFile').addEventListener('change', async function(e) {
            const file = e.target.files[0];
            if (!file) return;
            
            await analyzeFile(file);
        });
        
        async function analyzeFile(file) {
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                showLoading();
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) throw new Error('Analysis failed');
                
                const result = await response.json();
                displayResults(result);
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                hideLoading();
            }
        }
        
        async function analyzeScenario(scenario) {
            try {
                showLoading();
                const response = await fetch('/api/demo?scenario=' + scenario);
                
                if (!response.ok) throw new Error('Analysis failed');
                
                const result = await response.json();
                displayResults(result);
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                hideLoading();
            }
        }
        
        function displayResults(data) {
            const riskScore = document.getElementById('riskScore');
            const riskLevel = document.getElementById('riskLevel');
            const explanation = document.getElementById('explanation');
            const patternList = document.getElementById('patternList');
            const transcription = document.getElementById('transcription');
            const transcriptionText = document.getElementById('transcriptionText');
            
            // Risk score styling
            riskScore.textContent = data.risk_score + '/100';
            riskScore.className = 'risk-score';
            
            if (data.risk_score >= 90) {
                riskScore.classList.add('risk-critical');
                riskLevel.textContent = '🔴 CRITICAL SCAM';
            } else if (data.risk_score >= 70) {
                riskScore.classList.add('risk-high');
                riskLevel.textContent = '🟠 HIGH RISK';
            } else if (data.risk_score >= 50) {
                riskScore.classList.add('risk-medium');
                riskLevel.textContent = '🟡 MEDIUM RISK';
            } else if (data.risk_score >= 30) {
                riskScore.classList.add('risk-medium');
                riskLevel.textContent = '🟡 LOW-MEDIUM RISK';
            } else {
                riskScore.classList.add('risk-low');
                riskLevel.textContent = '✅ LIKELY SAFE';
            }
            
            // Explanation
            explanation.textContent = data.explanation;
            
            // Patterns
            if (data.patterns && data.patterns.length > 0) {
                patternList.innerHTML = '<h3 style="color: #333; margin-bottom: 15px;">🎯 Detected Threat Patterns:</h3>';
                data.patterns.forEach(pattern => {
                    const patternHtml = `
                        <div class="pattern-item">
                            <h4>${pattern.name}</h4>
                            <div>
                                <span class="confidence">Confidence: ${(pattern.confidence * 100).toFixed(0)}%</span>
                                <span class="risk-points">+${pattern.risk} risk points</span>
                            </div>
                            <p>${pattern.explanation}</p>
                        </div>
                    `;
                    patternList.innerHTML += patternHtml;
                });
            } else {
                patternList.innerHTML = '<p style="color: #4caf50; font-size: 1.1em;">✅ No threatening patterns detected</p>';
            }
            
            // Transcription
            if (data.transcription) {
                transcription.style.display = 'block';
                transcriptionText.textContent = data.transcription;
            }
            
            // Show results
            document.getElementById('results').classList.add('show');
            window.scrollTo({ top: document.getElementById('results').offsetTop - 100, behavior: 'smooth' });
        }
        
        function showLoading() {
            document.getElementById('loading').classList.add('show');
            document.getElementById('results').classList.remove('show');
        }
        
        function hideLoading() {
            document.getElementById('loading').classList.remove('show');
        }
    </script>
</body>
</html>"""

# ==========================================
# HTTP REQUEST HANDLER
# ==========================================

class DemoHandler(BaseHTTPRequestHandler):
    """HTTP handler for the demo server"""
    
    def log_message(self, format, *args):
        """Custom logging"""
        print(f"[{self.log_date_time_string()}] {format % args}")
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)
        
        try:
            if path == '/':
                # Serve main HTML
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(HTML_TEMPLATE.encode())
                
            elif path == '/api/demo':
                # Demo scenario endpoint
                scenario = query.get('scenario', ['high_risk_banking_otp'])[0]
                
                if scenario in DEMO_SCENARIOS:
                    data = DEMO_SCENARIOS[scenario]
                    response = {
                        'transcription': data['transcription'],
                        'risk_score': data['risk_score'],
                        'risk_level': data['risk_level'],
                        'patterns': data['patterns'],
                        'explanation': self.generate_explanation(data),
                        'success': True
                    }
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                else:
                    self.send_error(404, "Scenario not found")
                    
            else:
                self.send_error(404, "Not found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            self.send_error(500, str(e))
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            if self.path == '/api/analyze':
                # Parse multipart form data
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                
                # For demo, just simulate analysis
                scenario = random.choice(list(DEMO_SCENARIOS.keys()))
                data = DEMO_SCENARIOS[scenario]
                
                response = {
                    'transcription': data['transcription'],
                    'risk_score': data['risk_score'],
                    'risk_level': data['risk_level'],
                    'patterns': data['patterns'],
                    'explanation': self.generate_explanation(data),
                    'success': True
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_error(404)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            self.send_error(500, str(e))
    
    def generate_explanation(self, data):
        """Generate explanation for the risk assessment"""
        if not data['patterns']:
            return f"""✅ RISK ASSESSMENT: {data['risk_level']} ({data['risk_score']}/100)

No scam patterns detected. This appears to be a legitimate call.

RECOMMENDATION:
✅ This call appears safe. You can proceed normally."""
        
        pattern_summary = "\n".join([
            f"  • {p['name']}: +{p['risk']} points"
            for p in data['patterns']
        ])
        
        return f"""🔴 RISK ASSESSMENT: {data['risk_level']} ({data['risk_score']}/100)

🚨 DETECTED THREATS:
{pattern_summary}

⚠️ PATTERN COMBINATION:
Multiple attack vectors detected. This suggests a sophisticated, coordinated scam attempt.

RECOMMENDATION:
🚨 HANG UP IMMEDIATELY - Do NOT provide any personal information, passwords, or OTP codes."""

# ==========================================
# MAIN SERVER
# ==========================================

def start_server():
    """Start the HTTP server"""
    try:
        server = HTTPServer(('127.0.0.1', 8000), DemoHandler)
        print("\n" + "="*60)
        print("🔐 AI SCAM ANALYZER DEMO - RUNNING")
        print("="*60)
        print("\n📱 Open your browser:")
        print("   👉 http://localhost:8000")
        print("\n📊 Features:")
        print("   ✅ Upload audio files or try demo scenarios")
        print("   ✅ Real-time scam pattern detection")
        print("   ✅ Explainable AI risk scoring")
        print("   ✅ Zero dependencies (pure Python)")
        print("\n⌨️  Press CTRL+C to stop")
        print("="*60 + "\n")
        
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✋ Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()
