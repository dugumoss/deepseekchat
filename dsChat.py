from openai import OpenAI

api_key = "{输入你的API key}"  # 用于存储 API Key
selected_model = "deepseek-chat"  # 默认模型
api_url = "https://api.deepseek.com"  # DeepSeek API URL

msSRT = ".srt"      # 字幕翻译
msCHAT = ".chat" # 对话聊天
msTranslate = ".translate" # 文本翻译

deepseek = None

class DeepSeekChat:
    def __init__(self):
        # 初始化API客户端
        self.client = OpenAI(api_key=api_key, base_url=api_url)
        self.messages = []
        self.results = []
        self.current_mstype = None


    def init_srt_content(self, content, dst_lang: str = 'zh-cn'):
        self.clear()
        prompt = (
            f"You are a professional subtitle translator. Translate the following text into natural and fluent language. "
            f"Use the provided context to optimize phrasing, but do not include it in the output. If needed, adjust sentence segmentation for readability, but avoid altering the original meaning or creating overly long sentences. "
            f"For ambiguous terms, prioritize the meaning that best fits the context. Output only the translated result, without additional explanations or notes. "
            f"**Ensure the translation does not contain any punctuation marks, as subtitles typically do not use them.** If the content violates safety standards, provide a compliant translation.")

        src_lang = "Auto Detect"
        # dst_lang = "zh-cn"

        prompt += f" Translate from {src_lang} to {dst_lang}\n"
        prompt += " Context:\n" + content + "\n"

        return prompt

    def init_trans_content(self, content, dst_lang: str = 'zh-cn'):
        self.clear()
        # 文本翻译
        prompt = (
            f"You are a professional translator. Translate the following text into natural and fluent language. "
            f"Use the provided context to optimize phrasing, but do not include it in the output. If needed, adjust sentence segmentation for readability, but avoid altering the original meaning or creating overly long sentences. "
            f"For ambiguous terms, prioritize the meaning that best fits the context. Output only the translated result, without additional explanations or notes. "
            f"** If the content violates safety standards, provide a compliant translation.")

        src_lang = "Auto Detect"
        # dst_lang = "zh-cn"

        prompt += f" Translate from {src_lang} to {dst_lang}\n"
        prompt += " Context:\n" + content + "\n"

        return prompt

    def clear(self):
        self.messages = []
        self.results = []

    def deepseek_to_chat(self, content, msType: str, dstLang: str = 'zh-cn') -> str:
        print(f"deepseek_to_chat: {content}, {msType}, {dstLang}")
        if self.current_mstype is None:
            self.clear()
            self.current_mstype = msType
        elif self.current_mstype != msType:
            self.clear()
            self.current_mstype = msType

        if not self.messages:
            if msType == msSRT:
                content = self.init_srt_content(content, dstLang)
            elif msType == msCHAT:
                pass
            elif msType == msTranslate:
                content = self.init_trans_content(content, dstLang)

        self.messages.append({"role": "user", "content": content})
        response = self.client.chat.completions.create(model=selected_model, messages=self.messages)
        self.messages.append(response.choices[0].message)
        result = response.choices[0].message.content
        self.results.append(result)
        return result

    def close(self):
        self.clear()
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

def get_deepseek():
    global deepseek
    if deepseek is None:
        deepseek = DeepSeekChat()
    return deepseek

