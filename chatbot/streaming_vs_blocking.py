import os, time
from dotenv import load_dotenv
load_dotenv()
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
PROMPT = "Write a 300-word story about a lighthouse keeper."

def call_blocking():
    start = time.time()
    client.messages.create(
        model="claude-haiku-5-5", max_tokens=500,
        thinking={"type": "disabled"},
        messages=[{"role": "user", "content": PROMPT}],
    )
    return time.time() - start

def call_streaming():
    start = time.time()
    ttft = None
    with client.messages.stream(
        model="claude-haiku-5-5", max_tokens=500,
        thinking={"type": "disabled"},
        messages=[{"role": "user", "content": PROMPT}],
    ) as stream:
        for _ in stream.text_stream:
            if ttft is None:
                ttft = time.time() - start
    return ttft, time.time() - start

if __name__ == "__main__":
    for i in range(3):
        blocking_total = call_blocking()
        ttft, streaming_total = call_streaming()
        print(f"run {i+1}: blocking={blocking_total:.2f}s  |  "
              f"streaming ttft={ttft:.2f}s total={streaming_total:.2f}s")