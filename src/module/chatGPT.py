from openai import OpenAI
from src.module.read_conf import read_conf


class openAI:
    key = None
    model = None
    base_url = None
    prompt = None

    def __init__(self):
        self.conf = read_conf()
        self.key, self.model, self.base_url, self.prompt = self.conf.ChatGPT()

    def openai_chat(self, question):
        """
        :param question: what you want to ask for
        """

        # prompt = ("你是一个英语专业的高材生，我发给你什么英语句子你都会回复翻译好的中文内容给我，在我给你翻译的语句都为论文标题和论文学科分类"
        #           "我只需要给出翻译,在翻译句子的前面不要给出任何注释，在括号内的文字不要翻译原文返回给我")
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
