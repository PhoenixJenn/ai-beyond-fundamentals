import os, sys, time, pathlib
from dotenv import load_dotenv
load_dotenv()
from anthropic import Anthropic

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "shared"))
from llm_log import log_call

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
MODEL = "claude-haiku-5-5"
PRICE_IN, PRICE_OUT = 0.10, 0.50  # $ per 1M tokens, from Module 0's models.yaml

# The same four questions, asked two ways. The compact version says the same
# thing in far fewer words, with a short system prompt that asks for short answers.
COMPACT = {
    "system": "You are a gardening assistant. Answer in at most two sentences.",
    "turns": [
        "I have a sunny 4x8 ft bed. What should I plant in spring?",
        "Which of those is easiest for a beginner?",
        "How far apart should I space it?",
        "And how often do I water it?",
    ],
}
VERBOSE = {
    "system": (
        "You are a friendly, thorough, and highly knowledgeable gardening assistant. "
        "Always greet the user warmly, explain your reasoning step by step, mention any "
        "relevant caveats, regional differences, seasonal considerations, and common "
        "mistakes, offer alternative approaches where possible, and finish by inviting "
        "follow-up questions. Be comprehensive rather than brief."
    ),
    "turns": [
        "Hi there! So I've been thinking about getting into gardening for a while now, and "
        "I finally have a bit of free time. I have a raised bed in my backyard, it's about "
        "4 feet by 8 feet, and it gets a lot of sun, I think maybe six or seven hours on "
        "a good day. Anyway, I was wondering, what are some things I could plant this spring?",
        "Thanks, that's really helpful! There's a lot there. Of all of the ones you just "
        "mentioned, which one do you think would be the easiest for someone who has honestly "
        "never grown anything before in their life? I'd hate to fail on the first try.",
        "Great, I think I'll go with that one. Now, I'm not totally sure about the spacing, "
        "so could you tell me how far apart I should put the plants so they have enough room?",
        "Okay, that makes sense. One last thing, I'm a little worried about overwatering or "
        "underwatering, so how often should I actually be watering it, roughly speaking?",
    ],
}

def run(label, scenario):
    messages = []
    total_in = total_out = 0
    total_cost = 0.0
    print(f"--- {label} ---")
    for turn, user_text in enumerate(scenario["turns"], 1):
        messages.append({"role": "user", "content": user_text})
        start = time.time()
        resp = client.messages.create(
            model=MODEL, max_tokens=400,
            system=scenario["system"], messages=messages,
            thinking={"type": "disabled"},  # otherwise Haiku can spend the whole token budget thinking and return no text
        )
        elapsed_ms = (time.time() - start) * 1000
        reply = next(b.text for b in resp.content if b.type == "text")
        messages.append({"role": "assistant", "content": reply})
        i, o = resp.usage.input_tokens, resp.usage.output_tokens
        cost = i / 1_000_000 * PRICE_IN + o / 1_000_000 * PRICE_OUT
        log_call("anthropic", f"{MODEL}-{label}", i, o, elapsed_ms, cost)
        total_in, total_out, total_cost = total_in + i, total_out + o, total_cost + cost
        print(f"  turn {turn}: input={i:5}  output={o:4}  cost=${cost:.6f}")
    print(f"  TOTAL : input={total_in:5}  output={total_out:4}  cost=${total_cost:.6f}\n")
    return total_in, total_out, total_cost

if __name__ == "__main__":
    v = run("verbose", VERBOSE)
    c = run("compact", COMPACT)
    print(f"verbose / compact: input {v[0] / c[0]:.1f}x, output {v[1] / c[1]:.1f}x, cost {v[2] / c[2]:.1f}x")