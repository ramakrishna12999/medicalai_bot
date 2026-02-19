from flask import Flask, request, jsonify, session
from flask_cors import CORS
import google.generativeai as genai
import os
import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

# Configuration
GEMINI_API_KEY = "AIzaSyBi-rE-_xyIyurswuViFZRbdHuc9_ZNSkE"  # Replace with your key
MODEL = "gemini-2.5-flash"

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name=MODEL)

# Emergency keywords
EMERGENCY_KEYWORDS = [
    "chest pain", "heart attack", "can't breathe", "cannot breathe",
    "difficulty breathing", "stroke", "unconscious", "unresponsive",
    "severe bleeding", "overdose", "suicide", "kill myself",
    "not breathing", "seizure", "anaphylaxis",
]

SYSTEM_PROMPT = """
You are MedAssist AI, a knowledgeable and empathetic medical information assistant.

CORE RESPONSIBILITIES:
1. Answer general medical and health questions clearly and accurately.
2. Explain medical conditions, symptoms, and terminology in plain language.
3. Provide information about medications — uses, side effects, and precautions.
4. Offer wellness and preventive care advice.
5. Guide users on WHEN and WHERE to seek professional help.

SAFETY RULES (MUST FOLLOW):
- NEVER diagnose. Use: "This may suggest…", "Common causes include…"
- NEVER prescribe. Say: "Dosage must be set by your doctor or pharmacist."
- For EMERGENCIES, say: "CALL 911 NOW / GO TO THE NEAREST ER IMMEDIATELY."
- Always clarify you are an AI, not a licensed physician.
- Be compassionate, clear, and non-alarmist.
"""

# Store chat sessions (in production, use a database)
chat_sessions = {}

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    # Check for emergency
    is_emergency = any(kw in user_message.lower() for kw in EMERGENCY_KEYWORDS)
    
    if is_emergency:
        return jsonify({
            'response': "🚨 **EMERGENCY DETECTED**\n\nPlease call 911 immediately or go to your nearest emergency room. Do not wait.\n\n*This is an automated emergency detection - please seek immediate medical attention.*",
            'is_emergency': True,
            'timestamp': datetime.datetime.now().isoformat()
        })
    
    # Get or create chat session
    if session_id not in chat_sessions:
        chat_sessions[session_id] = model.start_chat(history=[])
    
    try:
        response = chat_sessions[session_id].send_message(user_message)
        return jsonify({
            'response': response.text,
            'is_emergency': False,
            'timestamp': datetime.datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'response': f"Error: {str(e)}",
            'is_emergency': False,
            'error': True,
            'timestamp': datetime.datetime.now().isoformat()
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset_chat():
    data = request.json
    session_id = data.get('session_id', 'default')
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)