# shared/llm_client.py
import os, time, random, pathlib, yaml
from llm_log import log_call

from anthropic import RateLimitError as AnthropicRateLimitError
from openai import RateLimitError as OpenAIRateLimitError
from google.genai.errors import ClientError as GeminiClientError
RATE_LIMIT_ERRORS = (AnthropicRateLimitError, OpenAIRateLimitError, GeminiClientError)
# GeminiClientError covers other 4xx errors too (bad request, auth), not
# just 429 — check e.code == 429 inside the except block if you want to be
# precise. Good enough to make the retry loop fire for this exercise.

CONFIG = yaml.safe_load((pathlib.Path(__file__).parent / "models.yaml").read_text())

def call(prompt, model, max_attempts=5):
    cfg = CONFIG[model]
    start = time.time()
    for attempt in range(max_attempts):
        try:
            text, usage = _dispatch(cfg["provider"], model, prompt)
            break
        except RATE_LIMIT_ERRORS:
            if attempt == max_attempts - 1:
                raise
            time.sleep(2 ** attempt + random.random())
    elapsed_ms = (time.time() - start) * 1000
    cost = (usage["input_tokens"] / 1_000_000 * cfg["price_in"]
            + usage["output_tokens"] / 1_000_000 * cfg["price_out"])
    log_call(cfg["provider"], model, usage["input_tokens"], usage["output_tokens"], elapsed_ms, cost)
    return text

def _dispatch(provider, model, prompt):
    if provider == "anthropic":
        from anthropic import Anthropic
        client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        resp = client.messages.create(
            model=model, max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        # same ThinkingBlock gotcha as Lab 2 - don't assume index 0 is the text block
        text = next(b.text for b in resp.content if b.type == "text")
        return text, {
            "input_tokens": resp.usage.input_tokens,
            "output_tokens": resp.usage.output_tokens,
        }
    if provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        resp = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content, {
            "input_tokens": resp.usage.prompt_tokens,
            "output_tokens": resp.usage.completion_tokens,
        }
    if provider == "gemini":
        from google import genai
        from google.genai import types
        client = genai.Client(
            api_key=os.environ["GEMINI_API_KEY"],
            http_options=types.HttpOptions(timeout=20000),  # milliseconds
        )
        resp = client.models.generate_content(model=model, contents=prompt)
        return resp.text, {
            "input_tokens": resp.usage_metadata.prompt_token_count,
            "output_tokens": resp.usage_metadata.candidates_token_count,
        }
    if provider == "ollama":
        from openai import OpenAI
        local = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
        resp = local.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}],
        )
        usage = resp.usage
        return resp.choices[0].message.content, {
            "input_tokens": usage.prompt_tokens if usage else 0,
            "output_tokens": usage.completion_tokens if usage else 0,
        }
    raise ValueError(f"Unknown provider: {provider}")
