from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.schemas import (
    EventoCalendario, PilotoSesion, 
    RespuestaTelemetria, SolicitudEstrategia, 
    RecomendacionEstrategia,
)
from app.services import f1_service, ai_service

app = FastAPI( title = "SENNA - Strategy Engine for Next-stop Navigation & Analysis")

app.add_middleware(
    CORSMiddleware,
    allow_origins = settings.allowed_origins,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

#Manejo global de exepciones para fallos de red externos
@app.exception_handler(ConnectionError)
async def manejarErrorConexion(request, exc):
    return JSONResponse(
        status_code=502,
        content={"detail": "No se pudo conectar con con el proveedor de datos externo"})

@app.exception_handler(TimeoutError)
async def manejarTimeout(request, exc):
    return JSONResponse(
        status_code=503,
        content={"detail": "El proveedor de datos externo tardó demaciado en responder"})

@app.get("/api/schedule/{anio}", response_model=list[EventoCalendario])
async def obtenerCalendario(anio: int):
    try:
        return f1_service.obtenerCalendarioTemporada(anio)
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Error al obtener el calendario: {error}")

@app.get("/api/session/{anio}/{ronda}/drivers", response_model=list[PilotoSesion])
async def obtenerPilotos(anio: int, ronda: int):
    try:
        return f1_service.obtenerPilotosSesion(anio, ronda)
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Error al obtener los pilotos: {error}")

@app.get("/api/telemetry/stint-analysis", response_model=RespuestaTelemetria)
async def obtenerAnalisisStint(anio: int, ronda: int, piloto: str):
    try:
        return f1_service.analizarStint(anio, ronda, piloto)
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Error al analizar la telemetría: {error}")

@app.post("/api/strategy/consult-engineer", response_model=RecomendacionEstrategia)
async def consultarEstratega(solicitud: SolicitudEstrategia):
    try:
        analisis = f1_service.analizarStint(solicitud.anio, solicitud.numeroRonda, solicitud.abreviaturaPiloto)
        stintActual = next((s for s in analisis["stints"] if solicitud.vueltaActual in s["vueltas"]), None)
        pendiente = stintActual["pendienteDegradacion"] if stintActual else 0.0
        return ai_service.consultarIngenieroEstratega(solicitud, pendiente)
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Error al generar recomendación: {error}")