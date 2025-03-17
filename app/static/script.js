document.addEventListener("DOMContentLoaded", () => {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const micBtn = document.getElementById("mic-btn");

    let typingAnimation;
    function loadLottieAnimation() {
        const typingIndicatorContainer = document.createElement("div");
        typingIndicatorContainer.classList.add("message-container", "typing-anim");
        typingAnimation = lottie.loadAnimation({
            container: typingIndicatorContainer,
            renderer: 'svg',
            loop: true,
            autoplay: true,
            path: 'assets/animations/Animation - 1741897132430.json'
        });
        chatBox.appendChild(typingIndicatorContainer);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function appendMessage(sender, data, changes, isHTML = false) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message-container", sender === "user" ? "user-message" : "bot-message");

        if (isHTML){
            messageDiv.innerHTML = data;
        }
        else{
            const messageElement = document.createElement("p");
            messageElement.classList.add("message");
            const button = document.createElement("button");
            const logo = document.createElement("i");
            if (changes === true) {
                button.classList.add("action-btn");
                button.classList.add("exclamation-btn");
                logo.classList.add("fa-solid", "fa-exclamation");
                button.appendChild(logo);
                button.addEventListener("click", function() {
                    messageElement.innerHTML = data.corrected_text;
                    button.classList.remove("exclamation-btn");
                    button.classList.add("tick-btn");
                    logo.classList.remove("fa-solid", "fa-exclamation");
                    logo.classList.add("fa-solid", "fa-check")
                })
                messageDiv.appendChild(button);
                messageElement.innerHTML = data.text_html;
                messageDiv.appendChild(messageElement);
            } else {
                button.classList.add("action-btn");
                button.classList.add("tick-btn");
                logo.classList.add("fa-solid", "fa-check");
                button.appendChild(logo);
                messageDiv.appendChild(button);
                messageElement.innerText = data.corrected_text;
                messageDiv.appendChild(messageElement);
            }

        }
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.lang = "en-US";

        let isRecording = false;
        micBtn.addEventListener("click", () => {
            if (isRecording) {
                isRecording = false
                recognition.stop()
                micBtn.style.color = "";
            } else {
                isRecording = true;
                micBtn.style.color = "red";
                recognition.start();
            }
        });

        recognition.onresult = (event) => {
            let transcript = event.results[0][0].transcript;
            transcript = transcript.charAt(0).toUpperCase() + transcript.slice(1);
            userInput.value = transcript;
            micBtn.style.color = "";  // Reset button style
        };

        recognition.onaudioend = () => {
            isRecording = false;
            recognition.stop();
            micBtn.style.color= "";
        };

        recognition.onspeechend = () => {
        isRecording = false;
        recognition.stop();
        micBtn.style.color= "";
        };

        recognition.error = (event) => {
        isRecording = false;
            console.error("Speech recognition error", event);
            micBtn.style.color = "";
        };
    } else {
        alert("Speech recognition is not supported in this browser.");
        micBtn.style.display = "none";
    }

     async function sendMessage() {
        const message = userInput.value.trim();
        if (message === "") return;

        const grammar_response = await fetch("http://127.0.0.1:7860/grammar", {
                                method: "POST",
                                headers: {
                                    "Content-Type": "application/json",
                                },
                                body: JSON.stringify({"content": message }),
                            });

        const grammar_data = await grammar_response.json();

        if (grammar_data.changes===true) {
            appendMessage("user", grammar_data, changes=true);
        } else {
            appendMessage("user", grammar_data, changes=false);
        }

        loadLottieAnimation()
        try {
            const response = await fetch("http://127.0.0.1:7860/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({"content": message }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const bot_data = await response.json();
            const audioURL = "http://127.0.0.1:7860/assets/output.mp3";
            const audio = new Audio(audioURL);
            audio.play().catch(error => console.error("Playback error:", error));

            document.querySelector(".typing-anim").remove();

            appendMessage("AI", marked.parse(bot_data.bot_response),  changes=false, isHTML=true);  // Display AI response
        } catch (error) {
            console.error("Error:", error);
            appendMessage("Error", "Failed to fetch response.");
        }

        userInput.value = "";
    }

    // Send message on button click
    sendBtn.addEventListener("click", sendMessage);

    // Send message on Enter key press
    userInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") sendMessage();
    });
});


