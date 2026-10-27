import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "shared"))
from llm_client import stream_chat, CONFIG

MODELS = list(CONFIG.keys())
SYSTEM_PROMPT = "You are a helpful assistant. Keep answers short."  # resent on every turn, so keep it lean

def pick_model():
    print("Models:")
    for i, name in enumerate(MODELS, 1):
        print(f"  {i}. {name}")
    choice = input(f"Pick a model [1-{len(MODELS)}]: ").strip()
    try:
        return MODELS[int(choice) - 1]
    except (ValueError, IndexError):
        print("Not a valid choice, defaulting to the first model.")
        return MODELS[0]

def main():
    model = pick_model()
    print(f"\nChatting with {model}. Type 'quit' to exit.\n")
    messages = []
    session_cost = 0.0

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit"):
            break
        if not user_input:
            continue
        messages.append({"role": "user", "content": user_input})

        print(f"{model}: ", end="", flush=True)
        text, cost, elapsed_ms = stream_chat(
            messages, model, on_chunk=lambda c: print(c, end="", flush=True),
            system=SYSTEM_PROMPT,
        )
        print()
        messages.append({"role": "assistant", "content": text})
        session_cost += cost
        print(f"  [turn: ${cost:.6f}, {elapsed_ms:.0f}ms | session total: ${session_cost:.6f}]\n")

    print(f"\nSession total: ${session_cost:.6f}")

if __name__ == "__main__":
    main()