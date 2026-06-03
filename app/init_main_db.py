import sqlite3

# Connect to SQLite database (it will be created if it doesn't exist)
conn = sqlite3.connect('fintrack.db')
cursor = conn.cursor()

# Create Users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
    User_id INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Email TEXT UNIQUE NOT NULL,
    Password_Hash TEXT NOT NULL
)
''')

# Create AI Insights table
cursor.execute('''
CREATE TABLE IF NOT EXISTS AI_Insights (
    Insight_id INTEGER PRIMARY KEY AUTOINCREMENT,
    User_id INTEGER,
    Insight_text TEXT NOT NULL,
    Created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (User_id) REFERENCES Users(User_id)
)
''')

# Create Transactions table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Transactions (
    Transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    User_id INTEGER,
    Amount DECIMAL NOT NULL,
    Transaction_type TEXT CHECK (Transaction_type IN ('income', 'expense')) NOT NULL,
    Transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Description TEXT,
    FOREIGN KEY (User_id) REFERENCES Users(User_id)
)
''')

# Commit and close
conn.commit()
conn.close()


print("Database initialized with custom schema.")
