# Guess first! Write your estimate for each sample below, then run this
# file and see how close you were.
#   English: 50    Code: 60    JSON: 60    Emoji: 40    Japanese: 46

#English    anthropic= 26  openai= 10  gemini= 11
#Code       anthropic= 40  openai= 24  gemini= 29
#JSON       anthropic= 38  openai= 22  gemini= 23
#Emoji      anthropic= 33  openai= 15  gemini= 11
#Japanese   anthropic= 28  openai= 13  gemini= 11

import os
from dotenv import load_dotenv
load_dotenv()

SAMPLES = {
    "English": "The quick brown fox jumps over the lazy dog.",
    "Code": "def fib(n):\n    return n if n < 2 else fib(n-1) + fib(n-2)",
    "JSON": '{"name": "Ada", "age": 36, "skills": ["math", "engineering"]}',
    "Emoji": "🚀🔥😂👍💯🎉😍🙌✨🤔",
    "Japanese": "猫はかわいいです。今日は良い天気ですね。",
}

def anthropic_tokens(text):
    from anthropic import Anthropic
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    resp = client.messages.count_tokens(
        model="claude-haiku-5-5", messages=[{"role": "user", "content": text}],
    )
    return resp.input_tokens

def openai_tokens(text):
    import tiktoken
    enc = tiktoken.encoding_for_model("gpt-5.4-mini")
    return len(enc.encode(text))

def gemini_tokens(text):
    from google import genai
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    resp = client.models.count_tokens(model="gemini-flash-lite-latest", contents=text)
    return resp.total_tokens

if __name__ == "__main__":
    for label, text in SAMPLES.items():
        a, o, g = anthropic_tokens(text), openai_tokens(text), gemini_tokens(text)
        print(f"{label:10} anthropic={a:3}  openai={o:3}  gemini={g:3}")