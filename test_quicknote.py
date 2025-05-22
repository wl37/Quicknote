import unittest
from unittest.mock import patch, Mock, MagicMock
import os
import sys
import time
import tempfile
import shutil

# Mock tkinter before importing quicknote
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()

# Define a mock TclError that can be raised and caught as an Exception
# This needs to be done before quicknote is imported if quicknote references tk.TclError at module level
MockTclErrorBase = type('MockTclErrorBase', (Exception,), {})
sys.modules['tkinter'].TclError = MockTclErrorBase

import quicknote

class TestSaveNoteToFile(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_save_path = quicknote.current_save_path
        quicknote.current_save_path = self.test_dir

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        quicknote.current_save_path = self.original_save_path

    def test_save_plain_text(self):
        comments = "Test plain text note"
        text_content = "This is a simple plain text note.\nWith two lines."
        curr_time_obj = time.localtime()
        
        result = quicknote.save_note_to_file(self.test_dir, text_content, comments, curr_time_obj, is_markdown=False)
        self.assertTrue(result, "save_note_to_file should return True on success")

        expected_filename = time.strftime("%Y-%m-quicknotes.md", curr_time_obj)
        expected_filepath = os.path.join(self.test_dir, expected_filename)
        self.assertTrue(os.path.exists(expected_filepath), f"File {expected_filepath} was not created.")

        with open(expected_filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn(f"## {comments}\n", content)
        self.assertIn("```\n", content) 
        self.assertIn(text_content.splitlines()[0], content)
        self.assertIn(text_content.splitlines()[1], content)
        self.assertIn("```\n", content.split("```\n", 1)[1]) 
        self.assertIn(f"Note taken at {time.strftime('%Y-%m-%d %H:%M:%S', curr_time_obj)}\n\n", content)

    def test_save_markdown_text(self):
        comments = "Test Markdown note"
        md_content = "# Markdown Header\n* Bold point\n*Another point"
        curr_time_obj = time.localtime()

        result = quicknote.save_note_to_file(self.test_dir, md_content, comments, curr_time_obj, is_markdown=True)
        self.assertTrue(result, "save_note_to_file should return True for markdown")

        expected_filename = time.strftime("%Y-%m-quicknotes.md", curr_time_obj)
        expected_filepath = os.path.join(self.test_dir, expected_filename)
        self.assertTrue(os.path.exists(expected_filepath), f"Markdown file {expected_filepath} was not created.")

        with open(expected_filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn(f"## {comments}\n", content)
        self.assertNotIn("```", content.split(f"## {comments}\n")[1]) # Markdown should not be in code blocks after the comment
        self.assertIn(md_content, content)
        self.assertIn(f"Note taken at {time.strftime('%Y-%m-%d %H:%M:%S', curr_time_obj)}\n\n", content)

    def test_save_empty_content(self):
        comments = "Test empty content"
        empty_content = ""
        curr_time_obj = time.localtime()
        
        with patch('quicknote.messagebox.showwarning') as mock_showwarning:
            result = quicknote.save_note_to_file(self.test_dir, empty_content, comments, curr_time_obj, is_markdown=False)
            self.assertFalse(result, "save_note_to_file should return False for empty content")
            mock_showwarning.assert_called_once() 
        
        expected_filename = time.strftime("%Y-%m-quicknotes.md", curr_time_obj)
        expected_filepath = os.path.join(self.test_dir, expected_filename)
        self.assertFalse(os.path.exists(expected_filepath), "File should not be created for empty content")

    def test_save_permission_error(self):
        comments = "Test permission error"
        text_content = "Some content"
        curr_time_obj = time.localtime()

        with patch('builtins.open', side_effect=PermissionError("Test permission denied")) as mock_file_open, \
             patch('quicknote.messagebox.showerror') as mock_showerror:
            result = quicknote.save_note_to_file(self.test_dir, text_content, comments, curr_time_obj, is_markdown=False)
            self.assertFalse(result, "save_note_to_file should return False on PermissionError")
            mock_file_open.assert_called_once() 
            mock_showerror.assert_called_once()
            self.assertIn("Permission Error", mock_showerror.call_args[0][0])

    def test_filename_increment_monthly(self):
        time_oct_15 = time.strptime("2023-10-15 10:00:00", "%Y-%m-%d %H:%M:%S")
        time_oct_20 = time.strptime("2023-10-20 11:00:00", "%Y-%m-%d %H:%M:%S")
        time_nov_01 = time.strptime("2023-11-01 12:00:00", "%Y-%m-%d %H:%M:%S")

        res1 = quicknote.save_note_to_file(self.test_dir, "Note 1", "First", time_oct_15, is_markdown=False)
        self.assertTrue(res1)
        res2 = quicknote.save_note_to_file(self.test_dir, "Note 2", "Second", time_oct_20, is_markdown=False)
        self.assertTrue(res2)
        res3 = quicknote.save_note_to_file(self.test_dir, "Note 3", "Third", time_nov_01, is_markdown=False)
        self.assertTrue(res3)

        oct_filename = "2023-10-quicknotes.md"
        nov_filename = "2023-11-quicknotes.md"
        
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, oct_filename)))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, nov_filename)))

        with open(os.path.join(self.test_dir, oct_filename), 'r', encoding='utf-8') as f:
            oct_content = f.read()
        self.assertIn("Note 1", oct_content)
        self.assertIn("Note 2", oct_content)
        
        with open(os.path.join(self.test_dir, nov_filename), 'r', encoding='utf-8') as f:
            nov_content = f.read()
        self.assertIn("Note 3", nov_content)

