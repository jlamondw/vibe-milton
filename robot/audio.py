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


        # Start listening above this volume
        self.start_threshold = 1000

        # Stop listening below this volume
        self.stop_threshold = 850

        # Require multiple samples before changing state
        self.required_count = 3

        self.high_count = 0
        self.low_count = 0

        self.listening = False



    def is_speaking(self):

        # About ~100ms of audio
        data = self.process.stdout.read(8192)


        if len(data) == 0:
            return False


        volume = audioop.rms(
            data,
            2
        )


        print(
            "volume:",
            volume,
            "listening:",
            self.listening
        )


        if not self.listening:

            # Need sustained sound to start listening
            if volume > self.start_threshold:

                self.high_count += 1

            else:

                self.high_count = 0


            if self.high_count >= self.required_count:

                self.listening = True
                self.low_count = 0



        else:

            # Need sustained quiet to stop listening
            if volume < self.stop_threshold:

                self.low_count += 1

            else:

                self.low_count = 0


            if self.low_count >= self.required_count:

                self.listening = False
                self.high_count = 0



        return self.listening



    def close(self):

        self.process.terminate()

        try:

            self.process.wait(timeout=1)

        except Exception:

            self.process.kill()