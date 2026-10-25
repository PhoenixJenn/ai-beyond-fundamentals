# shared/try_client.py — a quick smoke test: one call to each model
from dotenv import load_dotenv
load_dotenv()
from llm_client import call

for model in ["claude-haiku-5-5", "gpt-5.4-mini", "gemini-flash-lite-latest", "qwen3-vl:4b-instruct"]:
    print(model, "->", call("Say hello in five words.", model))
