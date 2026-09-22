let graficaActual = null;

function renderizarGraficaDegradacion(analisis) {
  const canvas = document.getElementById("graficaDegradacion");
  const contexto = canvas.getContext("2d");

  const datasets = analisis.stints.map((stint) => ({
    label: `Stint ${stint.stint} — ${stint.compuesto}`,
    data: stint.vueltas.map((vuelta, i) => ({ x: vuelta, y: stint.tiemposVueltaSegundos[i] })),
    borderColor: COLORES_COMPUESTO[stint.compuesto] || "#ffffff",
    backgroundColor: COLORES_COMPUESTO[stint.compuesto] || "#ffffff",
    tension: 0.2,
    pointRadius: 3,
  }));

  if (graficaActual) {
    graficaActual.destroy();
  }

  graficaActual = new Chart(contexto, {
    type: "line",
    data: { datasets },
    options: {
      responsive: true,
      animation: {
        duration: 800,
        easing: "easeOutQuart",
      },
      scales: {
        x: { type: "linear", title: { display: true, text: "Vuelta" }, ticks: { color: "#e6e6e6" } },
        y: { title: { display: true, text: "Tiempo de vuelta (s)" }, ticks: { color: "#e6e6e6" } },
      },
      plugins: {
        legend: { labels: { color: "#e6e6e6" } },
      },
    },
  });
}