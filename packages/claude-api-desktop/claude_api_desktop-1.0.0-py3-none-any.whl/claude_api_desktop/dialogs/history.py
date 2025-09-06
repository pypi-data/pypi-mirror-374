"""Conversation history management dialog."""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
from datetime import datetime


class ConversationHistoryDialog:
    """Dialog for managing conversation history"""
    
    def __init__(self, parent, client):
        self.client = client
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Conversation History")
        self.dialog.geometry("800x600")
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.selected_conversation_id = None
        self.create_widgets()
        self.load_conversations()
        
    def create_widgets(self):
        """Create history dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - conversation list
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Label(left_frame, text="Conversations", font=("", 10, "bold")).pack(pady=5)
        
        # Search bar
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=5)
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_conversations)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Conversation list
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.conversation_tree = ttk.Treeview(list_frame, columns=("date", "model"), 
                                              show="tree headings", height=15)
        self.conversation_tree.heading("#0", text="Title")
        self.conversation_tree.heading("date", text="Last Updated")
        self.conversation_tree.heading("model", text="Model")
        self.conversation_tree.column("#0", width=200)
        self.conversation_tree.column("date", width=150)
        self.conversation_tree.column("model", width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.conversation_tree.yview)
        self.conversation_tree.configure(yscrollcommand=scrollbar.set)
        
        self.conversation_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.conversation_tree.bind("<<TreeviewSelect>>", self.on_conversation_select)
        self.conversation_tree.bind("<Double-Button-1>", self.load_conversation)
        
        # Action buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        buttons = [
            ("Load", self.load_conversation),
            ("Rename", self.rename_conversation),
            ("Delete", self.delete_conversation),
            ("Branch", self.branch_conversation)
        ]
        
        for text, command in buttons:
            ttk.Button(button_frame, text=text, command=command).pack(side=tk.LEFT, padx=2)
        
        # Right panel - preview and branch info
        right_frame = ttk.LabelFrame(main_frame, text="Preview", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Branch info panel
        branch_info_frame = ttk.Frame(right_frame)
        branch_info_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.branch_info_label = ttk.Label(branch_info_frame, text="", font=("", 8, "italic"))
        self.branch_info_label.pack()
        
        self.preview_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, 
                                                      width=40, height=25, state=tk.DISABLED)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
    def load_conversations(self):
        """Load conversations from database"""
        conversations = self.client.db_manager.get_conversations()
        for conv in conversations:
            try:
                date = datetime.fromisoformat(conv['updated_at']).strftime("%Y-%m-%d %H:%M")
            except:
                date = conv['updated_at']
            
            model_name = self.client.models.get(conv['model'], conv['model'])
            
            title = conv['title']
            if conv['branch_name']:
                title = f"🌿 {title} ({conv['branch_name']})"
            
            self.conversation_tree.insert("", tk.END, iid=conv['id'], 
                                         text=title, 
                                         values=(date, model_name))
            
    def filter_conversations(self, *args):
        """Filter conversations based on search text"""
        search_text = self.search_var.get().lower()
        for item in self.conversation_tree.get_children():
            title = self.conversation_tree.item(item, "text").lower()
            if search_text in title:
                self.conversation_tree.reattach(item, "", tk.END)
            else:
                self.conversation_tree.detach(item)
                
    def on_conversation_select(self, event):
        """Handle conversation selection"""
        selection = self.conversation_tree.selection()
        if selection:
            self.selected_conversation_id = selection[0]
            self.show_preview()
            
    def show_preview(self):
        """Show preview of selected conversation"""
        if not self.selected_conversation_id:
            return
            
        conversation = self.client.db_manager.get_conversation(self.selected_conversation_id)
        if not conversation:
            return
        
        # Update branch info
        branches = self.client.db_manager.get_conversation_branches(self.selected_conversation_id)
        if branches:
            self.branch_info_label.config(text=f"🌿 {len(branches)} branches available")
        else:
            # Check if this conversation IS a branch
            conv_info = self.client.db_manager.get_conversations()
            current_conv = next((c for c in conv_info if c['id'] == self.selected_conversation_id), None)
            if current_conv and current_conv.get('parent_id'):
                parent_branches = self.client.db_manager.get_conversation_branches(current_conv['parent_id'])
                self.branch_info_label.config(text=f"🌿 Branch of conversation (1 of {len(parent_branches) + 1})")
            else:
                self.branch_info_label.config(text="")
            
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete("1.0", tk.END)
        
        # Add conversation info
        self.preview_text.insert(tk.END, f"Model: {self.client.models.get(conversation['model'], conversation['model'])}\n")
        if conversation['system_prompt']:
            self.preview_text.insert(tk.END, f"System: {conversation['system_prompt'][:100]}...\n")
        self.preview_text.insert(tk.END, "\n" + "="*40 + "\n\n")
        
        # Add messages
        for msg in conversation['messages']:
            role = "You" if msg['role'] == "user" else "Claude"
            content = msg['content']
            if isinstance(content, list):
                content = content[0].get('text', '') if content else ''
            
            if len(content) > 200:
                content = content[:200] + "..."
                
            self.preview_text.insert(tk.END, f"{role}:\n{content}\n\n")
            
        self.preview_text.config(state=tk.DISABLED)
        
    def load_conversation(self, event=None):
        """Load selected conversation into main chat"""
        if not self.selected_conversation_id:
            return
            
        # Implementation would continue from original...
        messagebox.showinfo("Load", "Conversation loading functionality would be implemented here")
        
    def rename_conversation(self):
        """Rename selected conversation"""
        if not self.selected_conversation_id:
            return
            
        current_title = self.conversation_tree.item(self.selected_conversation_id, "text")
        new_title = simpledialog.askstring("Rename Conversation", 
                                          "Enter new title:", 
                                          initialvalue=current_title)
        if new_title:
            self.client.db_manager.update_conversation_title(self.selected_conversation_id, new_title)
            self.conversation_tree.item(self.selected_conversation_id, text=new_title)
            
    def delete_conversation(self):
        """Delete selected conversation"""
        if not self.selected_conversation_id:
            return
            
        if messagebox.askyesno("Delete Conversation", 
                               "Are you sure you want to delete this conversation?"):
            self.client.db_manager.delete_conversation(self.selected_conversation_id)
            self.conversation_tree.delete(self.selected_conversation_id)
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.config(state=tk.DISABLED)
            
    def branch_conversation(self):
        """Create a branch from selected conversation"""
        if not self.selected_conversation_id:
            return
            
        branch_name = simpledialog.askstring("Branch Conversation", 
                                            "Enter branch name:",
                                            initialvalue=f"Branch {len(self.client.db_manager.get_conversation_branches(self.selected_conversation_id)) + 1}")
        if branch_name:
            try:
                original_conv = self.client.db_manager.get_conversation(self.selected_conversation_id)
                if not original_conv:
                    messagebox.showerror("Error", "Could not load conversation")
                    return
                
                branch_id = self.client.db_manager.create_conversation(
                    f"{original_conv['title']} - {branch_name}",
                    original_conv['model'],
                    original_conv['system_prompt'],
                    original_conv['parameters'],
                    parent_id=self.selected_conversation_id,
                    branch_name=branch_name
                )
                
                for msg in original_conv['messages']:
                    self.client.db_manager.save_message(branch_id, msg['role'], msg['content'])
                
                messagebox.showinfo("Branch Created", f"Branch '{branch_name}' created successfully!")
                
                self.conversation_tree.delete(*self.conversation_tree.get_children())
                self.load_conversations()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create branch: {e}")