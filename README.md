
## Dependencies

### Hardware
- NVIDIA Jetson Nano 2GB
- Ubuntu 18.04 / JetPack 4.5
- HDMI display
- USB microphone

### Software
- Python 3.6.9
- Pygame 2.6.1
- Vosk speech recognition
- ALSA audio subsystem
- llama.cpp (b4510)

### Language Model
- Qwen 2.5 0.5B Instruct
- GGUF Q4_K_M quantization
- `qwen2.5-0.5b-instruct-q4_k_m.gguf`

### Build Requirements
- GCC 8 / G++ 8
- CMake 3.27.9
- C++17

### Architecture
Milton uses:
- Vosk for offline speech recognition
- llama.cpp for local LLM inference
- Pygame for the robot's animated display
- Python threads for asynchronous LLM requests

All language processing runs locally on the Jetson Nano.
