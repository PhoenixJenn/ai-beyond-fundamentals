import json
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# added in Lab 4
import sys, pathlib, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "shared"))
from llm_log import log_call

PROMPT = "Explain what a token is, in three sentences."

def call_anthropic():
    from anthropic import Anthropic
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    start = time.time()
    resp = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=200,
        messages=[{"role": "user", "content": PROMPT}],
    )
    elapsed_ms = (time.time() - start) * 1000
    # a "thinking" response can put a ThinkingBlock before the text block,
    # so pick the block that actually is text rather than assuming index 0
    text = next(b.text for b in resp.content if b.type == "text")
    log_call("anthropic", "claude-haiku-5-5", resp.usage.input_tokens, resp.usage.output_tokens, elapsed_ms, cost_usd=0)
    return {"text": text, "usage": resp.usage.model_dump(mode="json", exclude_none=True)}

def call_openai():
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    start = time.time()
    resp = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=[{"role": "user", "content": PROMPT}],
    )
    elapsed_ms = (time.time() - start) * 1000
    log_call("openai", "gpt-5.4-mini", resp.usage.prompt_tokens, resp.usage.completion_tokens, elapsed_ms, cost_usd=0)
    return {
        "text": resp.choices[0].message.content,
        "usage": resp.usage.model_dump(mode="json", exclude_none=True),
    }


def call_gemini():
    from google import genai
    from google.genai import types
    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"],
        http_options=types.HttpOptions(timeout=20000),  # milliseconds
    )
    start = time.time()
    resp = client.models.generate_content(model="gemini-flash-lite-latest", contents=PROMPT)
    elapsed_ms = (time.time() - start) * 1000
    log_call("gemini", "gemini-flash-lite-latest", resp.usage_metadata.prompt_token_count, resp.usage_metadata.candidates_token_count, elapsed_ms, cost_usd=0)
    return {
        "text": resp.text,
        "usage": resp.usage_metadata.model_dump(mode="json", exclude_none=True),
    }

def call_ollama():
    from openai import OpenAI
    local = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")  # key is unused but required by the SDK
    start = time.time()
    resp = local.chat.completions.create(
        model="qwen3-vl:4b-instruct",  # or whichever model `ollama list` shows on your machine
        messages=[{"role": "user", "content": PROMPT}],
    )
    elapsed_ms = (time.time() - start) * 1000
    input_tokens = resp.usage.prompt_tokens if resp.usage else 0
    output_tokens = resp.usage.completion_tokens if resp.usage else 0
    log_call("ollama", "qwen3-vl:4b-instruct", input_tokens, output_tokens, elapsed_ms, cost_usd=0)
    usage = resp.usage.model_dump(mode="json", exclude_none=True) if resp.usage else None
    return {"text": resp.choices[0].message.content, "usage": usage}

if __name__ == "__main__":
    results = {}
    for name, call in [("anthropic", call_anthropic), ("openai", call_openai), ("gemini", call_gemini), ("ollama", call_ollama)]:
        try:
            results[name] = call()
        except Exception as e:
            # one provider failing (a 503, say) shouldn't lose the other two answers
            results[name] = {"error": f"{type(e).__name__}: {e}"}
    output = json.dumps(results, indent=2)
    print(output)
    filename = f"lab2-output-{datetime.now():%Y%m%d-%H%M%S}.json"  # a new file every run
    with open(filename, "w") as f:
        f.write(output + "\n")
    print("saved to", filename)

# usage field names, from the lab2-output-*.json file:
#   anthropic: input_tokens: 22 / output_tokens: 109
#   openai:    prompt_tokens: 16  / completion_tokens: 90
#   gemini:    prompt_token_count: 11 / candidates_token_count: 85