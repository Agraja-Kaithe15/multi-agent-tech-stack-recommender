# ===== IMPORTS =====
import streamlit as st
from agents import (
    analyzer_agent,
    research_agent,
    decision_agent,
    explanation_agent,
    input_agent,
    output_agent,
    user_guide_agent
)

# ===== UI TITLE =====
st.title("💻 Multi-Agent Tech Stack Recommender")

# ===== USER INPUT =====
st.subheader("🔹 Select Your Experience Level")

experience = st.selectbox(
    "Experience Level",
    ["Beginner", "Intermediate", "Expert"]
)

# ===== BUTTON =====
if st.button("Get Recommendation"):

    try:
        user_input = {"experience": experience}

        # ===== PIPELINE =====
        level = analyzer_agent(user_input)
        stack = research_agent(level)
        final_stack = decision_agent(stack)
        explanation = explanation_agent(final_stack)

        # ===== OUTPUT DISPLAY =====
        st.subheader("✅ Recommended Tech Stack")

        st.write(f"**Frontend:** {final_stack['frontend']}")
        st.write(f"**Backend:** {final_stack['backend']}")
        st.write(f"**Database:** {final_stack['database']}")
        st.write(f"**Hosting:** {final_stack['hosting']}")

        st.subheader("🧠 Explanation")
        st.write(explanation)

    except Exception as e:
        st.error(f"Error: {e}")

# ===== EXPLANATION AGENTS SECTION =====
st.subheader("📘 System Guide")

st.write(input_agent())
st.write(output_agent())
st.write(user_guide_agent())