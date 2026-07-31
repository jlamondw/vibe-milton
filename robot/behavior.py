class Behavior:

    IDLE = "idle"
    TRACKING = "tracking"
    LISTENING = "listening"


    def __init__(self):

        self.state = self.IDLE



    def update(self, face, speaking):

        if speaking:

            self.state = self.LISTENING


        elif face["found"]:

            self.state = self.TRACKING


        else:

            self.state = self.IDLE



    def get_state(self):

        return self.state