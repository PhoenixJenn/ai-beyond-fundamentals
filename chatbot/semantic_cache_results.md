# Semantic cache: threshold results

Module 1, Lab 6. `chatbot/semantic_cache.py` embeds three seed questions with
`text-embedding-3-small`, then compares nine test questions to them by cosine
similarity. A test question is a cache hit when its best score is at or above
the threshold.

The nine test questions are three kinds:

- **Paraphrases of a seed** (should hit): the four questions about the capital
  of France, spider legs, and the boiling point of water.
- **Same topic, different question** (should not hit): the population of
  France, spider eyes, and the freezing point of water.
- **Unrelated** (should not hit): baking a chocolate cake, and the capital of
  Japan.

## Summary

| Threshold | Hits | What happened |
|---|---|---|
| 0.95 | 1/9 | Too strict. It missed real paraphrases, like "Which city is the capital of France?" (0.899). |
| 0.85 | 3/9 | Clean. All three hits were genuine paraphrases, with zero wrong answers. |
| 0.75 | 6/9 | Two wrong answers slipped through. |
| 0.60 | 6/9 | Same as 0.75, but only just. "What is the population of France?" scored 0.594, so a threshold of 0.59 would have wrongly matched it too. |

The two wrong matches at 0.75:

- "How many eyes does a spider have?" matched the spider-legs question (0.790)
  and would have answered "Eight."
- "What's the freezing point of water in Celsius?" matched the boiling-point
  question (0.785) and would have answered "100 degrees."

A genuine paraphrase, "What's France's capital city?", scored 0.811, and the
wrong "eyes" question scored 0.790. A threshold near 0.80 would separate them in
this test, but the margin is only about 0.02 on nine questions, so it is not
safe to rely on.

## Decision

I would use **0.85** as the threshold. At 0.85 every hit was a genuine
paraphrase and nothing wrong slipped through. It misses some paraphrases (for
example "What's France's capital city?" at 0.811), which is the safer way to
fail: a miss only costs one extra model call, while a wrong cached answer is
served with full confidence.

## Full output

```
--- threshold=0.95 ---
  0.899  'Which city is the capital of France?' -> miss
  0.811  "What's France's capital city?" -> miss
  0.972  'How many legs do spiders have?' -> HIT (matched 'How many legs does a spider have?')
  0.851  'What temperature does water boil at, in Celsius?' -> miss
  0.594  'What is the population of France?' -> miss
  0.790  'How many eyes does a spider have?' -> miss
  0.785  "What's the freezing point of water in Celsius?" -> miss
  0.109  'How do I bake a chocolate cake?' -> miss
  0.556  "What's the capital of Japan?" -> miss
  1/9 hits

--- threshold=0.85 ---
  0.899  'Which city is the capital of France?' -> HIT (matched 'What is the capital of France?')
  0.811  "What's France's capital city?" -> miss
  0.972  'How many legs do spiders have?' -> HIT (matched 'How many legs does a spider have?')
  0.851  'What temperature does water boil at, in Celsius?' -> HIT (matched "What's the boiling point of water in Celsius?")
  0.594  'What is the population of France?' -> miss
  0.790  'How many eyes does a spider have?' -> miss
  0.785  "What's the freezing point of water in Celsius?" -> miss
  0.109  'How do I bake a chocolate cake?' -> miss
  0.556  "What's the capital of Japan?" -> miss
  3/9 hits

--- threshold=0.75 ---
  0.899  'Which city is the capital of France?' -> HIT (matched 'What is the capital of France?')
  0.811  "What's France's capital city?" -> HIT (matched 'What is the capital of France?')
  0.972  'How many legs do spiders have?' -> HIT (matched 'How many legs does a spider have?')
  0.851  'What temperature does water boil at, in Celsius?' -> HIT (matched "What's the boiling point of water in Celsius?")
  0.594  'What is the population of France?' -> miss
  0.790  'How many eyes does a spider have?' -> HIT (matched 'How many legs does a spider have?')
  0.785  "What's the freezing point of water in Celsius?" -> HIT (matched "What's the boiling point of water in Celsius?")
  0.109  'How do I bake a chocolate cake?' -> miss
  0.556  "What's the capital of Japan?" -> miss
  6/9 hits

--- threshold=0.6 ---
  0.899  'Which city is the capital of France?' -> HIT (matched 'What is the capital of France?')
  0.811  "What's France's capital city?" -> HIT (matched 'What is the capital of France?')
  0.972  'How many legs do spiders have?' -> HIT (matched 'How many legs does a spider have?')
  0.851  'What temperature does water boil at, in Celsius?' -> HIT (matched "What's the boiling point of water in Celsius?")
  0.594  'What is the population of France?' -> miss
  0.790  'How many eyes does a spider have?' -> HIT (matched 'How many legs does a spider have?')
  0.785  "What's the freezing point of water in Celsius?" -> HIT (matched "What's the boiling point of water in Celsius?")
  0.109  'How do I bake a chocolate cake?' -> miss
  0.556  "What's the capital of Japan?" -> miss
  6/9 hits
```
