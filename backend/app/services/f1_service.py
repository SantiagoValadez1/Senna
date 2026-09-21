import fastf1
import numpy as np
import pandas as pd
from pathlib import Path

from app.config import settings

Path(settings.cache_dir).mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(settings.cache_dir)


def obtenerCalendarioTemporada(anio: int) -> list[dict]:
    calendario = fastf1.get_event_schedule(anio, include_testing=False)
    return [
        {"ronda": int(fila.RoundNumber), "nombre": fila.EventName, "ubicacion": fila.Location}
        for _, fila in calendario.iterrows()
    ]


def obtenerPilotosSesion(anio: int, numeroRonda: int) -> list[dict]:
    sesion = fastf1.get_session(anio, numeroRonda, "R")
    sesion.load(telemetry=False, weather=False, messages=False)
    resultados = sesion.results
    return [
        {"numeroPiloto": str(fila.DriverNumber), "abreviatura": fila.Abbreviation, "nombreCompleto": fila.FullName}
        for _, fila in resultados.iterrows()
    ]


def _cargarSesion(anio: int, numeroRonda: int):
    sesion = fastf1.get_session(anio, numeroRonda, "R")
    sesion.load(telemetry=False, weather=False, messages=False)
    return sesion


def _limpiarVueltas(vueltas: pd.DataFrame) -> pd.DataFrame:
    """RF02 — descarta in-laps, out-laps y vueltas bajo VSC/SC/bandera amarilla."""
    limpias = vueltas[
        (vueltas["PitInTime"].isna())
        & (vueltas["PitOutTime"].isna())
        & (vueltas["TrackStatus"].astype(str).isin(["1"]))  # 1 = bandera verde
    ].copy()
    limpias["tiempoVueltaSegundos"] = limpias["LapTime"].dt.total_seconds()
    return limpias.dropna(subset=["tiempoVueltaSegundos"])


def analizarStint(anio: int, numeroRonda: int, abreviaturaPiloto: str) -> dict:
    sesion = _cargarSesion(anio, numeroRonda)
    vueltasPiloto = sesion.laps.pick_drivers(abreviaturaPiloto)
    vueltasLimpias = _limpiarVueltas(vueltasPiloto)

    stintsResultado = []
    for (idStint, compuesto), vueltasStint in vueltasLimpias.groupby(["Stint", "Compound"]):
        if len(vueltasStint) < 3:
            continue  # muy corto para regresión confiable

        x = vueltasStint["LapNumber"].to_numpy()
        y = vueltasStint["tiempoVueltaSegundos"].to_numpy()

        # RF03 — regresión lineal: pendiente = degradación (s/vuelta)
        pendiente, intercepto = np.polyfit(x, y, 1)

        # RF04 — delta respecto a la vuelta de referencia del stint
        tiempoReferencia = y[0]
        deltas = (y - tiempoReferencia).round(3).tolist()

        stintsResultado.append({
            "stint": int(idStint),
            "compuesto": compuesto,
            "vueltas": x.astype(int).tolist(),
            "tiemposVueltaSegundos": y.round(3).tolist(),
            "deltas": deltas,
            "pendienteDegradacion": round(float(pendiente), 4),
        })

    return {"piloto": abreviaturaPiloto, "stints": stintsResultado}