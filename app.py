

import streamlit as st
import pandas as pd
from core_logic import process_transcript, load_meetings, export_to_slack


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
