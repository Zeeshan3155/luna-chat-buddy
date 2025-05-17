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
        setTimeout(() => {
        chatBox.scrollTop = chatBox.scrollHeight;
    }, 100); // adjust timing if needed
    }

    function appendMessage(sender, data, changes, isHTML = false) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message-container", sender === "user" ? "user-message" : "bot-message");

        if (sender==="AI"){
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
        tippy('.highlight-error:not([data-tippy-initialized])', {
          arrow: true,
          animation: 'elastic',
          delay: [100, 100],
          onShow(instance) {
            instance.reference.setAttribute('data-tippy-initialized', 'true');
          }
        });
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
        const grammar_response = await fetch("/grammar", {
                                method: "POST",
                                headers: {
                                    "Content-Type": "application/json",
                                },
                                body: JSON.stringify({
                                    "text": message
                                }),
                            });

        const grammar_data = await grammar_response.json();

        if (grammar_data.changes===true) {
            appendMessage(sender="user", data=grammar_data, changes=true, isHTML=true);
        } else {
            appendMessage(sender="user", data=grammar_data, changes=false);
        }

        loadLottieAnimation()
        try {
            const chat_response = await fetch("/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({"text": message }),
            });

            if (!chat_response.ok) {
                throw new Error(`HTTP error! Status: ${chat_response.status}`);
            }
            const bot_data = await chat_response.json();

            try {
                const audio_response = await fetch("/get_audio", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ "file_name": bot_data.file_name })
                });
                if (!audio_response.ok) {
                    throw new Error("Failed to fetch audio");
                }
                const audioBlob = await audio_response.blob();
                const audioURL = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioURL);
                audio.play();

                audio.onended = async () => {
                    await fetch("/delete_audio", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ "file_name": bot_data.file_name })
                });
                    };
            } catch (error) {
                console.error("Error playing audio:", error);
            };

            document.querySelector(".typing-anim").remove();

            appendMessage("AI", marked.parse(bot_data.bot_response),  changes=false, isHTML=true);  // Display AI response
        } catch (error) {
            console.error("Error:", error);
            appendMessage("Error", "Failed to fetch response.");
        }

        userInput.value = "";
    }

    sendBtn.addEventListener("click", sendMessage);

    userInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") sendMessage();
    });
});


