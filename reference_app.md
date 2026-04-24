# Multi-Agent AI – Tech Stack Recommender

## 1. Introduction

### 1.1 Lab Overview

In this project, you act as an **AI system designer** building a **multi-agent tech stack recommender system**.

Instead of manually selecting technologies, you design a system where multiple agents collaborate to:
- Understand user requirements
- Recommend a suitable tech stack
- Explain the decision clearly

This simulates a real-world scenario where AI assists developers in choosing the right tools.

---

## 1.2 Learning Outcome

By completing this project, you will learn:

- How to design a **multi-agent system**
- How agents can collaborate step-by-step
- How to use **LLMs (Gemini)** for explanation
- How to structure input → process → output pipeline

---

## 2. System Overview

Your system consists of **4 agents**:

| Agent | Role |
|------|------|
| Analyzer Agent | Understands user input |
| Research Agent | Finds suitable tech stack |
| Decision Agent | Finalizes recommendation |
| Explanation Agent | Explains using AI |

---

## 3. Input

User provides:
- Experience level (Beginner / Intermediate / Expert)
- Project type (optional)

---

## 4. Output

System generates:
- Frontend
- Backend
- Database
- Hosting
- AI-based explanation

---

## 5. Agents

### 5.1 Analyzer Agent

- Takes user input
- Classifies experience level

---

### 5.2 Research Agent

- Fetches data from `tech_stack.json`
- Matches stack based on level

---

### 5.3 Decision Agent

- Finalizes selected stack

---

### 5.4 Explanation Agent

- Uses Gemini API
- Generates professional explanation

---

## 6. Workflow

1. User enters input  
2. Analyzer Agent processes it  
3. Research Agent fetches data  
4. Decision Agent selects stack  
5. Explanation Agent explains result  

---

## 7. Tech Stack Used

- Python
- Streamlit (UI)
- Gemini API (AI explanation)
- JSON (data storage)

---

## 8. Key Takeaways

- Multi-agent systems improve modular design
- AI can assist in decision-making
- Structured pipelines are scalable and reusable

---

🎉 **Project Completed: Tech Stack Recommender using Multi-Agent AI**