# Shellpomodoro

---

[![PyPI version](https://img.shields.io/pypi/v/shellpomodoro.svg)](https://pypi.org/project/shellpomodoro/) [![Python versions](https://img.shields.io/pypi/pyversions/shellpomodoro.svg)](https://pypi.org/project/shellpomodoro/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`shellpomodoro` = Shell + Pomodoro timer. Built for my own use; sharing in case it helps others too.

A cross-platform terminal-based Pomodoro timer CLI application that can be installed via pip and run anywhere. Built with Python's standard library only - no external dependencies required.

## Features

- 🍅 Classic Pomodoro technique with customizable work and break durations
- ⏱️ Real-time countdown display with MM:SS format
- 🔔 Terminal bell notifications at phase transitions
- ⌨️ Keypress-controlled phase transitions (no need to wait)
- 🎨 ASCII art congratulations upon session completion
- 🖥️ Cross-platform support (Windows, macOS, Linux)
- 📦 Zero external dependencies (Python stdlib only)
- 🚀 Fast installation via pip

## Installation

### From PyPI (Recommended)

```bash
pip install shellpomodoro
```

### Development Installation (from source)

```bash
git clone https://github.com/inspiringsource/shellpomodoro.git
cd shellpomodoro
python3 -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e .
```

Alternative: Using pipx (isolated install)

```bash
pipx install .
```

## Usage

### Basic Usage

Start a default Pomodoro session (25min work, 5min break, 4 iterations):

```bash
shellpomodoro
```

### Customization Options

```bash
# Custom work and break durations
shellpomodoro --work 30 --break 10

# Custom number of iterations
shellpomodoro --iterations 6

# Custom notification beeps
shellpomodoro --beeps 3

# Combine all options
shellpomodoro --work 45 --break 15 --iterations 3 --beeps 1
```

### Command Line Options

- `--work N`: Set work period duration in minutes (default: 25)
- `--break N`: Set break period duration in minutes (default: 5)
- `--iterations N`: Set number of Pomodoro cycles (default: 4)
- `--beeps N`: Set number of notification beeps (default: 2)
- `--help`: Show help message and exit

## How It Works

1. **Work Phase**: Focus on your task while the timer counts down
2. **Notification**: Terminal bell sounds when work phase ends
3. **Keypress Transition**: Press any key when ready for break
4. **Break Phase**: Take a break while the timer counts down
5. **Repeat**: Continue until all iterations are complete
6. **Completion**: Enjoy ASCII art congratulations!

### Session Control

- **Abort Session**: Press `Ctrl+C` at any time to abort the current session
- **Phase Transitions**: Press any key to advance from work to break or break to work
- **Real-time Display**: See countdown timer, current phase, and instructions

## Requirements

- Python 3.9 or higher
- No external dependencies required

## Cross-Platform Compatibility

Shellpomodoro works seamlessly across different operating systems:

- **Windows**: Uses `msvcrt` for keypress detection
- **Unix/Linux/macOS**: Uses `termios` and `tty` for terminal control
- **Terminal Bell**: Uses standard `\a` character (may require terminal configuration)

### Troubleshooting: No Beep in VS Code

If you don't hear the terminal bell when running in the VS Code integrated terminal, you may need to enable audio cues in your VS Code settings. Add the following to your `settings.json`:

```json
{
  "terminal.integrated.enableVisualBell": true,
  "accessibility.signals.terminalBell": {
    "sound": "on"
  },
  "audioCues.enabled": "on",
  "audioCues.terminalBell": "on"
}
```

This enables the audible bell and ensures `\a` is played as a sound when Shellpomodoro triggers notifications.

## Examples

### Quick 15-minute session

```bash
shellpomodoro --work 15 --break 5 --iterations 1
```

### Extended deep work session

```bash
shellpomodoro --work 50 --break 10 --iterations 3
```

### Silent mode (no beeps)

```bash
shellpomodoro --beeps 0
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.

## Development History

This project was initiated using Kiro, which helped establish the initial structure and core functionality of the Pomodoro timer (the original `design.md`, `requirements.md`, and `tasks.md` are included in the repo). Later, the codebase was optimized and refined using Grok code to improve performance, code quality, and maintainability.
