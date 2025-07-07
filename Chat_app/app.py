from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['DATABASE'] = 'chat.db'

socketio = SocketIO(app, cors_allowed_origins="*")

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Users table - just store active users by name
    c.execute('''CREATE TABLE IF NOT EXISTS active_users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE NOT NULL,
                 last_seen DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Groups table
    c.execute('''CREATE TABLE IF NOT EXISTS groups (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT UNIQUE NOT NULL,
                 created_by TEXT NOT NULL,
                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Messages table
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 sender TEXT NOT NULL,
                 group_id INTEGER NOT NULL,
                 content TEXT NOT NULL,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                 FOREIGN KEY (group_id) REFERENCES groups(id))''')
    
    # Personal messages table
    c.execute('''CREATE TABLE IF NOT EXISTS personal_messages (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 sender TEXT NOT NULL,
                 receiver TEXT NOT NULL,
                 content TEXT NOT NULL,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

def get_user_by_username(username):
    """Get user by username."""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM active_users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def create_user(username):
    """Create a new user."""
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO active_users (username) VALUES (?)', (username,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def update_user_last_seen(username):
    """Update user's last seen timestamp."""
    conn = get_db_connection()
    conn.execute('UPDATE active_users SET last_seen = CURRENT_TIMESTAMP WHERE username = ?', (username,))
    conn.commit()
    conn.close()

def get_all_users():
    """Get all active users."""
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM active_users ORDER BY username').fetchall()
    conn.close()
    return users

def get_groups():
    """Get all groups."""
    conn = get_db_connection()
    groups = conn.execute('SELECT * FROM groups ORDER BY name').fetchall()
    conn.close()
    return groups

def create_group(name, created_by):
    """Create a new group."""
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO groups (name, created_by) VALUES (?, ?)', (name, created_by))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_messages_for_group(group_id, limit=50):
    """Get messages for a specific group."""
    conn = get_db_connection()
    messages = conn.execute('''
        SELECT * FROM messages 
        WHERE group_id = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (group_id, limit)).fetchall()
    conn.close()
    return messages

def save_message(sender, group_id, content):
    """Save a new message."""
    conn = get_db_connection()
    conn.execute('INSERT INTO messages (sender, group_id, content) VALUES (?, ?, ?)', 
                (sender, group_id, content))
    conn.commit()
    conn.close()

def save_personal_message(sender, receiver, content):
    """Save a new personal message."""
    conn = get_db_connection()
    conn.execute('INSERT INTO personal_messages (sender, receiver, content) VALUES (?, ?, ?)', 
                (sender, receiver, content))
    conn.commit()
    conn.close()

def get_personal_messages(user1, user2, limit=50):
    """Get personal messages between two users."""
    conn = get_db_connection()
    messages = conn.execute('''
        SELECT * FROM personal_messages 
        WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (user1, user2, user2, user1, limit)).fetchall()
    conn.close()
    return messages

@app.route('/')
def index():
    """Main chat page."""
    if 'username' not in session:
        return render_template('enter_name.html')
    
    username = session['username']
    update_user_last_seen(username)
    
    users = get_all_users()
    groups = get_groups()
    
    return render_template('chat.html', username=username, users=users, groups=groups)

@app.route('/set_username', methods=['POST'])
def set_username():
    """Set username for the session."""
    username = request.form.get('username', '').strip()
    
    if not username or len(username) < 2:
        return jsonify({'success': False, 'message': 'Username must be at least 2 characters'})
    
    if len(username) > 20:
        return jsonify({'success': False, 'message': 'Username must be less than 20 characters'})
    
    # Create user if doesn't exist
    if not get_user_by_username(username):
        if not create_user(username):
            return jsonify({'success': False, 'message': 'Username already taken'})
    
    session['username'] = username
    return jsonify({'success': True})

@app.route('/api/groups')
def get_groups_api():
    """API endpoint to get all groups."""
    groups = get_groups()
    return jsonify([{'id': g['id'], 'name': g['name'], 'created_by': g['created_by']} for g in groups])

@app.route('/api/create_group', methods=['POST'])
def create_group_api():
    """API endpoint to create a new group."""
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    name = request.form.get('name', '').strip()
    if not name or len(name) < 3:
        return jsonify({'success': False, 'message': 'Group name must be at least 3 characters'})
    
    if len(name) > 30:
        return jsonify({'success': False, 'message': 'Group name must be less than 30 characters'})
    
    if create_group(name, session['username']):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Group name already exists'})

@app.route('/api/users')
def get_users_api():
    """API endpoint to get all online users (active in last 2 minutes)."""
    conn = get_db_connection()
    users = conn.execute('SELECT username, last_seen FROM active_users WHERE strftime("%s", "now") - strftime("%s", last_seen) < 120 ORDER BY username').fetchall()
    conn.close()
    return jsonify([{'username': u['username']} for u in users])

@app.route('/api/update_user_status', methods=['POST'])
def update_user_status():
    """Update user's last seen timestamp."""
    if 'username' in session:
        update_user_last_seen(session['username'])
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/messages/<int:group_id>')
def get_messages_api(group_id):
    """API endpoint to get messages for a group."""
    messages = get_messages_for_group(group_id)
    return jsonify([{
        'id': m['id'],
        'sender': m['sender'],
        'content': m['content'],
        'timestamp': m['timestamp']
    } for m in messages])

@app.route('/api/personal_messages/<username>')
def get_personal_messages_api(username):
    """API endpoint to get personal messages with a specific user."""
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'})
    
    current_user = session['username']
    messages = get_personal_messages(current_user, username)
    return jsonify([{
        'id': m['id'],
        'sender': m['sender'],
        'receiver': m['receiver'],
        'content': m['content'],
        'timestamp': m['timestamp']
    } for m in messages])

@app.route('/logout', methods=['POST'])
def logout():
    """Logout user."""
    session.clear()
    return jsonify({'success': True})

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print(f"Client disconnected: {request.sid}")

@socketio.on('join')
def on_join(data):
    """Join a chat room."""
    group_id = data.get('group_id')
    if group_id:
        room = f'group_{group_id}'
        join_room(room)
        print(f"User joined room: {room}")
        # Broadcast to all users in the room
        emit('status', {'msg': f'A user joined the room'}, room=room, include_self=False)

@socketio.on('leave')
def on_leave(data):
    """Leave a chat room."""
    group_id = data.get('group_id')
    if group_id:
        room = f'group_{group_id}'
        leave_room(room)
        print(f"User left room: {room}")
        # Broadcast to all users in the room
        emit('status', {'msg': f'A user left the room'}, room=room, include_self=False)

@socketio.on('send_message')
def handle_message(data):
    """Handle incoming message."""
    content = data.get('message', '').strip()
    group_id = data.get('group_id')
    
    if not content or not group_id:
        return
    
    # Get username from the client (since session might not be available in Socket.IO)
    username = data.get('username', 'Anonymous')
    
    # Save message to database
    save_message(username, group_id, content)
    
    # Create message object
    message_data = {
        'sender': username,
        'message': content,
        'timestamp': datetime.now().isoformat()
    }
    
    # Broadcast to all users in the room (including sender)
    room = f'group_{group_id}'
    emit('message', message_data, room=room)
    print(f"Message sent to room {room}: {username}: {content}")

@socketio.on('send_personal_message')
def handle_personal_message(data):
    """Handle incoming personal message."""
    content = data.get('message', '').strip()
    receiver = data.get('receiver')
    sender = data.get('username', 'Anonymous')
    
    if not content or not receiver:
        return
    
    # Save message to database
    save_personal_message(sender, receiver, content)
    
    # Create message object
    message_data = {
        'sender': sender,
        'receiver': receiver,
        'message': content,
        'timestamp': datetime.now().isoformat()
    }
    
    # Send to sender
    emit('personal_message', message_data)
    
    # Send to receiver if they're online
    room = f'user_{receiver}'
    emit('personal_message', message_data, room=room)
    print(f"Personal message sent: {sender} -> {receiver}: {content}")

@socketio.on('join_personal')
def on_join_personal(data):
    """Join personal chat room for receiving messages."""
    username = data.get('username')
    if username:
        room = f'user_{username}'
        join_room(room)
        print(f"User joined personal room: {room}")

if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)