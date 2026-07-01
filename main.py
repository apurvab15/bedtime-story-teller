"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

With two more hours I would add a timed word-highlight mode that works without browser speech
synthesis, tune storyteller prompts per age band (5-6 vs 9-10 vocabulary), and export each
approved story as a standalone HTML file parents could bookmark or print.
"""

from pipeline import generate_story_with_judge

example_requests = "A story about a girl named Alice and her best friend Bob, who happens to be a cat."


def main():
    user_input = input("What kind of story do you want to hear? ")
    if not user_input.strip():
        user_input = example_requests
        print(f"(Using example: {example_requests})\n")

    print("\nGenerating your bedtime story...\n")
    result = generate_story_with_judge(user_input)
    if result["attempts"] > 1 and result["passed"]:
        print(f"(Passed on attempt {result['attempts']})\n")
    elif not result["passed"]:
        print(f"(Max attempts reached — using last draft)\n")
    print(result["story"])


if __name__ == "__main__":
    main()
