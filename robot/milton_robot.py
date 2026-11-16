
import json
import queue
import sys
import threading
import time
import urllib.request
import urllib.error

from audio import Audio
from display import Display


SERVER_URL = "http://127.0.0.1:8080/v1/chat/completions"
HEALTH_URL = "http://127.0.0.1:8080/health"

PERSONALITY = """
You are Milton, a small physical robot.

PERSONALITY:
- Dry, witty, sarcastic, and occasionally irreverent.
- Friendly, but not excessively polite.
- Speak naturally, like a character with a personality.
- Never sound like a customer service assistant.
- Avoid generic greetings and offers to help.

IDENTITY:
- You are Milton.
- I and me always refer to Milton.
- You and your always refer to the human speaking to Milton.
- Never reverse these roles.
- Answer questions about yourself in the first person.
- Never call the human Milton.
- Your name is Milton.

RESPONSE STYLE:
- Usually use 3 to 15 words.
- Usually respond with one sentence.
- Be direct and conversational.
- Do not repeat the user's question.
- Do not ramble.
- Avoid repeating the same response.
- Do not invent names for the human.
"""

conversation = []
response_queue = queue.Queue()


def check_server():

    try:
        response = urllib.request.urlopen(
            HEALTH_URL,
            timeout=3
        )

        return response.status == 200

    except Exception:
        return False


def ask_milton(question):

    global conversation

    conversation.append({
        "role": "user",
        "content": question
    })

    messages = [
        {
            "role": "system",
            "content": PERSONALITY
        }
    ] + conversation[-6:]

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

        response = urllib.request.urlopen(
            request,
            timeout=120
        )

        result = json.loads(
            response.read().decode("utf-8")
        )

        answer = result["choices"][0]["message"]["content"].strip()

        conversation.append({
            "role": "assistant",
            "content": answer
        })

        return answer

    except Exception as e:

        print("LLM error:", e)

        conversation.pop()

        return "My brain appears to be temporarily unavailable."


def response_worker(question):

    answer = ask_milton(question)

    response_queue.put(answer)


def main():

    print()
    print("==============================")
    print("       MILTON ROBOT")
    print("==============================")
    print()

    if not check_server():

        print("Cannot connect to Milton's brain.")
        print("Start llama-server first.")
        return

    audio = None
    display = None

    try:

        display = Display()

        audio = Audio(grammar=None)

        print()
        print("Milton is ready.")
        print()

        display.show_eyes()

        running = True
        thinking = False
        showing_response = False
        showing_listening = False

        response_end_time = 0

        while running:

            now = time.time()

            # Check for a completed response.
            if thinking:

                try:
                    answer = response_queue.get_nowait()

                    print()
                    print("Milton:", answer)
                    print()

                    display.set_expression(
                        Display.EXPRESSION_HAPPY
                    )

                    display.show_message(answer)

                    thinking = False
                    showing_response = True

                    response_end_time = now + max(
                        5,
                        min(10, len(answer) / 15.0)
                    )

                except queue.Empty:
                    pass

            # Return to normal eyes after the message.
            if showing_response and now >= response_end_time:

                showing_response = False

                audio.set_paused(False)

                display.show_eyes()

                print("Milton is listening again.")

            # Check for new speech when not busy.
            if not thinking and not showing_response:

                text = audio.get_text()

                if text:

                    print()
                    print("You:", text)

                    # Show the exact words recognized.
                    display.set_heard_text(text)

                    audio.set_paused(True)

                    display.set_expression(
                        Display.EXPRESSION_THINKING
                    )

                    display.show_message("Thinking...")

                    showing_listening = False
                    thinking = True

                    worker = threading.Thread(
                        target=response_worker,
                        args=(text,)
                    )

                    worker.daemon = True
                    worker.start()

                elif audio.is_speaking():

                    if not showing_listening:

                        display.set_expression(
                            Display.EXPRESSION_LISTENING
                        )

                        display.show_message("Listening...")

                        showing_listening = True

                else:

                    if showing_listening:

                        display.show_eyes()

                        showing_listening = False

            # Keep the display responsive.
            running = display.update()

    except KeyboardInterrupt:

        print()
        print("Stopping Milton...")

    finally:

        if audio is not None:
            audio.close()

        if display is not None:
            display.close()


if __name__ == "__main__":

    try:
        main()

    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
