import random
import time


class Behavior:
    IDLE = "idle"
    TRACKING = "tracking"
    LISTENING = "listening"
    THINKING = "thinking"
    RESPONDING = "responding"

    def __init__(self):
        self.state = self.IDLE

        self.thinking_start = None
        self.response_start = None

        self.thinking_time = 1.5
        self.response_time = 3.0

        self.current_message = ""
        self.current_command = ""

        self.command_responses = {
            "hello": [
                "Hello!",
                "Oh. Hi.",
                "Greetings, human.",
                "Hello, carbon unit.",
                "I see you."
            ],

            "joke": [
                "Why did the robot cross the road?",
                "I would tell you a robot joke...",
                "Beep boop. That's the joke.",
                "My humor circuits are fully operational.",
                "Knock knock. I don't have hands."
            ],

            "happy": [
                "I'm a tiny robot. Of course I'm happy.",
                "Happiness level: adequate.",
                "I am experiencing approximately 73% joy.",
                "Beep boop. Emotion detected.",
                "Yes. Probably."
            ],

            "sleep": [
                "Sleep mode denied.",
                "No. I'm busy.",
                "I don't need sleep.",
                "I'll pretend to sleep.",
                "Fine. Wake me later."
            ]
        }

        self.random_responses = [
            "Beep boop.",
            "Interesting...",
            "I have no idea what that means.",
            "Processing... still processing.",
            "That sounds like a human problem.",
            "Please consult the manual.",
            "I forgot my manual.",
            "Hmm.",
            "Fascinating.",
            "My circuits have questions.",
            "That was definitely words.",
            "I am choosing to ignore that.",
            "Error: human detected.",
            "I have concerns.",
        ]

    def get_intent(self, text):
        text = text.lower().strip()

        if text in ("hello", "hi", "hey"):
            return "hello"

        if text in ("joke", "tell me a joke"):
            return "joke"

        if text in ("happy", "are you happy"):
            return "happy"

        if text in ("sleep", "go to sleep"):
            return "sleep"

        return "unknown"

    def choose_response(self, intent):
        if intent in self.command_responses:
            return random.choice(
                self.command_responses[intent]
            )

        return random.choice(self.random_responses)

    def update(self, face, speaking, text):
        now = time.time()

        # Currently responding.
        if self.state == self.RESPONDING:
            if now - self.response_start >= self.response_time:
                self.state = self.TRACKING

            return

        # Currently thinking about the thing the user said.
        if self.state == self.THINKING:
            if now - self.thinking_start >= self.thinking_time:
                intent = self.get_intent(self.current_command)

                self.current_message = self.choose_response(intent)

                self.state = self.RESPONDING
                self.response_start = now

            return

        # User is currently speaking.
        if speaking:
            self.state = self.LISTENING
            return

        # We have just received a completed utterance.
        if text:
            self.current_command = text

            print("COMMAND:", repr(text))
            print("INTENT:", self.get_intent(text))

            self.state = self.THINKING
            self.thinking_start = now

            return

        # Nobody is speaking.
        if face["found"]:
            self.state = self.TRACKING
        else:
            self.state = self.IDLE

    def get_state(self):
        return self.state

    def get_message(self):
        return self.current_message