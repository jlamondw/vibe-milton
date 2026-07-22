import pygame

WIDTH = 800
HEIGHT = 480


class Display:

    MODE_EYES = "eyes"
    MODE_LISTENING = "listening"
    MODE_THINKING = "thinking"
    MODE_MESSAGE = "message"


    def __init__(self):

        pygame.init()

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        pygame.display.set_caption("Robot")

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(None, 42)


        self.eye_radius = int(HEIGHT * 0.2)
        self.pupil_radius = int(self.eye_radius * 0.35)


        self.left_eye = (
            int(WIDTH * 0.3),
            int(HEIGHT * 0.5)
        )

        self.right_eye = (
            int(WIDTH * 0.7),
            int(HEIGHT * 0.5)
        )


        self.mode = self.MODE_EYES
        self.message = ""


        self.pupil_x = 0
        self.pupil_y = 0



    def show_eyes(self):
        self.mode = self.MODE_EYES


    def show_listening(self):
        self.mode = self.MODE_LISTENING


    def show_thinking(self):
        self.mode = self.MODE_THINKING


    def show_message(self, text):
        self.mode = self.MODE_MESSAGE
        self.message = text



    def track_face(self, x, y):

        # Maximum pupil movement
        max_move = int(self.eye_radius * 0.45)


        # Convert normalized camera coordinates
        # into eye movement

        self.pupil_x = int(
            (x - 0.5) * 2 * max_move
        )

        self.pupil_y = int(
            (y - 0.5) * 2 * max_move
        )


        self.show_eyes()



    def idle(self):

        self.show_eyes()



    def draw_eye(self, center, dx, dy):

        cx, cy = center


        pygame.draw.circle(
            self.screen,
            (255, 255, 255),
            (cx, cy),
            self.eye_radius
        )


        pygame.draw.circle(
            self.screen,
            (0, 0, 0),
            (
                int(cx + dx),
                int(cy + dy)
            ),
            self.pupil_radius
        )



    def draw_eyes(self):

        self.screen.fill((0, 0, 0))


        self.draw_eye(
            self.left_eye,
            self.pupil_x,
            self.pupil_y
        )


        self.draw_eye(
            self.right_eye,
            self.pupil_x,
            self.pupil_y
        )



    def draw_centered_text(self, text):

        self.screen.fill(
            (20, 20, 20)
        )


        lines = text.split("\n")

        total_height = len(lines) * 50

        y = (
            HEIGHT - total_height
        ) // 2


        for line in lines:

            surface = self.font.render(
                line,
                True,
                (255, 255, 255)
            )


            rect = surface.get_rect(
                center=(
                    WIDTH // 2,
                    y
                )
            )


            self.screen.blit(
                surface,
                rect
            )


            y += 50



    def update(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False


        if self.mode == self.MODE_EYES:

            self.draw_eyes()


        elif self.mode == self.MODE_LISTENING:

            self.draw_centered_text(
                "Listening..."
            )


        elif self.mode == self.MODE_THINKING:

            self.draw_centered_text(
                "Thinking..."
            )


        elif self.mode == self.MODE_MESSAGE:

            self.draw_centered_text(
                self.message
            )


        pygame.display.flip()

        self.clock.tick(30)

        return True



    def close(self):

        pygame.quit()