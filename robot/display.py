import pygame
import random
import time


WIDTH = 800
HEIGHT = 480


class Display:

    MODE_EYES = "eyes"
    MODE_MESSAGE = "message"


    def __init__(self):

        pygame.init()

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        pygame.display.set_caption("Robot")

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(None, 42)


        # Eye geometry
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


        # Current eye position
        self.current_x = 0.5
        self.current_y = 0.5


        # Target eye position
        self.target_x = 0.5
        self.target_y = 0.5


        # How quickly eyes move
        self.follow_speed = 0.12


        # State
        self.mode = self.MODE_EYES
        self.message = ""


        # Blink state
        self.blinking = False
        self.blink_amount = 0
        self.next_blink = time.time() + random.uniform(2, 5)



    def look_at(self, x, y):

        # print(
        #     "LOOK AT:",
        #     round(x, 2),
        #     round(y, 2)
        # )

        # Clamp values
        # self.target_x = max(0, min(1, x))
        # self.target_y = max(0, min(1, y))
        # Increase sensitivity around center
        self.target_x = 0.5 + (x - 0.5) * 3
        self.target_y = 0.5 + (y - 0.5) * 3

        self.target_x = max(0, min(1, self.target_x))
        self.target_y = max(0, min(1, self.target_y))        


        self.mode = self.MODE_EYES



    def look_forward(self):

        self.look_at(0.5, 0.5)



    def show_message(self, text):

        self.mode = self.MODE_MESSAGE
        self.message = text



    def update_animation(self):

        # Smooth movement toward target

        self.current_x += (
            self.target_x - self.current_x
        ) * self.follow_speed


        self.current_y += (
            self.target_y - self.current_y
        ) * self.follow_speed



    def update_blink(self):

        now = time.time()


        if not self.blinking:

            if now >= self.next_blink:
                self.blinking = True
                self.blink_amount = 0


        else:

            self.blink_amount += 0.25


            if self.blink_amount >= 1:

                self.blinking = False
                self.blink_amount = 0

                self.next_blink = (
                    now + random.uniform(2, 5)
                )



    def get_pupil_offset(self):

        max_move = int(
            self.eye_radius * 1.2
            # self.eye_radius * 0.45
        )


        dx = (
            self.current_x - 0.5
        ) * 2 * max_move


        dy = (
            self.current_y - 0.5
        ) * 2 * max_move


        return int(dx), int(dy)



    def draw_eye(self, center, dx, dy):

        cx, cy = center


        pygame.draw.circle(
            self.screen,
            (255, 255, 255),
            (cx, cy),
            self.eye_radius
        )


        # Simple blink effect
        if self.blinking:

            height = int(
                self.eye_radius *
                (1 - self.blink_amount)
            )

            pygame.draw.rect(
                self.screen,
                (0, 0, 0),
                (
                    cx - self.eye_radius,
                    cy - height,
                    self.eye_radius * 2,
                    height * 2
                )
            )

            return



        pygame.draw.circle(
            self.screen,
            (0, 0, 0),
            (
                cx + dx,
                cy + dy
            ),
            self.pupil_radius
        )



    def draw_eyes(self):

        self.screen.fill(
            (0, 0, 0)
        )


        dx, dy = self.get_pupil_offset()


        self.draw_eye(
            self.left_eye,
            dx,
            dy
        )


        self.draw_eye(
            self.right_eye,
            dx,
            dy
        )



    def draw_message(self):

        self.screen.fill(
            (20, 20, 20)
        )


        surface = self.font.render(
            self.message,
            True,
            (255, 255, 255)
        )


        rect = surface.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2
            )
        )


        self.screen.blit(
            surface,
            rect
        )



    def update(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False


        self.update_animation()
        self.update_blink()


        if self.mode == self.MODE_EYES:
            self.draw_eyes()

        elif self.mode == self.MODE_MESSAGE:
            self.draw_message()


        pygame.display.flip()

        self.clock.tick(30)

        return True



    def close(self):

        pygame.quit()