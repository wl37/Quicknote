#!/usr/bin/env python

import os
import time
import pyperclip # Replaced pandas.io.clipboard
import tkinter as tk
from tkinter import ttk # For themed widgets
from tkinter import messagebox, filedialog # For user feedback and directory dialog
import glob # For listing files
import sys # For stdin checking
from markdownify import markdownify as md # HTML to Markdown
# import argparse # No longer needed for command-line arguments
# from PIL import ImageGrab # For future image handling - INVESTIGATED

""" quicknote.py
take quick note from system copy clipboard. 
Usage: save clipborad copied text to .md file save on local disk.  
"""

# Global variable for the current save path
current_save_path = os.path.expanduser("~")
# home = os.path.expanduser("~") # Replaced by current_save_path for flexibility
# note_file_location = os.path.join(home, "quicknote.md") # This will be dynamic now

def save_note_to_file(save_dir, text_content, comments, curr_time_obj, is_markdown=False):
    """ Saves the note to a file named YYYY-MM-quicknotes.md in the specified directory.
        If is_markdown is True, the text_content is assumed to be Markdown.
    """
    if not text_content:
        print("Content is empty, nothing to record") # Console feedback
        messagebox.showwarning("Empty Note", "Content is empty. Nothing to save.")
        return False

    # filename = curr_time_obj.strftime("%Y-%m-quicknotes.md") # Incorrect for struct_time
    filename = time.strftime("%Y-%m-quicknotes.md", curr_time_obj) # Corrected
    full_path = os.path.join(save_dir, filename)

    try:
        # Create directory if it doesn't exist (though askdirectory usually returns existing ones)
        if not os.path.isdir(save_dir):
            os.makedirs(save_dir, exist_ok=True) # exist_ok=True handles race condition

        # Create file if not found - this check is implicitly handled by 'a' mode if file DNE
        # if not os.path.isfile(full_path):
        #   with open(full_path, 'w', encoding='utf-8') as md: # Ensure UTF-8 encoding
        #     pass # Create the file
        #   print(f"Note file {filename} not found. New file created in {save_dir}.\n")

        with open(full_path, 'a', encoding='utf-8') as file_obj: # Renamed md to file_obj
            file_obj.writelines(f"## {comments}\n")
            if is_markdown:
                # If it's already Markdown, write it directly (perhaps without code fences, depending on desired output)
                # For now, let's assume markdownify output is suitable for direct inclusion.
                # Or, if you want to always quote it:
                # file_obj.writelines("```markdown\n")
                # for t_line in text_content.splitlines():
                #     file_obj.writelines(t_line + "\n")
                # file_obj.writelines("```\n")
                file_obj.write(text_content + "\n") # Write markdown content as is
            else:
                # If it's plain text, wrap it in code fences
                file_obj.writelines("```\n")
                for t_line in text_content.splitlines():
                    file_obj.writelines(t_line + "\n")
                file_obj.writelines("```\n")
            # file_obj.writelines(f"Note taken at {time.strftime('%Y-%m-%d %H:%M:%S', curr_time_obj.timetuple())}\n\n") # .timetuple() is for datetime objects
            file_obj.writelines(f"Note taken at {time.strftime('%Y-%m-%d %H:%M:%S', curr_time_obj)}\n\n") # Corrected for struct_time
        
        print(f"\n~~~Note recorded to {full_path}~~~\n") # Console feedback
        return True
    except PermissionError:
        messagebox.showerror("Permission Error", f"Cannot write to {full_path}. Please check permissions or choose a different save directory.")
        return False
    except Exception as e:
        messagebox.showerror("Save Error", f"An error occurred while saving the note to {full_path}:\n{e}")
        return False


