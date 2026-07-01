"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

"""

from storyteller import generate_story

example_requests = "A story about a girl named Alice and her best friend Bob, who happens to be a cat."


def main():
    user_input = input("What kind of story do you want to hear? ")
    if not user_input.strip():
        user_input = example_requests
        print(f"(Using example: {example_requests})\n")

    print("\nGenerating your bedtime story...\n")
    story = generate_story(user_input)
    print(story)


if __name__ == "__main__":
    main()
