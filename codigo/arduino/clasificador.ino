#include <Servo.h>

// --- Configuración de Pines ---
const int pinServo  = 9;
const int Trigger = 12;
const int Echo = 11;
const int pinRele = 6;

// Motor 1 (eje X)
const int stepM1 = 4;
const int dirM1  = 5;
const int enM1   = 10;

// Motor 2 (eje Y)
const int stepM2 = 2;
const int dirM2  = 3;
const int enM2   = 8;

// Pasos por mm
const float PASOS_POR_MM = 5.0;

// Distancias (en mm)
const int DIST_X_B  = 2500;   // mm de A a B (eje X)
const int DIST_X_C  = 2500;   // mm en X para llegar a la Y de C
const int DIST_Y_C  = 800;    // mm adicionales en Y para llegar a C

// Tiempos de espera
const int STEP_DELAY_US1  = 200;
const int STEP_DELAY_US2  = 550;
const int SERVO_90_MS     = 500;
const int PAUSA_DESTINO_MS = 1000;

// Velocidades servo
const int VEL_HORARIA   = 110;   // > 90 para sentido horario
const int VEL_STOP      = 91;    // Punto muerto
const int TIEMPO_GIRO_90 = 780;  // ms para lograr 90° exactos

// Distancia de detección del cubo (cm)
const int umbralDistancia = 30;

Servo miServo;

// ============================================================
// Mover motor genérico por nombre de eje
// ============================================================
void moverMotor(char motor, long pasos, bool adelante) {
  int pinStep, pinDir, pinEn;

  if (motor == 'X') {
    pinStep = stepM1; pinDir = dirM1; pinEn = enM1;
  } else {
    pinStep = stepM2; pinDir = dirM2; pinEn = enM2;
  }

  digitalWrite(pinEn, LOW);
  delay(5);
  digitalWrite(pinDir, adelante ? HIGH : LOW);
  delayMicroseconds(5);

  for (long i = 0; i < pasos; i++) {
    digitalWrite(pinStep, HIGH);
    delayMicroseconds(motor == 'X' ? STEP_DELAY_US1 : STEP_DELAY_US2);
    digitalWrite(pinStep, LOW);
    delayMicroseconds(motor == 'X' ? STEP_DELAY_US1 : STEP_DELAY_US2);
  }

  delay(10);
  digitalWrite(pinEn, HIGH);
}

// ============================================================
// Convertir mm a pasos
// ============================================================
long mmAPasos(float mm) {
  return (long)(mm * PASOS_POR_MM);
}

// ============================================================
// Girar cubo 90° con servo de rotación continua
// ============================================================
void girar90EnA() {
  miServo.write(VEL_HORARIA);
  delay(TIEMPO_GIRO_90);
  miServo.write(VEL_STOP);
  delay(200);
}

// ============================================================
// Movimientos a posiciones B y C
// ============================================================
void irAPosicionB() {
  moverMotor('X', mmAPasos(DIST_X_B), true);
  girar90EnA();
}

void irAPosicionC() {
  moverMotor('X', mmAPasos(DIST_X_C), true);
  delay(200);
  moverMotor('Y', mmAPasos(DIST_Y_C), true);
  girar90EnA();
}

void volverDesdeB() {
  moverMotor('X', mmAPasos(DIST_X_B), false);
}

void volverDesdeC() {
  moverMotor('Y', mmAPasos(DIST_Y_C), false);
  delay(200);
  moverMotor('X', mmAPasos(DIST_X_C), false);
}

// ============================================================
// Esperar a que el sensor HC-SR04 confirme cubo en posición A
// ============================================================
void esperarCuboEnA(int distanciaLimite) {
  long d = 999;
  while (d > distanciaLimite) {
    digitalWrite(Trigger, HIGH);
    delayMicroseconds(10);
    digitalWrite(Trigger, LOW);
    long t = pulseIn(Echo, HIGH);
    d = t / 59;
    delay(50);
  }
  delay(200);
}

// ============================================================
// Setup
// ============================================================
void setup() {
  Serial.begin(9600);
  while (!Serial) {}

  pinMode(pinRele, OUTPUT);
  pinMode(Trigger, OUTPUT);
  pinMode(Echo, INPUT);
  digitalWrite(Trigger, LOW);

  pinMode(stepM1, OUTPUT); pinMode(dirM1, OUTPUT); pinMode(enM1, OUTPUT);
  pinMode(stepM2, OUTPUT); pinMode(dirM2, OUTPUT); pinMode(enM2, OUTPUT);

  digitalWrite(enM1, HIGH);
  digitalWrite(enM2, HIGH);

  miServo.attach(pinServo);

  // Esperar cubo en A antes de arrancar
  esperarCuboEnA(umbralDistancia);

  // Avisar a HALCON que puede tomar la primera foto
  digitalWrite(pinRele, LOW);
  Serial.write('R');
}

// ============================================================
// Loop principal
// ============================================================
void loop() {
  if (Serial.available() > 0) {
    char dato = Serial.read();

    digitalWrite(pinRele, HIGH);

    if (dato == '1') {
      // CÍRCULO → Posición B
      irAPosicionB();
      delay(PAUSA_DESTINO_MS);
      volverDesdeB();
    }

    if (dato == '2') {
      // CUADRADO → Posición C
      irAPosicionC();
      delay(PAUSA_DESTINO_MS);
      volverDesdeC();
    }

    esperarCuboEnA(umbralDistancia);
    digitalWrite(pinRele, LOW);
    Serial.write('R');
  }
}
