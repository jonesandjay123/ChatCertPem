document.addEventListener("DOMContentLoaded", function () {
  const chatBox = document.getElementById("chat-box");
  const userInput = document.getElementById("user-input");
  const sendButton = document.getElementById("send-button");

  // Function to send message
  function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    // Add user message to chat box
    addMessageToChatBox(message, "user-message");

    // Clear input box
    userInput.value = "";

    // Add loading indicator
    const loadingElement = document.createElement("div");
    loadingElement.className = "loading";
    loadingElement.textContent = "Thinking...";
    chatBox.appendChild(loadingElement);

    // Scroll to bottom
    scrollToBottom();

    // Send request to backend
    fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question: message }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network request failed");
        }
        return response.json();
      })
      .then((data) => {
        // Remove loading indicator
        chatBox.removeChild(loadingElement);

        // Add bot response to chat box
        if (data.answer) {
          addMessageToChatBox(data.answer, "bot-message");
        } else if (data.error) {
          addMessageToChatBox("Error: " + data.error, "system-message");
        }
      })
      .catch((error) => {
        // Remove loading indicator
        if (loadingElement.parentNode === chatBox) {
          chatBox.removeChild(loadingElement);
        }

        // Add error message
        addMessageToChatBox(
          "Request failed: " + error.message,
          "system-message"
        );
      });
  }

  // Function to add message to chat box
  function addMessageToChatBox(text, className) {
    const messageDiv = document.createElement("div");
    messageDiv.className = "message " + className;

    const paragraph = document.createElement("p");
    paragraph.textContent = text;
    messageDiv.appendChild(paragraph);

    chatBox.appendChild(messageDiv);

    // Scroll to bottom
    scrollToBottom();
  }

  // Function to scroll to bottom
  function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  // Click send button to send message
  sendButton.addEventListener("click", sendMessage);

  // Press Enter key to send message
  userInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
});
