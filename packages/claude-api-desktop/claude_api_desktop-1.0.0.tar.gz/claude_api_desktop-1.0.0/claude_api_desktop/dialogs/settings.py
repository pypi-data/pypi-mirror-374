"""Settings dialog for all configuration options."""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog


class SettingsDialog:
    """Settings dialog for all configuration options"""
    
    def __init__(self, parent, client):
        self.client = client
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.geometry("700x600")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.load_current_settings()
        
    def create_widgets(self):
        """Create all settings widgets"""
        notebook = ttk.Notebook(self.dialog, padding="10")
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # General tab
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="General")
        self.create_general_settings(general_frame)
        
        # API tab
        api_frame = ttk.Frame(notebook)
        notebook.add(api_frame, text="API")
        self.create_api_settings(api_frame)
        
        # Parameters tab
        params_frame = ttk.Frame(notebook)
        notebook.add(params_frame, text="Parameters")
        self.create_parameter_settings(params_frame)
        
        # Appearance tab
        appearance_frame = ttk.Frame(notebook)
        notebook.add(appearance_frame, text="Appearance")
        self.create_appearance_settings(appearance_frame)
        
        # History tab
        history_frame = ttk.Frame(notebook)
        notebook.add(history_frame, text="History")
        self.create_history_settings(history_frame)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self.save_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
    def create_general_settings(self, parent):
        """Create general settings widgets"""
        frame = ttk.LabelFrame(parent, text="General Settings", padding="10")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Model selection
        ttk.Label(frame, text="Default Model:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar()
        model_combo = ttk.Combobox(frame, textvariable=self.model_var,
                                   values=list(self.client.models.values()), width=30)
        model_combo.grid(row=0, column=1, pady=5, padx=10)
        
        # System prompt
        ttk.Label(frame, text="System Prompt:").grid(row=1, column=0, sticky=tk.NW, pady=5)
        self.system_prompt_text = scrolledtext.ScrolledText(frame, height=10, width=40, wrap=tk.WORD)
        self.system_prompt_text.grid(row=1, column=1, pady=5, padx=10)
        
    def create_api_settings(self, parent):
        """Create API settings widgets"""
        frame = ttk.LabelFrame(parent, text="API Configuration", padding="10")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # API Key
        ttk.Label(frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.api_key_var = tk.StringVar()
        api_entry = ttk.Entry(frame, textvariable=self.api_key_var, width=40, show="*")
        api_entry.grid(row=0, column=1, pady=5, padx=10)
        
        # Show/Hide API key button
        self.show_key_var = tk.BooleanVar(value=False)
        def toggle_key_visibility():
            api_entry.config(show="" if self.show_key_var.get() else "*")
        ttk.Checkbutton(frame, text="Show API Key", variable=self.show_key_var,
                       command=toggle_key_visibility).grid(row=0, column=2, pady=5)
        
        # Retry settings
        ttk.Label(frame, text="Retry Count:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.retry_count_var = tk.IntVar()
        ttk.Spinbox(frame, from_=1, to=10, textvariable=self.retry_count_var,
                   width=10).grid(row=1, column=1, sticky=tk.W, pady=5, padx=10)
        
        ttk.Label(frame, text="Retry Delay (seconds):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.retry_delay_var = tk.IntVar()
        ttk.Spinbox(frame, from_=1, to=30, textvariable=self.retry_delay_var,
                   width=10).grid(row=2, column=1, sticky=tk.W, pady=5, padx=10)
        
    def create_parameter_settings(self, parent):
        """Create parameter settings widgets"""
        frame = ttk.LabelFrame(parent, text="Model Parameters", padding="10")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Temperature
        ttk.Label(frame, text="Temperature:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.temp_var = tk.DoubleVar()
        temp_frame = ttk.Frame(frame)
        temp_frame.grid(row=0, column=1, pady=5, padx=10)
        temp_scale = ttk.Scale(temp_frame, from_=0.0, to=2.0, variable=self.temp_var,
                              orient=tk.HORIZONTAL, length=200)
        temp_scale.pack(side=tk.LEFT)
        self.temp_label = ttk.Label(temp_frame, text="1.0", width=5)
        self.temp_label.pack(side=tk.LEFT, padx=5)
        temp_scale.configure(command=lambda v: self.temp_label.config(text=f"{float(v):.2f}"))
        
        # Top-p
        ttk.Label(frame, text="Top-p:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.top_p_var = tk.DoubleVar()
        top_p_frame = ttk.Frame(frame)
        top_p_frame.grid(row=1, column=1, pady=5, padx=10)
        top_p_scale = ttk.Scale(top_p_frame, from_=0.0, to=1.0, variable=self.top_p_var,
                               orient=tk.HORIZONTAL, length=200)
        top_p_scale.pack(side=tk.LEFT)
        self.top_p_label = ttk.Label(top_p_frame, text="0.999", width=5)
        self.top_p_label.pack(side=tk.LEFT, padx=5)
        top_p_scale.configure(command=lambda v: self.top_p_label.config(text=f"{float(v):.3f}"))
        
        # Stop sequences
        ttk.Label(frame, text="Stop Sequences:").grid(row=2, column=0, sticky=tk.NW, pady=5)
        self.stop_sequences_text = scrolledtext.ScrolledText(frame, height=5, width=30, wrap=tk.WORD)
        self.stop_sequences_text.grid(row=2, column=1, pady=5, padx=10)
        ttk.Label(frame, text="(One per line)", font=("", 8)).grid(row=3, column=1, sticky=tk.W, padx=10)
        
    def create_appearance_settings(self, parent):
        """Create appearance settings widgets"""
        frame = ttk.LabelFrame(parent, text="Appearance", padding="10")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Theme
        ttk.Label(frame, text="Theme:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.theme_var = tk.StringVar()
        theme_frame = ttk.Frame(frame)
        theme_frame.grid(row=0, column=1, sticky=tk.W, pady=5, padx=10)
        ttk.Radiobutton(theme_frame, text="Light", variable=self.theme_var,
                       value="light").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(theme_frame, text="Dark", variable=self.theme_var,
                       value="dark").pack(side=tk.LEFT, padx=5)
        
        # Font size
        ttk.Label(frame, text="Chat Font Size:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.font_size_var = tk.IntVar()
        ttk.Spinbox(frame, from_=8, to=20, textvariable=self.font_size_var,
                   width=10).grid(row=1, column=1, sticky=tk.W, pady=5, padx=10)
        
        # Code highlighting
        self.code_highlight_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Enable code syntax highlighting",
                       variable=self.code_highlight_var).grid(row=2, column=0, columnspan=2,
                                                             sticky=tk.W, pady=5, padx=10)
        
    def create_history_settings(self, parent):
        """Create history settings widgets"""
        frame = ttk.LabelFrame(parent, text="Conversation History", padding="10")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Auto-save
        self.auto_save_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Auto-save conversations",
                       variable=self.auto_save_var).grid(row=0, column=0, columnspan=2,
                                                        sticky=tk.W, pady=5, padx=10)
        
        # Auto-save interval
        ttk.Label(frame, text="Auto-save interval:").grid(row=1, column=0, sticky=tk.W, pady=5)
        interval_frame = ttk.Frame(frame)
        interval_frame.grid(row=1, column=1, sticky=tk.W, pady=5, padx=10)
        self.save_interval_var = tk.StringVar()
        ttk.Radiobutton(interval_frame, text="After each message", variable=self.save_interval_var,
                       value="message").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(interval_frame, text="Every 5 minutes", variable=self.save_interval_var,
                       value="timed").pack(side=tk.LEFT, padx=5)
        
        # History retention
        ttk.Label(frame, text="Keep conversations for:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.retention_var = tk.StringVar()
        ttk.Combobox(frame, textvariable=self.retention_var,
                    values=["Forever", "30 days", "90 days", "1 year"],
                    width=15).grid(row=2, column=1, sticky=tk.W, pady=5, padx=10)
        
        # Database location
        ttk.Label(frame, text="Database location:").grid(row=3, column=0, sticky=tk.W, pady=5)
        db_frame = ttk.Frame(frame)
        db_frame.grid(row=3, column=1, sticky=tk.W, pady=5, padx=10)
        self.db_path_var = tk.StringVar()
        ttk.Entry(db_frame, textvariable=self.db_path_var, width=30).pack(side=tk.LEFT)
        ttk.Button(db_frame, text="Browse...", command=self.browse_db_path).pack(side=tk.LEFT, padx=5)
        
    def browse_db_path(self):
        """Browse for database file location"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All files", "*.*")]
        )
        if file_path:
            self.db_path_var.set(file_path)
        
    def load_current_settings(self):
        """Load current settings from client"""
        # General
        self.model_var.set(self.client.models.get(self.client.model, ""))
        self.system_prompt_text.insert("1.0", self.client.system_prompt)
        
        # API
        self.api_key_var.set(self.client.api_key_var.get())
        self.retry_count_var.set(self.client.retry_count)
        self.retry_delay_var.set(self.client.retry_delay)
        
        # Parameters
        self.temp_var.set(self.client.temperature)
        self.temp_label.config(text=f"{self.client.temperature:.2f}")
        self.top_p_var.set(self.client.top_p)
        self.top_p_label.config(text=f"{self.client.top_p:.3f}")
        self.stop_sequences_text.insert("1.0", "\n".join(self.client.stop_sequences))
        
        # Appearance
        self.theme_var.set("dark" if self.client.dark_mode else "light")
        self.font_size_var.set(10)  # Default, will make configurable
        self.code_highlight_var.set(True)  # Default
        
        # History
        self.auto_save_var.set(self.client.auto_save)
        self.save_interval_var.set(self.client.save_interval)
        self.retention_var.set("Forever")  # Default
        self.db_path_var.set(self.client.db_manager.db_path)
        
    def save_settings(self):
        """Save all settings"""
        # General
        for model_id, display_name in self.client.models.items():
            if display_name == self.model_var.get():
                self.client.model = model_id
                self.client.model_var.set(display_name)
                break
        self.client.system_prompt = self.system_prompt_text.get("1.0", tk.END).strip()
        
        # API
        self.client.api_key_var.set(self.api_key_var.get())
        self.client.retry_count = self.retry_count_var.get()
        self.client.retry_delay = self.retry_delay_var.get()
        
        # Parameters
        self.client.temperature = self.temp_var.get()
        self.client.top_p = self.top_p_var.get()
        
        sequences = self.stop_sequences_text.get("1.0", tk.END).strip()
        self.client.stop_sequences = [s.strip() for s in sequences.split("\n") if s.strip()]
        
        # Appearance
        self.client.dark_mode = self.theme_var.get() == "dark"
        self.client.apply_theme()
        
        # History
        self.client.auto_save = self.auto_save_var.get()
        self.client.save_interval = self.save_interval_var.get()
        
        # Save to config
        self.client.save_config()
        
        self.dialog.destroy()