# TypeMaster Pro

TypeMaster Pro is an advanced terminal-based typing test suite written in Python. It features user management, session statistics, and persistent data storage using SQLite. The UI is rendered in the terminal using a double-buffer technique for smooth, flicker-free updates.

## Features
- User login, registration, and guest mode
- Typing test with WPM, accuracy, and error tracking
- Persistent statistics for registered users
- Leaderboard showing top users by best WPM
- Export statistics to JSON (admin only)
- Modern terminal UI (Windows and POSIX compatible)

## Technologies Used
- Python 3.7+
- SQLite (via `sqlite3`)
- Terminal input handling (`msvcrt` for Windows, `termios`/`tty` for POSIX)
- ANSI escape codes for UI rendering

## How It Works
- On launch, users can log in, register, or continue as guest.
- Typing tests present a random sentence; stats are tracked live.
- Registered users' stats are saved in `data/users.db`.
- Exported stats are saved as JSON in the user's home directory.

## Installation
Install TypeMaster Pro from PyPI:
```bash
pip install typemaster-pro
```

Or install from source:
```bash
git clone https://github.com/yourusername/typemaster-pro.git
cd typemaster-pro
pip install .
```

## Usage
Run the app:
```bash
typemaster
```

Or directly:
```bash
python -m typemaster_pro
```

## Features
- User login, registration, and guest mode
- Typing test with WPM, accuracy, and error tracking
- Persistent statistics for registered users
- Export statistics to JSON
- Modern terminal UI (Windows and POSIX compatible)

## Upcoming Features
- Colorful UI with true color support
- Multi-sentence and paragraph typing tests
- Online leaderboard integration
- Customizable test texts
- Sound feedback for errors and completion
- Mouse/touch support for compatible terminals

## File Overview
- `typemaster_pro.py`: Main application logic and UI
- `money-type.py`: (To be documented)
- `monkey-type.html`: (To be documented)
- `data/users.db`: SQLite database for user and stats

---

# Documentation for other files

## money-type.py
*Purpose*: (Add your typing logic, utilities, or alternate test modes here.)
*Tech*: Python 3.x
*How to use*: Import or run as a script. Extend with new typing exercises or utilities.
*Deployment*: Same as main app. No external dependencies.
*Upcoming*: Add advanced typing modes, analytics, or integration with main app.

## monkey-type.html
*Purpose*: (Web-based typing test or UI.)
*Tech*: HTML5, CSS, JavaScript (if present)
*How to use*: Open in a browser. Extend with interactive typing features.
*Deployment*: Static file; host on any web server or open locally.
*Upcoming*: Add live stats, connect to backend, improve UI/UX.

---

# Comments in Code
- All major classes and methods are documented with docstrings.
- Inline comments explain key logic, especially for input handling and buffer rendering.
- Database schema and queries are commented for clarity.

---

For questions or contributions, open an issue or contact the maintainer.
