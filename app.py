import streamlit as st
import pandas as pd
import json
import base64
from supabase import create_client, Client
import corelogic
from datetime import datetime
st.set_page_config(page_title="AI Meeting Summarizer", layout="wide")

@st.cache_resource
def init_connection() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# --- ROBUST SESSION MANAGEMENT ---
# This block is the key to fixing the issue.
# On every script rerun, it checks for a session in st.session_state and
# re-authenticates the supabase client if one is found.
if "user_session" not in st.session_state:
    st.session_state.user_session = None

# If a session exists in the state, tell the supabase client to use it
if st.session_state.user_session:
    supabase.auth.set_session(
        st.session_state.user_session.access_token,
        st.session_state.user_session.refresh_token
    )

# ... (The display_meeting_results function remains the same as before) ...
def display_meeting_results(results):
    st.markdown("### Summary")
    st.write(results.get("summary", "No summary available."))
    st.markdown("### Action Items")
    action_items_raw = results.get("action_items", [])
    action_items = json.loads(action_items_raw) if isinstance(action_items_raw, str) else action_items_raw
    if action_items:
        st.data_editor(pd.DataFrame(action_items), hide_index=True, use_container_width=True)
    else:
        st.write("No action items identified.")
    st.divider()
    if st.button("Send to Slack", key=f"slack_{results.get('id', 'new')}_btn"):
        with st.spinner("Sending to Slack..."):
            corelogic.export_to_slack(results)

# --- APP LAYOUT ---
# If user is not logged in, show the login/signup page.
if st.session_state.user_session is None:
    st.title("🤖 AI Meeting Summarizer")
    st.header("Welcome! Please log in to continue.")
    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])
    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login", use_container_width=True):
                try:
                    # Sign in and save the session object to the state
                    session = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user_session = session.session
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {e}")
    # ... (Signup tab remains the same) ...
    with signup_tab:
        with st.form("signup_form"):
            email = st.text_input("Choose an Email")
            password = st.text_input("Choose a Password", type="password")
            if st.form_submit_button("Sign Up", use_container_width=True):
                try:
                    supabase.auth.sign_up({"email": email, "password": password})
                    st.success("Signup successful! Please log in.")
                except Exception as e:
                    st.error(f"Signup failed: {e}")
else:
    # --- LOGGED-IN USER INTERFACE ---
    user_id = st.session_state.user_session.user.id
    with st.sidebar:
        st.title("🤖 AI Meeting Summarizer")
        st.write(f"Welcome, {st.session_state.user_session.user.email}")
        if st.button("Sign Out", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.user_session = None
            st.rerun()
        st.divider()
        page = st.radio("Navigation", ["New Meeting", "History"], label_visibility="collapsed")

    # ... (The rest of the app logic for "New Meeting" and "History" pages remains the same) ...
    if page == "New Meeting":
        st.title("Process a New Meeting")
        params = st.query_params
        url_transcript = params.get("transcript", "")
        if url_transcript:
            try:
                url_transcript = base64.b64decode(url_transcript).decode('utf-8')
            except Exception:
                st.error("Could not decode transcript from URL.")
                url_transcript = ""
        transcript_text = st.text_area("Paste your transcript here...", value=url_transcript, height=300, label_visibility="collapsed")
        if st.button("Process Meeting", type="primary", use_container_width=True):
            if transcript_text.strip():
                with st.spinner("AI is summarizing..."):
                    results = corelogic.process_transcript(transcript_text)
                    if results:
                        corelogic.save_meeting(supabase, user_id, transcript_text, results)
                        st.session_state["results"] = results
            else:
                st.warning("Please paste a transcript before processing.")
        st.divider()
        st.subheader("Your Results")
        if "results" in st.session_state and st.session_state["results"]:
            display_meeting_results(st.session_state["results"])
        else:
            st.info("Your summary and action items will appear here once processed.")
    elif page == "History":
        st.title("📖 Meeting History")
        meetings = corelogic.load_meetings(supabase, user_id)
        if not meetings:
            st.info("No past meetings found.")
        else:
            meeting_options = {f"Meeting from {datetime.fromisoformat(m['created_at']).strftime('%Y-%m-%d %H:%M')}": m['id'] for m in meetings}
            selected_option = st.selectbox("Select a past meeting to view:", options=meeting_options.keys())
            if selected_option:
                selected_id = meeting_options[selected_option]
                selected_meeting = next((m for m in meetings if m["id"] == selected_id), None)
                if selected_meeting:
                    display_meeting_results(selected_meeting)