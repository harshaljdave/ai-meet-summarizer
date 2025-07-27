import streamlit as st
import json
from datetime import datetime
import requests
import google.generativeai as genai
from supabase import Client

def process_transcript(transcript: str) -> dict:
    """Processes a transcript using the Gemini API."""
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception:
        st.error("Gemini API Key not configured correctly in secrets.")
        return {}
        
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = f"""
    You are an expert meeting analyst. Your task is to analyze the following meeting transcript and provide a concise summary and a list of action items in a valid JSON format with two keys: "summary" and "action_items".

    - The "summary" should be a brief paragraph.
    - The "action_items" should be a list of JSON objects with keys: "task", "owner", "deadline", and "completed".
    - Infer owner and deadline from context. Assume today's date is {datetime.now().strftime('%Y-%m-%d')}. If not mentioned, use "Not specified".
    - "completed" should always be `false`.

    Transcript:
    ---
    {transcript}
    ---
    """
    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Error calling Gemini API: {e}")
        return {}

def save_meeting(supabase: Client, user_id: str, transcript: str, analysis_data: dict):
    """Saves a meeting analysis to the Supabase database for a specific user."""
    if not analysis_data:
        st.error("Cannot save empty analysis.")
        return

    try:
        # This record is what gets inserted into the database.
        # It MUST include the user_id to satisfy the RLS policy.
        record = {
            "user_id": user_id,
            "transcript": transcript,
            "summary": analysis_data.get("summary"),
            "action_items": json.dumps(analysis_data.get("action_items", []))
        }
        
        # The execute() call sends this record to the database.
        response = supabase.table("meetings").insert(record).execute()
        
        # Optional: Check if the insert was successful
        if response.data:
            st.success("Meeting analysis saved successfully!")
        else:
            st.error("Failed to save data. Please check database logs.")

    except Exception as e:
        st.error(f"Error saving to database: {e}")

def load_meetings(supabase: Client, user_id: str) -> list:
    """Loads all meetings for a specific user from the Supabase database."""
    try:
        response = supabase.table("meetings").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"Error loading meeting history: {e}")
        return []

def export_to_slack(meeting_data: dict):
    """Formats and sends meeting data to a Slack channel."""
    try:
        webhook_url = st.secrets["SLACK_WEBHOOK_URL"]
    except Exception:
        st.error("Slack Webhook URL not configured correctly in secrets.")
        return

    summary = meeting_data.get("summary", "No summary available.")
    
    # Check if action_items is a string and load it as JSON
    action_items_raw = meeting_data.get("action_items", [])
    if isinstance(action_items_raw, str):
        try:
            action_items = json.loads(action_items_raw)
        except json.JSONDecodeError:
            action_items = []
    else:
        action_items = action_items_raw

    action_items_text = ""
    if not action_items:
        action_items_text = "_No action items identified._"
    else:
        for item in action_items:
            action_items_text += f"• *{item.get('task', 'N/A')}* - Owner: {item.get('owner', 'N/A')}\n"
    
    payload = { "blocks": [ { "type": "header", "text": { "type": "plain_text", "text": "🤖 AI Meeting Summary", "emoji": True } }, { "type": "section", "text": { "type": "mrkdwn", "text": f"*Summary:*\n>{summary.replace('\n', '\n> ')}" } }, { "type": "divider" }, { "type": "section", "text": { "type": "mrkdwn", "text": f"*Action Items:*\n{action_items_text}" } } ] }
    
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        st.success("Message successfully posted to Slack!")
    except Exception as e:
        st.error(f"Error posting to Slack: {e}")