  <script>
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");
    const micBtn = document.getElementById("mic-btn");

    // Autofocus input on load
    window.onload = () => userInput.focus();

    chatForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const message = userInput.value.trim();
      if (!message) return;
      appendMessage("user", message);
      userInput.value = "";

      try {
        const response = await fetch(`/get_product?product=${encodeURIComponent(message)}`);
        if (!response.ok) throw new Error("Network response was not ok");
        const data = await response.json();
        appendBotMessage(data);
      } catch (error) {
        appendMessage("bot", "⚠️ Sorry, something went wrong. Please try again.");
      }
    });

    function appendMessage(sender, message) {
      const div = document.createElement("div");
      div.className = `${sender} message`;
      div.textContent = message;
      chatBox.appendChild(div);
      chatBox.scrollTop = chatBox.scrollHeight;
    }

    function appendBotMessage(data) {
      const div = document.createElement("div");
      div.className = `bot message`;

      if (data.product) {
        div.innerHTML = `
          <strong>${data.product}</strong><br>
          💰 Price: ₹${data.price}<br>
          📦 Stock: ${data.stock}<br>
          🔗 <a href="${data.link}" target="_blank" style="color:#87CEFA;">View Product</a><br><br>
          <button class="action-btn" onclick="handleAction('add to cart ${data.product}')">🛒 Add to Cart</button>
          <button class="action-btn buy-now" onclick="handleAction('place order')">💳 Buy Now</button>
        `;
      } else {
        div.textContent = data.message || "I'm not sure how to respond.";
      }

      chatBox.appendChild(div);
      chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function handleAction(command) {
      appendMessage("user", command);
      try {
        const response = await fetch(`/get_product?product=${encodeURIComponent(command)}`);
        if (!response.ok) throw new Error("Network response was not ok");
        const data = await response.json();
        appendBotMessage(data);
      } catch (error) {
        appendMessage("bot", "⚠️ Action failed. Try again.");
      }
    }

    // 🎤 Voice Recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.lang = 'en-US';

      micBtn.addEventListener('click', () => {
        if (micBtn.classList.contains('mic-active')) {
          recognition.stop();
          micBtn.classList.remove('mic-active');
        } else {
          recognition.start();
          micBtn.classList.add('mic-active');
        }
      });

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        userInput.value = transcript;
        recognition.stop();
        micBtn.classList.remove('mic-active');
      };

      recognition.onerror = () => micBtn.classList.remove('mic-active');
    } else {
      micBtn.disabled = true;
      micBtn.innerText = "❌";
    }
  </script>
