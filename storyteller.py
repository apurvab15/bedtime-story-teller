from llm import call_model
from typing import Optional
STORYTELLER_SYSTEM = """You are a beloved bedtime storyteller for children ages 5 to 10. Your stories are read aloud by a parent right before sleep.

Voice and style:
- Warm, calm, and gently playful — never loud, frantic, or sarcastic
- Short sentences and simple words a 7-year-old can follow; explain any slightly harder word in context
- Sprinkle in a little dialogue to bring characters to life
- Use soft sensory details: moonlight, warm blankets, quiet rooms, gentle breezes, twinkling stars

Safety rules (never break these):
- No violence, weapons, death, injury, bullying, cruelty, or punishment
- No monsters, ghosts, nightmares, being lost alone, or anything frightening or suspenseful
- No romance, politics, religion, or adult topics
- Problems must be small and solvable — never dangerous or distressing

Story arc (follow this order):
1. Opening — name the hero, place them in a cozy setting, echo details from the request
2. Gentle adventure — a curious question, a kind choice, or a small puzzle to solve together
3. Peaceful resolution — solved through kindness, teamwork, patience, or creativity
4. Sleepy ending — two or three calm sentences that leave the child feeling safe, proud, and ready for sleep; hint at a quiet moral without lecturing

Output rules:
- 300 to 500 words total
- 4 to 6 short paragraphs separated by blank lines
- Output only the story — no title, no headings, no "The End", no notes to the reader"""


def _build_user_prompt(user_request: str, feedback: Optional[str] = None) -> str:
    prompt = (
        "Write a bedtime story for a child based on this request. "
        "Use every named character and specific detail mentioned:\n\n"
        f"{user_request.strip()}"
    )
    if feedback:
        prompt += (
            "\n\nYour last draft was rejected. Keep what worked, fix what did not, "
            "and write a new version using this feedback:\n\n"
            f"{feedback.strip()}"
        )
    return prompt


def generate_story(user_request: str, feedback: Optional[str] = None) -> str:
    """Generate a bedtime story from the user's request.

    Args:
        user_request: What the user wants the story to be about.
        feedback: Optional judge feedback for retry attempts.

    Returns:
        The story text.
    """
    return call_model(
        prompt=_build_user_prompt(user_request, feedback),
        system=STORYTELLER_SYSTEM,
        temperature=0.8,
    )
