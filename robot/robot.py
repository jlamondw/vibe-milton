import time

from vision import Vision
from display import Display


def main():

    vision = Vision()
    display = Display()

    running = True

    try:

        while running:

            face = vision.get_face()

            print(face)


            if face["found"]:

                display.track_face(
                    face["x"],
                    face["y"]
                )

            else:

                display.idle()


            running = display.update()

            time.sleep(0.01)


    except KeyboardInterrupt:

        print("Stopping robot...")


    finally:

        vision.close()
        display.close()



if __name__ == "__main__":
    main()