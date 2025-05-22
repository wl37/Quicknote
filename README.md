# QuickNote - Modern Clipboard Note-Taking

## Overview

QuickNote is a Python application designed to help you quickly capture and organize information from your clipboard. It saves your notes in Markdown format, making them easy to read, edit, and integrate with other tools. Notes are automatically organized into monthly files (e.g., `2023-10-quicknotes.md`) in a configurable directory.

The application features a user-friendly GUI for browsing notes, managing settings, and saving content. It intelligently attempts to convert HTML content copied from web pages into clean Markdown. For users who prefer the command line or want to script it, QuickNote also supports piped input and offers a "Quick Import" button for instant clipboard saving with a default comment.

## Key Features

*   **Graphical User Interface (GUI):** Intuitive interface to preview clipboard content, add comments, browse saved note files, and configure settings.
*   **HTML to Markdown Conversion:** Automatically converts rich text/HTML content from the clipboard (e.g., copied from a web page) into Markdown format for clean storage. Plain text is also supported.
*   **Monthly Note Organization:** Notes are saved into files named `YYYY-MM-quicknotes.md` (e.g., `2023-10-quicknotes.md`), making it easy to find notes by month.
*   **Configurable Save Directory:** Users can choose the directory where their monthly note files are stored via the in-app settings. Defaults to the user's home directory.
*   **Clipboard Preview & Refresh:** View the current clipboard content (plain text preview) directly in the app and refresh it on demand.
*   **File Browser:** Browse existing Markdown note files in the configured save directory.
*   **Flexible Saving Options:**
    *   **Save Note:** Save clipboard content with a custom comment via the GUI.
    *   **Save Clipboard Now:** Instantly save the current clipboard content with a timestamped default comment.
*   **Command-Line (Piped) Input:** Directly pipe text to the script for non-GUI saving (e.g., `echo "My note" | python quicknote.py`).

## Requirements

*   **Python:** Python 3.7+
*   **Dependencies:**
    *   `pyperclip` (for cross-platform clipboard access)
    *   `markdownify` (for HTML to Markdown conversion)
*   **Tkinter:** For the GUI.
    *   Tkinter is often included with standard Python installations.
    *   On some Linux systems, it might need to be installed separately. For Debian/Ubuntu based systems:
        ```bash
        sudo apt-get update
        sudo apt-get install python3-tk
        ```

## Installation

1.  **Get the Code:**
    Clone or download the repository containing `quicknote.py` to your local machine.
    ```bash
    # Example if using Git
    # git clone <repository_url>
    # cd <repository_directory>
    ```

2.  **Install Dependencies:**
    Open a terminal or command prompt and install the required Python libraries using pip:
    ```bash
    pip install pyperclip markdownify
    ```

## How to Run

Navigate to the directory where `quicknote.py` is located and run:

```bash
python quicknote.py
```
Or, if you've made it executable and it's in your PATH:
```bash
./quicknote.py
```

## Using the Application

### GUI Mode

When you run `python quicknote.py` without any piped input, the main GUI window will appear.

*   **Main Window Components:**
    *   **Clipboard Content (Plain Text Preview):** A text area showing the current plain text content of your clipboard.
    *   **Refresh Clipboard Button:** Updates the preview area with the latest clipboard content.
    *   **Comments Field:** Enter any comments or context for the note you're about to save. It defaults to "notes taken at \[timestamp]".
    *   **Save Note Button:** Saves the current clipboard content (processing HTML to Markdown if applicable) along with your custom comment into the relevant monthly note file.
    *   **Save Clipboard Now Button:** Immediately saves the current clipboard content with a default timestamped comment (e.g., "Quick import - \[timestamp]"). Useful for very fast captures.
    *   **File Browser (Right Panel):** Displays a list of `.md` files found in the currently configured save directory.
    *   **Refresh Files Button:** Manually refreshes the list of files in the file browser.
    *   **Settings Button:** Opens the settings window.

*   **Settings Window:**
    *   Accessed via the "Settings" button.
    *   **Save Directory:** Allows you to view and change the directory where your monthly note files (`YYYY-MM-quicknotes.md`) are stored.
        *   Use the "Browse..." button to select a new directory.
        *   Click "Apply Settings" to save your changes. The file browser will update to reflect the new directory.

*   **How Notes Are Saved:**
    *   Notes are appended to a file named according to the current year and month (e.g., `2023-10-quicknotes.md`) within the configured save directory.
    *   If HTML content is detected on the clipboard, QuickNote attempts to convert it to Markdown. If no HTML is found, or conversion fails, plain text is used.
    *   Plain text content saved via the GUI (or Markdown from HTML) is typically stored directly, while plain text saved via the command line pipe is wrapped in Markdown code fences.