def main():
    """ Initialize and run the Tkinter GUI, or process piped input """
    global current_save_path

    # Check for piped input (stdin)
    if not sys.stdin.isatty():
        piped_text = sys.stdin.read().strip()
        if piped_text:
            now_struct = time.localtime()
            default_comment = f"Note from command line - {time.strftime('%Y-%m-%d %H:%M:%S', now_struct)}"
            # Save as plain text, no HTML conversion for piped input for simplicity
            if save_note_to_file(current_save_path, piped_text, default_comment, now_struct, is_markdown=False):
                print(f"Piped content saved successfully to {current_save_path}")
            else:
                # save_note_to_file will show its own error via messagebox if GUI were running,
                # but here we need console output.
                print(f"Failed to save piped content to {current_save_path}", file=sys.stderr)
        else:
            print("No piped text received.", file=sys.stderr)
        sys.exit(0) # Exit after processing piped input

    # If not piped input, proceed with GUI
    root = tk.Tk()
    root.title("Quick Note")
    root.geometry("700x500")

    # --- Frames for layout ---
    # (Frame setup remains the same as previous version)
    top_frame = ttk.Frame(root, padding="10")
    top_frame.pack(fill=tk.X, expand=False)
    middle_frame = ttk.Frame(root, padding="10")
    middle_frame.pack(fill=tk.BOTH, expand=True)
    left_middle_frame = ttk.Frame(middle_frame)
    left_middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
    right_middle_frame = ttk.Frame(middle_frame)
    right_middle_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
    bottom_frame = ttk.Frame(root, padding="10")
    bottom_frame.pack(fill=tk.X, expand=False)
    
    # --- Clipboard and Comment Section (Left Middle Frame) ---
    # (Clipboard UI elements remain largely the same)
    ct_struct = time.localtime() # Get current time as struct for formatting
    default_comment_time = time.strftime('%Y-%m-%d %H:%M:%S', ct_struct)


    clipboard_label = ttk.Label(left_middle_frame, text="Clipboard Content (Plain Text Preview):") # Updated label
    clipboard_label.pack(pady=(0,5), anchor='w')
    clipboard_text_area = tk.Text(left_middle_frame, height=10, width=40) # GUI Element
    clipboard_text_area.pack(fill=tk.BOTH, expand=True, pady=(0,10))

    # get_clipboard_content_types will be moved to module level

    def refresh_clipboard_gui(): # Renamed, this is the GUI update function
        clipboard_text_area.delete("1.0", tk.END)
        # root is from main() scope
        html_content, plain_text = get_clipboard_content_types(root) 

        if html_content:
            clipboard_text_area.insert(tk.END, plain_text if plain_text else "HTML content detected (preview below is plain text).\n\n" + html_content)
        elif plain_text:
            clipboard_text_area.insert(tk.END, plain_text)
        else:
            clipboard_text_area.insert(tk.END, "Clipboard is empty or content type not supported for preview.")

    refresh_clipboard_button = ttk.Button(left_middle_frame, text="Refresh Clipboard", command=refresh_clipboard_gui)
    refresh_clipboard_button.pack(pady=(0,10), anchor='w')
    # Initial clipboard load is deferred until after root.mainloop() has started implicitly,
    # or explicitly call root.update() before first refresh_clipboard() if needed sooner.
    # For now, it's called when GUI is built.

    comment_label = ttk.Label(left_middle_frame, text="Comments:")
    comment_label.pack(pady=(0,5), anchor='w')
    comment_entry = ttk.Entry(left_middle_frame, width=40)
    comment_entry.pack(fill=tk.X, expand=False, pady=(0,10))
    comment_entry.insert(0, f"notes taken at {default_comment_time}")


    # --- File Browser Section (Right Middle Frame) ---
    file_browser_label = ttk.Label(right_middle_frame, text=f"Note Files (.md in {os.path.basename(current_save_path)}):") # Dynamic label
    file_browser_label.pack(pady=(0,5), anchor='w')

    file_listbox = tk.Listbox(right_middle_frame, height=10)
    file_listbox.pack(fill=tk.BOTH, expand=True, pady=(0,10))

    def populate_file_browser():
        global current_save_path
        file_listbox.delete(0, tk.END)
        
        # Update label to show current directory name
        current_dir_name = os.path.basename(current_save_path) if current_save_path else "~"
        file_browser_label.config(text=f"Note Files (.md in {current_dir_name}):")

        if not os.path.isdir(current_save_path):
            file_listbox.insert(tk.END, f"Directory not found: {current_save_path}")
            return
        
        search_path = os.path.join(current_save_path, "*.md")
        try:
            md_files = glob.glob(search_path)
            if not md_files:
                file_listbox.insert(tk.END, f"No .md files found in {current_dir_name}")
            else:
                for md_file in sorted(md_files):
                    file_listbox.insert(tk.END, os.path.basename(md_file))
        except Exception as e:
            file_listbox.insert(tk.END, f"Error listing files: {e}")
            messagebox.showerror("File Browser Error", f"Could not list files from {current_save_path}:\n{e}")


    refresh_files_button = ttk.Button(right_middle_frame, text="Refresh Files", command=populate_file_browser)
    refresh_files_button.pack(pady=(0,10), anchor='w')
    # Initial population done after settings window setup, in case path changes.

    # --- Settings Window ---
    def open_settings_window():
        global current_save_path
        settings_window = tk.Toplevel(root)
        settings_window.title("Settings")
        settings_window.geometry("450x200") # Adjusted size
        settings_window.transient(root)
        settings_window.grab_set()

        path_var = tk.StringVar(value=current_save_path)

        ttk.Label(settings_window, text="Save Directory:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        path_entry = ttk.Entry(settings_window, textvariable=path_var, width=40)
        path_entry.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

        def browse_directory():
            new_dir = filedialog.askdirectory(initialdir=path_var.get(), title="Select Save Directory")
            if new_dir: # If a directory was selected
                path_var.set(new_dir)
        
        browse_button = ttk.Button(settings_window, text="Browse...", command=browse_directory)
        browse_button.grid(row=0, column=2, padx=10, pady=10)

        def apply_settings():
            global current_save_path
            new_path = path_var.get()
            if os.path.isdir(new_path):
                current_save_path = new_path
                populate_file_browser() # Refresh file browser with new path
                settings_window.destroy()
                messagebox.showinfo("Settings Applied", f"Save directory updated to:\n{current_save_path}", parent=root)
            else:
                messagebox.showerror("Invalid Path", "The selected path is not a valid directory.", parent=settings_window)

        apply_button = ttk.Button(settings_window, text="Apply Settings", command=apply_settings)
        apply_button.grid(row=1, column=0, columnspan=3, pady=10)
        
        settings_window.columnconfigure(1, weight=1) # Make entry field expandable


    # --- Bottom Buttons (Save, Settings, Quick Save) ---
    settings_button = ttk.Button(bottom_frame, text="Settings", command=open_settings_window)
    settings_button.pack(side=tk.LEFT, padx=(0, 5))

    # process_and_save_clipboard_content will be moved to module level

    def save_note_action_gui(): # Renamed to indicate it's the GUI action
        # root, comment_entry, populate_file_browser, refresh_clipboard_gui are from main's scope
        process_and_save_clipboard_content( # Call module-level function
            root_widget=root,
            comment_widget=comment_entry,
            comments_override=None,
            populate_files_callback=populate_file_browser,
            refresh_clipboard_callback=refresh_clipboard_gui # Pass the renamed GUI refresh
        )

    def quick_save_from_clipboard_action_gui(): # Renamed
        now_struct = time.localtime()
        quick_comment = f"Quick import - {time.strftime('%Y-%m-%d %H:%M:%S', now_struct)}"
        process_and_save_clipboard_content( # Call module-level function
            root_widget=root,
            comment_widget=comment_entry, 
            comments_override=quick_comment,
            populate_files_callback=populate_file_browser,
            refresh_clipboard_callback=refresh_clipboard_gui # Pass the renamed GUI refresh
        )

    quick_save_button = ttk.Button(bottom_frame, text="Save Clipboard Now", command=quick_save_from_clipboard_action_gui)
    quick_save_button.pack(side=tk.LEFT, padx=(0,10))

    save_button = ttk.Button(bottom_frame, text="Save Note", command=save_note_action_gui) # Main save button
    save_button.pack(side=tk.RIGHT)
    
    # These should only run if GUI is starting
    populate_file_browser() 
    refresh_clipboard_gui() 
    root.mainloop()

# --- Module-level functions for core logic ---

def get_clipboard_content_types(widget_for_clipboard):
    """Attempts to get HTML and plain text from clipboard.
       Requires a Tkinter widget (e.g., root) to access clipboard_get.
    """
    html_content = None
    plain_text = None
    try:
        html_content = widget_for_clipboard.clipboard_get(type='text/html')
    except tk.TclError: # Tkinter raises TclError if type is not available
        html_content = None
    except Exception as e: # Other potential errors
        print(f"Error getting HTML from clipboard: {e}")
        html_content = None

    try:
        plain_text = pyperclip.paste()
    except pyperclip.PyperclipException as e:
        print(f"Pyperclip error: {e}")
        plain_text = f"Error reading clipboard via pyperclip: {e}"
    except Exception as e: # Other potential errors with pyperclip
        print(f"Generic error with pyperclip: {e}")
        plain_text = f"Generic error reading clipboard: {e}"
    
    # Placeholder for image detection
    # try:
    #     img = ImageGrab.grabclipboard() # From PIL/Pillow
    #     if img:
    #         messagebox.showinfo("Image Detected", "Image detected on clipboard. Image saving is not yet implemented.", parent=widget_for_clipboard)
    # except ImportError:
    #     pass 
    # except Exception:
    #     pass
        
    return html_content, plain_text

def process_and_save_clipboard_content(root_widget, comment_widget, comments_override, populate_files_callback, refresh_clipboard_callback):
    """Shared logic for processing clipboard and saving.
       This function contains the core, testable logic independent of specific button clicks.
       It requires GUI elements/callbacks to be passed in.
    """
    global current_save_path
    
    # Use .get() on the comment_widget if it's an Entry widget
    comments_text = comments_override if comments_override is not None else comment_widget.get()
    now_struct = time.localtime()
    
    html_clipboard_content, plain_clipboard_text = get_clipboard_content_types(root_widget)
    text_to_save_final = None
    is_markdown_content = False

    if html_clipboard_content:
        try:
            markdown_text = md(html_clipboard_content, heading_style='atx')
            text_to_save_final = markdown_text.strip()
            is_markdown_content = True
            print("HTML content converted to Markdown.")
        except Exception as e:
            messagebox.showerror("Markdown Conversion Error", f"Could not convert HTML to Markdown: {e}\n\nSaving as plain text instead.", parent=root_widget)
            text_to_save_final = plain_clipboard_text.strip() if plain_clipboard_text else ""
            is_markdown_content = False
    else:
        text_to_save_final = plain_clipboard_text.strip() if plain_clipboard_text else ""
        is_markdown_content = False
        print("No HTML content found, using plain text.")

    if not text_to_save_final and not (is_markdown_content and text_to_save_final == ""):
         if not text_to_save_final: # Check again if it's truly empty
            messagebox.showwarning("Empty Note", "No text content found on clipboard to save.", parent=root_widget)
            return False
    
    if save_note_to_file(current_save_path, text_to_save_final, comments_text, now_struct, is_markdown=is_markdown_content):
        messagebox.showinfo("Note Saved", f"Note saved successfully to {current_save_path}", parent=root_widget)
        
        # Callbacks for GUI updates
        if populate_files_callback: populate_files_callback()
        if refresh_clipboard_callback: refresh_clipboard_callback()
        
        # Reset main comment entry only if not a quick save
        if comments_override is None: 
            new_default_comment_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            comment_widget.delete(0, tk.END)
            comment_widget.insert(0, f"notes taken at {new_default_comment_time}")
        return True
    return False

if __name__ == "__main__":
    # If not piped input, main() will setup and run the GUI.
    # If piped, main() will process and exit.
    main()
