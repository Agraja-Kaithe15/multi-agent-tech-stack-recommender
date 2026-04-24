# Multi-Agent Tech Stack Recommender

A simple and modular **multi-agent system** that recommends a suitable tech stack based on the user's experience level.

The system simulates how different AI agents collaborate to analyze input, retrieve data, make decisions, and generate explanations.

Built using **Streamlit** for the UI and **Google Gemini API** for AI-powered explanations.

---

## 🚀 Overview

This project demonstrates a **multi-agent pipeline** where each agent performs a specific role in the recommendation process.

### 🔄 Workflow

1. User selects experience level
2. Analyzer Agent processes input
3. Research Agent fetches matching tech stack
4. Decision Agent finalizes selection
5. Explanation Agent generates AI-based explanation

---

## 🤖 Agents

| Agent                 | Role                                           |
| --------------------- | ---------------------------------------------- |
| **Analyzer Agent**    | Converts user input into a standardized format |
| **Research Agent**    | Retrieves matching tech stack from dataset     |
| **Decision Agent**    | Finalizes the recommended stack                |
| **Explanation Agent** | Uses Gemini AI to explain the recommendation   |

---

## 🧠 Tech Stack

* **Python 3.10+**
* **Streamlit** — Frontend UI
* **Google Gemini API** — AI explanation
* **python-dotenv** — Environment variable handling
* **JSON** — Tech stack dataset

---

## ⚙️ Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-username/tech-stack-recommender.git
cd tech-stack-recommender
```

### 2. Create virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
# OR
source .venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the root directory:

```
GOOGLE_API_KEY=your_api_key_here
```

---

### 5. Run the application

```bash
streamlit run app.py
```

Open in browser:

```
http://localhost:8501
```

---

## 📁 Project Structure

```
.
├── app.py                  # Streamlit UI
├── agents.py              # Multi-agent pipeline logic
├── config.py              # API key & configuration
├── tools/
│   ├── tech_catalog.py    # Loads JSON dataset
│   ├── tech_search.py     # Search logic
├── data/
│   └── tech_stack.json    # Tech stack dataset
├── outputs/               # (optional) generated outputs
├── requirements.txt
├── .env.example
└── README.md
```

---

## 💡 Example

### Input:

* Experience: Beginner

### Output:

* Frontend: React
* Backend: Node.js
* Database: MongoDB
* Hosting: Vercel

👉 Plus an AI-generated explanation of why this stack is suitable.

---

## 🌟 Features

* Multi-agent architecture (modular design)
* AI-powered explanations using Gemini
* Clean and beginner-friendly UI
* JSON-based configurable dataset
* Easy to extend and customize

---

## ⚠️ Limitations

* Currently based only on experience level
* Limited dataset (static recommendations)
* Decision agent uses simple logic (no ranking)

---

## 📌 Future Improvements

* Add project type (Web, AI, Mobile)
* Provide multiple recommendations with ranking
* Add user preferences and goals
* Improve decision-making logic
* Deploy on cloud platforms

---

## 🔐 Security Notes

* Do NOT commit `.env` file
* Keep API keys private
* Use environment variables or Streamlit secrets

---

## 📄 License

This project is for educational purposes.

---

## 🙌 Acknowledgment

Inspired by multi-agent systems and AI-based recommendation engines.

---
