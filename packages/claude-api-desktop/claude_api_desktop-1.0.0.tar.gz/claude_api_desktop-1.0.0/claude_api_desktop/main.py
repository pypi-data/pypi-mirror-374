"""Main entry point for Claude API Desktop application."""

import tkinter as tk
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the application."""
    try:
        # Import after logging is configured
        from .client import ClaudeClient
        
        # Create main window
        root = tk.Tk()
        
        # Set application icon if available
        try:
            icon_path = Path(__file__).parent / "assets" / "icon.ico"
            if icon_path.exists():
                root.iconbitmap(str(icon_path))
        except Exception:
            pass  # Icon not critical
        
        # Create and run application
        app = ClaudeClient(root)
        
        logger.info("Starting Claude API Desktop application")
        root.mainloop()
        
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        print("Error: Failed to start Claude API Desktop. Please check your installation.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error starting application: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()