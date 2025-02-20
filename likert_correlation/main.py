"""Main entry point for the Likert Scale Correlation Analyzer."""
import sys
import threading
import webbrowser
from pathlib import Path
from time import sleep

import pystray
import requests
from PIL import Image
from pystray import MenuItem as item

from likert_correlation.web import create_app

class LikertAnalyzer:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        if hasattr(sys, '_MEIPASS'):
            # Running from PyInstaller bundle
            self.base_dir = Path(sys._MEIPASS) / 'likert_correlation'
        
        # Initialize Flask app
        self.app = create_app(self.base_dir)
        self.server_thread = None
        self.icon = None
        self.url = "http://localhost:5000"
        
    def run_server(self):
        """Run Flask server in a separate thread."""
        self.app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
        
    def open_browser(self):
        """Open web browser after short delay to ensure server is running."""
        sleep(1.5)  # Wait for server to start
        webbrowser.open(self.url)
        
    def create_system_tray(self):
        """Create system tray icon with menu."""
        icon_path = self.base_dir / 'static' / 'icon.png'
        
        # Create fallback icon if none exists
        if not icon_path.exists():
            img = Image.new('RGB', (64, 64), color='blue')
        else:
            img = Image.open(icon_path)
            
        def open_ui(icon, item):
            webbrowser.open(self.url)
            
        def exit_app(icon, item):
            icon.stop()
            if self.server_thread and self.server_thread.is_alive():
                try:
                    requests.get(f"{self.url}/shutdown")
                except:
                    pass
            sys.exit(0)
            
        menu = (
            item('Open Interface', open_ui),
            item('Exit', exit_app),
        )
        
        self.icon = pystray.Icon(
            "likert_analyzer",
            img,
            "Likert Scale Analyzer",
            menu
        )
        
    def run(self):
        """Run the complete application."""
        # Start Flask server in separate thread
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # Open browser
        threading.Thread(target=self.open_browser).start()
        
        # Create and run system tray icon
        self.create_system_tray()
        self.icon.run()

def main():
    """Entry point for the application."""
    analyzer = LikertAnalyzer()
    analyzer.run()

if __name__ == '__main__':
    main()