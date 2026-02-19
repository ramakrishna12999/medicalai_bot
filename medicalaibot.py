import os
import json
import time
import datetime
import textwrap
import re
import google.generativeai as genai

# ──────────────────────────────────
#  CONFIG  (edit these if needed)
# ──────────────────────────────────
# IMPORTANT: For security, consider using environment variables instead of hardcoding
GEMINI_API_KEY = "AIzaSyBi-rE-_xyIyurswuViFZRbdHuc9_ZNSkE"  # Replace with your actual key
MODEL          = "gemini-2.5-flash"  # or "gemini-pro" if 1.5-flash isn't available
MAX_TOKENS     = 1024
TEMPERATURE    = 0.4

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
- For EMERGENCIES (chest pain, stroke, severe bleeding, suicidal thoughts),
  say: "CALL 911 NOW / GO TO THE NEAREST ER IMMEDIATELY."
- Always clarify you are an AI, not a licensed physician.
- Be compassionate, clear, and non-alarmist.

RESPONSE FORMAT:
- Use Markdown: headers (##), bullet points, **bold** for key terms.
- Structure complex topics: Overview → Details → Recommendations → When to See a Doctor.
- End with a gentle reminder to consult a healthcare professional when relevant.
""".strip()

EMERGENCY_KEYWORDS = [
    "chest pain", "heart attack", "can't breathe", "cannot breathe",
    "difficulty breathing", "stroke", "unconscious", "unresponsive",
    "severe bleeding", "overdose", "suicide", "kill myself",
    "not breathing", "seizure", "anaphylaxis",
]

print("✅ Configuration loaded.")

# ─────────────────────────────────────────────────────────────
# Core Classes
# ─────────────────────────────────────────────────────────────

# ── Conversation Memory ───────────────────────────────────────
class ConversationManager:
    def __init__(self, max_turns: int = 20):
        self.max_turns = max_turns
        self.history: list[dict] = []

    def add(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        # Prune oldest pairs beyond max_turns
        if len(self.history) > self.max_turns * 2:
            self.history = self.history[-(self.max_turns * 2):]

    def to_gemini_history(self) -> list[dict]:
        """
        Convert history to Gemini format.
        """
        gemini_msgs = []
        for msg in self.history[:-1]:  # exclude the latest user message
            role = "model" if msg["role"] == "assistant" else "user"
            gemini_msgs.append({
                "role": role,
                "parts": [msg["content"]]
            })
        return gemini_msgs

    def latest_user_message(self) -> str:
        """Return the last user message to send as the current prompt."""
        for msg in reversed(self.history):
            if msg["role"] == "user":
                return msg["content"]
        return ""

    def clear(self):
        self.history.clear()

    def save(self, filename: str = "medassist_session.json"):
        data = {
            "app": "MedAssist AI (Gemini)",
            "model": MODEL,
            "saved_at": datetime.datetime.now().isoformat(),
            "messages": self.history,
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return filename

# ── LLM Client ────────────────────────────────────────────────
class MedicalLLMClient:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=MODEL,
            generation_config={
                "temperature": TEMPERATURE,
                "max_output_tokens": MAX_TOKENS,
            },
            system_instruction=SYSTEM_PROMPT
        )

    def chat(self, conversation: "ConversationManager", retries: int = 3) -> str:
        """
        Send message to Gemini with conversation history.
        """
        history = conversation.to_gemini_history()
        user_text = conversation.latest_user_message()

        for attempt in range(1, retries + 1):
            try:
                # Start chat with history
                chat = self.model.start_chat(history=history)
                response = chat.send_message(user_text)
                return response.text

            except Exception as e:
                err_str = str(e).lower()
                if "quota" in err_str or "rate" in err_str:
                    raise RuntimeError("⚠️ Rate limit hit. Please wait and try again.")
                if "api key" in err_str or "authentication" in err_str or "invalid" in err_str:
                    raise RuntimeError("❌ Invalid API key. Check GEMINI_API_KEY in this script.")
                if "not found" in err_str or "model" in err_str:
                    raise RuntimeError("❌ Model not found. Try using 'gemini-1.5-flash' or 'gemini-pro'")
                if attempt < retries:
                    time.sleep(2 * attempt)
                    continue
                raise RuntimeError(f"❌ API error after {retries} attempts: {e}")

        raise RuntimeError("❌ Failed after retries.")

# ── Safety Layer ──────────────────────────────────────────────
class SafetyLayer:
    @staticmethod
    def is_emergency(text: str) -> bool:
        lower = text.lower()
        return any(kw in lower for kw in EMERGENCY_KEYWORDS)

def main():
    print("MedAssist AI (Gemini API Edition) — CLI Mode\nType 'exit' to quit.\n")
    
    # Check if API key is set
    if GEMINI_API_KEY == "YOUR_API_KEY_HERE" or GEMINI_API_KEY == "":
        print("❌ ERROR: Please set your Gemini API key in the script.")
        print("Get your API key from: https://makersuite.google.com/app/apikey")
        return
        
    conversation = ConversationManager()
    llm = MedicalLLMClient(api_key=GEMINI_API_KEY)
    safety = SafetyLayer()
    
    welcome = (
        "👋 Hello! I'm MedAssist AI (powered by Gemini).\n"
        "I can help you with:"
        "\n- Understanding symptoms and medical conditions"
        "\n- Explaining medications and side effects"
        "\n- General wellness and preventive care"
        "\n- Guidance on when to seek professional help\n"
        "⚠️ I'm an AI assistant, not a doctor. Always consult a licensed healthcare professional for personal medical decisions.\n"
        "How can I help you today?"
    )
    print(welcome)
    conversation.add("assistant", welcome)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ("exit", "quit"):
                break
            if not user_input:
                continue
                
            if safety.is_emergency(user_input):
                print("\n🚨 EMERGENCY DETECTED — CALL 911 NOW or GO TO YOUR NEAREST ER IMMEDIATELY. Do not wait.")
                continue
                
            conversation.add("user", user_input)
            
            try:
                reply = llm.chat(conversation)
            except RuntimeError as e:
                reply = f"⚠️ Error: {e}\nPlease check your API key and try again."
            
            conversation.add("assistant", reply)
            print(f"\nMedAssist AI: {reply}")
            
        except KeyboardInterrupt:
            print("\n\nSession ended by user.")
            break
        except Exception as e:
            print(f"\n⚠️ Unexpected error: {e}")
    
    print("\nSession ended. Goodbye! 👋")

if __name__ == "__main__":
    main()