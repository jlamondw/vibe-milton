import time

from vision import Vision
from audio import Audio
from display import Display
from behavior import Behavior


def main():
    vision = Vision()
    audio = Audio()
    display = Display()
    behavior = Behavior()

    running = True

    try:
        while running:
            face = vision.get_face()

            speaking = audio.is_speaking()
            text = audio.get_text()

            behavior.update(
                face,
                speaking,
                text
            )

            state = behavior.get_state()

            print("STATE:", state)

            if state == Behavior.LISTENING:
                display.set_expression(
                    Display.EXPRESSION_LISTENING
                )
                display.show_message(
                    "Listening..."
                )

            elif state == Behavior.THINKING:
                display.set_expression(
                    Display.EXPRESSION_THINKING
                )
                display.show_message(
                    "Thinking..."
                )

            elif state == Behavior.RESPONDING:
                display.set_expression(
                    Display.EXPRESSION_HAPPY
                )
                display.show_message(
                    behavior.get_message()
                )

            elif state == Behavior.TRACKING:
                display.set_expression(
                    Display.EXPRESSION_NORMAL
                )
                display.look_at(
                    face["x"],
                    face["y"]
                )

            elif state == Behavior.IDLE:
                display.set_expression(
                    Display.EXPRESSION_NORMAL
                )
                display.look_forward()

            running = display.update()

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Stopping robot...")

    finally:
        vision.close()
        audio.close()
        display.close()


if __name__ == "__main__":
    main()