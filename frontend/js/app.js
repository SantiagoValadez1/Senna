const GRANDES_PREMIOS_2024 = [
  { ronda: 1, nombre: "Bahrain Grand Prix" },
];

let analisisActual = null;

async function inicializar() {
  poblarSelector("selectGranPremio", GRANDES_PREMIOS_2024.map((gp) => ({ valor: gp.ronda, texto: gp.nombre })));
  await cargarPilotos();
}

function poblarSelector(idSelector, opciones) {
  const selector = document.getElementById(idSelector);
  selector.innerHTML = "";
  opciones.forEach(({ valor, texto }) => {
    const opcion = document.createElement("option");
    opcion.value = valor;
    opcion.textContent = texto;
    selector.appendChild(opcion);
  });
}

async function cargarPilotos() {
  const anio = document.getElementById("selectAnio").value;
  const ronda = document.getElementById("selectGranPremio").value;
  const pilotos = await obtenerPilotos(anio, ronda);
  poblarSelector("selectPiloto", pilotos.map((p) => ({ valor: p.abreviatura, texto: p.nombreCompleto })));
}

async function analizarTelemetria() {
  const anio = document.getElementById("selectAnio").value;
  const ronda = document.getElementById("selectGranPremio").value;
  const piloto = document.getElementById("selectPiloto").value;

  const cargaGrafica = document.getElementById("cargaGrafica");
  cargaGrafica.classList.remove("oculto");

  try {
    analisisActual = await obtenerAnalisisStint(anio, ronda, piloto);
    renderizarGraficaDegradacion(analisisActual);
  } catch (error) {
    alert(`Error al analizar telemetría: ${error.message}`);
  } finally {
    cargaGrafica.classList.add("oculto");
  }
}

function encontrarStintDeVuelta(vueltaActual) {
  if (!analisisActual) return null;
  return analisisActual.stints.find((s) => s.vueltas.includes(vueltaActual)) || null;
}

async function consultarEstrategiaUI() {
  if (!analisisActual) {
    alert("Primero analiza la telemetría de una vuelta.");
    return;
  }

  const anio = Number(document.getElementById("selectAnio").value);
  const ronda = Number(document.getElementById("selectGranPremio").value);
  const piloto = document.getElementById("selectPiloto").value;
  const vueltaActual = Number(document.getElementById("inputVueltaActual").value);

  const stintActual = encontrarStintDeVuelta(vueltaActual);
  if (!stintActual) {
    alert("Esa vuelta no cae dentro de ningún stint analizado.");
    return;
  }

  const cargaEstrategia = document.getElementById("cargaEstrategia");
  const recomendacionDiv = document.getElementById("recomendacion");
  cargaEstrategia.classList.remove("oculto");
  recomendacionDiv.classList.add("oculto");

  try {
    const recomendacion = await consultarEstrategia({
      anio,
      numeroRonda: ronda,
      abreviaturaPiloto: piloto,
      vueltaActual,
      vueltasTotales: Math.max(...analisisActual.stints.flatMap((s) => s.vueltas)),
      compuestoActual: stintActual.compuesto,
      juegosRestantes: { SOFT: 1, MEDIUM: 2, HARD: 1 },
    });
    mostrarRecomendacion(recomendacion);
  } catch (error) {
    alert(`Error al consultar estrategia: ${error.message}`);
  } finally {
    cargaEstrategia.classList.add("oculto");
  }
}

function mostrarRecomendacion(recomendacion) {
  const badge = document.getElementById("badgeCompuesto");
  badge.textContent = recomendacion.recommended_compound;
  badge.style.backgroundColor = COLORES_COMPUESTO[recomendacion.recommended_compound] || "#ffffff";

  document.getElementById("ventanaParada").textContent =
    `Vueltas ${recomendacion.pit_window_laps[0]}–${recomendacion.pit_window_laps[1]}`;
  document.getElementById("tipoEstrategia").textContent = recomendacion.strategy_type;
  document.getElementById("riesgoTrafico").textContent = recomendacion.estimated_traffic_risk;
  document.getElementById("justificacionTecnica").textContent = recomendacion.technical_rationale;

  document.getElementById("recomendacion").classList.remove("oculto");
}

document.getElementById("selectGranPremio").addEventListener("change", cargarPilotos);
document.getElementById("btnAnalizar").addEventListener("click", analizarTelemetria);
document.getElementById("btnConsultarEstrategia").addEventListener("click", consultarEstrategiaUI);

inicializar();