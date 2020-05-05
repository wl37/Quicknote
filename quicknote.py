#!/usr/bin/env python

import os
import time
import pandas.io.clipboard as clipboard
import argparse

""" quicknote.py
take quick note from system copy clipboard. 
Usage: save clipborad copied text to .md file save on local disk.  
"""

# quicknote.md file location
home = os.path.expanduser("~")
note_file_location = os.path.join(home, "quicknote.md")

def append_text_to_file(file_location, text, comments, curr_time):
    """ open file and ADD text to it. """
    if not os.path.isfile(note_file_location): # create file if not found
      with open(file_location, 'w') as md:
        pass
      print("note file not found. New file created.\n")
    
    if text:
        # write each line of text with formatting of the note
        with open(file_location, 'a') as md:
            md.writelines("## {}\n".format(comments))
            md.writelines("```\n")
            for t in text.split(os.linesep):
                md.writelines(t+"\n")
            md.writelines("```\n")
            md.writelines("Note taken at " + curr_time + "\n\n")

        print("\n~~~Note recorded~~~\n")
    else:
        print("Clipboard is empty, nothing to record")


def main():
    """ process command-line arguments and save clipboard text to .md file """
    ct = time.asctime()  # current time
    parser = argparse.ArgumentParser(
        prog="Short comments for the notes you want to save")
    parser.add_argument("comments", type=str, nargs="?",
                        default="notes taken at {}".format(ct))
    args = parser.parse_args()
    comments = args.comments

    text = clipboard.paste()
    append_text_to_file(note_file_location, text, comments, ct)


if __name__ == "__main__":
    main()
