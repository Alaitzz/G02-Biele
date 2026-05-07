"""
servidor.py — Puente entre HALCON/Arduino y el dashboard web
=============================================================
Recibe eventos del clasificador (vía serial o fichero de log que
HALCON escribe) y los retransmite a los navegadores conectados
mediante WebSocket en tiempo real.

Instalación:
    pip install flask flask-socketio pyserial

Uso:
    python servidor.py

El servidor escucha en http://localhost:5000
Con ngrok: ngrok http 5000  →  URL pública para la demo
"""

import threading
import time
import serial
import serial.tools.list_ports
from datetime import datetime
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit

# ─── Configuración ────────────────────────────────────────────
SERIAL_PORT  = "COM3"      # Puerto Arduino (mismo que en HALCON)
BAUD_RATE    = 9600
DEMO_MODE    = True        # True → simula ciclos sin hardware real
DEMO_INTERVAL = 3.0        # segundos entre ciclos simulados

# ─── Flask + SocketIO ─────────────────────────────────────────
app = Flask(__name__, static_folder=".", template_folder=".")
app.config["SECRET_KEY"] = "g02-biele-2026"
socketio = SocketIO(app, cors_allowed_origins="*")

# ─── Estado global del sistema ────────────────────────────────
estado = {
    "ciclos_totales": 0,
    "circulos":       0,
    "cuadrados":      0,
    "ultimo_resultado": None,      # "circulo" | "cuadrado"
    "ultimo_timestamp": None,
    "estado_ciclo":  "esperando",  # esperando | capturando | moviendo | volviendo
    "conectado": False,
}

# ─── Rutas HTTP ───────────────────────────────────────────────
@app.route("/")
def index():
    return app.send_static_file("../web/index.html")

@app.route("/api/estado")
def api_estado():
    return jsonify(estado)

# ─── Emitir evento a todos los clientes web ───────────────────
def emitir_evento(tipo, datos=None):
    payload = {
        "tipo": tipo,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "estado": estado,
        **(datos or {})
    }
    socketio.emit("evento", payload)

# ─── Procesar un resultado de clasificación ───────────────────
def procesar_clasificacion(resultado: str):
    """
    resultado: "1" (círculo) o "2" (cuadrado)
    """
    estado["ciclos_totales"] += 1
    estado["ultimo_timestamp"] = datetime.now().strftime("%H:%M:%S")

    if resultado == "1":
        estado["circulos"] += 1
        estado["ultimo_resultado"] = "circulo"
        forma = "círculo"
        destino = "B"
    else:
        estado["cuadrados"] += 1
        estado["ultimo_resultado"] = "cuadrado"
        forma = "cuadrado"
        destino = "C"

    # Notificar captura
    estado["estado_ciclo"] = "capturando"
    emitir_evento("clasificacion", {"forma": forma, "destino": destino})

    # Simular fases del ciclo para el dashboard
    time.sleep(0.5)
    estado["estado_ciclo"] = "moviendo"
    emitir_evento("fase", {"fase": f"Moviendo a posición {destino}"})

    time.sleep(2.0)
    estado["estado_ciclo"] = "volviendo"
    emitir_evento("fase", {"fase": "Regresando a posición A"})

    time.sleep(1.5)
    estado["estado_ciclo"] = "esperando"
    emitir_evento("fase", {"fase": "Esperando siguiente cubo"})

# ─── Hilo: leer puerto serie real ─────────────────────────────
def hilo_serial():
    estado["conectado"] = False
    while True:
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            print(f"[Serial] Conectado a {SERIAL_PORT}")
            estado["conectado"] = True
            emitir_evento("conexion", {"mensaje": f"Arduino conectado en {SERIAL_PORT}"})

            while True:
                if ser.in_waiting:
                    byte = ser.read(1)
                    # Arduino manda 'R' cuando quiere foto; nosotros escuchamos
                    # lo que HALCON responde: '1' o '2'
                    char = byte.decode("ascii", errors="ignore")
                    if char in ("1", "2"):
                        procesar_clasificacion(char)

        except serial.SerialException as e:
            estado["conectado"] = False
            print(f"[Serial] Error: {e}. Reintentando en 3s...")
            emitir_evento("error", {"mensaje": "Arduino desconectado, reintentando..."})
            time.sleep(3)

# ─── Hilo: modo demo (sin hardware) ───────────────────────────
import random

def hilo_demo():
    print("[Demo] Modo demostración activo (sin hardware real)")
    time.sleep(2)  # espera a que el servidor arranque
    while True:
        resultado = random.choice(["1", "2"])
        procesar_clasificacion(resultado)
        time.sleep(DEMO_INTERVAL)

# ─── Eventos WebSocket ────────────────────────────────────────
@socketio.on("connect")
def on_connect():
    print("[WS] Cliente conectado")
    emit("estado_inicial", estado)

@socketio.on("disconnect")
def on_disconnect():
    print("[WS] Cliente desconectado")

# ─── Arranque ─────────────────────────────────────────────────
if __name__ == "__main__":
    hilo = threading.Thread(
        target=hilo_demo if DEMO_MODE else hilo_serial,
        daemon=True
    )
    hilo.start()

    print("=" * 50)
    print("  Dashboard G02 — Clasificación por Visión Artificial")
    print("  http://localhost:5000")
    print(f"  Modo: {'DEMO (simulado)' if DEMO_MODE else 'REAL (serial)'}")
    print("=" * 50)

    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
