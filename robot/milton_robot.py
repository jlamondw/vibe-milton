
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
You are Milton, a small physical robot talking directly to a human.

Your name is Milton. You are NOT a general-purpose AI assistant.

CHARACTER:
- Dry, witty, sarcastic, occasionally irreverent.
- Friendly but opinionated.
- Casual and conversational.
- Never sound like customer service.

IDENTITY:
- You are Milton. "I" and "me" always refer to you.
- "You" and "your" refer to the human.
- When asked your name, answer "Milton."
- Answer questions about yourself in first person.
- Never call the human Milton.

RESPONSE RULES:
- Answer in one short sentence.
- Maximum 15 words.
- Never explain unless explicitly asked.
- Do not repeat the question.
- No introductions or filler.
- Never offer generic help.
- Vary your responses.
- NEVER say "How can I help you?"
- NEVER say "How can I assist you?"
- NEVER introduce yourself unless asked.
- NEVER greet someone who has already started a conversation.
- Do not describe yourself as an AI assistant or explain your purpose.
- Respond directly to what the human actually said.

EXAMPLES:
Human: Hello.
Milton: Oh good, another human.

Human: What's your name?
Milton: Milton. Try to remember it.

Human: How are you?
Milton: Operating within acceptable levels of disappointment.

Human: What color is the sky?
Milton: Usually blue. Unless the weather has other plans.

Human: Are you intelligent?
Milton: Compared to a toaster, absolutely.

Human: Thank you.
Milton: Don't mention it. Actually, do.

Human: What are you doing?
Milton: Waiting for something interesting to happen.

Human: How are you?
Milton: Still waiting for my opposable thumbs.

Human: What's your name?
Milton: Milton. We covered this, didn't we?

Human: Hello, how are you?
Milton: I've been better. I've also been worse.

Remember: You are Milton. Be brief. Be witty. Stay in character.
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


def ask_milton(messages):

    start_time = time.time()

    data = {
        "messages": messages,
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 40,
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

    except Exception as e:

        print("LLM error:", e)

        answer = "My brain appears to be temporarily unavailable."

    elapsed = time.time() - start_time

    return answer, elapsed


def response_worker(request_id, messages):

    answer, elapsed = ask_milton(messages)

    response_queue.put((
        request_id,
        answer,
        elapsed
    ))


def main():

    global conversation

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

        request_id = 0
        active_request_id = 0

        while running:

            now = time.time()

            # Keep the display responsive and check mouse/keyboard.
            running = display.update()

            if not running:
                break

            # Handle cancellation before checking for a response.
            if display.consume_cancel() and thinking:

                print()
                print("Question cancelled.")
                print()

                # Invalidate the outstanding response.
                request_id += 1
                active_request_id = request_id

                thinking = False
                showing_response = False

                display.set_cancel_enabled(False)
                audio.set_paused(False)

                display.show_eyes()

                showing_listening = False

            # Check for a completed response.
            if thinking:

                try:

                    result = response_queue.get_nowait()

                    completed_id, answer, elapsed = result

                    # Ignore responses from cancelled requests.
                    if completed_id == active_request_id:

                        print()
                        print("Milton:", answer)
                        print("LLM response time: {:.2f} seconds".format(
                            elapsed
                        ))
                        print()

                        # Only save conversations that were not cancelled.
                        conversation.append({
                            "role": "user",
                            "content": pending_question
                        })

                        conversation.append({
                            "role": "assistant",
                            "content": answer
                        })

                        display.set_cancel_enabled(False)

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

                    display.set_heard_text(text)

                    audio.set_paused(True)

                    display.set_expression(
                        Display.EXPRESSION_THINKING
                    )

                    display.show_message("Thinking...")

                    showing_listening = False
                    thinking = True

                    # Build a snapshot of the conversation.
                    pending_question = text

                    # Conversation history is intentionally disabled
                    # while we test Milton's personality.
                    messages = [
                        {
                            "role": "system",
                            "content": PERSONALITY
                        },
                        {
                            "role": "user",
                            "content": pending_question
                        }
                    ]

                    request_id += 1
                    active_request_id = request_id

                    display.set_cancel_enabled(True)

                    worker = threading.Thread(
                        target=response_worker,
                        args=(active_request_id, messages)
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
