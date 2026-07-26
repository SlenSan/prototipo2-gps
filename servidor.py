from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb+srv://srojas13_db_user:x7e53tZiX2kV3JAj@paseos-caninos.ucljfcn.mongodb.net/?appName=paseos-caninos")
db = client["paseos_caninos"]
coleccion = db["recorridos"]

@app.route("/guardar", methods=["POST"])
def guardar():
    try:
        raw = request.get_data(as_text=True)
        raw_limpio = raw.replace('\\"', '"')
        import json
        datos = json.loads(raw_limpio)
        datos["fecha_servidor"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        coleccion.insert_one(datos)
        return jsonify({"mensaje": "Guardado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/ultimo_recorrido", methods=["GET"])
def ultimo_recorrido():
    # Obtiene la fecha del último punto guardado
    ultimo = coleccion.find_one(sort=[("fecha_servidor", -1)])
    if not ultimo:
        return jsonify([]), 200
    
    fecha_ultimo = ultimo["fecha_servidor"][:10]  # solo dd/MM/yyyy
    
    # Trae todos los puntos de esa misma fecha
    puntos = list(coleccion.find(
        {}, {"_id": 0, "latitud": 1, "longitud": 1, "hora": 1}
    ).sort("hora", 1))
    
    return jsonify(puntos), 200

from flask import send_from_directory

@app.route("/mapa")
def mapa():
    return send_from_directory('.', 'mapa.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)