"""Main Claude API Desktop client."""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import json
import threading
import queue
import requests
import base64
from datetime import datetime
from pathlib import Path
import configparser
import re
import time
from typing import Optional, Dict, List, Any

# Import our modular components
from .database import DatabaseManager
from .dialogs import SettingsDialog, ConversationHistoryDialog, HelpDialog, BranchDialog


class ClaudeClient:
    """Main Claude API Desktop client application."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Claude API Desktop")
        self.root.geometry("1200x800")
        
        # Configuration
        # Use platform-appropriate config directory
        import platform
        system = platform.system()
        if system == "Windows":
            config_dir = Path.home() / "AppData" / "Local" / "claude-api-desktop"
        elif system == "Darwin":  # macOS
            config_dir = Path.home() / "Library" / "Application Support" / "claude-api-desktop"
        else:  # Linux and others
            config_dir = Path.home() / ".local" / "share" / "claude-api-desktop"
        
        config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = config_dir / "claude_client_config"
        self.api_key = ""
        self.model = "claude-sonnet-4-20250514"
        self.system_prompt = ""
        self.messages = []
        self.total_tokens = 0
        self.message_queue = queue.Queue()
        self.attached_files = []
        self.current_session = None
        self.abort_event = threading.Event()
        self.dark_mode = False
        self.retry_count = 3
        self.retry_delay = 2
        
        # Conversation management
        self.current_conversation_id = None
        self.auto_save = True
        self.save_interval = "message"
        self.db_manager = DatabaseManager()
        
        # Parameters
        self.temperature = 1.0
        self.top_p = 0.999
        self.stop_sequences = []
        
        # Model configurations
        self.models = {
            "claude-opus-4-1-20250805": "Claude Opus 4.1",
            "claude-opus-4-20250514": "Claude Opus 4",
            "claude-sonnet-4-20250514": "Claude Sonnet 4",
            "claude-3-7-sonnet-20250219": "Claude Sonnet 3.7",
            "claude-3-5-haiku-20241022": "Claude Haiku 3.5"
        }
        
        # Color schemes
        self.themes = {
            "light": {
                "bg": "#ffffff", "fg": "#000000", "input_bg": "#ffffff", "input_fg": "#000000",
                "user_color": "#0066cc", "assistant_color": "#008800", "error_color": "#cc0000",
                "system_color": "#666666", "code_bg": "#f5f5f5", "code_fg": "#333333"
            },
            "dark": {
                "bg": "#1e1e1e", "fg": "#e0e0e0", "input_bg": "#2d2d2d", "input_fg": "#e0e0e0", 
                "user_color": "#4da6ff", "assistant_color": "#66ff66", "error_color": "#ff6666",
                "system_color": "#999999", "code_bg": "#2d2d2d", "code_fg": "#e0e0e0"
            }
        }
        
        # Code syntax patterns for highlighting
        self.code_patterns = {
            'keyword': (r'\b(def|class|import|from|return|if|else|elif|for|while|try|except|with|as|lambda|yield|assert|break|continue|pass|raise|finally|is|in|and|or|not|None|True|False|self|async|await)\b', '#cf222e'),
            'string': (r'(["\'])(?:(?=(\\?))\2.)*?\1', '#0a3069'),
            'comment': (r'#.*?$', '#6e7781'),
            'number': (r'\b\d+\.?\d*\b', '#0550ae'),
            'function': (r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', '#8250df'),
            'decorator': (r'@[a-zA-Z_][a-zA-Z0-9_]*', '#0550ae'),
        }
        
        self.setup_ui()
        self.load_config()
        self.apply_theme()
        self.root.after(100, self.process_message_queue)
        
        # Auto-save timer
        if self.auto_save and self.save_interval == "timed":
            self.root.after(300000, self.auto_save_timer)
        
    def setup_ui(self):
        """Setup the main UI"""
        style = ttk.Style()
        style.theme_use('clam')
        
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Toolbar
        toolbar = ttk.Frame(main_container)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        left_toolbar = ttk.Frame(toolbar)
        left_toolbar.pack(side=tk.LEFT)
        
        ttk.Label(left_toolbar, text="Model:").pack(side=tk.LEFT, padx=5)
        self.model_var = tk.StringVar(value=self.model)
        model_combo = ttk.Combobox(left_toolbar, textvariable=self.model_var, 
                                   values=list(self.models.values()), width=20)
        model_combo.pack(side=tk.LEFT, padx=5)
        model_combo.bind("<<ComboboxSelected>>", self.on_model_change)
        
        right_toolbar = ttk.Frame(toolbar)
        right_toolbar.pack(side=tk.RIGHT)
        
        buttons = [
            ("📚 History", self.open_history),
            ("💾 Save", self.save_conversation),
            ("🆕 New", self.new_conversation),
            ("🌿 Branch", self.show_branch_options),
            ("⚙️ Settings", self.open_settings),
            ("❓ Help", self.open_help)
        ]
        
        for text, command in buttons:
            ttk.Button(right_toolbar, text=text, command=command).pack(side=tk.LEFT, padx=2)
        
        # Stats Frame
        stats_frame = ttk.Frame(main_container)
        stats_frame.pack(fill=tk.X, pady=2)
        
        self.stats_label = ttk.Label(stats_frame, text="Tokens: 0 | Messages: 0 | Cost: $0.0000")
        self.stats_label.pack(side=tk.LEFT, padx=10)
        
        self.attachment_label = ttk.Label(stats_frame, text="")
        self.attachment_label.pack(side=tk.LEFT, padx=10)
        
        self.status_label = ttk.Label(stats_frame, text="Ready", foreground="green")
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        # Chat Display
        chat_frame = ttk.LabelFrame(main_container, text="Conversation", padding="5")
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, 
                                                      width=80, height=25, font=("Consolas", 10))
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        self.setup_text_tags()
        
        # Input Frame
        input_frame = ttk.LabelFrame(main_container, text="Message", padding="5")
        input_frame.pack(fill=tk.X, pady=5)
        
        input_container = ttk.Frame(input_frame)
        input_container.pack(fill=tk.X)
        
        self.input_text = tk.Text(input_container, height=4, width=70, font=("Consolas", 10))
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        button_frame = ttk.Frame(input_container)
        button_frame.pack(side=tk.RIGHT, padx=5)
        
        input_buttons = [
            ("📎 Attach", self.attach_file),
            ("▶ Send", self.send_message),
            ("⏹ Abort", self.abort_request),
            ("🗑 Clear Files", self.clear_attachments)
        ]
        
        for text, command in input_buttons:
            btn = ttk.Button(button_frame, text=text, command=command)
            btn.pack(pady=2)
            if "Abort" in text:
                self.abort_button = btn
                btn.config(state=tk.DISABLED)
            elif "Send" in text:
                self.send_button = btn
        
        # Bind keyboard shortcuts
        shortcuts = [
            ("<Control-Return>", self.send_message),
            ("<Control-n>", self.new_conversation),
            ("<Control-s>", self.save_conversation),
            ("<Control-h>", self.open_history),
            ("<Control-comma>", self.open_settings),
            ("<Control-e>", self.export_conversation),
            ("<Control-d>", self.toggle_dark_mode),
            ("<Control-l>", self.clear_chat),
            ("<F1>", self.open_help),
            ("<Escape>", self.abort_request)
        ]
        
        for shortcut, command in shortcuts:
            self.root.bind(shortcut, lambda e, cmd=command: cmd())
    
    def setup_text_tags(self):
        """Configure text tags for chat display"""
        self.chat_display.tag_config("user", font=("Consolas", 10, "bold"))
        self.chat_display.tag_config("assistant", font=("Consolas", 10, "bold"))
        self.chat_display.tag_config("system", font=("Consolas", 10, "italic"))
        self.chat_display.tag_config("error", font=("Consolas", 10, "bold"))
        self.chat_display.tag_config("code", font=("Courier", 9))
        self.chat_display.tag_config("code_block", font=("Courier", 9))
    
    # Dialog methods
    def open_settings(self):
        """Open settings dialog"""
        SettingsDialog(self.root, self)
        
    def open_history(self):
        """Open conversation history dialog"""
        ConversationHistoryDialog(self.root, self)
        
    def open_help(self):
        """Open help dialog"""
        HelpDialog(self.root)
        
    def show_branch_options(self):
        """Show branching options for current conversation"""
        if not self.messages:
            messagebox.showinfo("Branch", "No conversation to branch from")
            return
        if not self.current_conversation_id:
            self.save_conversation()
        BranchDialog(self.root, self)
    
    def send_message(self):
        """Send message to Claude API"""
        message = self.input_text.get("1.0", tk.END).strip()
        if not message and not self.attached_files:
            return
            
        if not self.api_key_var.get().strip():
            messagebox.showerror("Error", "Please set your API key in Settings")
            return
            
        self.send_button.config(state=tk.DISABLED)
        self.abort_button.config(state=tk.NORMAL)
        self.abort_event.clear()
        
        # Add user message to display
        if message:
            self.add_message_to_display("You", message, "user")
            
        # Handle file attachments
        content_parts = []
        if message:
            content_parts.append({"type": "text", "text": message})
            
        for file_path in self.attached_files:
            try:
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    with open(file_path, 'rb') as f:
                        image_data = base64.b64encode(f.read()).decode('utf-8')
                        content_parts.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": f"image/{file_path.split('.')[-1].lower()}",
                                "data": image_data
                            }
                        })
                else:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        file_content = f.read()
                        content_parts.append({
                            "type": "text", 
                            "text": f"File: {Path(file_path).name}\n\n{file_content}"
                        })
            except Exception as e:
                self.add_message_to_display("System", f"Error reading file {file_path}: {e}", "error")
                
        # Clear input and attachments
        self.input_text.delete("1.0", tk.END)
        self.clear_attachments()
        
        # Prepare messages
        user_message = {"role": "user", "content": content_parts if len(content_parts) > 1 else message}
        self.messages.append(user_message)
        
        # Save message if auto-save is enabled
        if self.auto_save and self.current_conversation_id:
            self.db_manager.save_message(self.current_conversation_id, "user", user_message["content"])
        
        # Start API request in separate thread
        self.current_session = threading.Thread(target=self._api_request, args=(self.messages.copy(),))
        self.current_session.daemon = True
        self.current_session.start()
        
        self.status_label.config(text="Sending...", foreground="orange")
        
    def _api_request(self, messages):
        """Make API request in separate thread"""
        try:
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.api_key_var.get(),
                "Anthropic-Version": "2023-06-01",
                "Anthropic-Beta": "max-tokens-3-5-sonnet-2024-07-15,computer-use-2024-10-22,pdfs-2024-09-25,prompt-caching-2024-07-31"
            }
            
            # Prepare request body
            request_data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 8192,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "stream": True
            }
            
            if self.system_prompt:
                request_data["system"] = self.system_prompt
                
            if self.stop_sequences:
                request_data["stop_sequences"] = self.stop_sequences
                
            # Make request with retry logic
            for attempt in range(self.retry_count):
                if self.abort_event.is_set():
                    return
                    
                try:
                    response = requests.post(
                        "https://api.anthropic.com/v1/messages",
                        headers=headers,
                        json=request_data,
                        stream=True,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        self._handle_streaming_response(response)
                        return
                    else:
                        error_msg = f"HTTP {response.status_code}: {response.text}"
                        if attempt < self.retry_count - 1:
                            time.sleep(self.retry_delay * (2 ** attempt))
                            continue
                        else:
                            raise Exception(error_msg)
                            
                except requests.exceptions.RequestException as e:
                    if attempt < self.retry_count - 1 and not self.abort_event.is_set():
                        time.sleep(self.retry_delay * (2 ** attempt))
                        continue
                    else:
                        raise e
                        
        except Exception as e:
            if not self.abort_event.is_set():
                self.message_queue.put(("error", str(e)))
            
    def _handle_streaming_response(self, response):
        """Handle streaming response from API"""
        assistant_message = ""
        
        try:
            for line in response.iter_lines():
                if self.abort_event.is_set():
                    return
                    
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                            
                        try:
                            chunk = json.loads(data)
                            if chunk.get('type') == 'content_block_delta':
                                text = chunk.get('delta', {}).get('text', '')
                                assistant_message += text
                                self.message_queue.put(("stream", text))
                        except json.JSONDecodeError:
                            continue
                            
            if not self.abort_event.is_set():
                # Add complete message to history
                self.messages.append({"role": "assistant", "content": assistant_message})
                
                # Save message if auto-save is enabled
                if self.auto_save and self.current_conversation_id:
                    self.db_manager.save_message(self.current_conversation_id, "assistant", assistant_message)
                elif self.auto_save and self.save_interval == "message":
                    self.save_conversation()
                    
                self.message_queue.put(("complete", assistant_message))
                
        except Exception as e:
            if not self.abort_event.is_set():
                self.message_queue.put(("error", str(e)))
    
    def apply_theme(self):
        """Apply the current theme to all widgets"""
        theme = self.themes["dark" if self.dark_mode else "light"]
        
        self.root.configure(bg=theme["bg"])
        self.chat_display.configure(bg=theme["bg"], fg=theme["fg"], insertbackground=theme["fg"])
        self.input_text.configure(bg=theme["input_bg"], fg=theme["input_fg"], insertbackground=theme["input_fg"])
        
        self.chat_display.tag_config("user", foreground=theme["user_color"])
        self.chat_display.tag_config("assistant", foreground=theme["assistant_color"])
        self.chat_display.tag_config("system", foreground=theme["system_color"])
        self.chat_display.tag_config("error", foreground=theme["error_color"])
        self.chat_display.tag_config("code_block", background=theme["code_bg"], foreground=theme["code_fg"])
    
    def load_config(self):
        """Load configuration from file"""
        self.api_key_var = tk.StringVar()
        if self.config_file.exists():
            config = configparser.ConfigParser()
            config.read(self.config_file)
            if 'Settings' in config:
                self.api_key_var.set(config['Settings'].get('api_key', ''))
                self.model = config['Settings'].get('model', self.model)
                self.system_prompt = config['Settings'].get('system_prompt', '')
                self.temperature = float(config['Settings'].get('temperature', '1.0'))
                self.top_p = float(config['Settings'].get('top_p', '0.999'))
                self.dark_mode = config['Settings'].get('dark_mode', 'False') == 'True'
                self.auto_save = config['Settings'].get('auto_save', 'True') == 'True'
                self.save_interval = config['Settings'].get('save_interval', 'message')
                self.retry_count = int(config['Settings'].get('retry_count', '3'))
                self.retry_delay = int(config['Settings'].get('retry_delay', '2'))
                
                stop_seq = config['Settings'].get('stop_sequences', '')
                if stop_seq:
                    self.stop_sequences = json.loads(stop_seq)
    
    def save_config(self):
        """Save configuration to file"""
        config = configparser.ConfigParser()
        config['Settings'] = {
            'api_key': self.api_key_var.get(),
            'model': self.model,
            'system_prompt': self.system_prompt,
            'temperature': str(self.temperature),
            'top_p': str(self.top_p),
            'stop_sequences': json.dumps(self.stop_sequences),
            'dark_mode': str(self.dark_mode),
            'auto_save': str(self.auto_save),
            'save_interval': self.save_interval,
            'retry_count': str(self.retry_count),
            'retry_delay': str(self.retry_delay)
        }
        with open(self.config_file, 'w') as f:
            config.write(f)
    
    def on_model_change(self, event=None):
        """Handle model selection change"""
        selected_display_name = self.model_var.get()
        for model_id, display_name in self.models.items():
            if display_name == selected_display_name:
                self.model = model_id
                break
                
    def new_conversation(self):
        """Start a new conversation"""
        if self.messages and messagebox.askyesno("New Conversation", 
                                                "Start new conversation? Current conversation will be saved."):
            if self.auto_save:
                self.save_conversation()
            
            self.messages = []
            self.current_conversation_id = None
            self.attached_files = []
            self.total_tokens = 0
            self.clear_chat()
            self.update_stats()
            self.status_label.config(text="Ready", foreground="green")
            
    def save_conversation(self, title=None):
        """Save current conversation to database"""
        if not self.messages:
            messagebox.showinfo("Save", "No conversation to save")
            return
            
        if not title and not self.current_conversation_id:
            title = simpledialog.askstring("Save Conversation", "Enter conversation title:")
            if not title:
                return
                
        try:
            if self.current_conversation_id:
                # Update existing conversation
                for msg in self.messages:
                    self.db_manager.save_message(self.current_conversation_id, msg['role'], msg['content'])
            else:
                # Create new conversation
                if not title:
                    # Auto-generate title from first message
                    first_user_msg = next((m for m in self.messages if m['role'] == 'user'), None)
                    if first_user_msg:
                        content = first_user_msg['content']
                        if isinstance(content, list):
                            content = content[0].get('text', '') if content else ''
                        title = content[:50] + "..." if len(content) > 50 else content
                    else:
                        title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                        
                parameters = {
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "stop_sequences": self.stop_sequences
                }
                
                self.current_conversation_id = self.db_manager.create_conversation(
                    title, self.model, self.system_prompt, parameters
                )
                
                for msg in self.messages:
                    self.db_manager.save_message(self.current_conversation_id, msg['role'], msg['content'])
                    
            messagebox.showinfo("Save", "Conversation saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save conversation: {e}")
            
    def export_conversation(self):
        """Export conversation to file"""
        if not self.messages:
            messagebox.showinfo("Export", "No conversation to export")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    export_data = {
                        "model": self.model,
                        "system_prompt": self.system_prompt,
                        "messages": self.messages,
                        "parameters": {
                            "temperature": self.temperature,
                            "top_p": self.top_p,
                            "stop_sequences": self.stop_sequences
                        },
                        "exported_at": datetime.now().isoformat()
                    }
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, indent=2, ensure_ascii=False)
                else:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"Claude API Desktop - Conversation Export\n")
                        f.write(f"Model: {self.models.get(self.model, self.model)}\n")
                        f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write("="*50 + "\n\n")
                        
                        if self.system_prompt:
                            f.write(f"System: {self.system_prompt}\n\n")
                            
                        for msg in self.messages:
                            role = "You" if msg['role'] == 'user' else "Claude"
                            content = msg['content']
                            if isinstance(content, list):
                                content = content[0].get('text', '') if content else ''
                            f.write(f"{role}:\n{content}\n\n")
                            
                messagebox.showinfo("Export", f"Conversation exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export conversation: {e}")
                
    def toggle_dark_mode(self):
        """Toggle dark mode theme"""
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        self.save_config()
        
    def clear_chat(self):
        """Clear the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
    def attach_file(self):
        """Attach file to message"""
        filetypes = [
            ("All supported", "*.txt;*.py;*.js;*.html;*.css;*.json;*.xml;*.md;*.png;*.jpg;*.jpeg;*.gif;*.webp"),
            ("Text files", "*.txt;*.py;*.js;*.html;*.css;*.json;*.xml;*.md"),
            ("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.webp"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.attached_files.append(filename)
            self.update_attachment_display()
            
    def clear_attachments(self):
        """Clear all file attachments"""
        self.attached_files = []
        self.update_attachment_display()
        
    def update_attachment_display(self):
        """Update attachment display label"""
        if self.attached_files:
            file_names = [Path(f).name for f in self.attached_files]
            display_text = f"📎 {len(self.attached_files)} file(s): {', '.join(file_names[:3])}"
            if len(self.attached_files) > 3:
                display_text += "..."
            self.attachment_label.config(text=display_text)
        else:
            self.attachment_label.config(text="")
            
    def abort_request(self):
        """Abort current API request"""
        self.abort_event.set()
        self.send_button.config(state=tk.NORMAL)
        self.abort_button.config(state=tk.DISABLED)
        self.status_label.config(text="Aborted", foreground="red")
        
    def process_message_queue(self):
        """Process messages from API thread"""
        try:
            while True:
                msg_type, content = self.message_queue.get_nowait()
                
                if msg_type == "stream":
                    self.add_stream_text(content)
                elif msg_type == "complete":
                    self.complete_response()
                elif msg_type == "error":
                    self.handle_api_error(content)
                    
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_message_queue)
            
    def add_stream_text(self, text):
        """Add streaming text to display"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Start assistant response if not started
        if not hasattr(self, '_streaming_response'):
            self._streaming_response = True
            self.chat_display.insert(tk.END, "\nClaude:\n", "assistant")
            
        # Add text with syntax highlighting if it looks like code
        if self._looks_like_code(text):
            self.add_highlighted_text(text)
        else:
            self.chat_display.insert(tk.END, text)
            
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
    def complete_response(self):
        """Complete the streaming response"""
        if hasattr(self, '_streaming_response'):
            del self._streaming_response
            
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "\n\n")
        self.chat_display.config(state=tk.DISABLED)
        
        self.send_button.config(state=tk.NORMAL)
        self.abort_button.config(state=tk.DISABLED)
        self.status_label.config(text="Ready", foreground="green")
        self.update_stats()
        
    def handle_api_error(self, error_msg):
        """Handle API error"""
        if hasattr(self, '_streaming_response'):
            del self._streaming_response
            
        self.add_message_to_display("Error", error_msg, "error")
        self.send_button.config(state=tk.NORMAL)
        self.abort_button.config(state=tk.DISABLED)
        self.status_label.config(text="Error", foreground="red")
        
    def auto_save_timer(self):
        """Auto-save timer for timed saves"""
        if self.auto_save and self.save_interval == "timed" and self.messages:
            self.save_conversation()
        self.root.after(300000, self.auto_save_timer)  # 5 minutes
        
    def branch_from_current(self, branch_name: str = None):
        """Create a branch from current conversation"""
        if not self.messages:
            raise Exception("No conversation to branch from")
            
        # Save current conversation first if needed
        if not self.current_conversation_id:
            self.save_conversation()
            
        if not branch_name:
            existing_branches = self.db_manager.get_conversation_branches(self.current_conversation_id)
            branch_name = f"Branch {len(existing_branches) + 1}"
            
        # Get original conversation
        original_conv = self.db_manager.get_conversation(self.current_conversation_id)
        if not original_conv:
            raise Exception("Could not load current conversation")
            
        # Create branch
        branch_id = self.db_manager.create_conversation(
            f"{original_conv['title']} - {branch_name}",
            original_conv['model'],
            original_conv['system_prompt'],
            original_conv['parameters'],
            parent_id=self.current_conversation_id,
            branch_name=branch_name
        )
        
        # Copy messages to branch
        for msg in self.messages:
            self.db_manager.save_message(branch_id, msg['role'], msg['content'])
            
        # Switch to the new branch
        self.current_conversation_id = branch_id
        
        return branch_id
    
    def add_message_to_display(self, role: str, content: str, tag: str):
        """Add a message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"\n{role}:\n", tag)
        
        if self._looks_like_code(content):
            self.add_highlighted_text(content)
        else:
            self.chat_display.insert(tk.END, content)
            
        self.chat_display.insert(tk.END, "\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
    def display_messages(self):
        """Display all messages in the chat"""
        self.clear_chat()
        for msg in self.messages:
            role = "You" if msg['role'] == 'user' else "Claude"
            tag = msg['role']
            content = msg['content']
            if isinstance(content, list):
                content = content[0].get('text', '') if content else ''
            self.add_message_to_display(role, content, tag)
            
    def update_stats(self):
        """Update statistics display"""
        msg_count = len(self.messages)
        # Estimate tokens (rough approximation)
        total_chars = sum(len(str(msg.get('content', ''))) for msg in self.messages)
        estimated_tokens = total_chars // 4  # Rough estimate
        
        # Estimate cost (approximate rates)
        cost_per_1k_tokens = 0.003  # Rough average
        estimated_cost = (estimated_tokens / 1000) * cost_per_1k_tokens
        
        self.stats_label.config(text=f"Tokens: {estimated_tokens} | Messages: {msg_count} | Cost: ${estimated_cost:.4f}")
        
    def _looks_like_code(self, text: str) -> bool:
        """Check if text looks like code"""
        code_indicators = ['def ', 'class ', 'import ', 'from ', '```', '    ', '\t', '{', '}', '()', '[]']
        return any(indicator in text for indicator in code_indicators)
        
    def add_highlighted_text(self, text: str):
        """Add syntax-highlighted text to display"""
        self.chat_display.insert(tk.END, text, "code_block")