class TestGetClipboardContentTypes(unittest.TestCase):
    def setUp(self):
        # Ensure tk.TclError is an exception class that can be caught
        self.MockTclError = type('MockTclError', (Exception,), {})
        self.original_tk_TclError = sys.modules['tkinter'].TclError
        sys.modules['tkinter'].TclError = self.MockTclError

    def tearDown(self):
        sys.modules['tkinter'].TclError = self.original_tk_TclError

    @patch('quicknote.pyperclip.paste')
    def test_get_html_and_plain_text(self, mock_pyperclip_paste):
        mock_root_instance = MagicMock()
        # No need to mock tk.Tk constructor if only passing an instance
        
        mock_root_instance.clipboard_get.return_value = "<h1>Hello</h1>"
        mock_pyperclip_paste.return_value = "Hello"
        
        html_content, plain_text = quicknote.get_clipboard_content_types(mock_root_instance)
        
        self.assertEqual(html_content, "<h1>Hello</h1>")
        self.assertEqual(plain_text, "Hello")
        mock_root_instance.clipboard_get.assert_called_with(type='text/html')

    @patch('quicknote.pyperclip.paste')
    def test_get_only_plain_text(self, mock_pyperclip_paste):
        mock_root_instance = MagicMock()
        mock_root_instance.clipboard_get.side_effect = self.MockTclError("mock TclError")
        mock_pyperclip_paste.return_value = "Plain text only"
        
        html_content, plain_text = quicknote.get_clipboard_content_types(mock_root_instance)
        
        self.assertIsNone(html_content)
        self.assertEqual(plain_text, "Plain text only")

    @patch('quicknote.pyperclip.paste')
    def test_get_clipboard_errors(self, mock_pyperclip_paste):
        mock_root_instance = MagicMock()
        mock_root_instance.clipboard_get.side_effect = self.MockTclError("mock TclError")
        mock_pyperclip_paste.side_effect = quicknote.pyperclip.PyperclipException("pyperclip error")
        
        html_content, plain_text = quicknote.get_clipboard_content_types(mock_root_instance)
        
        self.assertIsNone(html_content)
        self.assertIn("Error reading clipboard via pyperclip", plain_text)

