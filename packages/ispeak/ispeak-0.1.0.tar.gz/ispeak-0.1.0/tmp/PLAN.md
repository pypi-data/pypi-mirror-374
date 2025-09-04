# Refactoring Plan: claude_speak → code_speak

## Overview
Transform `claude_speak` into a generic `code_speak` framework that can work with various CLI AI code generation tools, not just Claude Code.

**IMPORTANT**: No Backward Compatibility required


## Current State Analysis

### Claude-specific Components Found:
- **Package name**: `claude_speak` → `code_speak`
- **Module paths**: `src/claude_speak/*` → `src/code_speak/*`
- **Configuration**: `ClaudeSpeakConfig` → `CodeSpeakConfig`
- **Environment variables**: `CLAUDE_SPEAK_CONFIG` → `CODE_SPEAK_CONFIG`
- **Config files**: `claude_speak.json` → `code_speak.json`
- **Hard-coded executable**: `claude` command in `cli.py:186`
- **UI text**: "Claude Speak" → "ispeak"

## Refactoring Strategy

### 1. Name Changes (claude_speak → code_speak)

#### Files to Rename:
```
src/claude_speak/           → src/code_speak/
src/claude_speak/__init__.py → src/code_speak/__init__.py
src/claude_speak/cli.py     → src/code_speak/cli.py
src/claude_speak/config.py  → src/code_speak/config.py
src/claude_speak/core.py    → src/code_speak/core.py
src/claude_speak/recorder.py → src/code_speak/recorder.py
```

#### pyproject.toml Changes:
```toml
# Before
name = "claude-speak"
description = "Speech-to-text for claude code"
[project.scripts]
claude-speak = "claude_speak.cli:main"
[tool.hatch.build.targets.wheel]
packages = ["src/claude_speak"]

# After
name = "code-speak"
description = "Speech-to-text for AI code generation tools"
[project.scripts]
code-speak = "code_speak.cli:main"
[tool.hatch.build.targets.wheel]
packages = ["src/code_speak"]
```

#### main.py Changes:
```python
# Before
from claude_speak.cli import main

# After
from code_speak.cli import main
```

### 2. Configuration Changes

#### Class Renames:
- `ClaudeSpeakConfig` → `CodeSpeakConfig`
- `AppConfig.claude_speak` → `AppConfig.code_speak`

#### Environment Variable:
- `CLAUDE_SPEAK_CONFIG` → `CODE_SPEAK_CONFIG`

#### Config File Paths:
- `~/.claude/claude_speak.json` → `~/.config/code_speak.json`
- `./claude_speak.json` → `./code_speak.json`

#### New Configuration Fields:
Add `bin` parameter to `CodeSpeakConfig`:
```python
@dataclass
class CodeSpeakConfig:
    bin: str = "claude"  # Default executable
    push_to_talk_key: str = "right_shift"
    recording_indicator: str = ";"
    delete_keywords: list[str] = None
    fast_delete: bool = True
    strip: bool = True
```

### 3. CLI Argument Changes

#### New Arguments:
Add `-b/--bin` option to specify executable:
```python
parser.add_argument("-b", "--bin", help="AI code generation executable (default from config)")
```

#### Command Execution Logic:
Update `run_with_claude()` → `run_with_ai_tool()`:
```python
def run_with_ai_tool(ai_args: list, bin_override: str | None = None) -> int:
    # Use bin_override, then config.code_speak.bin, then fallback
    executable = bin_override or config.code_speak.bin
    cmd = [executable, *ai_args]
    # ... rest of logic
```

### 4. User-Facing Text Updates

#### UI Messages:
```python
# Before
console.print("\n[bold][red]◉[/red] [green]Claude Speak Configuration[/green][/bold]")
console.print("\n[bold][red]◉[/red] [green]Claude Speak Active[/green][/bold]")
console.print("\n[bold][red]◉[/red] [yellow]Claude Speak Init[/yellow][/bold]\n")

# After
console.print("\n[bold][red]◉[/red] [green]ispeak Configuration[/green][/bold]")
console.print("\n[bold][red]◉[/red] [green]ispeak Active[/green][/bold]")
console.print("\n[bold][red]◉[/red] [yellow]ispeak Init[/yellow][/bold]\n")
```

#### Error Messages:
```python
# Before
"Error: 'claude' command not found. Make sure Claude Code is installed."

# After
f"Error: '{executable}' command not found. Make sure it is installed and in PATH."
```

#### Help Text:
```python
# Before
description="Claude Code with Voice Input"

# After
description="AI Code Generation Tools with Voice Input"
```

## Implementation Order

### Phase 1: Core Renaming
1. Rename directory structure
2. Update import statements
3. Update class names and references
4. Update pyproject.toml
5. Update main.py

### Phase 2: Configuration Enhancement
1. Add `bin` parameter to config dataclass
2. Update environment variable handling
3. Update config file paths
4. Add CLI argument parsing for `-b/--bin`

### Phase 3: Runtime Logic Updates
1. Update command execution logic
2. Update error messages with dynamic executable names
3. Update UI text to be generic

### Phase 4: Testing & Documentation
1. Test with different executables (claude, cursor, etc.)
2. Update README.md
3. Update configuration examples



## Testing Scenarios

### Supported Executables:
- `claude` (Claude Code)
- `cursor` (Cursor)
- `aider` (Aider)
- `continue` (Continue)
- Custom executables

### Test Cases:
1. Default behavior (bin="claude")
2. Config-specified executable
3. CLI override with `-b/--bin`
4. Error handling for missing executables
5. Configuration migration
6. Voice input with different tools

## Benefits

### Extensibility:
- Support for multiple AI coding assistants
- Easy addition of tool-specific configurations
- Flexible executable specification

### User Experience:
- Single tool for voice input across different AI assistants
- Consistent interface regardless of underlying tool
- Easy switching between tools

### Maintenance:
- Generic codebase easier to maintain
- Reduced coupling to specific tools
- Future-proof architecture