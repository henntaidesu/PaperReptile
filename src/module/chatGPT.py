from openai import OpenAI
from src.module.read_conf import ReadConf


class openAI:
    key = None
    model = None
    base_url = None
    prompt = None

    def __init__(self):
        self.conf = ReadConf()
        self.key, self.model, self.base_url, self.prompt = self.conf.ChatGPT()

    def openai_chat(self, question):
        client = OpenAI(
            # This is the default and can be omitted
            api_key=self.key,
            base_url=self.base_url
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": self.prompt
                },
                {
                    "role": "user",
                    "content": question,
                }
            ],
            model=self.model
        )

        return chat_completion.choices[0].message.content
