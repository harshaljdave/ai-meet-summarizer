# 🤖 AI Meeting Summarizer

A full-stack application that transforms messy meeting conversations into structured summaries and actionable tasks. This project combines a powerful AI backend with a user-friendly web interface and a companion Chrome Extension to capture live meeting captions.

---

### ## 🚀 Live Demo

[**Launch the Web App Here!**](https://your-app.streamlit.app/) *(Replace with your actual Streamlit app URL)*
### Username : p24cs012@coed.svnit.ac.in
### password : qwerty
---

### ## ✨ Key Features

- **AI-Powered Analysis:** Uses the Google Gemini API to generate concise, human-like summaries and extract key action items.
- **Secure User Accounts:** Full user authentication system powered by Supabase, ensuring each user's meeting history is private and secure.
- **Live Caption Scraping:** A companion Chrome Extension that captures live captions directly from Google Meet, eliminating the need for audio files.
- **Persistent History:** All meeting analyses are saved to a cloud database, allowing users to review their history at any time.
- **Interactive UI:** A clean interface built with Streamlit, featuring an interactive data editor for action items.
- **Slack Integration:** Send meeting summaries and tasks directly to a Slack channel with a single click.

---

### ## 🛠️ Tech Stack

- **Web Framework:** Streamlit
- **Database & Authentication:** Supabase
- **AI Model:** Google Gemini Pro
- **Chrome Extension:** JavaScript, HTML, CSS (Manifest V3)
- **Deployment:** Streamlit Community Cloud

---

### ## How It Works

Our application streamlines the process of analyzing meetings into a simple, three-step workflow, moving from live conversation to actionable insights without manual note-taking.

1.  **Capture with the Chrome Extension** 📝
    While in a Google Meet call, the user enables the built-in live captions. Our companion Chrome Extension runs securely in the background, scraping these captions in real-time to build a complete, accurate transcript of the conversation.

2.  **Analyze in the Web App** 🧠
    With a single click, the captured transcript is sent from the extension to our Streamlit web app. The user logs into their secure account, and the AI engine—powered by the Google Gemini API—processes the text to generate a concise summary and a structured list of action items, automatically identifying owners and deadlines.

3.  **Review and Act** 🚀
    The results are instantly displayed and saved permanently to the user's private meeting history, powered by a Supabase database. The user can review past meetings, ask questions about their entire history using our RAG-powered chat, or export key results to Slack to keep their team aligned and accountable.
### ## ⚙️ Setup and Installation

This project has two parts: the Streamlit web app and the Chrome Extension.

---

### ### 1. Web App Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/harshaljdave/ai-meet-summarizer.git](https://github.com/harshaljdave/ai-meet-summarizer.git)
    cd ai-meet-summarizer
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Set up local secrets:**
    * Create a file at `.streamlit/secrets.toml`.
    * Add your API keys and credentials:
        ```toml
        GEMINI_API_KEY = "YOUR_GEMINI_KEY_HERE"
        SLACK_WEBHOOK_URL = "YOUR_SLACK_WEBHOOK_URL_HERE"
        SUPABASE_URL = "YOUR_SUPABASE_PROJECT_URL"
        SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"
        ```

4.  **Run the app locally:**
    ```bash
    streamlit run app.py
    ```

### ### 2. Chrome Extension Setup

1.  **Open Chrome and navigate to `chrome://extensions`.**
2.  **Enable "Developer mode"** using the toggle in the top-right corner.
3.  Click the **"Load unpacked"** button.
4.  Select the `chrome-extension` folder from the cloned repository.
5.  Pin the extension to your toolbar for easy access.
