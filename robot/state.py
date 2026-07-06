class RobotState:
    MODE_EYES = "eyes"
    MODE_LISTENING = "listening"
    MODE_THINKING = "thinking"
    MODE_MESSAGE = "message"

    def __init__(self):
        self.mode = self.MODE_EYES

        # Eye position
        self.pupil_x = 0
        self.pupil_y = 0

        # Text shown on screen
        self.message = ""

        # Time when current mode started
        self.mode_start = 0