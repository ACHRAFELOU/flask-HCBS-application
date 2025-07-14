from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)


# Initialiser la base de données locale SQLite
def init_db():
    conn = sqlite3.connect('temperature.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS temperatures 
                 (id INTEGER PRIMARY KEY, sensor1 REAL, sensor2 REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()


# Route pour recevoir les données des capteurs
@app.route('/temperature', methods=['POST'])
def receive_temperature():
    data = request.json
    sensor1 = data['sensor1']
    sensor2 = data['sensor2']

    conn = sqlite3.connect('temperature.db')
    c = conn.cursor()
    c.execute("INSERT INTO temperatures (sensor1, sensor2) VALUES (?, ?)", (sensor1, sensor2))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Données reçues'}), 200


# Route pour récupérer les données des capteurs
@app.route('/get_temperatures', methods=['GET'])
def get_temperatures():
    conn = sqlite3.connect('temperature.db')
    c = conn.cursor()
    c.execute("SELECT sensor1, sensor2 FROM temperatures")
    rows = c.fetchall()
    conn.close()

    return jsonify(rows)


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
