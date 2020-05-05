# Quicknote
A simple python script to save clipboard text to a markdown file.

Text copied to the clipboard could be useful for later references. This simple script can be used in a linux system to save the text to a markdown file (or any text file you defined). It can run in Windows with a little tweak.

Make sure Python is working in your system, and do the following: 
1. Execute the following command in the Terminal to make the file executable: 
```bash
chmod -x quicknote.py
```
2. (Optional) Rename it to remove the ".py" extension to make calling simple.
```bash
mv quicknote.py quicknote
```
3. Copy it to a directory in the $PATH env, such as "~/.local/bin"
```bash
sudo cp quicknote ~/.local/bin
```

Any text copied to the system clipboard can be saved by running command *quicknote* in the terminal. You can add an informative message (optional).
```bash
quicknote "A new piece of note saved for later reading"
```
By default, the note will be saved to "~/quicknote.md" with a message as you typed, and a timestamp at the end of the note. Future savings will append to the end of the file. 
