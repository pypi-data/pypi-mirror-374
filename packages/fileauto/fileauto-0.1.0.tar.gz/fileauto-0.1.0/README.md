# FileAuto

**FileAuto** is a Python tool to help you organize your files automatically into category folders based on their file extensions.

## Features

- Automatically sorts files into folders like Images, Documents, Videos, Music, Archives, and Scripts.
- Creates category folders if they do not exist.
- Prevents overwriting files by skipping moves if the destination file already exists.
- Copies the file path to your clipboard for quick access.
- Colorful terminal output and ASCII art welcome message.

## Supported Categories

| Category   | Extensions                              |
|------------|-----------------------------------------|
| Images     | `.jpg`, `.jpeg`, `.png`, `.gif`         |
| Documents  | `.pdf`, `.doc`, `.docx`, `.txt`         |
| Videos     | `.mp4`, `.mkv`, `.avi`, `.mov`          |
| Music      | `.mp3`, `.wav`                          |
| Archives   | `.zip`, `.tar`, `.gz`                   |
| Scripts    | `.sh`, `.bat`, `.py`                    |
| Others     | Any other file types                    |

## Usage

1. **Install dependencies:**
   ```
   pip install pyfiglet colorama pyperclip
   ```

2. **Edit the file path in `fileauto.py`:**
   ```python
   fileauto = FileAuto("C:/Users/DELL/Downloads/yourfile.jpg")
   ```

3. **Run the script:**
   ```
   python fileauto.py
   ```

## How It Works

- The script checks the file extension and moves the file into the corresponding category folder inside its current directory.
- If the file already exists in the destination folder, it skips the move and prints a message.
- The file path is copied to your clipboard for convenience.

## About

See `fileauto_about.txt` for a brief description of the tool and its categories.