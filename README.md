# 👁 Clasificación de objetos por Visión Artificial

**Reto Making & Hacking 2025-26 · Grupo G02 · Biele Group · TECNUN**

Sistema automático de inspección y clasificación de piezas mediante visión artificial, capaz de distinguir piezas con pegatinas circulares (Ø28 mm) de piezas con pegatinas cuadradas (25×25 mm) y clasificarlas físicamente en menos de 30 segundos por ciclo.

---

## 🎯 El reto

Diseñar una máquina que inspeccione y clasifique cubos de 50×50×50 mm (PLA negro) usando una cámara fija. El sistema:

1. Detecta el cubo en posición A (sensor HC-SR04)
2. Captura imagen con cámara industrial GigE
3. Analiza la forma de la pegatina blanca (HALCON)
4. Mueve el cubo a posición **B** (círculo) o **C** (cuadrado)
5. Gira el cubo 90° y repite el ciclo de forma continua

---

## 🏗️ Arquitectura del sistema

```
┌─────────────────────────────────────────────────┐
│                  PC de control                  │
│                                                 │
│  ┌──────────┐  Serial   ┌──────────────────┐    │
│  │ Arduino  │◄─────────►│     HALCON       │    │
│  │          │   R/1/2   │  (visión art.)   │    │
│  │ Motores  │           └──────────────────┘    │
│  │ Servo    │                    │              │
│  │ Sensor   │           ┌──────────────────┐    │
│  └──────────┘           │ servidor.py      │    │
│                         │ Flask+WebSocket  │    │
└─────────────────────────┼──────────────────┘    
                          │ WebSocket
                    ┌─────▼──────┐
                    │ Dashboard  │
                    │   Web      │
                    │(tiempo real│
                    └────────────┘
```

### Protocolo de comunicación Arduino ↔ HALCON

| Byte | Quién lo manda | Significado |
|------|---------------|-------------|
| `R`  | Arduino       | Cubo listo, tomar foto |
| `1`  | HALCON        | Círculo detectado → ir a B |
| `2`  | HALCON        | Cuadrado detectado → ir a C |

---

## 📁 Estructura del repositorio

```
G02-clasificacion-vision-artificial/
├── codigo/
│   ├── arduino/
│   │   └── clasificador.ino      ← Control de motores, servo y sensor
│   └── halcon/
│       └── clasificador.hdev     ← Visión artificial (segmentación + decisión)
├── servidor/
│   ├── servidor.py               ← Puente Flask+WebSocket (Python)
│   └── requirements.txt
├── web/
│   └── index.html                ← Dashboard en tiempo real
├── docs/
│   └── esquema_electrico.png     ← (añadir)
└── README.md
```

---

## 🚀 Poner en marcha

### 1. Hardware (modo real)

Conectar Arduino al PC por USB. Verificar que el puerto coincide con `COM3` tanto en `clasificador.hdev` como en `servidor.py`.

### 2. Dashboard web (modo demo, sin hardware)

```bash
# Instalar dependencias
cd servidor
pip install -r requirements.txt

# Arrancar servidor (DEMO_MODE = True en servidor.py)
python servidor.py
```

Abrir http://localhost:5000 en el navegador.

### 3. Modo real (con Arduino + HALCON)

```python
# En servidor.py, cambiar:
DEMO_MODE = False
SERIAL_PORT = "COM3"   # ajustar al puerto real
```

Abrir `clasificador.hdev` en HALCON HDevelop y ejecutarlo. Después arrancar el servidor Python.

### 4. Exposición pública con ngrok

```bash
# En otra terminal, con el servidor corriendo:
ngrok http 5000
```

Compartir la URL `https://xxxx.ngrok.io` para que cualquiera vea el dashboard en directo.

---

## 🔩 Hardware utilizado

| Componente | Descripción |
|-----------|-------------|
| Arduino UNO | Microcontrolador principal |
| Motor paso a paso (×2) | Traslación ejes X e Y |
| Servo de rotación continua | Giro 90° del cubo |
| HC-SR04 | Sensor de distancia (detección cubo en A) |
| Cámara GigE MVCU01610GM | Captura de imagen (industrial) |
| Drivers A4988 | Control de motores paso a paso |
| Relé | Sincronización cámara–Arduino |

---

## 👁 Algoritmo de visión (HALCON)

1. **Captura** imagen en escala de grises desde cámara GigE
2. **Umbralización** automática (`bin_threshold`) para separar pegatina blanca del cubo negro
3. **Apertura morfológica** (radio 3.5 px) para eliminar ruido
4. **Selección de región** de mayor área
5. **Clasificación**: si `circularity > rectangularity` → círculo; si no → cuadrado

---

## 👥 Equipo

- Paula Amundarain
- Mikel Barrena
- Amara Echeverría
- Alaitz Iriarte
- Uxue Perkaz

---

## 🏢 Empresa colaboradora

**[Biele Group](https://www.biele.com/)** — especialistas en soluciones llave en mano para plantas de producción.
