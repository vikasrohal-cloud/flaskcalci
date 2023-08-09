from flask import Flask, request, jsonify, render_template
import sqlite3
from collections import deque

app = Flask(__name__)

# Maximum number of entries to keep in the database
MAX_ENTRIES = 5

# Creating sqlite
conn = sqlite3.connect('cal1.sqlite')
cur = conn.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS calculations (
        id INTEGER PRIMARY KEY,
        operation TEXT NOT NULL,
        expression TEXT NOT NULL,
        result REAL NOT NULL
    )
''')
conn.commit()

# Using deque to maintain the last 5 entries
last_entries = deque(maxlen=MAX_ENTRIES)

@app.route('/', methods=['GET'])
def home():
    return render_template('calcu.html')

# Endpoint for addition
@app.route('/api', methods=['POST'])
def solve():
    data = request.json

    result = eval(str(data['expression']))

    # Connect to DB
    conn = sqlite3.connect('cal1.sqlite')
    cur = conn.cursor()
    # Save in sqlite
    cur.execute('INSERT INTO calculations (operation, expression, result) VALUES (?, ?, ?)',
              ('add', data['expression'], result))
    conn.commit()

    # Update the last_entries queue
    last_entries.append({ 'operation':'add' ,'expression': data['expression'], 'result': result})

    return jsonify({'result': result})



@app.route('/history', methods=['GET'])
def history():
    return render_template('history.html')


# Endpoint to retrieve the last 5 entries
@app.route('/api/last_entries', methods=['GET'])
def get_last_entries():
    conn = sqlite3.connect('cal1.sqlite')
    cur = conn.cursor()
    cur.execute('SELECT * FROM calculations order by id desc limit 10 ')
    entries = cur.fetchall()

    entry_list = []
    for entry in entries:
        entry_dict = {
            'id': entry[0],
            'operation': entry[1],
            'expression': entry[2],
            'result': entry[3],

        }
        entry_list.append(entry_dict)

    return jsonify(entry_list)

if __name__ == '__main__':
    app.run(debug=True)
