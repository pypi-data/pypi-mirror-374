# `code_speak`

A hotkey-driven low-latency speech-to-text library that provides seamless voice input integration with any text or CLI Agentic/AI tool such as: [`claude`](https://claude.ai/code), [`vim`](https://www.vim.org/), [`aider`](https://github.com/paul-gauthier/aider), [`firefox`](https://www.firefox.com), [`codex`](https://github.com/openai/codex), really anything and everything.

- **Agnostic** keyboard interaction-based implementation via [pyautogui](https://pyautogui.readthedocs.io/en/latest/index.html) that works with any and all tools
- **Local & Fast Transcription** via [RealtimeSTT](https://github.com/KoljaB/RealtimeSTT) and [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- **Configurable** multiple Speech-To-Text Models, push-to-record hotkey, recording indicator, plus other goodies
- **Easy Installation** that works in Linux, macOS, and Windows with or without gpu support


## Quick Start

#### ▎Workflow

1. **Start**: Run `code_speak` to launch voice integration (set `binary` via `-b` or a default in the config)
2. **Press**: The configured push-to-talk key (default: `shift_r`)
3. **Speak**: A configurable recording indicator (`;`) appears while recording
    - Or press `escape` to cancel the current recording without transcription
4. **Press**: The configured push-to-talk key again to stop recording
5. **Done**:  Your transcribed speech is automatically typed into Claude Code
    - Whatever application has the target (keyboard) focus will be the output target. Upside, you only need a single instace up and running an you can use it with any/all applications running. Downside, you can't trabscribe the output while typing.


#### ▎Install

```bash
git clone https://github.com/fetchTe/code_speak
cd code_speak

# local install (with cuda)
uv sync
uv sync --extra cpu   # local install (with cpu / no-cuda)
uv sync --extra cu118 # local install (cuda v11.8)
uv sync --extra cu128 # local install (cuda v12.8)

# global install (with cuda) 
uv tool install .
uv tool install ".[cpu]"   # global install (with cpu / no-cuda)
uv sync --extra ".[cu118]" # global install (cuda v11.8)
uv sync --extra ".[cu128]" # global install (cuda v12.8)


# setup & create a virtual environment
uv venv -p 3.12 && source .venv/bin/activate

# manual (with cuda)
uv pip install RealtimeSTT pyautogui pynput rich

# cpu-only (no cuda)
uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
uv pip install RealtimeSTT pyautogui pynput rich
```
> Assumes [`claude`](https://claude.ai/code), [`aider`](https://github.com/paul-gauthier/aider), [`codex`](https://github.com/openai/codex), or similar is installed and available in the `PATH`

#### ▎Setup & Usage

```bash
# via helper script
./claude_speak --setup      # Initial configuration helper
./claude_speak --config     # Show configuration
./claude_speak --test       # Test voice functionality

./claude_speak              # Start voice-enabled using default config binary
./claude_speak --b aider    # Start voice-enabled with aider

# via uv
uv run ./main.py
uv run ./main.py --setup
uv run ./main.py --b aider
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
    "push_to_talk_key": "shift_r",
    "push_to_talk_key_delay": 0.2,
    "escape_key": "esc",
    "recording_indicator": ";",
    "delete_keywords": ["delete", "undo"],
    "fast_delete": true,
    "strip_whitespace": true,
    "pyautogui_interval": 0.0
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

Hotkey/code handling is done via [pynput](https://github.com/moses-palmer/pynput) and can be a simple character such as `a`, a key desciptor like `alt_l` (view full class  [here](https://github.com/moses-palmer/pynput/blob/74c5220a61fecf9eec0734abdbca23389001ea6b/lib/pynput/keyboard/_base.py#L162)), or even a key-combos such as `<ctrl>+<alt>+h`.


- `binary` (str, default: "claude"): Default executable for AI code generation
- `push_to_talk_key` (str, default: "right_shift"): Key to initialize recording session
- `push_to_talk_key_delay` (float|int, default: 0.2): Execution delay applied after push-to-talk key (via time.sleep) - helps prevent mistypes
- `escape_key` (str|Key|KeyCode|null, default: Key.esc): Key to "escape" current recording session, ends without outputting transcription
- `recording_indicator` (str, default: ";"): Character/word output when recording starts
- `delete_keywords` (list[str]|bool|null, default: True): List of words/phrases that, when detected, will delete previous output
- `fast_delete` (bool, default: True): Use a list of backspaces with pyautogui.press - faster, but not as accurate
- `strip_whitespace` (bool, default: True): Removes extra whitespace (an extra space is always added to end)
- `pyautogui_interval` (float|int, default: 0.0): PyAutoGUI interval between each press (in seconds) - if experiencing typing/output issues like partial outputs, increase this value

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

#### ▎Type/Lint/Format

```bash
# Type check
pyright

# Lint code
ruff check .
# Lint fix
ruff check . --fix

# Format
ruff format .
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

