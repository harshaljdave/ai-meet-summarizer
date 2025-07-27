// File: content.js

// The new CSS selector for the main container holding all captions.
// We use '.ygicle.VbkSUe' to select an element with BOTH classes.
const CAPTION_CONTAINER_SELECTOR = '.ygicle.VbkSUe';

let captionObserver = null;
let saveTimeout = null;

console.log("Caption Scraper script loaded. Searching for caption container...");

function processAndSaveTranscript() {
  const container = document.querySelector(CAPTION_CONTAINER_SELECTOR);
  if (container) {
    const transcriptText = container.innerText;
    chrome.storage.local.set({ transcript: transcriptText }, () => {
      // console.log("Transcript updated."); // Uncomment for debugging
    });
  }
}

function startObserver(targetNode) {
  if (captionObserver) {
    captionObserver.disconnect(); // Disconnect any previous observer
  }

  captionObserver = new MutationObserver(() => {
    // This function is called on any change. We use a timeout to "debounce"
    // the save operation, so it doesn't run hundreds of times a second.
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(processAndSaveTranscript, 500); // Wait 500ms after last change to save
  });

  // Observe the target node for changes to its children and their content
  captionObserver.observe(targetNode, {
    childList: true,
    subtree: true,
    characterData: true,
  });

  console.log("Observer attached to caption container.");
}

// Google Meet loads content dynamically, so the caption container might not
// exist when the page first loads. We'll use an interval to periodically
// check for it.
const intervalId = setInterval(() => {
  const targetNode = document.querySelector(CAPTION_CONTAINER_SELECTOR);
  if (targetNode) {
    // Once we find the container, we start observing it and stop checking.
    clearInterval(intervalId);
    startObserver(targetNode);
  }
}, 2000); // Check every 2 seconds