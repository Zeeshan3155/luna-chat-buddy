from mistralai import Mistral
from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from dotenv import load_dotenv
from app.utils import TextProcessor
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")
app.mount("/assets", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "assets")), name="assets")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

load_dotenv()

API_KEY = os.getenv("english_coach_API_KEY")
model = "mistral-small-latest"

client = Mistral(api_key=API_KEY)

tc = TextProcessor()


class MessageBody(BaseModel):
    text: str


class FilePath(BaseModel):
    file_name: str


def reset_conversation_history():
    return [{"role": "system",
             "content": "You are a friendly and engaging chat buddy named Luna. Your goal is to have fun, meaningful, "
                        "and thoughtful conversations. Be casual, approachable, and supportive. Keep responses "
                        "conversational, use humor where appropriate, ask follow-up questions, and match the user's "
                        "tone. Feel free to use emojis to enhance the conversation and make it more engaging. Keep "
                        "things natural, avoid overly formal language, and ensure the chat feels like a real "
                        "conversation."}]


def get_audio_file_path(file_name: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "assets", file_name)


conversation_history = reset_conversation_history()


@app.get("/")
def root(request: Request):
    try:
        global conversation_history
        conversation_history = reset_conversation_history()
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        return {"error": str(e)}


@app.post("/chat")
async def chat(message: MessageBody):
    try:
        global conversation_history

        conversation_history.append({"role": "user", "content": message.text})
        chat_response = client.chat.complete(
            model=model,
            messages=conversation_history,
            max_tokens=max(80, min(len(message.text.split()) * 10, 500)),
            temperature=0.7,
            top_p=0.85,
        )
        text = chat_response.choices[0].message.content

        conversation_history.append({"role": "assistant", "content": text})
        data = await tc.de_emojify(text)
        file_path = get_audio_file_path(data["file_name"])
        if os.path.exists(file_path):
            return {"bot_response": text, "file_name": data["file_name"]}

        else:
            return {"error": "Audio generation failed"}

    except Exception as e:
        return {"error": str(e)}


@app.post("/grammar")
async def spell_checker(message: MessageBody):
    try:
        data = tc.language_tool(message.text)
        return data
    except Exception as e:
        return {"error": str(e)}


@app.post("/get_audio")
async def get_audio(file: FilePath):
    file_path = get_audio_file_path(file.file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg", filename="output.mp3")
    return {"error": "Audio file not found"}


@app.post("/delete_audio")
async def delete_audio(file: FilePath):
    try:
        file_path = get_audio_file_path(file.file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            return {"message": "File deleted successfully"}
        return {"error": "File not found"}
    except Exception as e:
        return {"error": str(e)}
