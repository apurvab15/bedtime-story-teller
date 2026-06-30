# Project Context — Hippocratic AI Bedtime Story Assignment

## Goal
Build a bedtime story generator for ages 5–10 using `gpt-3.5-turbo`.
Assignment repo: current working directory.

## Constraints
- Model: `gpt-3.5-turbo` (OpenAI) — do not change
- Must include: LLM judge, block diagram in README
- API key: use your own, never commit it
- Time budget: 2–3 hours total

## Core Theme
**Responsible AI / age-safe content** — the differentiator of this submission.
The judge explicitly reasons about child safety, not just story quality.

---

## Architecture

```
User input
    │
    ▼
Storyteller (gpt-3.5-turbo)
    │  system prompt: story arc + age-appropriate tone
    ▼
Judge (gpt-3.5-turbo)
    │  scores safety + quality criteria
    │  passed? ──No──► feedback → Storyteller (retry, max 3x)
    │  Yes
    ▼
scene_gen → CSS-animated HTML story card
    │
    ▼
Output printed + HTML auto-opens in browser
```

## File Map

| File | Responsibility | Returns |
|---|---|---|
| `main.py` | Orchestrator — wires all modules together | — |
| `storyteller.py` | Story generation with system prompt | `str` (story text) |
| `judge.py` | Safety + quality scoring, retry feedback | `dict {"passed": bool, "scores": {...}, "feedback": str}` |
| `scene_gen.py` | CSS-animated HTML story card | `str` (HTML content) |
| `output/` | Generated HTML files saved here | — |

---

## Judge Criteria
*(To be filled in after research chat — paste findings here)*

Planned dimensions:
- Age-appropriateness (vocabulary, concepts, themes)
- Emotional safety (no fear, violence, distressing content)
- Positive message / moral
- Narrative arc (beginning, middle, end)
- Engagement for 5–10 year olds

Scoring: each criterion 1–10, story passes if average ≥ 7.0, max 3 retries.

---

## Storyteller Prompt Strategy
*(To be filled in during storyteller.py session)*

Planned elements:
- System prompt enforcing age-appropriate tone
- Story arc structure (setup → adventure → resolution → lesson)
- Character naming from user input
- Length: ~300–500 words

---

## CSS Animation Approach
Simple, no Three.js. Ideas:
- Twinkling stars background
- Floating moon
- Soft text fade-in for story paragraphs
- Color palette: soft purples, blues, warm yellows

---

## How to Use This File
Paste the relevant sections at the top of any new chat to give it full project context.
Update the "Judge Criteria" and "Storyteller Prompt Strategy" sections as you complete research.
