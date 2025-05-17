import os
import requests
import re
import edge_tts
import io
from dotenv import load_dotenv
import uuid


class TextProcessor:
    def __init__(self):
        load_dotenv()
        self.url = "http://localhost:8081/v2/check"
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

    @staticmethod
    async def text_to_speech(text):
        try:
            # Generate speech using edge_tts
            tts = edge_tts.Communicate(text, "en-US-AvaNeural")
            audio_stream = io.BytesIO()
            async for chunk in tts.stream():
                if chunk["type"] == "audio":
                    audio_stream.write(chunk["data"])

            audio_stream.seek(0)
            unique_file_name = f"output_{uuid.uuid4().hex}.mp3"
            base_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(base_dir, "assets", unique_file_name)

            with open(file_path, "wb") as f:
                f.write(audio_stream.getvalue())
            return {"file_name": unique_file_name}
        except Exception as e:
            return {"error": str(e)}

    def language_tool(self, text):
        data = {
            "text": text,
            "language": "en-US"
        }

        text_html = text

        try:
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            response = requests.post(url=self.url, data=data, headers=headers).json()
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
                        text_html[:start] + f"<span class='highlight-error' data-tippy-content='{matches['message']}'>"
                        +
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
