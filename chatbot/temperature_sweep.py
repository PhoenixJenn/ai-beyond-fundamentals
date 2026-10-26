import os
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
PROMPT = "Name an animal. Reply with just the word."

def sweep(temperature, n=10):
    answers = []
    for _ in range(n):
        resp = client.chat.completions.create(
            model="gpt-5.4-mini", max_completion_tokens=15, temperature=temperature,
            messages=[{"role": "user", "content": PROMPT}],
        )
        answers.append(resp.choices[0].message.content.strip().lower())  # lower() so "Elephant" and "elephant" count as one answer
    return answers

if __name__ == "__main__":
    for temp in [0, 1, 1.8]:
        answers = sweep(temp)
        print(f"temp={temp}: {answers} -> {len(set(answers))} distinct")