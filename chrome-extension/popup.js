// File: popup.js

document.addEventListener('DOMContentLoaded', () => {
  const transcriptDisplay = document.getElementById('transcript-display');
  const copyBtn = document.getElementById('copy-btn');
  const sendBtn = document.getElementById('send-btn');

  // --- 1. Load and display the saved transcript ---
  chrome.storage.local.get(['transcript'], (result) => {
    if (result.transcript) {
      transcriptDisplay.value = result.transcript;
    } else {
      transcriptDisplay.value = "No transcript captured yet. Enable captions in a Google Meet call.";
    }
  });

  // --- 2. Implement the "Copy Transcript" button ---
  copyBtn.addEventListener('click', () => {
    transcriptDisplay.select();
    document.execCommand('copy');
    
    // Provide user feedback
    copyBtn.textContent = 'Copied!';
    setTimeout(() => {
      copyBtn.textContent = 'Copy Transcript';
    }, 2000);
  });

  // --- 3. Implement the "Send to Summarizer" button ---
  sendBtn.addEventListener('click', () => {
    // IMPORTANT: Replace this with your actual deployed Streamlit app URL
    const streamlitAppUrl = 'https://ai-meet-summarizer.streamlit.app/';
    
    const transcript = transcriptDisplay.value;
    if (transcript && !transcript.startsWith("No transcript captured")) {
      // We must encode the transcript to make it safe to pass in a URL.
      // btoa() is a simple way to do Base64 encoding.
      const encodedTranscript = btoa(transcript);
      
      const finalUrl = `${streamlitAppUrl}?transcript=${encodedTranscript}`;
      
      // Open the Streamlit app in a new tab with the transcript
      chrome.tabs.create({ url: finalUrl });
    }
  });
});