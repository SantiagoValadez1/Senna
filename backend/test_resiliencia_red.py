from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


cliente = TestClient(app)


def probarFalloFastF1():
    with patch(
        "app.services.f1_service.fastf1.get_session",
        side_effect=ConnectionError("Sin red simulada"),
    ):
        respuesta = cliente.get(
            "/api/telemetry/stint-analysis?anio=2024&ronda=1&piloto=VER"
        )
        print(f"Status: {respuesta.status_code}")
        print(respuesta.json())
        assert respuesta.status_code == 502, "Se esperaba 502 ante fallo de red"
        print("RF10/RNF04 cumplido: la API captura el fallo y responde 502")


if __name__ == "__main__":
    probarFalloFastF1()
