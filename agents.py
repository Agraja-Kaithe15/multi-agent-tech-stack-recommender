# ===== IMPORTS =====
import google.generativeai as genai
from config import GOOGLE_API_KEY, GEMINI_MODEL
from tools.tech_search import search_tech_stack

# ===== GEMINI SETUP =====
if not GOOGLE_API_KEY:
    raise ValueError("GEMINI API key not found. Check your .env file.")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)


# =========================================================
# 🧠 FUNCTIONAL AGENTS (MAIN SYSTEM)
# =========================================================

# ===== AGENT 1: ANALYZER =====
def analyzer_agent(user_input):
    return user_input["experience"].lower()


# ===== AGENT 2: RESEARCH =====
def research_agent(level):
    result = search_tech_stack(level)

    if not result:
        raise ValueError(f"No tech stack found for level: {level}")

    return {
        "frontend": result["frontend"],
        "backend": result["backend"],
        "database": result["database"],
        "hosting": result["hosting"]
    }


# ===== AGENT 3: DECISION =====
def decision_agent(options):
    return options


# ===== AGENT 4: EXPLANATION (GEMINI AI) =====
def explanation_agent(stack):
    prompt = f"""
Explain this tech stack in simple terms:

Frontend: {stack['frontend']}
Backend: {stack['backend']}
Database: {stack['database']}
Hosting: {stack['hosting']}

Keep the explanation short, simple, and professional.
"""

    response = model.generate_content(prompt)
    return response.text


# =========================================================
# 📘 EXPLANATION AGENTS (FOR REQUIREMENT / VIVA)
# =========================================================

# ===== INPUT AGENT =====
def input_agent():
    return """
📥 Input:
The user provides their experience level:
- Beginner
- Intermediate
- Expert
"""


# ===== OUTPUT AGENT =====
def output_agent():
    return """
📤 Output:
The system generates:
- Frontend technology
- Backend technology
- Database
- Hosting platform
- AI-based explanation of the selected stack
"""


# ===== USER GUIDE AGENT =====
def user_guide_agent():
    return """
👤 How to Use:
1. Select your experience level from the dropdown
2. Click the 'Get Recommendation' button
3. View the recommended tech stack
4. Read the AI-generated explanation
"""