import os
import json
from datetime import datetime
import uuid
import requests # Import the requests library
import google.generativeai as genai

# --- Configuration ---
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
except KeyError:
    print("🚨 Error: GEMINI_API_KEY environment variable not set!")

DATA_FILE = "meetings.json"

# ... (process_transcript, save_meeting, and load_meetings functions remain unchanged) ...
def process_transcript(transcript: str) -> dict:
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = f"""You are an expert meeting analyst. Your task is to analyze the following meeting transcript and provide a concise summary and a list of action items in a valid JSON format with two keys: "summary" and "action_items".
    - The "summary" should be a brief paragraph capturing the key decisions and outcomes of the meeting.
    - The "action_items" should be a list of JSON objects. Each object must have the following keys: "task", "owner", "deadline", and "completed".
    - Infer the owner and deadline from the context. If a deadline is relative (e.g., "by Friday"), convert it to a specific date. Assume today's date is {datetime.now().strftime('%Y-%m-%d')}.
    - If any information (like owner or deadline) is not mentioned, set the value to "Not specified".
    - The "completed" key should always be `false`.
    Here is the transcript:
    ---
    {transcript}
    ---
    """
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except Exception as e:
        print(f"An error occurred while calling the Gemini API: {e}")
        return {"summary": "Error: Could not process the transcript.", "action_items": []}

def save_meeting(analysis_data: dict):
    analysis_data['id'] = str(uuid.uuid4())
    analysis_data['saved_at'] = datetime.now().isoformat()
    all_meetings = load_meetings()
    all_meetings.append(analysis_data)
    with open(DATA_FILE, 'w') as f:
        json.dump(all_meetings, f, indent=2)
    print(f"✅ Meeting {analysis_data['id']} saved successfully.")

def load_meetings() -> list:
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


# --- NEW: Slack Integration Function ---

def export_to_slack(meeting_data: dict):
    """Formats meeting data and sends it to a Slack channel via webhook."""
    try:
        webhook_url = os.environ["SLACK_WEBHOOK_URL"]
    except KeyError:
        print("🚨 Error: SLACK_WEBHOOK_URL environment variable not set!")
        print("   Skipping Slack export.")
        return False

    # Format the summary using Slack's blockquote markdown
    summary = meeting_data.get("summary", "No summary available.")
    
    # Format the action items as a bulleted list
    action_items = meeting_data.get("action_items", [])
    action_items_text = ""
    if not action_items:
        action_items_text = "_No action items identified._"
    else:
        for item in action_items:
            task = item.get('task', 'N/A')
            owner = item.get('owner', 'N/A')
            deadline = item.get('deadline', 'N/A')
            action_items_text += f"• *{task}* - Owner: {owner}, Deadline: {deadline}\n"
    
    # Construct the payload using Slack's Block Kit format for a rich message
    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🤖 AI Meeting Summary",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Summary:*\n>{summary.replace('\n', '\n> ')}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Action Items:*\n{action_items_text}"
                }
            }
        ]
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        print("✅ Message successfully posted to Slack!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"🚨 Error posting to Slack: {e}")
        return False

# --- UPDATED: Testing Block ---
if __name__ == "__main__":
    print("Running test for Phase 3...")
    
    # We will use the last saved meeting for the export test
    all_meetings = load_meetings()
    
    if not all_meetings:
        print("❌ No saved meetings found. Run the Phase 2 test first.")
    else:
        latest_meeting = all_meetings[-1]
        print(f"\nTesting Slack export for meeting ID: {latest_meeting.get('id', 'N/A')}")
        export_to_slack(latest_meeting)
        print("\n✅ Phase 3 test completed.")
