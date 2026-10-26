import os, sys, time, pathlib
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "shared"))
from llm_log import log_call

DOC = pathlib.Path(__file__).parent.joinpath("long_doc.txt").read_text()
QUESTIONS = [
    "What is the main topic of this document?",
    "Summarize it in one sentence.",
    "What is the second paragraph about?",
    "Does it mention any numbers? Which ones?",
    "What tone does it use?",
]

def ask(cached):
    from anthropic import Anthropic
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    system = [{"type": "text", "text": DOC}]
    if cached:
        system[0]["cache_control"] = {"type": "ephemeral"}

    label = "claude-haiku-5-5-cached" if cached else "claude-haiku-5-5-uncached"
    for q in QUESTIONS:
        start = time.time()
        resp = client.messages.create(
            model="claude-haiku-5-5", max_tokens=100,
            thinking={"type": "disabled"},
            system=system, messages=[{"role": "user", "content": q}],
        )
        elapsed_ms = (time.time() - start) * 1000
        cost = (resp.usage.input_tokens / 1_000_000 * 0.10
                + resp.usage.output_tokens / 1_000_000 * 0.50)
        log_call("anthropic", label, resp.usage.input_tokens, resp.usage.output_tokens, elapsed_ms, cost)
        print(f"  cache_read={resp.usage.cache_read_input_tokens:5}  "
              f"cache_write={resp.usage.cache_creation_input_tokens:5}  {elapsed_ms:.0f}ms")

if __name__ == "__main__":
    print("--- without caching ---")
    ask(cached=False)
    print("--- with caching ---")
    ask(cached=True)