import streamlit as st
import pandas as pd
from corelogic import process_transcript, load_meetings, export_to_slack
import base64 # Needed to decode the transcript

# --- Add this block to your Streamlit app ---
# Check for transcript data in the URL query parameters
params = st.query_params
url_transcript = params.get("transcript", "")

# The transcript will be Base64 encoded, so we need to decode it
if url_transcript:
    try:
        decoded_bytes = base64.b64decode(url_transcript)
        url_transcript = decoded_bytes.decode('utf-8')
    except Exception as e:
        st.error(f"Could not decode transcript from URL: {e}")
        url_transcript = ""
# ---------------------------------------------

# In your st.text_area, use the decoded transcript as the default value
transcript_input = st.text_area(
    "Paste your meeting transcript here, or send it from the Chrome Extension.",
    value=url_transcript, # This pre-fills the text area
    height=250
)


st.set_page_config(
    page_title="AI Meeting Summarizer",
    layout="wide",
)


def display_meeting_results(results):
    """A reusable function to display summary and action items."""
    st.markdown(f" Summary")
    st.write(results["summary"])

    st.markdown("  Action Items")
    if results["action_items"]:
        df = pd.DataFrame(results["action_items"])
        st.data_editor(
            df,
            column_config={"completed": st.column_config.CheckboxColumn("Completed?", default=False)},
            hide_index=True,
            use_container_width=True
        )
    else:
        st.write("No action items were identified.")
    
  
    st.divider()
    if st.button(" Send to Slack"):
        with st.spinner("Sending to Slack..."):
            if export_to_slack(results):
                st.toast(" Successfully sent to Slack!")
            else:
                st.error(" Failed to send to Slack.")


with st.sidebar:
    st.title(" AI Meeting Summarizer")
    page = st.radio("Navigation", ["New Meeting", "History"], label_visibility="hidden")


if page == "New Meeting":
    st.title("Process a New Meeting")

    st.subheader("1. Paste Your Meeting Transcript")
    transcript_text = st.text_area(
        "Transcript Input", height=250, placeholder="Paste the full meeting transcript here...", label_visibility="collapsed"
    )

    if st.button("Process Meeting", type="primary"):
        if transcript_text:
            with st.spinner("AI is summarizing, please wait..."):
                results = process_transcript(transcript_text)
                st.session_state["results"] = results
                
        else:
            st.warning("Please paste a transcript before processing.")
    
    st.divider()
    st.subheader("2. Review Your Results")

    if "results" in st.session_state and st.session_state["results"]:
        display_meeting_results(st.session_state["results"])
    else:
        st.write("Your summary and action items will appear here once processed.")


elif page == "History":
    st.title("📖 Meeting History")
    
    meetings = load_meetings()
    
    if not meetings:
        st.write("No past meetings found.")
    else:
       
        meeting_ids = [m["id"] for m in meetings]
        selected_id = st.selectbox("Select a past meeting to view:", meeting_ids)
        
     
        selected_meeting = next((m for m in meetings if m["id"] == selected_id), None)

        if selected_meeting:
            display_meeting_results(selected_meeting)
