"""Branch management dialog for conversation branching."""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime


class BranchDialog:
    """Dialog for managing conversation branches"""
    
    def __init__(self, parent, client):
        self.client = client
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Conversation Branching")
        self.dialog.geometry("600x400")
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.load_branch_info()
        
    def create_widgets(self):
        """Create branch dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Current conversation info
        info_frame = ttk.LabelFrame(main_frame, text="Current Conversation", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.current_info_label = ttk.Label(info_frame, text="")
        self.current_info_label.pack(anchor=tk.W)
        
        # Branch options
        options_frame = ttk.LabelFrame(main_frame, text="Branch Options", padding="10")
        options_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create new branch section
        create_frame = ttk.Frame(options_frame)
        create_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(create_frame, text="Create New Branch:", font=("", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        name_frame = ttk.Frame(create_frame)
        name_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(name_frame, text="Branch Name:").pack(side=tk.LEFT, padx=(0, 5))
        self.branch_name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.branch_name_var, width=30).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(name_frame, text="Create Branch", command=self.create_branch).pack(side=tk.LEFT)
        
        # Existing branches section
        if self.client.current_conversation_id:
            branches_frame = ttk.Frame(options_frame)
            branches_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(branches_frame, text="Existing Branches:", font=("", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
            
            # Branch list
            list_frame = ttk.Frame(branches_frame)
            list_frame.pack(fill=tk.BOTH, expand=True)
            
            self.branch_tree = ttk.Treeview(list_frame, columns=("date", "messages"), 
                                          show="tree headings", height=8)
            self.branch_tree.heading("#0", text="Branch Name")
            self.branch_tree.heading("date", text="Last Updated")
            self.branch_tree.heading("messages", text="Messages")
            self.branch_tree.column("#0", width=200)
            self.branch_tree.column("date", width=150)
            self.branch_tree.column("messages", width=80)
            
            scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.branch_tree.yview)
            self.branch_tree.configure(yscrollcommand=scrollbar.set)
            
            self.branch_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Branch action buttons
            branch_button_frame = ttk.Frame(branches_frame)
            branch_button_frame.pack(fill=tk.X, pady=(5, 0))
            
            ttk.Button(branch_button_frame, text="Switch to Branch", 
                      command=self.switch_to_branch).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(branch_button_frame, text="Delete Branch", 
                      command=self.delete_branch).pack(side=tk.LEFT, padx=(0, 5))
        
        # Dialog buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Close", command=self.dialog.destroy).pack(side=tk.RIGHT)
        
    def load_branch_info(self):
        """Load information about current conversation and branches"""
        if not self.client.current_conversation_id:
            self.current_info_label.config(text="No active conversation to branch from")
            return
            
        # Get current conversation info
        conversation = self.client.db_manager.get_conversation(self.client.current_conversation_id)
        if conversation:
            msg_count = len(conversation.get('messages', []))
            info_text = f"Current: {conversation['title']} ({msg_count} messages)"
            
            if conversation.get('branch_name'):
                info_text += f" - Branch: {conversation['branch_name']}"
                
            self.current_info_label.config(text=info_text)
            
        # Load existing branches
        if hasattr(self, 'branch_tree'):
            self.load_branches()
            
        # Set default branch name
        existing_branches = self.client.db_manager.get_conversation_branches(
            self.client.current_conversation_id
        ) if self.client.current_conversation_id else []
        default_name = f"Branch {len(existing_branches) + 1}"
        self.branch_name_var.set(default_name)
        
    def load_branches(self):
        """Load existing branches into the tree"""
        self.branch_tree.delete(*self.branch_tree.get_children())
        
        if not self.client.current_conversation_id:
            return
            
        branches = self.client.db_manager.get_conversation_branches(self.client.current_conversation_id)
        
        for branch in branches:
            try:
                date = datetime.fromisoformat(branch['updated_at']).strftime("%Y-%m-%d %H:%M")
            except:
                date = branch['updated_at']
                
            # Get message count for this branch
            branch_conv = self.client.db_manager.get_conversation(branch['id'])
            msg_count = len(branch_conv.get('messages', [])) if branch_conv else 0
            
            branch_name = branch.get('branch_name', f"Branch {branch['id']}")
            
            self.branch_tree.insert("", tk.END, iid=branch['id'],
                                   text=branch_name,
                                   values=(date, msg_count))
                                   
    def create_branch(self):
        """Create a new branch from current conversation"""
        if not self.client.current_conversation_id:
            messagebox.showerror("Error", "No active conversation to branch from")
            return
            
        branch_name = self.branch_name_var.get().strip()
        if not branch_name:
            messagebox.showerror("Error", "Please enter a branch name")
            return
            
        try:
            # Use the client's branching method
            self.client.branch_from_current(branch_name)
            messagebox.showinfo("Branch Created", f"Branch '{branch_name}' created successfully!")
            
            # Refresh the branch list
            if hasattr(self, 'branch_tree'):
                self.load_branches()
                
            # Update default name for next branch
            existing_branches = self.client.db_manager.get_conversation_branches(
                self.client.current_conversation_id
            )
            default_name = f"Branch {len(existing_branches) + 1}"
            self.branch_name_var.set(default_name)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create branch: {e}")
            
    def switch_to_branch(self):
        """Switch to selected branch"""
        selection = self.branch_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a branch to switch to")
            return
            
        branch_id = selection[0]
        
        try:
            # Load the branch conversation
            branch_conversation = self.client.db_manager.get_conversation(branch_id)
            if not branch_conversation:
                messagebox.showerror("Error", "Could not load branch conversation")
                return
                
            # Switch to the branch
            self.client.current_conversation_id = branch_id
            self.client.messages = branch_conversation['messages']
            self.client.system_prompt = branch_conversation['system_prompt']
            self.client.model = branch_conversation['model']
            
            # Update the UI
            self.client.display_messages()
            self.client.update_stats()
            
            messagebox.showinfo("Branch Switched", 
                              f"Switched to branch: {branch_conversation.get('branch_name', 'Unnamed')}")
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to switch to branch: {e}")
            
    def delete_branch(self):
        """Delete selected branch"""
        selection = self.branch_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a branch to delete")
            return
            
        branch_id = selection[0]
        branch_name = self.branch_tree.item(branch_id, "text")
        
        if messagebox.askyesno("Delete Branch", 
                              f"Are you sure you want to delete branch '{branch_name}'?\n\nThis cannot be undone."):
            try:
                self.client.db_manager.delete_conversation(branch_id)
                self.load_branches()
                messagebox.showinfo("Branch Deleted", f"Branch '{branch_name}' has been deleted")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete branch: {e}")