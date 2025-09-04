# `code_speak`

A hotkey-driven low-latency speech-to-text library that provides seamless voice input integration with any CLI Agentic/AI coding tools such as: [`claude`](https://claude.ai/code), [`aider`](https://github.com/paul-gauthier/aider), [`codex`](https://github.com/openai/codex), etc.

- **Agnostic** though a direct keyboard-only implementation via [pyautogui](https://pyautogui.readthedocs.io/en/latest/index.html) 'should' work with all cli tools
- **Local & Low-latency Transcription** via [RealtimeSTT](https://github.com/KoljaB/RealtimeSTT) and [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- **Configurable** multiple Speech-To-Text Models, push-to-record hotkey, recording indicator, plus other goodies
- **Easy Installation** that should work in most environments thanks


## Quick Start

#### ▎Workflow

1. **Start**: Run `code_speak` to launch AI cli like `claude` with voice integration (set default `binary` via `-b` or in config)
2. **Press**: The configured push-to-talk key (default: `right_shift`)
3. **Speak**: A configurable recording indicator (`;`) appears while recording
    - Or press `escape` to cancel the current recording
4. **Press**: The configured push-to-talk key again to stop recording
5. **Done**:  Your transcribed speech is automatically typed into Claude Code


#### ▎Install

```bash
git clone <repository-url>
cd code_speak

# setup & create a virtual environment
uv venv -p 3.12 && source .venv/bin/activate

# standard install via uv (with cuda)
uv sync

# manual (with cuda)
uv pip install RealtimeSTT pyautogui pynput rich

# cpu-only (no cuda)
uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
uv pip install RealtimeSTT pyautogui pynput rich
```
> Assumes [`claude`](https://claude.ai/code), [`aider`](https://github.com/paul-gauthier/aider), [`codex`](https://github.com/openai/codex), or similar is installed and available in the `PATH`

#### ▎Setup

```bash
# via helper script
./code_speak --setup

# via uv
uv run ./main.py --setup
```

#### ▎Usage/Setup

```bash
# via helper script
./claude_speak                   # Start voice-enabled Claude Code
./claude_speak --setup           # Initial configuration helper
./claude_speak --config          # Show configuration
./claude_speak --test            # Test voice functionality

# via uv
uv run ./main.py
uv run ./main.py --setup
uv run ./main.py --config
uv run ./main.py --test
```


## Configuration

#### ▎Locations

1. **Environment Variable**: Set `CODE_SPEAK_CONFIG` to specify a custom path
2. **Default Config**: `<config>/code_speak/code_speak.json` (if it exists)
     - macOS: `~/Library/Preferences`
     - Windows: `%APPDATA%` (or `~/AppData/Roaming` as fallback)
     - Linux: `XDG_CONFIG_HOME` (or `~/.config` as fallback per XDG Base Directory spec)
3. **Fallback**: `./code_speak.json` in the current directory


#### ▎Defaults

```json
{
  "code_speak": {
    "binary": "claude",
    "delete_keywords": ["delete", "undo last"],
    "fast_delete": true,
    "push_to_talk_key": "right_shift",
    "recording_indicator": ";"
  },
  "realtime_stt": {
    "language": "auto",
    "model": "base",
    "post_speech_silence_duration": 1.0,
    "silero_use_onnx": true,
    "spinner": false,
    "use_main_model_for_realtime": true
  }
}
```
> [!IMPORTANT]
> The `recording_indicator` must be a type-able character (uses `pyautogui.typewrite`)


#### ▎Notable/Special

+ `delete_keywords`: If the configured delete keyword is the only word/phrased uttered in the current session it will delete previous input(s)
+ `fast_delete`: By default the if a `delete_keywords` is triggered it's handled via a list of `pyautogui.press` backspace's which is much, much, faster, but sometimes (os/env defendant) wrong/useless
+ `push_to_talk_key`: Uses [`pynput`](https://pynput.readthedocs.io/en/latest/) `key.char` representation or for non-printable key-codes `vk_{key.vk}`

#### ▎RealtimeSTT

All config options can be found in [./RealtimeSTT.md](RealtimeSTT.md) or by visiting [RealtimeSTT](https://github.com/KoljaB/RealtimeSTT).

- `model` (most models also have an `en` variant such as `tiny.en`)
    - `tiny`: Fastest, lowest accuracy (cpu)
    - `base`: Balance (gpu/high-end-cpu)
    - `small`: Better accuracy (gpu)
    - `large`: Best accuracy (gpu)
    - Local path or huggingface path to CTranslate2 STT model
- `language`: Probs should set this unless your multilingual-ing
- `download_root`: Path were the Whisper models is downloaded to or located
- `spinner`: Highly recommend you keep it `false`, it just causes problems


## Troubleshooting

Create a simple test file (`./rec.py`), run it (`uv run ./rec.py`). If this works, then file/pull an issue since in all likelihood you've found a bug in the code. If this doens't work, unfortunately, you'll have to work backwards. definitely check out [github.com/KoljaB/RealtimeSTT/issues](https://github.com/KoljaB/RealtimeSTT/issues) - if you're lucky you'll find a fix/solution within previous/closed issues

```py
# ./rec.py
from RealtimeSTT import AudioToTextRecorder

def process_text(text):
    print(text)

if __name__ == '__main__':
    print("Wait until it says 'speak now'")
    recorder = AudioToTextRecorder()

    while True:
        recorder.text(process_text)
```


## Development

#### ▎Structure

```
code_speak/
├── src/code_speak/            # Main source code
│   ├── __init__.py            # Package exports
│   ├── cli.py                 # Command-line interface
│   ├── config.py              # Configuration management
│   ├── core.py                # Core voice input functionality
│   └── recorder.py            # Audio recording abstractions
├── main.py                    # Entry point
├── code_speak                 # Shell run helper
├── code_speak.json            # Fallback config
├── pyproject.toml             # Project configuration
└── README.md                  # This file
```

#### ▎Format/Lint

```bash
# Format and lint code
uv run ruff format .
uv run ruff check . --fix
```


## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`uv run pytest && uv run ruff check .`)
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [pyautogui](https://pyautogui.readthedocs.io/en/latest/index.html) for the keyboard input interaction
- [RealtimeSTT](https://github.com/KoljaB/RealtimeSTT) for the excellent speech-to-text engine
- [OpenAI Whisper](https://github.com/openai/whisper) for the underlying transcription models

