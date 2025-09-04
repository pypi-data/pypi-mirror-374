# `code-speak`

A hotkey-driven, low-latency speech-to-text library that provides seamless voice input integration with any text-based or CLI AI/Agentic tool. Works with [`Claude Code`](https://claude.ai/code), [`vim`](https://www.vim.org/), [`aider`](https://github.com/paul-gauthier/aider), [`firefox`](https://www.firefox.com), and virtually any application that accepts text input.

- **Application Agnostic** - Keyboard interaction via [pyautogui](https://pyautogui.readthedocs.io/en/latest/index.html) that works with any text input/field
- **Local & Fast Transcription** - Powered by [RealtimeSTT](https://github.com/KoljaB/RealtimeSTT) and [faster-whisper](https://github.com/SYSTRAN/faster-whisper) for offline, low-latency processing
- **Configurable** - Customizable hotkeys, speech models, recording indicators, delete keywords, and audio/recording settings
- **Cross-Platform** - Works on Linux, macOS, and Windows (CPU and/or GPU)

## Quick Start

#### ▎Workflow

1. **Start**: Run `code-speak` to launch voice integration (optionally set target `binary` via `-b` or configure a default)
2. **Press**: The configured push-to-talk key (default: `end`)
3. **Speak**: A configurable recording indicator (`;`) appears in the focused application while recording
   - Press `escape` to cancel the current recording without transcription
4. **Release**: Press the push-to-talk key again to stop recording and process transcription
5. **Done**: Your transcribed speech is automatically typed into the focused application

> **Note**: The transcribed text is sent to whatever application currently has keyboard focus. This allows you to use a single code-speak instance with multiple applications, but you cannot transcribe while the target application is actively receiving other keyboard input.


#### ▎Install

```bash
git clone https://github.com/fetchTe/code_speak
cd code_speak

# Local development install
uv sync                    # with CUDA (default)
uv sync --extra cpu        # CPU-only (no CUDA)
uv sync --extra cu118      # CUDA v11.8
uv sync --extra cu128      # CUDA v12.8

# Global install
uv tool install .          # with CUDA (default)
uv tool install ".[cpu]"   # CPU-only (no CUDA)  
uv tool install ".[cu118]" # CUDA v11.8
uv tool install ".[cu128]" # CUDA v12.8

# Manual setup with virtual environment
uv venv -p 3.12 && source .venv/bin/activate

# Manual dependencies (with CUDA)
uv pip install RealtimeSTT pyautogui pynput rich

# Manual dependencies (CPU-only)
uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
uv pip install RealtimeSTT pyautogui pynput rich
```
> **Requirements**: Ensure your target AI tool ([`Claude Code`](https://claude.ai/code), [`aider`](https://github.com/paul-gauthier/aider), etc.) is installed and available in your `PATH`. Python 3.12+ is required.

#### ▎Setup & Usage

```bash
# Using the installed command
code-speak --setup          # Interactive configuration wizard
code-speak --config         # Display current configuration
code-speak --test          # Test voice input functionality

code-speak                 # Start with default AI tool from config
code-speak -b aider        # Start with specific AI tool (aider)
code-speak -b claude       # Start with Claude Code

# Using uv (for development)
uv run code-speak --setup
uv run code-speak -b aider

# Using the helper script (legacy)
./code_speak --setup
./code_speak -b aider
```


## Configuration

1. **Environment Variable**: Set `CODE_SPEAK_CONFIG` environment variable to specify a custom config file path
2. **Platform-Specific Default**: `<config_dir>/code_speak/code_speak.json`
   - **macOS**: `~/Library/Preferences/code_speak/code_speak.json`
   - **Windows**: `%APPDATA%\code_speak\code_speak.json` (or `~/AppData/Roaming/code_speak/code_speak.json`)
   - **Linux**: `$XDG_CONFIG_HOME/code_speak/code_speak.json` (or `~/.config/code_speak/code_speak.json`)
3. **Local Fallback**: `./code_speak.json` in the current working directory

```json
{
  "code_speak": {
    "binary": "claude",
    "push_to_talk_key": "end",
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


#### ▎ `code_speak` Configuration/Options

- `binary` (string, default: "claude"): Default executable to launch with voice input
- `delete_keywords` (list/bool, default: ["delete", "undo"]): Words that trigger deletion of previous input via backspace operations (must be exact word/phrase)
- `escape_key` (string, default: "esc"): Key to cancel current recording without transcription
- `fast_delete` (bool, default: true): Use batch backspace operations for faster deletion
- `push_to_talk_key_delay` (float, default: 0.2): Brief delay after hotkey press to prevent input conflicts
- `push_to_talk_key` (string, default: "end"): Hotkey to start/stop recording sessions
- `pyautogui_interval` (float, default: 0.0): Interval between keystrokes - increase if experiencing partial output
- `recording_indicator` (string, default: ";"): Visual indicator typed when recording starts
    - **IMPORATNT** must be a type-able character (uses `pyautogui.typewrite`)
- `strip_whitespace` (bool, default: true): Remove extra whitespace from transcribed text

> Hotkeys are handled via [pynput](https://github.com/moses-palmer/pynput) and support
> - Simple characters: `a`, `b`, `c`, `1`
> - Special keys: `end`, `alt_l`, `ctrl_l` - (see [pynput Key class](https://github.com/moses-palmer/pynput/blob/master/lib/pynput/keyboard/_base.py#L162))
> - Key combinations: `<ctrl>+<alt>+h`, `<shift>+<space>`





#### ▎`realtime_stt` Configuration/Options

All config options can be found in [./RealtimeSTT.md](RealtimeSTT.md) or by visiting [RealtimeSTT](https://github.com/KoljaB/RealtimeSTT).

**Model Selection** (each model has an English-only `.en` variant for better performance):
- `tiny`: Fastest processing, lower accuracy (~39 MB, CPU)
- `base`: Balanced speed/accuracy (~74 MB, GPU/CPU)
- `small`: Better accuracy (~244 MB, GPU)
- `medium`: High accuracy (~769 MB, GPU)
- `large-v1`/`large-v2`: Best accuracy (~1550 MB, GPU+)

**Key Settings**:
- `language`: Language code (`en`, `es`, `fr`, `de`, etc.) or `"auto"` for automatic detection
- `model`: Model size or path to custom CTranslate2 model
- `post_speech_silence_duration`: Duration of silence before processing transcription (default: 1.0s)
- `download_root`: Directory for storing downloaded Whisper models
- `device`: Force `"cpu"` or `"cuda"` (auto-detected by default)
- `spinner`: Set to `false` to avoid terminal display issues


## Troubleshooting


### Common Issues

+ **Partial transcriptions**: Increase `pyautogui_interval` in config (try 0.1-0.5)
+ **Recording indicator not typed/deleted**: Increasing the `push_to_talk_key_delay` (try 0.2-1.0)
+ **CUDA/GPU issues**: Use CPU-only installation or check CUDA compatibility
+ **Permission errors**: Ensure accessibility permissions on macOS/Windows

### Testing Audio Input

Create a minimal test to isolate audio/transcription issues:

```python
# test_audio.py
from RealtimeSTT import AudioToTextRecorder

def process_text(text):
    print(f"Transcribed: {text}")

if __name__ == '__main__':
    print("Testing RealtimeSTT - speak after you see 'Listening...'")
    try:
        recorder = AudioToTextRecorder()
        while True:
            recorder.text(process_text)
    except KeyboardInterrupt:
        print("\nTest completed.")
    except Exception as e:
        print(f"Error: {e}")
```

Run the test with: `uv run test_audio.py`



## Platform Limitations
> From the `pynput` docs: [here](https://pynput.readthedocs.io/en/latest/limitations.html)

#### ▎Linux Limitations

On *Linux*, *pynput* uses *X* or *uinput*. When running under *X*, the following must be true:
- An *X server* must be running.
- The environment variable `$DISPLAY` must be set.

When running under *uinput*, the following must be true:
- You must run your script as root, to that is has the required
  permissions for *uinput*.

The latter requirement for *X* means that running *pynput* over *SSH* generally will not work. To work around that, make sure to set `$DISPLAY`:

``` bash
$ DISPLAY=:0 python -c 'import pynput'
```

Please note that the value `DISPLAY=:0` is just an example. To find the
actual value, please launch a terminal application from your desktop
environment and issue the command `echo $DISPLAY`.

When running under *Wayland*, the *X server* emulator `Xwayland` will
usually run, providing limited functionality. Notably, you will only
receive input events from applications running under this emulator.

#### ▎macOS Limitations

Recent versions of *macOS* restrict monitoring of the keyboard for
security reasons. For that reason, one of the following must be true:

- The process must run as root.
- Your application must be white listed under *Enable access for
  assistive devices*. Note that this might require that you package your
  application, since otherwise the entire *Python* installation must be
  white listed.
- On versions after *Mojave*, you may also need to whitelist your
  terminal application if running your script from a terminal.

Please note that this does not apply to monitoring of the mouse or
trackpad.

All listener classes have the additional attribute `IS_TRUSTED`, which
is `True` if no permissions are lacking.

#### ▎Windows Limitations

On *Windows*, virtual events sent by *other* processes may not be
received. This library takes precautions, however, to dispatch any
virtual events generated to all currently running listeners of the
current process.

Furthermore, sending key press events will properly propagate to the
rest of the system, but the operating system does not consider the
buttons to be truly *pressed*. This means that key press events will not
be continuously emitted as when holding down a physical key, and certain
key sequences, such as *shift* pressed while pressing arrow keys, do not
work as expected.


## Development

#### ▎Project Structure

```
code-speak/
├── src/code_speak/            # Main package source
│   ├── __init__.py            # Package initialization and exports
│   ├── cli.py                 # Command-line interface and interactive setup
│   ├── config.py              # Configuration management and validation
│   ├── core.py                # Core voice input and text processing logic  
│   └── recorder.py            # Audio recording abstraction layer
├── main.py                    # Development entry point
├── code_speak                 # Legacy shell helper script
├── code_speak.json            # Local fallback configuration
├── pyproject.toml             # Project metadata and dependencies
└── README.md                  # Documentation
```

#### ▎Architecture

- **CLI Layer** (`cli.py`): Argument parsing, setup wizard, and AI tool integration
- **Configuration** (`config.py`): Cross-platform config management with validation
- **Voice Input** (`core.py`): Hotkey handling, text processing, and delete functionality
- **Audio Recording** (`recorder.py`): RealtimeSTT integration with protocol-based design

#### ▎Development Commands

```bash
# Type checking
uv run pyright                 # Type check all source files

# Code linting and formatting  
uv run ruff check .            # Lint code
uv run ruff check . --fix      # Auto-fix linting issues
uv run ruff format .           # Format code

# Run in development mode
uv run code-speak --setup      # Test setup wizard
uv run code-speak --test       # Test voice input
```


## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Install development dependencies: `uv sync --group dev`
4. Make your changes following the existing code style
5. Run quality checks:
   ```bash
   uv run ruff check . --fix    # Fix linting issues
   uv run ruff format .         # Format code
   uv run pyright              # Type checking
   ```
6. Test your changes: `uv run code-speak --test`
7. Commit your changes: `git commit -m 'feat: add amazing feature'`
8. Push to your branch: `git push origin feature/amazing-feature`
9. Open a Pull Request with a clear description of your changes

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **[RealtimeSTT](https://github.com/KoljaB/RealtimeSTT)** by KoljaB - Excellent real-time speech-to-text engine that powers this project
- **[OpenAI Whisper](https://github.com/openai/whisper)** - State-of-the-art speech recognition models
- **[pyautogui](https://pyautogui.readthedocs.io/)** - Cross-platform keyboard automation
- **[pynput](https://pynput.readthedocs.io/)** - Global hotkey handling and input monitoring
- **[Rich](https://rich.readthedocs.io/)** - Beautiful terminal output and interactive prompts

