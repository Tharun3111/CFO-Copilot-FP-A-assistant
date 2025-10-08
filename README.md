# CFO Copilot (FP&A) - Finance Q&A Assistant

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.38.0-FF4B4B.svg)](https://streamlit.io)
[![Tests](https://img.shields.io/badge/tests-6%2F6%20passing-brightgreen.svg)](tests/)

A rule-based AI assistant that answers finance questions directly from structured CSV/Excel data using natural language queries.

🚀 **[Live Demo]((https://cfo-copilot-fp-a-assistant.streamlit.app/))** | 📂 **[GitHub](https://github.com/Tharun3111/CFO-Copilot-FP-A-assistant)**

---

## 🎯 Features

- **Revenue vs Budget Analysis**: Compare actual vs budgeted revenue with variance calculation
- **Gross Margin % Trend**: Visualize gross margin trends over time
- **Operating Expenses Breakdown**: Analyze Opex by category (Marketing, Sales, R&D, Admin)
- **Cash Runway Calculator**: Calculate months of runway based on recent burn rate
- **Multi-Currency Support**: Automatic FX conversion with month-by-month rates
- **Rule-Based NLP**: Fast, deterministic query parsing without LLMs
- **Interactive Dashboard**: Beautiful Streamlit UI with Plotly charts

---

## 📊 Example Questions

Try asking questions like:

- "What was June 2025 revenue vs budget in USD?"
- "Show Gross Margin % trend for the last 3 months"
- "Break down Opex by category for June 2025"
- "What is our cash runway right now?"
- "What was EMEA's revenue in Q2 2024?"
- "Show ParentCo's expenses for 2023"

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Installation
```bash
# Clone the repository
git clone https://github.com/Tharun3111/CFO-Copilot-FP-A-assistant.git
cd CFO-Copilot-FP-A-assistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py

