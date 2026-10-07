import audioop
import json
import subprocess
import wave

from vosk import Model, KaldiRecognizer, SetLogLevel


# Vosk model is one directory above the robot scripts.
MODEL_PATH = "/home/jetbot/vosk-model-small-en-us-0.15"

# Your USB microphone.
AUDIO_DEVICE = "hw:2,0"

# Your microphone works at 44100 Hz.
INPUT_RATE = 44100

# Vosk will process the audio at 16000 Hz.
VOSK_RATE = 16000

# How long to listen each time.
RECORD_SECONDS = 5


# The four things our first robot understands.
# We've included a few natural variations.
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


def record_audio():
    print()
    print("Listening...")
    print("Say something.")

    command = [
        "arecord",
        "-D", AUDIO_DEVICE,
        "-f", "S16_LE",
        "-r", str(INPUT_RATE),
        "-c", "1",
        "-d", str(RECORD_SECONDS),
        "-q",
        "/tmp/robot_speech.wav"
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print("Recording failed:", e)
        return None

    return "/tmp/robot_speech.wav"


def recognize_audio(filename, model):
    print("Processing...")

    try:
        wf = wave.open(filename, "rb")
    except Exception as e:
        print("Could not open recording:", e)
        return ""

    raw_audio = wf.readframes(wf.getnframes())
    wf.close()

    # Convert 44100 Hz -> 16000 Hz for Vosk.
    converted_audio, _ = audioop.ratecv(
        raw_audio,
        2,              # 16-bit audio
        1,              # mono
        INPUT_RATE,
        VOSK_RATE,
        None
    )

    grammar = json.dumps(COMMANDS)

    recognizer = KaldiRecognizer(
        model,
        VOSK_RATE,
        grammar
    )

    recognizer.AcceptWaveform(converted_audio)

    result = json.loads(recognizer.FinalResult())

    return result.get("text", "").strip()


def get_intent(text):
    text = text.lower().strip()

    if text in ("hello", "hi", "hey"):
        return "hello"

    if text in ("joke", "tell me a joke"):
        return "joke"

    if text in ("happy", "are you happy"):
        return "happy"

    if text in ("sleep", "go to sleep"):
        return "sleep"

    return "unknown"


def main():
    print()
    print("================================")
    print(" Robot Speech Recognition Test")
    print("================================")
    print()
    print("The robot understands:")
    print("  hello")
    print("  joke")
    print("  happy")
    print("  sleep")
    print()
    print("Anything else should become 'unknown'.")
    print()

    SetLogLevel(-1)

    print("Loading speech model...")
    model = Model(MODEL_PATH)
    print("Speech model loaded.")

    while True:
        filename = record_audio()

        if filename is None:
            break

        text = recognize_audio(filename, model)

        print()
        print("Recognized:", repr(text))
        print("Intent:    ", get_intent(text))
        print()

        answer = input("Press Enter to listen again, or q to quit: ")

        if answer.lower() == "q":
            break


if __name__ == "__main__":
    main()