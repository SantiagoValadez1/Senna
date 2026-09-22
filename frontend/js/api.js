async function obtenerCalendario(anio) {
  const respuesta = await fetch(`${API_BASE_URL}/api/schedule/${anio}`);
  if (!respuesta.ok) throw new Error("No se pudo obtener el calendario");
  return respuesta.json();
}

async function obtenerPilotos(anio, ronda) {
  const respuesta = await fetch(`${API_BASE_URL}/api/session/${anio}/${ronda}/drivers`);
  if (!respuesta.ok) throw new Error("No se pudieron obtener los pilotos");
  return respuesta.json();
}

async function obtenerAnalisisStint(anio, ronda, piloto) {
  const parametros = new URLSearchParams({ anio, ronda, piloto });
  const respuesta = await fetch(`${API_BASE_URL}/api/telemetry/stint-analysis?${parametros}`);
  if (!respuesta.ok) throw new Error("No se pudo analizar la telemetría");
  return respuesta.json();
}

async function consultarEstrategia(solicitud) {
  const respuesta = await fetch(`${API_BASE_URL}/api/strategy/consult-engineer`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(solicitud),
  });
  if (!respuesta.ok) throw new Error("No se pudo generar la recomendación");
  return respuesta.json();
}