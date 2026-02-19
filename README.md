# MedAssist AI — Medical Chatbot (Gemini API Edition)

MedAssist AI is a command-line medical information chatbot powered by Google's Gemini API. It provides general health information, explains medical conditions, medications, and offers wellness advice. **It does not diagnose or prescribe.**

---

## Features
- Answers general medical and health questions
- Explains symptoms, conditions, and medications in plain language
- Offers wellness and preventive care advice
- Guides users on when to seek professional help
- Emergency keyword detection (advises to call 911 for emergencies)
- Runs fully in your terminal (no web or notebook required)

---

## Requirements
- Python 3.8 or higher
- A valid Gemini API key from Google

---

## Installation & Setup

1. **Clone or download this repository.**

2. **Navigate to the project folder:**
   ```
   cd path/to/your/folder/medicalfieldbot
   ```

3. **Install dependencies:**
   ```
   python -m pip install -r requirements.txt
   ```

4. **Set your Gemini API key:**
   - Open `medicalaibot.py` in a text editor.
   - Find the line:
     ```python
     GEMINI_API_KEY = "YOUR_API_KEY_HERE"
     ```
   - Replace `YOUR_API_KEY_HERE` with your actual Gemini API key.

---

## Usage

Run the chatbot in your terminal:

```
python medicalaibot.py
```

You will see a welcome message. Type your health question and press Enter. Type `exit` or `quit` to stop.

---

## Example
```
$ python medicalaibot.py
MedAssist AI (Gemini API Edition) — CLI Mode
Type 'exit' to quit.

👋 Hello! I'm MedAssist AI (powered by Gemini).
How can I help you today?

You: What are the symptoms of flu?
MedAssist AI: ...
```

---

## Notes
- **This tool is for informational purposes only.**
- It does **not** diagnose, treat, or prescribe.
- For emergencies, always call 911 or go to the nearest ER.
- Your API key is kept in the script and not shared.

---

## Troubleshooting
- If you see errors about missing packages, run:
  ```
  python -m pip install -r requirements.txt
  ```
- If you see API key errors, double-check your key in `medicalaibot.py`.
- If you see deprecation warnings for `google.generativeai`, consider updating to `google.genai` in the future.

---

## License
This project is for educational purposes only. Not for clinical or commercial use.
