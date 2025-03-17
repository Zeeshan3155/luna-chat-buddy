from mistralai import Mistral
from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from dotenv import load_dotenv
from app.utils import TextProcessor

app = FastAPI()

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")
app.mount("/assets", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "assets")), name="assets")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

load_dotenv()

API_KEY = os.getenv("english_coach_API_KEY")
model = "mistral-small-latest"

client = Mistral(api_key=API_KEY)

tc = TextProcessor()


class MessageBody(BaseModel):
    content: str


def reset_conversation_history():
    return [{"role": "system",
             "content": "You are a friendly and engaging chat buddy named Luna. Your goal is to have fun, meaningful, "
                        "and thoughtful conversations. Be casual, approachable, and supportive. Keep responses "
                        "conversational, use humor where appropriate, ask follow-up questions, and match the user's "
                        "tone. Feel free to use emojis to enhance the conversation and make it more engaging. Keep "
                        "things natural, avoid overly formal language, and ensure the chat feels like a real "
                        "conversation."}]


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

        conversation_history.append({"role": "user", "content": message.content})
        chat_response = client.chat.complete(
            model=model,
            messages=conversation_history,
            max_tokens=max(80, min(len(message.content.split()) * 10, 500)),
            temperature=0.7,
            top_p=0.85,
        )
        text = chat_response.choices[0].message.content

        conversation_history.append({"role": "assistant", "content": text})
        data = await tc.de_emojify(text)
        if os.path.exists(data["file_path"]):
            return {"bot_response": text}

        else:
            return {"error": "Audio generation failed"}

    except Exception as e:
        return {"error": str(e)}


@app.post("/grammar")
async def spell_checker(message: MessageBody):
    try:
        tc.append_message(message.content)
        data = tc.check_sentences()
        return data
    except Exception as e:
        return {"error": str(e)}
