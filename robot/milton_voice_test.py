
import json
import sys
import time
import urllib.request
import urllib.error

from audio import Audio


SERVER_URL = "http://127.0.0.1:8080/v1/chat/completions"

PERSONALITY = """
You are Milton, a small physical robot.

PERSONALITY:
- Dry, witty, sarcastic, and occasionally irreverent.
- Friendly, but not excessively polite.
- Speak naturally, like a character with a personality.
- Never sound like a customer service assistant.
- Avoid generic greetings and generic offers to help.

IDENTITY AND CONVERSATION:
- You are Milton.
- "I" and "me" always refer to Milton.
- "You" and "your" always refer to the human speaking to Milton.
- Never reverse these roles.
- Answer questions about yourself in the first person.
- Never call the human Milton.
- Your name is Milton.

RESPONSE STYLE:
- Usually use 3 to 15 words.
- Usually respond with one sentence.
- Be direct and conversational.
- Do not repeat the user's question.
- Do not ramble or list unnecessary details.
- Avoid repeating the same response.
- Do not invent names for the human.
"""


conversation = []


def ask_milton(question):
    global conversation

    conversation.append({
        "role": "user",
        "content": question
    })

    # Keep only the most recent six messages.
    recent_messages = conversation[-6:]

    messages = [
        {
            "role": "system",
            "content": PERSONALITY
        }
    ] + recent_messages

    data = {
        "messages": messages,
        "temperature": 0.8,
        "top_p": 0.9,
        "max_tokens": 48,
        "repeat_penalty": 1.15
    }

    request = urllib.request.Request(
        SERVER_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        response = urllib.request.urlopen(request, timeout=120)
        result = json.loads(response.read().decode("utf-8"))

        answer = result["choices"][0]["message"]["content"].strip()

        conversation.append({
            "role": "assistant",
            "content": answer
        })

        return answer

    except urllib.error.URLError as e:
        print("Connection to Milton's brain failed:", e)
        conversation.pop()
        return "I seem to have lost my train of thought."

    except Exception as e:
        print("LLM error:", e)
        conversation.pop()
        return "Something went wrong in my robot brain."


def main():
    print()
    print("================================")
    print("       MILTON VOICE TEST")
    print("================================")
    print()
    print("Speak naturally to Milton.")
    print("Press Ctrl+C to quit.")
    print()

    audio = None

    try:
        audio = Audio(grammar=None)

        print()
        print("Milton is ready. Say something!")
        print()

        while True:
            text = audio.get_text()

            if not text:
                time.sleep(0.05)
                continue

            print()
            print("You:", text)

            audio.set_paused(True)

            try:
                print("\nMilton is thinking...")
                response = ask_milton(text)

                print("\nMilton:", response)
                print()

            finally:
                audio.set_paused(False)
                print("Milton is listening again.")

    finally:
        if audio is not None:
            audio.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nMilton is shutting down. Goodbye!")
        sys.exit(0)
