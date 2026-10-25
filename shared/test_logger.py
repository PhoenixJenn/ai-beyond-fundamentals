import json
from llm_log import LOG_PATH

def test_all_providers_logged():
    rows = [json.loads(line) for line in LOG_PATH.read_text().splitlines()]
    providers = {row["provider"] for row in rows}
    assert providers == {"anthropic", "openai", "gemini", "ollama"}
