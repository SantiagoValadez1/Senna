from typing import Literal
from pydantic import BaseModel, Field, field_validator

ANIO_MINIMO = 2018
ANIO_MAXIMO = 2026

class EventoCalendario(BaseModel):
    ronda: int
    nombre: str
    ubication: str

class PilotoSesion(BaseModel):
    numeroPiloto: int
    abreviatura: str
    nombreCompleto: str

class StintTelemetria(BaseModel):
    stint: int
    compuesto: str
    vueltas: list[int]
    tiemposVueltaSegundos: list[float]
    deltas: list[float]
    pendienteDegradacion: float

class RespuestaTelemetria(BaseModel):
    piloto: str
    stints: list[StintTelemetria]


class SolicitudEstrategia(BaseModel):
    anio: int = Field(ge=ANIO_MINIMO, le=ANIO_MAXIMO)
    numeroRonda: int = Field(ge=1, le=24)
    abreviaturaPiloto: str = Field(min_length=3, max_length=3)
    vueltaActual: int = Field(ge=1)
    vueltasTotales: int = Field(ge=1)
    compuestoActual: Literal["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]
    juegosRestantes: dict[str, int]

    @field_validator("vueltaActual")
    @classmethod
    def validarVueltaDentroDeRango(cls, valor, info):
        vueltasTotales = info.data.get("vueltasTotales")
        if vueltasTotales is not None and valor > vueltasTotales:
            raise ValueError("La vuelta actual no puede ser mayor que las vueltas totales.")
        return valor
    
class RecomendacionEstrategia(BaseModel):
    recommended_compound: Literal["SOFT", "MEDIUM", "HARD"]
    pit_window_laps: list[int] = Field(min_length=2, max_length=2)
    strategy_type: Literal["UNDERCUT", "OVERCUT", "TIRE_MANAGEMENT"]
    technical_rationale: str = Field(max_length=800)
    estimated_traffic_risk: Literal["LOW", "MEDIUM", "HIGH"]