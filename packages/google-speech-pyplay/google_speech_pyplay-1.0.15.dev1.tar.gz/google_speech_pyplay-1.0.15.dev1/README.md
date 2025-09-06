# About

A lightweight fork of the `google_speech` library, that replaces `sox` with `pygame` and removes sound effects for a lightweight and straightforward implementation.

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->

**Table of Contents**

> - [About](#about)
>   - [Installation](#installation)
>   - [Usage](#usage)
>     - [Command-Line Interface (CLI)](#command-line-interface-cli)
>       - [Example: Save to File](#example-save-to-file)
>     - [Python Code Examples](#python-code-examples)
>       - [Example 1: Play Text-to-Speech](#example-1-play-text-to-speech)
>       - [Example 2: Save Speech to a File](#example-2-save-speech-to-a-file)
>   - [Setting Up Development Environment](#setting-up-development-environment)
>     - [Prerequisites](#prerequisites)
>     - [Steps to Set Up the Environment](#steps-to-set-up-the-environment)
>     - [Building the Project](#building-the-project)
>   - [Common Commands](#common-commands)
>   - [Notes](#notes)

<!-- markdown-toc end -->

## Installation

```bash
pip install google_speech_pyplay
```

## Usage

The library provides both a **Command-Line Interface (CLI)** and an **API** for programmatic use.

### Command-Line Interface (CLI)

You can use the `google_speech_pyplay` command directly from the terminal:

```bash
python -m google_speech_pyplay "Hello, world!" -l en
```

Options:

- `-l`, `--lang`: Specify the language (e.g., `en` for English, `es` for Spanish).
- `-o`, `--output`: Save the speech output to an MP3 file instead of playing it.

#### Example: Save to File

Save the text-to-speech output to `output.mp3`:

```bash
python -m google_speech_pyplay "Hello, world!" -l en -o output.mp3
```

---

### Python Code Examples

Here are some examples of how to use the library in Python scripts.

#### Example 1: Play Text-to-Speech

```python
from google_speech_pyplay import Speech

# Specify the text and language
text = "Hello, world!"
language = "en"

# Create a Speech object and play the text
speech = Speech(text, language)
speech.play()
```

#### Example 2: Save Speech to a File

```python
from google_speech_pyplay import Speech

# Specify the text and language
text = "Hola, mundo!"
language = "es"

# Create a Speech object and save the speech to an MP3 file
speech = Speech(text, language)
speech.save("output.mp3")
```

## Setting Up Development Environment

To set up a fresh development environment for the `google_speech_pyplay` project, follow these steps:

### Prerequisites

1. Ensure you have Python 3.10 or newer installed.
2. Install `pip` (comes bundled with Python) and upgrade it to the latest version:
   ```bash
   python3 -m pip install --upgrade pip
   ```

### Steps to Set Up the Environment

1. Clone the repository:

   ```bash
   git clone https://github.com/KarimAziev/google_speech_pyplay.git
   cd google_speech_pyplay
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # For Linux/Mac
   # or
   .venv\Scripts\activate     # On Windows
   ```

3. Upgrade core tools inside the virtual environment:

   ```bash
   pip install --upgrade pip setuptools wheel
   ```

4. Install the project in editable (development) mode with all dependencies:
   ```bash
   pip install -e ".[dev]"  # Includes dev dependencies like black, pre-commit, isort
   ```

---

### Building the Project

To build the project for distribution, e.g., creating `.tar.gz` and `.whl` files:

1. Install the build tool:

   ```bash
   pip install build
   ```

2. Build the distribution:
   ```bash
   python -m build
   ```

This will generate a `dist/` directory containing the following artifacts:

- Source distribution (`google_speech_pyplay-x.y.z.tar.gz`)
- Wheel file (`google_speech_pyplay-x.y.z-py3-none-any.whl`)

You can install these locally for testing or upload them to PyPI for publishing.

---

## Common Commands

- **Clean build artifacts:**
  ```bash
  rm -rf build dist *.egg-info
  ```
- **Deactivate virtual environment:**
  ```bash
  deactivate
  ```

---

## Notes

- This project uses `setuptools_scm` to handle versioning, based on the Git tags of the repository. Ensure you use proper semver tags like `v1.0.0` to manage versions correctly.
- Dev dependencies (like `black`, `isort`) are automatically installed when running `pip install -e ".[dev]"`.
