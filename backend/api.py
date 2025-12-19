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
        # EDB is a folder, but webview.SAVE_DIALOG might expect a file.
        # However, for "Save As", we usually want to pick a folder name.
        # Let's try SAVE_DIALOG but be aware it might return a file path.
        # Actually, for EDB "Save As", we are saving a folder.
        # webview.SAVE_DIALOG is usually for files.
        # If we use FOLDER_DIALOG, we pick a directory, but we can't type a new name easily.
        # Let's stick to SAVE_DIALOG and ensure it ends with .aedb
        result = self._window.create_file_dialog(webview.SAVE_DIALOG, allow_multiple=False, save_filename='new_project.aedb')
        if result:
            if isinstance(result, (list, tuple)):
                return result[0]
            return result
        return None
    
    def load_edb(self, path, version="2024.1"):
        print(f"Loading EDB from {path} with version {version}")
        try:
            return self.edb_manager.load_edb(path, version)
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
