"""Database manager for conversation history with branching support."""

import sqlite3
import json
import uuid
from typing import Optional, Dict, List, Any
from pathlib import Path


class DatabaseManager:
    """Manages SQLite database for conversation history with branching support"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Use platform-appropriate config directory
            import platform
            
            system = platform.system()
            if system == "Windows":
                base_dir = Path.home() / "AppData" / "Local" / "claude-api-desktop"
            elif system == "Darwin":  # macOS
                base_dir = Path.home() / "Library" / "Application Support" / "claude-api-desktop"
            else:  # Linux and others
                base_dir = Path.home() / ".local" / "share" / "claude-api-desktop"
            
            # Create directory if it doesn't exist
            base_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = str(base_dir / "conversations.db")
        else:
            self.db_path = db_path
            
        self.init_database()
        
    def init_database(self):
        """Initialize database with schema that supports branching"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Conversations table - supports branching
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    model TEXT,
                    system_prompt TEXT,
                    parameters TEXT,  -- JSON: temperature, top_p, stop_sequences
                    is_archived BOOLEAN DEFAULT 0,
                    parent_conversation_id TEXT,  -- For branching
                    branch_name TEXT,  -- Name of this branch
                    FOREIGN KEY (parent_conversation_id) REFERENCES conversations(id)
                )
            ''')
            
            # Messages table - supports branching
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,  -- JSON for complex content
                    parent_message_id TEXT,  -- For branching within conversation
                    branch_id TEXT,  -- Branch identifier
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    token_count INTEGER DEFAULT 0,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
                    FOREIGN KEY (parent_message_id) REFERENCES messages(id)
                )
            ''')
            
            # Indices for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_conv_updated ON conversations(updated_at DESC)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_msg_conv ON messages(conversation_id, created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_msg_branch ON messages(branch_id)')
            
            conn.commit()
    
    def create_conversation(self, title: str, model: str, system_prompt: str, 
                           parameters: dict, parent_id: Optional[str] = None, 
                           branch_name: Optional[str] = None) -> str:
        """Create a new conversation, optionally as a branch"""
        conv_id = str(uuid.uuid4())
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO conversations (id, title, model, system_prompt, parameters, 
                                         parent_conversation_id, branch_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (conv_id, title, model, system_prompt, json.dumps(parameters), 
                  parent_id, branch_name))
            conn.commit()
        return conv_id
    
    def save_message(self, conversation_id: str, role: str, content: Any, 
                    parent_message_id: Optional[str] = None, 
                    branch_id: Optional[str] = None) -> str:
        """Save a message to the conversation"""
        msg_id = str(uuid.uuid4())
        content_json = json.dumps(content) if not isinstance(content, str) else content
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (id, conversation_id, role, content, 
                                    parent_message_id, branch_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (msg_id, conversation_id, role, content_json, parent_message_id, branch_id))
            
            # Update conversation timestamp
            cursor.execute('''
                UPDATE conversations 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (conversation_id,))
            conn.commit()
        return msg_id
    
    def get_conversations(self, include_archived: bool = False) -> List[Dict]:
        """Get list of conversations"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = '''
                SELECT id, title, created_at, updated_at, model, 
                       parent_conversation_id, branch_name
                FROM conversations
                WHERE is_archived = 0 OR ?
                ORDER BY updated_at DESC
            '''
            cursor.execute(query, (include_archived,))
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append({
                    'id': row[0],
                    'title': row[1],
                    'created_at': row[2],
                    'updated_at': row[3],
                    'model': row[4],
                    'parent_id': row[5],
                    'branch_name': row[6]
                })
            return conversations
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Get a specific conversation with its messages"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get conversation details
            cursor.execute('''
                SELECT id, title, model, system_prompt, parameters
                FROM conversations
                WHERE id = ?
            ''', (conversation_id,))
            
            conv_row = cursor.fetchone()
            if not conv_row:
                return None
            
            # Get messages
            cursor.execute('''
                SELECT id, role, content, parent_message_id, branch_id
                FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at
            ''', (conversation_id,))
            
            messages = []
            for msg_row in cursor.fetchall():
                content = msg_row[2]
                try:
                    content = json.loads(content)
                except:
                    pass  # Keep as string if not JSON
                
                messages.append({
                    'id': msg_row[0],
                    'role': msg_row[1],
                    'content': content,
                    'parent_id': msg_row[3],
                    'branch_id': msg_row[4]
                })
            
            return {
                'id': conv_row[0],
                'title': conv_row[1],
                'model': conv_row[2],
                'system_prompt': conv_row[3],
                'parameters': json.loads(conv_row[4]) if conv_row[4] else {},
                'messages': messages
            }
    
    def update_conversation_title(self, conversation_id: str, title: str):
        """Update conversation title"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE conversations 
                SET title = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (title, conversation_id))
            conn.commit()
    
    def delete_conversation(self, conversation_id: str):
        """Delete a conversation and all its messages"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM conversations WHERE id = ?', (conversation_id,))
            conn.commit()
    
    def get_conversation_branches(self, conversation_id: str) -> List[Dict]:
        """Get all branches of a conversation"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, branch_name, created_at, updated_at
                FROM conversations
                WHERE parent_conversation_id = ?
                ORDER BY created_at
            ''', (conversation_id,))
            
            branches = []
            for row in cursor.fetchall():
                branches.append({
                    'id': row[0],
                    'title': row[1],
                    'branch_name': row[2],
                    'created_at': row[3],
                    'updated_at': row[4]
                })
            return branches
    
    def create_message_branch(self, message_id: str, new_content: str, role: str = "assistant") -> str:
        """Create a branch from a specific message"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get the original message
            cursor.execute('''
                SELECT conversation_id, parent_message_id, branch_id
                FROM messages WHERE id = ?
            ''', (message_id,))
            
            result = cursor.fetchone()
            if not result:
                raise ValueError("Message not found")
            
            conversation_id, parent_message_id, branch_id = result
            
            # Generate new branch ID
            new_branch_id = str(uuid.uuid4())
            
            # Create the branched message
            new_message_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO messages (id, conversation_id, role, content, 
                                    parent_message_id, branch_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (new_message_id, conversation_id, role, new_content, 
                  parent_message_id, new_branch_id))
            
            # Update conversation timestamp
            cursor.execute('''
                UPDATE conversations 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (conversation_id,))
            
            conn.commit()
            return new_message_id