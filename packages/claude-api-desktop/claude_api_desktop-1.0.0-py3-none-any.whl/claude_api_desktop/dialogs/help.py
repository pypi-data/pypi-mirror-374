"""Help dialog showing keyboard shortcuts and features."""

import tkinter as tk
from tkinter import ttk, scrolledtext


class HelpDialog:
    """Help dialog showing keyboard shortcuts and features"""
    
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Claude API Desktop - Help")
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create help content"""
        notebook = ttk.Notebook(self.dialog, padding="10")
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Keyboard Shortcuts tab
        shortcuts_frame = ttk.Frame(notebook)
        notebook.add(shortcuts_frame, text="Keyboard Shortcuts")
        self.create_shortcuts_help(shortcuts_frame)
        
        # Features tab
        features_frame = ttk.Frame(notebook)
        notebook.add(features_frame, text="Features")
        self.create_features_help(features_frame)
        
        # About tab
        about_frame = ttk.Frame(notebook)
        notebook.add(about_frame, text="About")
        self.create_about_help(about_frame)
        
        # Close button
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(button_frame, text="Close", command=self.dialog.destroy).pack(side=tk.RIGHT)
        
    def create_shortcuts_help(self, parent):
        """Create keyboard shortcuts help"""
        frame = ttk.LabelFrame(parent, text="Keyboard Shortcuts", padding="10")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        shortcuts_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=20, width=70, 
                                                   font=("Consolas", 10), state=tk.DISABLED)
        shortcuts_text.pack(fill=tk.BOTH, expand=True)
        
        shortcuts_content = """
MESSAGING:
  Ctrl+Enter       Send message
  Escape           Abort current request

CONVERSATION MANAGEMENT:
  Ctrl+N           Start new conversation
  Ctrl+S           Save current conversation
  Ctrl+H           Open conversation history
  Ctrl+L           Clear current chat

INTERFACE:
  Ctrl+,           Open Settings dialog
  Ctrl+D           Toggle dark/light theme
  F1               Show this help dialog

FILE OPERATIONS:
  Ctrl+E           Export conversation
  
ATTACHMENT SHORTCUTS:
  📎 Attach        Add files/images to message
  🗑 Clear Files   Remove all attached files

MODEL PARAMETERS:
  Temperature      Controls randomness (0.0-2.0)
  Top-p           Controls diversity (0.0-1.0)
  Stop Sequences   Custom stop tokens

BETA FEATURES:
  Sonnet 4        1M context window (automatic)
  Sonnet 3.7      128k output tokens (automatic)

TIP: All parameters auto-save and persist between sessions!
"""
        
        shortcuts_text.config(state=tk.NORMAL)
        shortcuts_text.insert("1.0", shortcuts_content)
        shortcuts_text.config(state=tk.DISABLED)
        
    def create_features_help(self, parent):
        """Create features help"""
        frame = ttk.LabelFrame(parent, text="Key Features", padding="10")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        features_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=20, width=70,
                                                  font=("Consolas", 10), state=tk.DISABLED)
        features_text.pack(fill=tk.BOTH, expand=True)
        
        features_content = """
🚀 STREAMING RESPONSES
Real-time streaming of Claude's responses for immediate feedback.

📁 FILE ATTACHMENTS
• Drag & drop or browse for files
• Images: PNG, JPG, JPEG, GIF, WebP
• Text files: TXT, MD, PY, JS, JSON, CSV
• Automatic base64 encoding for images

💾 CONVERSATION HISTORY
• SQLite database for reliable storage
• Auto-save after each message (configurable)
• Search and filter conversations
• Export to Markdown or JSON
• Full conversation branching support

⚙️ ADVANCED PARAMETERS
• Temperature and Top-p sliders
• Custom stop sequences
• Model-specific max tokens
• Retry logic with exponential backoff

🎨 APPEARANCE
• Light and dark themes
• Syntax highlighting for code blocks
• Customizable font sizes
• Clean, modern interface

🔧 BETA API FEATURES
• 1M context window (Sonnet 4)
• 128k output tokens (Sonnet 3.7)
• Extended context headers automatically applied

💰 COST TRACKING
Real-time token usage and cost estimation based on current Anthropic pricing.

🔒 PRIVACY
• API key stored locally only
• No data sent to third parties
• Full control over your conversations
"""
        
        features_text.config(state=tk.NORMAL)
        features_text.insert("1.0", features_content)
        features_text.config(state=tk.DISABLED)
        
    def create_about_help(self, parent):
        """Create about information"""
        frame = ttk.LabelFrame(parent, text="About Claude API Desktop", padding="10")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        about_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=20, width=70,
                                               font=("Consolas", 10), state=tk.DISABLED)
        about_text.pack(fill=tk.BOTH, expand=True)
        
        about_content = """
Claude API Desktop v1.0.0

A modern, feature-rich desktop client for the Anthropic Claude API with streaming support, extended context capabilities, and conversation management.

AUTHOR:
Anthony Maio (anthony.maio@gmail.com)
Passionate about AI/ML and building practical tools for developers.

TECHNOLOGY STACK:
• Python 3.8+ with tkinter for cross-platform GUI
• SQLite for conversation storage
• Requests library for HTTP/streaming
• Modern async patterns for responsive UI

FEATURES DESIGNED FOR POWER USERS:
• Direct API access (no web UI limitations)
• Beta features and extended context
• Full conversation history and branching
• Professional-grade error handling
• Extensible architecture for future enhancements

OPEN SOURCE:
This project is MIT licensed and welcomes contributions.
Source: https://github.com/anthony-maio/claude-api-desktop

SUPPORT:
• Report bugs: GitHub Issues
• Feature requests: GitHub Discussions
• Documentation: README.md

DISCLAIMER:
This is an independent project and is not affiliated with Anthropic.
Always comply with Anthropic's usage policies when using the API.

Thank you for using Claude API Desktop! ⚡
"""
        
        about_text.config(state=tk.NORMAL)
        about_text.insert("1.0", about_content)
        about_text.config(state=tk.DISABLED)