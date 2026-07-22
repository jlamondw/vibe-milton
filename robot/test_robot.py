from vision import Vision
from display import Display
import time


vision = Vision()
display = Display()


try:

    while True:

        face = vision.get_face()

        print(face)

        display.update()

        time.sleep(0.01)


except KeyboardInterrupt:
    pass


finally:
    vision.close()
    display.close()