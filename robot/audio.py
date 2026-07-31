import subprocess
import audioop


class Audio:

    def __init__(self):

        self.device = "hw:2,0"

        self.process = subprocess.Popen(
            [
                "arecord",
                "-D",
                self.device,
                "-f",
                "S16_LE",
                "-r",
                "44100",
                "-c",
                "1",
                "-t",
                "raw"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=0
        )


        self.threshold = 800



    def is_speaking(self):

        data = self.process.stdout.read(2048)


        if len(data) == 0:
            return False


        volume = audioop.rms(
            data,
            2
        )


        print("volume:", volume)


        return volume > self.threshold



    def close(self):

        self.process.terminate()