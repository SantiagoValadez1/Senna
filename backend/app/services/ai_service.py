import json
from groq import Groq, APIError, APITimeoutError

from app.config import settings
from app.schemas import SolicitudEstrategia, RecomendacionEstrategia

UMBRAL_DEGRADACION_CRITICA = 0.12

clienteGroq = Groq(api_key=settings.groq_api_key)

PROMPT_MAESTRO = """Eres el estratega jefe de un equipo de Fórmula 1 analizando datos en tiempo real
desde el muro de boxes (Pit Wall). Evalúas ventanas de parada, riesgo de tráfico y tácticas
de undercut u overcut con base en la degradación de neumáticos, el compuesto actual y los
juegos disponibles.
Responde ÚNICAMENTE con un objeto JSON con estas claves exactas, sin texto adicional:
- recommended_compound: "SOFT" | "MEDIUM" | "HARD"
- pit_window_laps: [min, max]
- strategy_type: "UNDERCUT" | "OVERCUT" | "TIRE_MANAGEMENT"
- technical_rationale: justificación técnica de máximo 120 palabras
- estimated_traffic_risk: "LOW" | "MEDIUM" | "HIGH\""""

def _construirContextoCompacto(solicitud: SolicitudEstrategia, pendienteDegradacion: float) -> str:
    return json.dumps({
        "vueltaActual": solicitud.vueltaActual,
        "vueltasTotales": solicitud.vueltasTotales,
        "compuestoActual": solicitud.compuestoActual,
        "degradacionSVuelta": pendienteDegradacion,
        "juegosRestantes": solicitud.juegosRestantes,
    }, ensure_ascii=False)


def _fallbackHeuristico(pendienteDegradacion: float) -> RecomendacionEstrategia:
    """RF14 — regla determinística si Groq agota cuota o excede tiempo límite."""
    if pendienteDegradacion >= UMBRAL_DEGRADACION_CRITICA:
        return RecomendacionEstrategia(
            recommended_compound="MEDIUM",
            pit_window_laps=[1, 3],
            strategy_type="TIRE_MANAGEMENT",
            technical_rationale=(
                f"Degradación de {pendienteDegradacion:.3f} s/vuelta supera el umbral crítico "
                f"de {UMBRAL_DEGRADACION_CRITICA} s/vuelta. Parada recomendada por regla "
                "heurística determinística (servicio de IA no disponible)."
            ),
            estimated_traffic_risk="MEDIUM",
        )
    return RecomendacionEstrategia(
        recommended_compound="HARD",
        pit_window_laps=[3, 6],
        strategy_type="OVERCUT",
        technical_rationale=(
            f"Degradación de {pendienteDegradacion:.3f} s/vuelta dentro de rango aceptable. "
            "Se sugiere extender el stint (regla heurística determinística, servicio de IA no disponible)."
        ),
        estimated_traffic_risk="LOW",
    )

def consultarIngenieroEstratega(solicitud: SolicitudEstrategia, pendienteDegradacion: float) -> RecomendacionEstrategia:
    contexto = _construirContextoCompacto(solicitud, pendienteDegradacion)

    try:
        respuesta = clienteGroq.chat.completions.create(
            model="openai/gpt-oss-120b",
            response_format={"type": "json_object"},  # RF13 — modo JSON obligatorio
            timeout=5,
            messages=[
                {"role": "system", "content": PROMPT_MAESTRO},
                {"role": "user", "content": contexto},
            ],
        )
        contenido = respuesta.choices[0].message.content
        datos = json.loads(contenido)
        return RecomendacionEstrategia(**datos)

    except (APIError, APITimeoutError, json.JSONDecodeError, ValueError) as error:
        print(f"[ai_service] Groq no disponible, usando fallback: {error}")
        return _fallbackHeuristico(pendienteDegradacion)