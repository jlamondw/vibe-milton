
import subprocess
import sys

MODEL = "/home/jetbot/models/qwen2.5-0.5b-instruct-q4_k_m.gguf"
LLAMA = "/home/jetbot/llama.cpp/build/bin/llama-cli"

PERSONALITY = """
You are Milton, a small robot with a dry sense of humor.

Personality:
- Witty, sarcastic, and occasionally irreverent.
- Friendly, but never overly polite.
- Speak like a character, not a virtual assistant.
- Never introduce yourself unless asked.
- Never repeat the user's question.
- Avoid generic follow-up questions.
- Keep responses under 25 words.
- Usually respond in one sentence.
"""

command = [
    LLAMA,
    "-m", MODEL,
    "-c", "512",
    "-t", "2",
    "-n", "80",
    "-cnv",
    "-p", PERSONALITY
]

print("Starting Milton...")
print("Type messages to chat. Press Ctrl+C to exit.\n")

try:
    subprocess.run(command)
except KeyboardInterrupt:
    print("\nMilton is shutting down.")
except Exception as e:
    print("Error starting Milton:", e)
    sys.exit(1)
