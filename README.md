# 🤖 AI Meeting Summarizer

A hackathon project that transforms raw meeting transcripts into concise summaries and actionable tasks using the Google Gemini API and Streamlit.

## ✨ Features

- **AI-Powered Summaries:** Instantly get a summary of your meeting.
- **Action Item Extraction:** Automatically pulls out tasks, assignees, and deadlines.
- **Meeting History:** View and manage past analyses.
- **Slack Integration:** Export key results directly to your Slack channel.

## 🛠️ Tech Stack

- **Framework:** Streamlit
- **Language:** Python
- **LLM:** Google Gemini API

## 🚀 Setup and Run

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/harshaljdave/ai-meeting-summarizer.git](https://github.com/harshaljdave/ai-meeting-summarizer.git)
    cd ai-meeting-summarizer
    ```
2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```
3.  **Set your API Key:**
    ```bash
    Linux/Mac: export GEMINI_API_KEY='YOUR_API_KEY_HERE'
    windows : set GEMINI_API_KEY='YOUR_API_KEY_HERE'
    ```
4.  **Run the app:**
    ```bash
    streamlit run app.py
    ```