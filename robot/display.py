import pygame
import math

WIDTH = 800
HEIGHT = 480

class Display:

    def __init__(self):
        # pygame.display.init()
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Robot")

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(None, 42)

        self.eye_radius = int(HEIGHT * 0.2)
        self.pupil_radius = int(self.eye_radius * 0.35)

        self.max_offset = self.eye_radius - self.pupil_radius - 12

        self.left_eye = (int(WIDTH * 0.3), int(HEIGHT * 0.5))
        self.right_eye = (int(WIDTH * 0.7), int(HEIGHT * 0.5))

    def draw_eye(self, center, dx, dy):
        cx, cy = center

        pygame.draw.circle(
            self.screen,
            (255,255,255),
            (cx,cy),
            self.eye_radius
        )

        pygame.draw.circle(
            self.screen,
            (0,0,0),
            (int(cx+dx), int(cy+dy)),
            self.pupil_radius
        )

    def draw_eyes(self, state):
        self.screen.fill((0,0,0))

        self.draw_eye(
            self.left_eye,
            state.pupil_x,
            state.pupil_y
        )

        self.draw_eye(
            self.right_eye,
            state.pupil_x,
            state.pupil_y
        )

    def draw_message(self, text):
        self.screen.fill((20,20,20))

        lines = text.split("\n")

        y = 100

        for line in lines:

            surface = self.font.render(
                line,
                True,
                (255,255,255)
            )

            rect = surface.get_rect(center=(WIDTH//2,y))

            self.screen.blit(surface, rect)

            y += 50

    def update(self, state):
        if state.mode == state.MODE_EYES:
            self.draw_eyes(state)

        elif state.mode == state.MODE_LISTENING:
            self.draw_message("Listening...")

        elif state.mode == state.MODE_THINKING:
            self.draw_message("Thinking...")

        elif state.mode == state.MODE_MESSAGE:
            self.draw_message(state.message)

        pygame.display.flip()

        self.clock.tick(30)