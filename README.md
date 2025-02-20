# Building the Executable

## For Developers
1. Install Poetry and dependencies:
```bash
curl -sSL https://install.python-poetry.org | python3 -
poetry install
```

2. Build the executable:
```bash
# Windows
poetry run pyinstaller likert.spec --clean

# macOS/Linux
poetry run pyinstaller likert.spec --clean
```

The executable will be created in the `dist` directory.

## For Users
Simply download the appropriate executable for your platform:
- Windows: `likert_analyzer.exe`
- macOS: `likert_analyzer`
- Linux: `likert_analyzer`

Double-click the executable to run, or from command line:
```bash
# Windows
likert_analyzer.exe

# macOS/Linux
./likert_analyzer
```

No Python installation required! The web interface will automatically open in your default browser.