
# Luna Chat Buddy

Luna Chat Buddy is a general-purpose conversational AI assistant that not only engages users in meaningful conversation but also automatically corrects grammar and spelling mistakes in the user's input. Users can interact with Luna using text or voice input, making it a versatile tool for practicing and improving English fluency.

🔗 Live Demo: https://zeeshan3155-luna-chat-buddy.hf.space


## Features
🗣️ voice and text input supported

🔍 Grammar and spelling correction in real-time

🤖 Smart, natural conversation powered by Mistral AI

🧠 Text-to-speech responses using Edge TTS

🌐 Web-based interface built with HTML, CSS, and JavaScript

🐳 Docker support for containerized deployment

⚙️ Backend powered by Flask and Uvicorn

🧾 LanguageTool server for grammar correction
## Technologies Used
#### Frontend:

- HTML, CSS, JavaScript

#### Backend:

- Python

- Flask

- Uvicorn

- Mistral AI (text generation)

- Edge TTS (text-to-speech)

#### Others:

- Docker (for containerization)

- LanguageTool (Java-based grammar correction)

- SpeechRecognition (voice input)
## Getting Started
### 1. Clone the Repository
```bash
git clone https://github.com/Zeeshan3155/luna-chat-buddy.git
cd luna-chat-buddy
```
### 2. LanguageTool Setup
To enable grammar and spelling correction, this app uses [LanguageTool](https://languagetool.org/).

1. Download the standalone LanguageTool server:  
   👉 https://languagetool.org/download/LanguageTool-stable.zip

2. Extract the ZIP and move the contents into this directory:
- app/languagetool/
### 2. Set Up API Key
- Sign up at Mistral
- Get your API key
- Create a .env file in the project root:
```env
english_coach_API_KEY=your_api_key_here
```
### 3. Install Python Dependencies
```cmd
pip install -r requirements.txt
```

### 4. Run Locally (Without Docker)
#### Start the FastAPI Server
```cmd
uvicorn app.main:app --host 0.0.0.0 --port 7860
```

#### Start the LanguageTool Server
Open a new terminal or bash shell inside the ./app/language-tool directory:
```bash
java -cp languagetool-server.jar org.languagetool.server.HTTPServer --port 8081
```

### Run with Docker
```cmd
docker build -t my-chat-buddy .
docker run --env-file .env -p 7860:7860 my-chat-buddy
```
⚠️ Note: The LanguageTool server doesn't need to be run manually outside Docker since it is bundled in the container.


## Project Structure
```
root/
│
├── app/
│   ├── assets/
│   ├── language-tool/
│   ├── static/
│   │    ├── script.js
│   │    └── styles.js
│   ├── templates/
│   │   └── index.html
│   ├── main.py  
│   ├── utils.py
│
├── .dockerignore
├── .gitignore
├── Dockerfile
├── requirements.txt
└── README.md
```
## How It Works
1. User inputs a message via text or microphone

2. Audio input (if any) is converted to text

3. The input is corrected using LanguageTool

4. The corrected prompt is passed to Mistral AI for response generation

5. The response is converted to speech using Edge TTS

6. Response is displayed and spoken aloud
## Requirements
- Python 3.8+
- Java (for LanguageTool)
- Docker (optional)
## License
This project is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0.txt).