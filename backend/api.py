import webview
import os
import json

from backend.edb_manager import EdbManager

class Api:
    def __init__(self):
        self._window = None
        self.edb_manager = EdbManager()

    def set_window(self, window):
        self._window = window

    def greet(self):
        print("Hello from Python!")
        return "Hello from Python!"

    def open_file_dialog(self):
        # .aedb is a folder, so we use FOLDER_DIALOG
        result = self._window.create_file_dialog(webview.FOLDER_DIALOG, allow_multiple=False)
        return result[0] if result else None

    def save_file_dialog(self):
        file_types = ('EDB Files (*.aedb)', 'All files (*.*)')
        result = self._window.create_file_dialog(webview.SAVE_DIALOG, allow_multiple=False, file_types=file_types)
        return result if result else None
    
    def load_edb(self, path):
        print(f"Loading EDB from {path}")
        try:
            return self.edb_manager.load_edb(path)
        except Exception as e:
            print(f"Error loading EDB: {e}")
            return {"error": str(e)}

    def save_edb(self, path):
        print(f"Saving EDB to {path}")
        try:
            return self.edb_manager.save_edb(path)
        except Exception as e:
            print(f"Error saving EDB: {e}")
            return False

    def generate_variation(self, settings):
        print(f"Generating variation with settings: {settings}")
        try:
            return self.edb_manager.apply_variation(settings)
        except Exception as e:
            print(f"Error generating variation: {e}")
            return False

    def get_primitive_stats(self, primitive_id):
        return self.edb_manager.get_primitive_stats(primitive_id)
