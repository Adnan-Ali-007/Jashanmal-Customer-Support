"""Database module for persistent conversation storage"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

DB_PATH = Path("storage/chat.db")
DB_PATH.parent.mkdir(exist_ok=True)


class ConversationDB:
    """Manages conversation persistence in SQLite"""
    
    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT UNIQUE NOT NULL,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (thread_id) REFERENCES conversations(thread_id)
            )
        """)
        
        # Indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_thread 
            ON messages(thread_id, created_at)
        """)
        
        conn.commit()
        conn.close()
    
    def create_conversation(self, thread_id: str, title: str = "New Conversation") -> bool:
        """Create a new conversation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO conversations (thread_id, title) VALUES (?, ?)",
                (thread_id, title)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating conversation: {e}")
            return False
    
    def save_message(self, thread_id: str, role: str, content: str, metadata: Dict = None):
        """Save a message to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Ensure conversation exists
            self.create_conversation(thread_id)
            
            # Save message
            cursor.execute(
                """INSERT INTO messages (thread_id, role, content, metadata) 
                   VALUES (?, ?, ?, ?)""",
                (thread_id, role, content, json.dumps(metadata) if metadata else None)
            )
            
            # Update conversation timestamp
            cursor.execute(
                "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE thread_id = ?",
                (thread_id,)
            )
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving message: {e}")
    
    def get_messages(self, thread_id: str) -> List[Dict]:
        """Get all messages for a conversation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT role, content, metadata, created_at 
               FROM messages 
               WHERE thread_id = ? 
               ORDER BY created_at ASC""",
            (thread_id,)
        )
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                "role": row[0],
                "content": row[1],
                "metadata": json.loads(row[2]) if row[2] else {},
                "created_at": row[3]
            })
        
        conn.close()
        return messages
    
    def get_all_conversations(self) -> List[Dict]:
        """Get all conversations ordered by most recent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                c.thread_id, 
                c.title, 
                c.created_at, 
                c.updated_at,
                COUNT(m.id) as message_count
            FROM conversations c
            LEFT JOIN messages m ON c.thread_id = m.thread_id
            GROUP BY c.thread_id
            ORDER BY c.updated_at DESC
        """)
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                "thread_id": row[0],
                "title": row[1],
                "created_at": row[2],
                "updated_at": row[3],
                "message_count": row[4]
            })
        
        conn.close()
        return conversations
    
    def update_conversation_title(self, thread_id: str, title: str):
        """Update conversation title"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE conversations SET title = ? WHERE thread_id = ?",
            (title, thread_id)
        )
        conn.commit()
        conn.close()
    
    def delete_conversation(self, thread_id: str):
        """Delete a conversation and all its messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE thread_id = ?", (thread_id,))
        cursor.execute("DELETE FROM conversations WHERE thread_id = ?", (thread_id,))
        conn.commit()
        conn.close()
    
    def generate_title_from_first_message(self, thread_id: str) -> str:
        """Generate a title from the first user message"""
        messages = self.get_messages(thread_id)
        if messages:
            first_msg = messages[0]["content"]
            # Take first 50 chars as title
            title = first_msg[:50] + "..." if len(first_msg) > 50 else first_msg
            return title
        return "New Conversation"


# Singleton instance
_db = None

def get_db() -> ConversationDB:
    """Get or create database instance"""
    global _db
    if _db is None:
        _db = ConversationDB()
    return _db
