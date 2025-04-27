

def init_db(conn):
  c = conn.cursor()
  c.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        entry_time TEXT,
        exit_time TEXT
    )
  ''')
  conn.commit()
  print("Database initialized")  # Debug message


# Insert entry time
def insert_entry(conn, date, entry_time):
    c = conn.cursor()
    c.execute('INSERT INTO attendance (date, entry_time) VALUES (?, ?)', (date, entry_time))
    conn.commit()
    print(f"Inserted entry for {date} at {entry_time}")  # Debug message

# Update exit time
def update_exit(conn, date, exit_time):
    c = conn.cursor()
    c.execute('UPDATE attendance SET exit_time = ? WHERE date = ?', (exit_time, date))
    conn.commit()
    print(f"Updated exit for {date} at {exit_time}")  # Debug message


# Fetch today's log
def get_today_log(conn, date):
    c = conn.cursor()
    c.execute('SELECT entry_time, exit_time FROM attendance WHERE date = ?', (date,))
    return c.fetchone()

# Fetch all attendance records
def get_all_logs(conn):
    c = conn.cursor()
    c.execute('SELECT date, entry_time, exit_time FROM attendance ORDER BY date DESC')
    return c.fetchall()

def reset_db(conn):
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS attendance')
    init_db(conn)
    print("Database reset")