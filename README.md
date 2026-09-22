## Caché de datos

SENNA usa dos capas complementarias:

- FastF1 mantiene los archivos de sesión en `backend/cache/` y evita repetir descargas de red.
- `analizarStint` conserva en memoria el análisis ya procesado durante el proceso de la API, evitando reconstruir el DataFrame en consultas repetidas.

La primera capa reduce dependencia de la red; la segunda cumple el objetivo de consultas repetidas en menos de 400 ms.
