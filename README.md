# AI Beyond Fundamentals

Working code for the AI Beyond Fundamentals course. Each module adds a folder
of labs on top of a small shared toolkit: one function that logs every model
call, and one client that talks to four providers through the same interface.

Module 0 (setup) is complete. Module 1 starts from this layout.

## Quick start

Requires Python 3.12 and, for the local model, [Ollama](https://ollama.com).

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env             # Windows: Copy-Item .env.example .env
```

Then paste your three API keys into `.env` and check that everything works:

```bash
python shared/try_client.py      # one call to each of the four models
pytest shared/test_logger.py     # checks all four providers were logged
```

## Layout

| Folder | What is in it |
|---|---|
| `shared/` | The toolkit every module reuses (see below) |
| `chatbot/` | Module 0 labs: `three_providers.py` calls Claude, OpenAI, Gemini and a local Ollama model with one prompt |
| `agent/`, `evals/`, `extraction/`, `rag/`, `ragvsfinetune/` | Planned module folders. Empty for now, so Git does not track them |

### `shared/`

| File | Purpose |
|---|---|
| `llm_log.py` | `log_call(...)` appends one JSON line per model call to `calls.jsonl`: provider, model, tokens, latency and cost |
| `llm_client.py` | `call(prompt, model)` looks up the provider in `models.yaml`, runs the call, retries rate-limit errors with exponential backoff, works out the cost, and logs it |
| `models.yaml` | One entry per model: provider and price per 1M input and output tokens. Swap a provider by editing one line here |
| `try_client.py` | Smoke test: one call to each model |
| `test_logger.py` | Pytest checkpoint: all four providers appear in the log |
| `calls.jsonl` | The call log. Generated, not committed |

To use the client from another module, add `shared/` to the import path and
call it:

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "shared"))
from llm_client import call

print(call("Say hello.", "claude-haiku-5-5"))
```

## Models and prices

| Model | Provider | Notes |
|---|---|---|
| `claude-haiku-5-5` | Anthropic | |
| `gpt-5.4-mini` | OpenAI | |
| `gemini-flash-lite-latest` | Gemini | An alias, so the model behind it can change |
| `qwen3-vl:4b-instruct` | Ollama (local) | Free to run. Any model shown by `ollama list` works if you add it to `models.yaml` |

Prices in `models.yaml` come from each provider's pricing page (October 2026).
Check them before trusting the cost numbers; they change.

## Keys and secrets

- Keys live in `.env`, which is ignored by Git. `.env.example` lists the names.
- `load_dotenv()` does not override a variable already set in your shell. If you
  rotate a key, open a new terminal window or you will keep using the old one
  and see a `401`.
- Never commit `.env`. Run `git status --ignored` to confirm it is listed as ignored.

## Conventions

- There is deliberately no `shared/__init__.py`. Files in `shared/` import each
  other by bare name (`from llm_log import log_call`).
- Generated files (`*.jsonl`, `*.log`, `lab2*output*`) are ignored by Git.
- Provider usage fields differ. Anthropic: `input_tokens` / `output_tokens`.
  OpenAI: `prompt_tokens` / `completion_tokens`. Gemini: `prompt_token_count` /
  `candidates_token_count`. `llm_client.py` normalizes all of them.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `401` from a provider | Stale or wrong key. Open a fresh terminal and check `.env` |
| `503` or `504` from Gemini | The model is overloaded. Rerun or try another Gemini model |
| `ModuleNotFoundError` | Virtual environment not active. Run `source .venv/bin/activate` |
| Ollama connection error | Ollama is not running. Start the app, or run `ollama serve` |