### Command-Line Mode (Piping Input)

You can directly send text to QuickNote without opening the GUI. This is useful for scripting or integrating with other command-line tools.

*   **Usage:**
    ```bash
    echo "This is my note from the command line" | python quicknote.py
    ```
    Or for multi-line input:
    ```bash
    printf "First line\nSecond line" | python quicknote.py
    ```
*   **Behavior:**
    *   The piped text will be saved as plain text (wrapped in Markdown code fences) to the appropriate monthly file in the configured save directory.
    *   A default comment including the timestamp (e.g., "Note from command line - YYYY-MM-DD HH:MM:SS") will be used.
    *   A confirmation message will be printed to the console.
    *   The GUI will not launch when input is piped.

## Advanced: Manual OS Integration (Simulating "Right-Click to Save")

While QuickNote provides a GUI and can accept piped input, you might want to integrate it more closely with your operating system for even faster note-taking from selected text. Here are some general approaches for different OSes. These require manual setup by the user.

**macOS:**

*   **Automator Service:**
    1.  Open Automator and create a new "Quick Action" (or "Service" in older macOS versions).
    2.  Set "Workflow receives current" to "text" in "any application".
    3.  Add a "Run Shell Script" action.
    4.  Set "Pass input" to "to stdin".
    5.  Use a script like (ensure `quicknote.py` is executable and you provide the full path):
        ```bash
        # Replace /path/to/your/quicknote.py with the actual path
        /usr/bin/python3 /path/to/your/quicknote.py
        ```
    6.  Save the Service (e.g., "Send to QuickNote"). It will then be available in the Services menu when you right-click selected text.

**Windows:**

*   **AutoHotkey (Third-Party Tool):**
    *   AutoHotkey is a powerful scripting tool. You could create a script that copies selected text and then runs `quicknote.py` with the content (either via clipboard for the GUI's "Save Clipboard Now" or by modifying `quicknote.py` further if AutoHotkey can pipe to stdin easily).
    *   Example AutoHotkey script concept (Win+S hotkey):
        ```autohotkey
        #s:: ; Win+S hotkey example
        SendInput, ^c
        Sleep, 100 ; Give clipboard time to be set
        Run, python C:\path\to\your\quicknote.py ; QuickNote GUI will open, use "Save Clipboard Now"
        Return
        ```
*   **Batch Script + Context Menu (More Complex):**
    *   Creating a true context menu item that copies selected text and pipes it directly is complex without third-party tools.
    *   A simpler manual approach:
        1.  Create a batch script that simply runs `python C:\path\to\your\quicknote.py`.
        2.  Create a shortcut to this batch script.
        3.  Manually copy text (Ctrl+C), then run the shortcut and use the "Save Clipboard Now" button in the QuickNote GUI.

**Linux:**

*   **Desktop Environment Keyboard Shortcuts + `xclip`/`xsel`:**
    *   Most Linux desktop environments (GNOME, KDE, XFCE, etc.) allow you to create custom keyboard shortcuts that run commands.
    *   Combine this with tools like `xclip` (for X11 selection buffer) or `xsel`.
    *   Example command for a shortcut (pipes current selection to `quicknote.py`):
        ```bash
        # For X primary selection (usually text selected with mouse)
        xsel -p | /usr/bin/python3 /path/to/your/quicknote.py
        # Or for clipboard selection (usually after Ctrl+C)
        # xclip -o -selection clipboard | /usr/bin/python3 /path/to/your/quicknote.py
        ```
        This pipes the selected text directly to `quicknote.py`'s stdin handling.
*   **Right-Click Menu (Desktop Environment Dependent):**
    *   Adding items to the right-click context menu depends on the desktop environment and file manager (e.g., Nautilus Scripts for GNOME, Dolphin Service Menus for KDE).
    *   These usually involve placing a small script in a specific directory. The script would typically use `xclip -o` or `xsel` to get the selection and then pipe it to `quicknote.py`.

**General Tip for OS Integration:**
Ensure `quicknote.py` is executable (`chmod +x quicknote.py`) if you're calling it directly in shell scripts, and use the appropriate Python interpreter (`python3` or the full path to it if necessary).

## License

This project is licensed under the MIT License. (The original `quicknote.py` was simple, this version builds upon it. Assuming MIT is appropriate.)
```
