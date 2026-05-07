# Arduino — clasificador.ino

## Descripción

Controla todos los actuadores del sistema:
- **Motor paso a paso M1** (eje X): traslación A→B y A→C
- **Motor paso a paso M2** (eje Y): traslación lateral para llegar a C
- **Servo de rotación continua**: giro 90° del cubo en posición A
- **Sensor HC-SR04**: detección de presencia del cubo
- **Relé**: disparo de iluminación sincronizado con la cámara

## Pines

| Pin | Función |
|-----|---------|
| 9   | Servo (rotación continua) |
| 12  | Trigger HC-SR04 |
| 11  | Echo HC-SR04 |
| 6   | Relé |
| 4   | STEP Motor 1 (X) |
| 5   | DIR Motor 1 (X) |
| 10  | EN Motor 1 (X) |
| 2   | STEP Motor 2 (Y) |
| 3   | DIR Motor 2 (Y) |
| 8   | EN Motor 2 (Y) |

## Parámetros clave a ajustar

```cpp
const float PASOS_POR_MM = 5.0;      // Depende de tu mecánica
const int DIST_X_B  = 2500;           // mm de A a B
const int DIST_X_C  = 2500;           // mm en X para C
const int DIST_Y_C  = 800;            // mm en Y para C
const int TIEMPO_GIRO_90 = 780;       // ms para 90° exactos (calibrar)
const int umbralDistancia = 30;       // cm de detección del cubo
```

## Librerías necesarias

- `Servo.h` (incluida en Arduino IDE)
