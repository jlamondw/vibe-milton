import time
import random


class Behavior:

    IDLE = "idle"
    TRACKING = "tracking"
    LISTENING = "listening"
    THINKING = "thinking"
    RESPONDING = "responding"


    def __init__(self):

        self.state = self.IDLE

        self.last_speaking = False

        self.thinking_start = None
        self.response_start = None

        self.thinking_time = 2.0
        self.response_time = 3.0


        self.responses = [
            "Hello!",
            "Nice to see you.",
            "I'm awake.",
            "I see you.",
            "Still here.",
            "Beep boop.",
            "Interesting..."
        ]

        self.current_message = ""



    def update(self, face, speaking):

        now = time.time()


        #
        # Currently listening
        #
        if self.state == self.LISTENING:

            if not speaking:

                self.state = self.THINKING
                self.thinking_start = now

            return



        #
        # Thinking
        #
        if self.state == self.THINKING:

            if now - self.thinking_start >= self.thinking_time:

                self.state = self.RESPONDING

                self.current_message = random.choice(
                    self.responses
                )

                self.response_start = now

            return



        #
        # Responding
        #
        if self.state == self.RESPONDING:

            if now - self.response_start >= self.response_time:

                self.state = self.TRACKING

            return



        #
        # Normal operation
        #

        if speaking:

            self.state = self.LISTENING


        elif face["found"]:

            self.state = self.TRACKING


        else:

            self.state = self.IDLE



    def get_state(self):

        return self.state



    def get_message(self):

        return self.current_message