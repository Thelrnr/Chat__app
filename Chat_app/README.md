# Simple Chat App

A simple, lightweight chat application built with Flask and SocketIO. No registration or login required - just enter your name and start chatting!

## Features

- **No Registration Required**: Just enter your name to start chatting
- **Group Chat**: Create and join groups to chat with others
- **Real-time Messaging**: Instant message delivery using WebSockets
- **User List**: See who's currently online
- **Simple Interface**: Clean, modern UI

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and go to `http://localhost:5000`

## How to Use

1. Enter your name on the welcome page
2. Create a group or join an existing one
3. Start chatting with other users
4. Use the logout button to exit

## Technology Stack

- **Backend**: Flask, Flask-SocketIO
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **Real-time Communication**: WebSockets via SocketIO

## Project Structure

```
Chat_app/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   ├── enter_name.html # Welcome/name entry page
│   └── chat.html      # Main chat interface
└── chat.db            # SQLite database (created automatically)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

If you encounter any issues:
1. Check the troubleshooting section
2. Review browser console for errors
3. Ensure all dependencies are installed
4. Verify environment configuration

---

**Happy Chatting! 🎉** 