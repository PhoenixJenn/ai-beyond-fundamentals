import os, math
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def embed(texts):
    resp = client.embeddings.create(model="text-embedding-3-small", input=texts)
    return [d.embedding for d in resp.data]

def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb)

SEED = {
    "What is the capital of France?": "Paris.",
    "How many legs does a spider have?": "Eight.",
    "What's the boiling point of water in Celsius?": "100 degrees.",
}
seed_questions = list(SEED.keys())
seed_vecs = embed(seed_questions)

def lookup(question, threshold):
    q_vec = embed([question])[0]
    best_score, best_q = 0, None
    for sq, sv in zip(seed_questions, seed_vecs):
        score = cosine_similarity(q_vec, sv)
        if score > best_score:
            best_score, best_q = score, sq
    if best_score >= threshold:
        return SEED[best_q], best_score, best_q
    return None, best_score, best_q




TEST_QUESTIONS = [
    # paraphrases -- should hit
    "Which city is the capital of France?",
    "What's France's capital city?",
    "How many legs do spiders have?",
    "What temperature does water boil at, in Celsius?",
    # same topic, different question -- should NOT hit
    "What is the population of France?",
    "How many eyes does a spider have?",
    "What's the freezing point of water in Celsius?",
    # unrelated -- should NOT hit
    "How do I bake a chocolate cake?",
    "What's the capital of Japan?",
]

if __name__ == "__main__":
    for threshold in [0.95, 0.85, 0.75, 0.6]:
        print(f"--- threshold={threshold} ---")
        hits = 0
        for q in TEST_QUESTIONS:
            answer, score, matched = lookup(q, threshold)
            status = f"HIT (matched {matched!r})" if answer else "miss"
            print(f"  {score:.3f}  {q!r} -> {status}")
            if answer:
                hits += 1
        print(f"  {hits}/{len(TEST_QUESTIONS)} hits\n")