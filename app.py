import webview
import os
import sys
import threading
from backend.api import Api

# Set up the API
api = Api()

def get_entrypoint():
    """
    Determine the entry point for the application.
    In development, it connects to the Vite dev server.
    In production, it loads the built HTML file.
    """
    # Check if running in development mode (e.g., via a flag or environment variable)
    # For simplicity, let's check if the frontend dev server port is open or just default to dev for now if not frozen
    if getattr(sys, 'frozen', False):
        # Production mode
        return os.path.join(os.path.dirname(__file__), 'frontend', 'dist', 'index.html')
    
    # Check if dist exists
    dist_path = os.path.join(os.path.dirname(__file__), 'frontend', 'dist', 'index.html')
    if os.path.exists(dist_path):
        return dist_path

    # Development mode fallback
    return 'http://localhost:5173'

if __name__ == '__main__':
    entry = get_entrypoint()
    
    window = webview.create_window(
        'Line Width Variator',
        entry,
        js_api=api,
        width=1200,
        height=800,
        resizable=True
    )
    api.set_window(window)
    
    webview.start(debug=True)
