"""Shared generate → judge → retry pipeline for CLI and web."""

from typing import Optional

from judge import judge_story
from storyteller import generate_story

MAX_ATTEMPTS = 3


def build_story_request(
    objects: list[str],
    age: int,
    length: str,
) -> str:
    """Turn structured form input into a storyteller user request."""
    length_guide = {
        "short": "about 200 words",
        "medium": "about 350 words",
        "long": "about 500 words",
    }.get(length, "about 350 words")

    obj_list = ", ".join(objects)
    return (
        f"Write a bedtime story for a {age}-year-old child, {length_guide}. "
        f"Include these three objects or themes in the story: {obj_list}."
    )


def generate_story_with_judge(
    user_request: str,
    age: Optional[int] = None,
    length: Optional[str] = None,
) -> dict:
    """Generate a story, judge it, and retry with feedback up to MAX_ATTEMPTS times."""
    feedback = None
    story = ""
    attempts = 0
    passed = False
    last_feedback = ""

    for attempt in range(1, MAX_ATTEMPTS + 1):
        attempts = attempt
        story = generate_story(user_request, feedback)
        result = judge_story(story, age=age, length=length)
        last_feedback = result["feedback"]

        if result["passed"]:
            passed = True
            break

        feedback = result["feedback"]

    return {
        "story": story,
        "passed": passed,
        "attempts": attempts,
        "feedback": last_feedback,
    }
