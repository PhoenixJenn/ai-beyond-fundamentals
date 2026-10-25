import json, time, pathlib

LOG_PATH = pathlib.Path(__file__).parent / "calls.jsonl"

def log_call(provider, model, input_tokens, output_tokens, elapsed_ms, cost_usd):
    row = {
        "ts": time.time(),
        "provider": provider,
        "model": model,
        "input_tokens": input_tokens or 0,
        "output_tokens": output_tokens or 0,
        "elapsed_ms": round(elapsed_ms, 1),
        "cost_usd": round(cost_usd, 6),
    }
    with LOG_PATH.open("a") as f:
        f.write(json.dumps(row) + "\n")
