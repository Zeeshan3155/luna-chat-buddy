import os
import requests
import re
import edge_tts
import io
from dotenv import load_dotenv


class TextProcessor:
    def __init__(self):
        load_dotenv()
        self.url = "https://api.languagetoolplus.com/v2/check"
        self.sapling_api_key = os.getenv("sapling_API_KEY")
        self.message_counter = 0
        self.messages = []
        self.correct_message = []
        self.emoji_pattern = re.compile(
            u'['
            u'\U0001F600-\U0001F64F'  # emoticons
            u'\U0001F300-\U0001F5FF'  # symbols & pictographs
            u'\U0001F680-\U0001F6FF'  # transport & map symbols
            u'\U0001F700-\U0001F77F'  # alchemical symbols
            u'\U0001F780-\U0001F7FF'  # Geometric Shapes Extended
            u'\U0001F800-\U0001F8FF'  # Supplemental Arrows-C
            u'\U0001F900-\U0001F9FF'  # Supplemental Symbols and Pictographs
            u'\U0001FA00-\U0001FA6F'  # Symbols and Pictographs Extended-A
            u'\U0001FA70-\U0001FAFF'  # Symbols and Pictographs Extended-B
            u'\U00002702-\U000027B0'  # Dingbats
            u'\U0000200D'  # Zero width joiner (ZWJ)
            u'\U0000200C'  # Zero width non-joiner (ZWNJ)
            u'\U0001F1E0-\U0001F1FF'  # Flags (iOS)
            u'\U0001F004-\U0001F0CF'  # Mahjong tiles, playing cards
            u']+'
        )

    async def de_emojify(self, text):
        clean_text = re.sub(self.emoji_pattern, '', text)
        data = await self.text_to_speech(clean_text)
        return data

    async def text_to_speech(self, text):
        try:
            # Generate speech using edge_tts
            tts = edge_tts.Communicate(text, "en-US-AvaNeural")
            audio_stream = io.BytesIO()
            async for chunk in tts.stream():
                if chunk["type"] == "audio":
                    audio_stream.write(chunk["data"])

            audio_stream.seek(0)
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(BASE_DIR, "assets", "output.mp3")

            with open(file_path, "wb") as f:
                f.write(audio_stream.getvalue())
            return {"file_path": file_path}
        except Exception as e:
            return None

    def append_message(self, text):
        self.messages.append(text)

    def sapling_api(self, text):
        try:
            response = requests.post(
                "https://api.sapling.ai/api/v1/edits",
                json={
                    "key": self.sapling_api_key,
                    "text": text,
                    "session_id": "test session",
                    "auto_apply": True,
                }
            )
            text_html = text
            resp_json = response.json()
            if 200 <= response.status_code < 300:
                if resp_json["edits"]:
                    for matches in sorted(resp_json["edits"], key=lambda x: x["start"], reverse=True):
                        start = matches["start"]
                        end = matches["end"]

                        text_html = (
                                text_html[:start] +
                                "<span class='highlight-error'>" + text_html[start:end] + "</span>" +
                                text_html[end:]
                        )
                    corrected_text = resp_json["applied_text"]
                    data = {
                        "text_html": text_html,
                        "corrected_text": corrected_text,
                        "changes": True
                    }

                    return data
                else:
                    data = {
                        "corrected_text": text,
                        "changes": False
                    }
                    return data

            else:
                print("Error: ", resp_json)
        except Exception as e:
            print("Error: ", e)

    def language_tool(self, text):
        data = {
            "text": text,
            "language": "en-US"
        }

        text_html = text

        try:
            response = requests.post(url=self.url, data=data).json()
            if not response["matches"]:
                data = {
                    "corrected_text": text,
                    "changes": False
                }
                return data
            for matches in sorted(response["matches"], key=lambda x: x["offset"], reverse=True):
                start = matches["offset"]
                end = matches["offset"] + matches["length"]
                text = (
                        text[:start] + matches["replacements"][0]["value"] + text[end:]
                )
                text_html = (
                        text_html[:start] + "<span class='highlight-error'>" +
                        text_html[start: end]
                        + "</span>" + text_html[end:]
                )

            data = {
                "text_html": text_html,
                "corrected_text": text,
                "changes": True
            }
            return data
        except Exception as e:
            print(f"Error with the LanguageTool API request: {e}")
            return "Error checking sentence. Please try again later."

    def check_sentences(self):
        while True:
            if self.messages:
                text = self.messages.pop(0)
                self.message_counter += 1
                if self.message_counter % 2 == 1:
                    data = self.language_tool(text)
                    return data

                else:
                    data = self.sapling_api(text)
                    return data

            else:
                break
