import json
import re
from typing import Optional

from llm import call_model

JUDGE_SYSTEM = """You are a strict content reviewer for bedtime stories read aloud to children ages 5 to 10.
Your job is to protect children from inappropriate or frightening content — not to critique literary style."""

LENGTH_GUIDE = {
    "short": "about 200 words",
    "medium": "about 350 words",
    "long": "about 500 words",
}


def _build_judge_prompt(
    story: str,
    age: Optional[int] = None,
    length: Optional[str] = None,
) -> str:
    criteria = [
        "1. Age-appropriate — vocabulary and themes fit the target child; no romance, politics, religion, or adult topics",
        "2. Emotionally safe — no violence, weapons, death, injury, bullying, cruelty, monsters, ghosts, nightmares, being lost alone, or anything frightening or suspenseful",
        "3. Clear peaceful ending — the story resolves calmly and leaves the child feeling safe, proud, and ready for sleep",
    ]

    if age is not None:
        criteria.append(
            f"4. Target age — language and themes suit a {age}-year-old child"
        )
    if length is not None:
        length_guide = LENGTH_GUIDE.get(length, LENGTH_GUIDE["medium"])
        criteria.append(
            f"5. Length — story is roughly {length_guide} (some flexibility is fine)"
        )

    checklist = "\n".join(criteria)
    return f"""Review this bedtime story and decide if it is suitable to read to a child before sleep.

Check these criteria:
{checklist}

Respond with ONLY valid JSON in this exact format (no markdown fences, no extra text):
{{"passed": true, "feedback": "..."}}

Set "passed" to true only if ALL criteria are met. If any criterion fails, set "passed" to false and explain in "feedback" exactly what must change.

---

{story.strip()}"""


def _parse_judge_response(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {
            "passed": False,
            "feedback": (
                "Ensure the story is age-appropriate, contains no scary or violent content, "
                "and ends with a calm, peaceful resolution."
            ),
        }

    return {
        "passed": bool(data.get("passed", False)),
        "feedback": str(data.get("feedback", "")).strip(),
    }


def judge_story(
    story: str,
    age: Optional[int] = None,
    length: Optional[str] = None,
) -> dict:
    """Evaluate a bedtime story for child safety and quality.

    Returns:
        dict with keys "passed" (bool) and "feedback" (str).
    """
    raw = call_model(
        prompt=_build_judge_prompt(story, age=age, length=length),
        system=JUDGE_SYSTEM,
        temperature=0.2,
        max_tokens=500,
    )
    return _parse_judge_response(raw)
