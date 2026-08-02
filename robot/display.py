import pygame
import time


WIDTH = 800
HEIGHT = 480


class Display:

    MODE_EYES = "eyes"
    MODE_MESSAGE = "message"


    EXPRESSION_NORMAL = "normal"
    EXPRESSION_LISTENING = "listening"
    EXPRESSION_THINKING = "thinking"
    EXPRESSION_HAPPY = "happy"



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


        # Eye movement
        self.current_x = 0.5
        self.current_y = 0.5

        self.target_x = 0.5
        self.target_y = 0.5

        self.follow_speed = 0.12


        # State
        self.mode = self.MODE_EYES
        self.message = ""

        self.expression = self.EXPRESSION_HAPPY



    def set_expression(self, expression):

        self.expression = expression



    def look_at(self, x, y):

        self.target_x = 0.5 + (x - 0.5) * 3
        self.target_y = 0.5 + (y - 0.5) * 3

        self.target_x = max(
            0,
            min(1, self.target_x)
        )

        self.target_y = max(
            0,
            min(1, self.target_y)
        )

        self.mode = self.MODE_EYES



    def look_forward(self):

        self.look_at(0.5, 0.5)



    def show_message(self, text):

        self.mode = self.MODE_MESSAGE
        self.message = text



    def update_animation(self):

        self.current_x += (
            self.target_x - self.current_x
        ) * self.follow_speed


        self.current_y += (
            self.target_y - self.current_y
        ) * self.follow_speed



    def get_pupil_offset(self):

        max_move = int(
            self.eye_radius * 1.2
        )

        dx = (
            self.current_x - 0.5
        ) * 2 * max_move


        dy = (
            self.current_y - 0.5
        ) * 2 * max_move


        return int(dx), int(dy)



    def draw_eyebrows(self):

        lx, ly = self.left_eye
        rx, ry = self.right_eye


        eyebrow_y = int(
            self.eye_radius * 1.35
        )

        eyebrow_width = int(
            self.eye_radius * 0.6
        )


        thickness = 10



        if self.expression == self.EXPRESSION_NORMAL:

            left_start = (
                lx - eyebrow_width // 2,
                ly - eyebrow_y
            )

            left_end = (
                lx + eyebrow_width // 2,
                ly - eyebrow_y
            )

            right_start = (
                rx - eyebrow_width // 2,
                ry - eyebrow_y
            )

            right_end = (
                rx + eyebrow_width // 2,
                ry - eyebrow_y
            )



        elif self.expression == self.EXPRESSION_LISTENING:

            # Slightly raised outer edges
            left_start = (
                lx - eyebrow_width // 2,
                ly - eyebrow_y + 8
            )

            left_end = (
                lx + eyebrow_width // 2,
                ly - eyebrow_y - 8
            )

            right_start = (
                rx - eyebrow_width // 2,
                ry - eyebrow_y - 8
            )

            right_end = (
                rx + eyebrow_width // 2,
                ry - eyebrow_y + 8
            )



        elif self.expression == self.EXPRESSION_THINKING:

            # One eyebrow slightly raised
            left_start = (
                lx - eyebrow_width // 2,
                ly - eyebrow_y - 8
            )

            left_end = (
                lx + eyebrow_width // 2,
                ly - eyebrow_y - 8
            )

            right_start = (
                rx - eyebrow_width // 2,
                ry - eyebrow_y
            )

            right_end = (
                rx + eyebrow_width // 2,
                ry - eyebrow_y + 12
            )



        else:  # happy

            left_start = (
                lx - eyebrow_width // 2,
                ly - eyebrow_y + 8
            )

            left_end = (
                lx + eyebrow_width // 2,
                ly - eyebrow_y - 8
            )

            right_start = (
                rx - eyebrow_width // 2,
                ry - eyebrow_y - 8
            )

            right_end = (
                rx + eyebrow_width // 2,
                ry - eyebrow_y + 8
            )



        pygame.draw.line(
            self.screen,
            (255,255,255),
            left_start,
            left_end,
            thickness
        )


        pygame.draw.line(
            self.screen,
            (255,255,255),
            right_start,
            right_end,
            thickness
        )



    def draw_eye(self, center, dx, dy):

        cx, cy = center


        pygame.draw.circle(
            self.screen,
            (255,255,255),
            (cx, cy),
            self.eye_radius
        )


        pygame.draw.circle(
            self.screen,
            (0,0,0),
            (
                cx + dx,
                cy + dy
            ),
            self.pupil_radius
        )



    def draw_eyes(self):

        self.screen.fill(
            (0,0,0)
        )


        self.draw_eyebrows()


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
            (20,20,20)
        )


        surface = self.font.render(
            self.message,
            True,
            (255,255,255)
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


        if self.mode == self.MODE_EYES:

            self.draw_eyes()


        elif self.mode == self.MODE_MESSAGE:

            self.draw_message()


        pygame.display.flip()

        self.clock.tick(30)

        return True



    def close(self):

        pygame.quit()