class TestProcessAndSaveClipboard(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_save_path = quicknote.current_save_path
        quicknote.current_save_path = self.test_dir
        
        self.mock_root_widget = MagicMock()
        self.mock_comment_widget = MagicMock()
        self.mock_comment_widget.get.return_value = "Test Comment"
        
        self.mock_populate_files_callback = MagicMock()
        self.mock_refresh_clipboard_callback = MagicMock()

        self.patcher_get_clipboard = patch('quicknote.get_clipboard_content_types')
        self.mock_get_clipboard = self.patcher_get_clipboard.start()

        self.patcher_save_note_file = patch('quicknote.save_note_to_file')
        self.mock_save_note_file = self.patcher_save_note_file.start()
        
        # Patching messagebox here as it's called by the function under test
        self.patcher_messagebox_showinfo = patch('quicknote.messagebox.showinfo')
        self.mock_showinfo = self.patcher_messagebox_showinfo.start()
        self.patcher_messagebox_showwarning = patch('quicknote.messagebox.showwarning')
        self.mock_showwarning = self.patcher_messagebox_showwarning.start()
        self.patcher_messagebox_showerror = patch('quicknote.messagebox.showerror')
        self.mock_showerror = self.patcher_messagebox_showerror.start()

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        quicknote.current_save_path = self.original_save_path
        self.patcher_get_clipboard.stop()
        self.patcher_save_note_file.stop()
        self.patcher_messagebox_showinfo.stop()
        self.patcher_messagebox_showwarning.stop()
        self.patcher_messagebox_showerror.stop()

    def test_process_html_clipboard_success_regular_save(self):
        self.mock_get_clipboard.return_value = ("<h1>Title</h1><p>Some text.</p>", "Title Some text.")
        self.mock_save_note_file.return_value = True

        result = quicknote.process_and_save_clipboard_content(
            root_widget=self.mock_root_widget,
            comment_widget=self.mock_comment_widget,
            comments_override=None, 
            populate_files_callback=self.mock_populate_files_callback,
            refresh_clipboard_callback=self.mock_refresh_clipboard_callback
        )
        self.assertTrue(result)
        self.mock_get_clipboard.assert_called_once_with(self.mock_root_widget)
        self.mock_save_note_file.assert_called_once()
        args, kwargs = self.mock_save_note_file.call_args
        self.assertEqual(args[0], self.test_dir)
        self.assertIn("Title", args[1]) 
        self.assertIn("Some text.", args[1]) # markdownify might add extra newlines
        self.assertEqual(args[2], "Test Comment")
        self.assertTrue(kwargs['is_markdown'])
        self.mock_showinfo.assert_called_once()
        self.mock_populate_files_callback.assert_called_once()
        self.mock_refresh_clipboard_callback.assert_called_once()
        self.mock_comment_widget.delete.assert_called_once() 
        self.mock_comment_widget.insert.assert_called_once()

    def test_process_plain_text_clipboard_quick_save(self):
        self.mock_get_clipboard.return_value = (None, "Plain text only")
        self.mock_save_note_file.return_value = True
        quick_comment_text = "Quick save comment"

        result = quicknote.process_and_save_clipboard_content(
            root_widget=self.mock_root_widget,
            comment_widget=self.mock_comment_widget,
            comments_override=quick_comment_text, 
            populate_files_callback=self.mock_populate_files_callback,
            refresh_clipboard_callback=self.mock_refresh_clipboard_callback
        )
        self.assertTrue(result)
        self.mock_save_note_file.assert_called_once()
        args, kwargs = self.mock_save_note_file.call_args
        self.assertEqual(args[1], "Plain text only")
        self.assertEqual(args[2], quick_comment_text)
        self.assertFalse(kwargs['is_markdown'])
        self.mock_showinfo.assert_called_once()
        self.mock_comment_widget.delete.assert_not_called() 

    def test_process_empty_clipboard_shows_warning(self):
        self.mock_get_clipboard.return_value = (None, "") 
        
        result = quicknote.process_and_save_clipboard_content(
            root_widget=self.mock_root_widget,
            comment_widget=self.mock_comment_widget,
            comments_override=None,
            populate_files_callback=self.mock_populate_files_callback,
            refresh_clipboard_callback=self.mock_refresh_clipboard_callback
        )
        self.assertFalse(result)
        self.mock_showwarning.assert_called_once()
        self.mock_save_note_file.assert_not_called()

class TestStdinProcessing(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_save_path = quicknote.current_save_path
        quicknote.current_save_path = self.test_dir

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        quicknote.current_save_path = self.original_save_path

    @patch('sys.stdin.isatty', return_value=False) 
    @patch('sys.stdin.read', return_value="Piped test content\n")
    @patch('quicknote.save_note_to_file') # Patch the actual save function
    @patch('sys.exit') 
    @patch('builtins.print') 
    def test_piped_input_saves_note(self, mock_print, mock_sys_exit, mock_save_note_file, mock_stdin_read, mock_isatty):
        mock_save_note_file.return_value = True
        mock_sys_exit.side_effect = SystemExit

        with self.assertRaises(SystemExit):
            quicknote.main()

        mock_isatty.assert_called_once()
        mock_stdin_read.assert_called_once()
        mock_save_note_file.assert_called_once()
        
        args, kwargs = mock_save_note_file.call_args
        self.assertEqual(args[0], self.test_dir)
        self.assertEqual(args[1], "Piped test content")
        self.assertIn("Note from command line", args[2])
        self.assertFalse(kwargs['is_markdown'])

        mock_print.assert_any_call(f"Piped content saved successfully to {self.test_dir}")
        mock_sys_exit.assert_called_once_with(0)

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdin.read', return_value="")
    @patch('quicknote.save_note_to_file') # Patch the actual save function
    @patch('sys.exit')
    @patch('builtins.print')
    def test_empty_piped_input(self, mock_print, mock_sys_exit, mock_save_note_file, mock_stdin_read, mock_isatty):
        mock_sys_exit.side_effect = SystemExit
        
        with self.assertRaises(SystemExit):
            quicknote.main()
        
        mock_save_note_file.assert_not_called()
        mock_print.assert_any_call("No piped text received.", file=sys.stderr)
        mock_sys_exit.assert_called_once_with(0)

if __name__ == '__main__':
    unittest.main()
