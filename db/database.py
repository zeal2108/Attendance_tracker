

def init_db(conn):
  c = conn.cursor()
  c.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id SERIAL PRIMARY KEY ,
        date TEXT,
        entry_time TEXT,
        exit_time TEXT,
        type TEXT, 
        parent_id INTEGER
       
    )
  ''')
  c.execute('CREATE INDEX IF NOT EXISTS idx_date ON attendance(date)')
  conn.commit()
  print("Database initialized")  # Debug message


# Insert entry time
def insert_entry(conn, date, entry_time, entry_type, parent_id = None):
    c = conn.cursor()
    c.execute('INSERT INTO attendance (date, entry_time, type, parent_id) VALUES (%s, %s, %s, %s)', (date, entry_time, entry_type, parent_id))
    conn.commit()
    print(f"Inserted entry for {date} at {entry_time}")# Debug message
    return c.lastrowid

# Update exit time
def update_exit(conn, entry_id, exit_time):
    c = conn.cursor()
    c.execute('UPDATE attendance SET exit_time = %s WHERE id = %s', (exit_time, entry_id))
    conn.commit()
    print(f"Updated exit for {entry_id} at {exit_time}")  # Debug message

# Fetch today's log
def fetch_today_log(conn, date):
    c = conn.cursor()
    c.execute('SELECT id, entry_time, exit_time, type, parent_id FROM attendance WHERE date = %s', (date,))
    return c.fetchall()

# Fetch all attendance records
def get_all_logs(conn, limit = 100):
    c = conn.cursor()
    c.execute('SELECT date, entry_time, exit_time, type FROM attendance ORDER BY date DESC LIMIT %s', (limit,))
    return c.fetchall()

def reset_db(conn):
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS attendance')
    init_db(conn)
    print("Database reset")