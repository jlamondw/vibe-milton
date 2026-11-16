
import audioop
import json
import subprocess
import threading
import time
from collections import deque

from vosk import Model, KaldiRecognizer, SetLogLevel


MODEL_PATH = "/home/jetbot/vosk-model-small-en-us-0.15"

AUDIO_DEVICE = "hw:2,0"

INPUT_RATE = 44100
VOSK_RATE = 16000

CHUNK_SECONDS = 0.10
CHUNK_BYTES = int(INPUT_RATE * 2 * CHUNK_SECONDS)

START_THRESHOLD = 1000
STOP_THRESHOLD = 850

START_COUNT_REQUIRED = 3
STOP_COUNT_REQUIRED = 6

PREBUFFER_CHUNKS = 5


COMMANDS = [
    "hello",
    "hi",
    "hey",
    "joke",
    "tell me a joke",
    "happy",
    "are you happy",
    "sleep",
    "go to sleep",
    "[unk]"
]


class Audio:
    def __init__(self, grammar=COMMANDS):
        SetLogLevel(-1)

        print("Loading speech model...")
        self.model = Model(MODEL_PATH)
        print("Speech model loaded.")

        # Keep the original command grammar by default.
        # Pass grammar=None to recognize unrestricted speech.
        self.grammar = grammar

        self.running = True
        self.paused = False
        self.speaking = False
        self.new_text = ""

        self.start_count = 0
        self.stop_count = 0

        self.prebuffer = deque(maxlen=PREBUFFER_CHUNKS)

        self.recognizer = None
        self.ratecv_state = None

        self.process = None
        self.lock = threading.Lock()

        self.start_microphone()

        self.thread = threading.Thread(
            target=self.capture_loop
        )
        self.thread.daemon = True
        self.thread.start()

    def start_microphone(self):
        print("Starting microphone...")

        command = [
            "arecord",
            "-D", AUDIO_DEVICE,
            "-f", "S16_LE",
            "-r", str(INPUT_RATE),
            "-c", "1",
            "-t", "raw",
            "-q"
        ]

        try:
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=0
            )
        except Exception as e:
            print("Could not start microphone:")
            print(e)
            self.process = None

    def make_recognizer(self):
        if self.grammar is None:
            return KaldiRecognizer(
                self.model,
                VOSK_RATE
            )

        return KaldiRecognizer(
            self.model,
            VOSK_RATE,
            json.dumps(self.grammar)
        )

    def set_paused(self, paused):
        self.paused = paused

    def capture_loop(self):
        if self.process is None:
            return

        while self.running:
            try:
                data = self.process.stdout.read(CHUNK_BYTES)
            except Exception:
                break

            if not data:
                break

            # Discard microphone input while Milton is responding.
            if self.paused:
                self.speaking = False
                self.start_count = 0
                self.stop_count = 0
                self.recognizer = None
                self.prebuffer.clear()
                self.ratecv_state = None
                continue

            rms = audioop.rms(data, 2)

            converted_audio, self.ratecv_state = audioop.ratecv(
                data,
                2,
                1,
                INPUT_RATE,
                VOSK_RATE,
                self.ratecv_state
            )

            if not self.speaking:
                self.prebuffer.append(converted_audio)

                if rms >= START_THRESHOLD:
                    self.start_count += 1
                else:
                    self.start_count = 0

                if self.start_count >= START_COUNT_REQUIRED:
                    self.speaking = True
                    self.stop_count = 0
                    self.start_count = 0

                    print("LISTENING")

                    self.recognizer = self.make_recognizer()

                    for buffered_audio in self.prebuffer:
                        self.recognizer.AcceptWaveform(
                            buffered_audio
                        )

                    self.prebuffer.clear()

            else:
                if self.recognizer is not None:
                    self.recognizer.AcceptWaveform(
                        converted_audio
                    )

                if rms <= STOP_THRESHOLD:
                    self.stop_count += 1
                else:
                    self.stop_count = 0

                if self.stop_count >= STOP_COUNT_REQUIRED:
                    self.finish_utterance()

            time.sleep(0.001)

    def finish_utterance(self):
        text = ""

        if self.recognizer is not None:
            try:
                result = json.loads(
                    self.recognizer.FinalResult()
                )
                text = result.get("text", "").strip()
            except Exception as e:
                print("Speech recognition error:")
                print(e)

        print("RECOGNIZED:", repr(text))

        with self.lock:
            self.new_text = text

        self.speaking = False
        self.stop_count = 0
        self.start_count = 0
        self.recognizer = None
        self.prebuffer.clear()

    def is_speaking(self):
        return self.speaking

    def get_text(self):
        with self.lock:
            text = self.new_text
            self.new_text = ""

        return text

    def close(self):
        print("Stopping microphone...")

        self.running = False

        if self.process is not None:
            try:
                self.process.terminate()
            except Exception:
                pass

        if hasattr(self, "thread"):
            self.thread.join(timeout=1.0)

        self.process = None
