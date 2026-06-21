import os
from openai import OpenAI
from dotenv import load_dotenv
from src.api.utils.llm.get_llm_type import get_model_type

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
XAI_API_KEY = os.getenv("XAI_API_KEY")

def chat_with_llm(messages, llm_name):
    def chat_with_gpt(messages, model):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set.")
        client = OpenAI(api_key=OPENAI_API_KEY)
        return client.chat.completions.create(model=model, messages=messages).choices[0].message.content

    def chat_with_grok(messages, model):
        if not XAI_API_KEY:
            raise ValueError("XAI_API_KEY is not set.")
        client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")
        return client.chat.completions.create(model=model, messages=messages).choices[0].message.content

    model_type = get_model_type(llm_name)
    if model_type == "openai":
        return chat_with_gpt(messages, llm_name)
    elif model_type == "grok":
        return chat_with_grok(messages, llm_name)
    raise ValueError(f"Unsupported model: {llm_name}")
