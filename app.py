from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sqlite3
from crypto_service import CryptoService

app = Flask(__name__)
CORS(app)

# Inicializar servicio de cifrado (usará DB_ENCRYPTION_KEY desde config)
crypto = CryptoService()

UNAUTHORIZED_RESPONSE = {"error": "Unauthorized: Invalid or missing API key"}

def validate_api_key():
    api_key = request.headers.get("x-api-key")
    try:
        with open("/app/.secret", "r") as f:
            current_secret = f.read().strip()
    except FileNotFoundError:
        # Si el archivo no existe, usar la variable de entorno (valor inicial)
        current_secret = os.getenv("API_SECRET", "my-secret-api-key-123")
    if api_key != current_secret:
        return jsonify(UNAUTHORIZED_RESPONSE), 401
    return None

# ---------------------------
# Endpoints de autenticación (existentes)
# ---------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/api/data", methods=["GET"])
def get_data():
    auth_error = validate_api_key()
    if auth_error:
        return auth_error
    return jsonify({
        "message": "Protected data",
        "course": "Security Exercise",
        "status": "success",
    })

@app.route("/api/data", methods=["POST"])
def post_data():
    auth_error = validate_api_key()
    if auth_error:
        return auth_error
    return jsonify({"message": "POST received"})

# ---------------------------
# Nuevos endpoints de cifrado/descifrado (como en el banco)
# ---------------------------
def get_db():
    conn = sqlite3.connect(os.getenv("DATABASE_PATH", "bank.db"))
    conn.row_factory = sqlite3.Row
    return conn

# ========== NUEVO: Inicialización de la base de datos ==========
def init_db():
    """Crea la tabla 'secrets' si no existe."""
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            value_encrypted TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("Tabla 'secrets' verificada/creada correctamente.")

# Ejecutar la inicialización al cargar la app
init_db()

@app.route("/api/secrets", methods=["POST"])
def create_secret():
    auth_error = validate_api_key()
    if auth_error:
        return auth_error
    data = request.json
    name = data.get("name")
    value = data.get("value")
    if not name or not value:
        return jsonify({"error": "name and value required"}), 400

    encrypted = crypto.encrypt(value)
    conn = get_db()
    conn.execute(
        "INSERT INTO secrets (name, value_encrypted) VALUES (?, ?)",
        (name, encrypted)
    )
    conn.commit()
    last_id = conn.lastrowid
    conn.close()
    return jsonify({"message": "Secret stored", "id": last_id}), 201

@app.route("/api/secrets/<int:id>", methods=["GET"])
def get_secret(id):
    auth_error = validate_api_key()
    if auth_error:
        return auth_error
    conn = get_db()
    row = conn.execute("SELECT id, name, value_encrypted FROM secrets WHERE id = ?", (id,)).fetchone()
    conn.close() 
    if not row:
        return jsonify({"error": "Not found"}), 404
    decrypted = crypto.decrypt(row["value_encrypted"])
    return jsonify({
        "id": row["id"],
        "name": row["name"],
        "value": decrypted
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
