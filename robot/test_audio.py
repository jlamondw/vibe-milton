from audio import Audio
import time


audio = Audio()


try:

    while True:

        if audio.is_speaking():
            print("SPEAKING")

        else:
            print("quiet")


        time.sleep(0.1)


except KeyboardInterrupt:
    pass


finally:
    audio.close()