document.addEventListener("DOMContentLoaded", function () {
  const chatBox = document.getElementById("chat-box");
  const userInput = document.getElementById("user-input");
  const sendButton = document.getElementById("send-button");
  const imageQuestion = document.getElementById("image-question");
  const imageFile = document.getElementById("image-file");
  const uploadImageButton = document.getElementById("upload-image-button");
  const previewContainer = document.getElementById("preview-container");
  const imagePreview = document.getElementById("image-preview");

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

  // Image preview functionality
  imageFile.addEventListener("change", function () {
    const file = this.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        imagePreview.src = e.target.result;
        previewContainer.classList.remove("hidden");
      };
      reader.readAsDataURL(file);
    } else {
      previewContainer.classList.add("hidden");
    }
  });

  // Function to upload and analyze image
  function uploadAndAnalyzeImage() {
    const question = imageQuestion.value.trim();
    const file = imageFile.files[0];

    if (!question) {
      addMessageToChatBox(
        "Please enter a question about the image.",
        "system-message"
      );
      return;
    }

    if (!file) {
      addMessageToChatBox(
        "Please select an image to upload.",
        "system-message"
      );
      return;
    }

    // Add user message to chat box
    addMessageToChatBox(question, "user-message");

    // Add image thumbnail to chat
    const messageDiv = document.createElement("div");
    messageDiv.className = "message user-message";

    const img = document.createElement("img");
    img.src = imagePreview.src;
    img.style.maxWidth = "200px";
    img.style.maxHeight = "200px";
    img.style.display = "block";
    img.style.marginTop = "10px";

    messageDiv.appendChild(img);
    chatBox.appendChild(messageDiv);

    // Scroll to bottom
    scrollToBottom();

    // Add loading indicator
    const loadingElement = document.createElement("div");
    loadingElement.className = "loading";
    loadingElement.textContent = "Analyzing image...";
    chatBox.appendChild(loadingElement);

    // Create form data for upload
    const formData = new FormData();
    formData.append("question", question);
    formData.append("image", file);

    // Send request to backend
    fetch("/process", {
      method: "POST",
      body: formData,
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

        // Clear image upload form
        imageQuestion.value = "";
        imageFile.value = "";
        previewContainer.classList.add("hidden");
      })
      .catch((error) => {
        // Remove loading indicator
        if (loadingElement.parentNode === chatBox) {
          chatBox.removeChild(loadingElement);
        }

        // Add error message
        addMessageToChatBox(
          "Image analysis failed: " + error.message,
          "system-message"
        );
      });
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

  // Click upload button to upload and analyze image
  uploadImageButton.addEventListener("click", uploadAndAnalyzeImage);
});
