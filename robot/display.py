
import pygame


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

        # Use the monitor's native resolution in fullscreen mode.
        self.screen = pygame.display.set_mode(
            (0, 0),
            pygame.FULLSCREEN
        )

        self.width, self.height = self.screen.get_size()

        pygame.display.set_caption("Milton")

        self.clock = pygame.time.Clock()

        # Smaller fonts for responses and speech debugging.
        self.font = pygame.font.SysFont(None, 26)
        self.debug_font = pygame.font.SysFont(None, 20)

        # Eye geometry, scaled to the display.
        self.eye_radius = int(self.height * 0.2)
        self.pupil_radius = int(self.eye_radius * 0.35)

        self.left_eye = (
            int(self.width * 0.3),
            int(self.height * 0.35)
        )

        self.right_eye = (
            int(self.width * 0.7),
            int(self.height * 0.35)
        )

        # Eye movement.
        self.current_x = 0.5
        self.current_y = 0.5

        self.target_x = 0.5
        self.target_y = 0.5

        self.follow_speed = 0.12

        # Display state.
        self.mode = self.MODE_EYES
        self.message = ""
        self.heard_text = ""
        self.expression = self.EXPRESSION_NORMAL

    def set_expression(self, expression):
        self.expression = expression

    def look_at(self, x, y):

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

    def show_eyes(self):
        self.mode = self.MODE_EYES
        self.expression = self.EXPRESSION_NORMAL

    def set_heard_text(self, text):
        self.heard_text = text

    def update_animation(self):

        self.current_x += (
            self.target_x - self.current_x
        ) * self.follow_speed

        self.current_y += (
            self.target_y - self.current_y
        ) * self.follow_speed

    def get_pupil_offset(self):

        max_move = int(self.eye_radius * 1.2)

        dx = (self.current_x - 0.5) * 2 * max_move
        dy = (self.current_y - 0.5) * 2 * max_move

        return int(dx), int(dy)

    def draw_eyebrows(self):

        lx, ly = self.left_eye
        rx, ry = self.right_eye

        eyebrow_y = int(self.eye_radius * 1.35)
        width = int(self.eye_radius * 0.6)
        thickness = max(2, int(self.height * 0.02))

        left_start = (
            lx - width // 2,
            ly - eyebrow_y
        )

        left_end = (
            lx + width // 2,
            ly - eyebrow_y
        )

        right_start = (
            rx - width // 2,
            ry - eyebrow_y
        )

        right_end = (
            rx + width // 2,
            ry - eyebrow_y
        )

        if self.expression == self.EXPRESSION_LISTENING:

            left_start = (
                lx - width // 2,
                ly - eyebrow_y + 8
            )

            left_end = (
                lx + width // 2,
                ly - eyebrow_y - 8
            )

            right_start = (
                rx - width // 2,
                ry - eyebrow_y - 8
            )

            right_end = (
                rx + width // 2,
                ry - eyebrow_y + 8
            )

        elif self.expression == self.EXPRESSION_THINKING:

            left_start = (
                lx - width // 2,
                ly - eyebrow_y - 5
            )

            left_end = (
                lx + width // 2,
                ly - eyebrow_y - 5
            )

            right_start = (
                rx - width // 2,
                ry - eyebrow_y + 10
            )

            right_end = (
                rx + width // 2,
                ry - eyebrow_y + 10
            )

        elif self.expression == self.EXPRESSION_HAPPY:

            left_start = (
                lx - width // 2,
                ly - eyebrow_y + 5
            )

            left_end = (
                lx + width // 2,
                ly - eyebrow_y - 5
            )

            right_start = (
                rx - width // 2,
                ry - eyebrow_y - 5
            )

            right_end = (
                rx + width // 2,
                ry - eyebrow_y + 5
            )

        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            left_start,
            left_end,
            thickness
        )

        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            right_start,
            right_end,
            thickness
        )

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
            (cx + dx, cy + dy),
            self.pupil_radius
        )

    def draw_face(self):

        self.draw_eyebrows()

        dx, dy = self.get_pupil_offset()

        self.draw_eye(self.left_eye, dx, dy)
        self.draw_eye(self.right_eye, dx, dy)

    def wrap_message(self, message, max_width):

        words = message.split()
        lines = []
        current_line = ""

        for word in words:

            test_line = (
                word if not current_line
                else current_line + " " + word
            )

            if self.font.size(test_line)[0] <= max_width:
                current_line = test_line

            else:
                if current_line:
                    lines.append(current_line)

                current_line = word

        if current_line:
            lines.append(current_line)

        if len(lines) > 3:
            lines = lines[:3]
            last = lines[2]

            while last and self.font.size(last + "...")[0] > max_width:
                last = last[:-1]

            lines[2] = last.rstrip() + "..."

        return lines

    def draw_message(self):

        self.draw_face()

        lines = self.wrap_message(
            self.message,
            self.width - 80
        )

        line_height = 32
        total_height = len(lines) * line_height

        center_y = int(self.height * 0.80)
        start_y = center_y - total_height // 2

        for index, line in enumerate(lines):

            surface = self.font.render(
                line,
                True,
                (255, 255, 255)
            )

            rect = surface.get_rect(
                center=(
                    self.width // 2,
                    start_y + index * line_height
                    + line_height // 2
                )
            )

            self.screen.blit(surface, rect)

    def draw_debug_text(self):

        if not self.heard_text:
            return

        text = "HEARD: " + self.heard_text

        max_width = self.width - 40

        while text and self.debug_font.size(text)[0] > max_width:
            text = text[:-4] + "..."

        surface = self.debug_font.render(
            text,
            True,
            (150, 150, 150)
        )

        rect = surface.get_rect(
            center=(
                self.width // 2,
                self.height - 22
            )
        )

        self.screen.blit(surface, rect)

    def update(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

        self.screen.fill((0, 0, 0))

        self.update_animation()

        if self.mode == self.MODE_EYES:
            self.draw_face()

        elif self.mode == self.MODE_MESSAGE:
            self.draw_message()

        self.draw_debug_text()

        pygame.display.flip()

        self.clock.tick(30)

        return True

    def close(self):
        pygame.quit()
