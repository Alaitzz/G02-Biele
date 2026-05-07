# HALCON — clasificador.hdev

## Descripción

Script HDevelop para inspección y clasificación de piezas por visión artificial.

## Requisitos

- HALCON 21+ con licencia HDevelop
- Cámara GigE Vision compatible (modelo: MVCU01610GM)
- Arduino conectado en `COM3` a 9600 baud

## Cambiar puerto serie o cámara

```hdevelop
* Puerto serie:
open_serial ('COM3', SerialHandle)   ← cambiar COM3 por el puerto real

* Cámara (identificador del dispositivo):
open_framegrabber (..., '34bd200dd39c_GEV_MVCU01610GM', ...)   ← cambiar por tu cámara
```

Para listar las cámaras GigE disponibles en tu PC:
```hdevelop
info_framegrabber ('GigEVision2', 'device', Info, DeviceList)
```

## Lógica de clasificación

| Condición | Resultado | Byte enviado |
|-----------|-----------|-------------|
| `circularity > rectangularity` | Círculo | `1` |
| `rectangularity >= circularity` | Cuadrado | `2` |

Los valores de `circularity` y `rectangularity` están normalizados entre 0 y 1.
Un círculo perfecto tiene `circularity = 1`; un cuadrado perfecto tiene `rectangularity = 1`.
