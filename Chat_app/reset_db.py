#!/usr/bin/env python3
"""
Database Reset Script
This script will delete the old database and create a new one with the correct schema
"""

import os
import sqlite3

def reset_database():
    """Delete old database and create new one with correct schema."""
    
    # Delete old database if it exists
    if os.path.exists('chat.db'):
        os.remove('chat.db')
        print("✓ Old database deleted")
    
    # Create new database with correct schema
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    
    # Users table - just store active users by name
    c.execute('''CREATE TABLE active_users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE NOT NULL,
                 last_seen DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Groups table
    c.execute('''CREATE TABLE groups (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT UNIQUE NOT NULL,
                 created_by TEXT NOT NULL,
                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Messages table with correct schema
    c.execute('''CREATE TABLE messages (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 sender TEXT NOT NULL,
                 group_id INTEGER NOT NULL,
                 content TEXT NOT NULL,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                 FOREIGN KEY (group_id) REFERENCES groups(id))''')
    
    conn.commit()
    conn.close()
    
    print("✓ New database created with correct schema")
    print("✓ Tables created:")
    print("  - active_users (id, username, last_seen)")
    print("  - groups (id, name, created_by, created_at)")
    print("  - messages (id, sender, group_id, content, timestamp)")

if __name__ == '__main__':
    print("🔄 Resetting database...")
    reset_database()
    print("✅ Database reset complete!") 