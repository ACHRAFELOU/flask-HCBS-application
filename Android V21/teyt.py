from flask import Flask, render_template, jsonify, request
import serial
import serial.tools.list_ports

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('see.html')
# Liste des ports disponibles
@app.route('/api/ports', methods=['GET'])
def get_ports():
    ports = [port.device for port in serial.tools.list_ports.comports()]
    return jsonify(ports)


# Connexion à un port série
@app.route('/api/connect', methods=['POST'])
def connect_port():
    data = request.json
    port = data.get('port')

    try:
        # Ouvrir le port série
        ser = serial.Serial(port, 9600, timeout=1)
        return jsonify({"message": f"Connecté à {port}."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
