import json
import os
from dotenv import load_dotenv
load_dotenv()

PROMPT = "Explain what a token is, in three sentences."

def call_anthropic():
    from anthropic import Anthropic
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    resp = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=200,
        messages=[{"role": "user", "content": PROMPT}],
    )
    # a "thinking" response can put a ThinkingBlock before the text block,
    # so pick the block that actually is text rather than assuming index 0
    text = next(b.text for b in resp.content if b.type == "text")
    return {"text": text, "usage": resp.usage.model_dump(mode="json", exclude_none=True)}

def call_openai():
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    resp = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=[{"role": "user", "content": PROMPT}],
    )
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
    resp = client.models.generate_content(model="gemini-flash-lite-latest", contents=PROMPT)
    return {
        "text": resp.text,
        "usage": resp.usage_metadata.model_dump(mode="json", exclude_none=True),
    }

if __name__ == "__main__":
    results = {}
    for name, call in [("anthropic", call_anthropic), ("openai", call_openai), ("gemini", call_gemini)]:
        try:
            results[name] = call()
        except Exception as e:
            # one provider failing (a 503, say) shouldn't lose the other two answers
            results[name] = {"error": f"{type(e).__name__}: {e}"}
    output = json.dumps(results, indent=2)
    print(output)
    with open("lab2-output.json", "w") as f:
        f.write(output + "\n")