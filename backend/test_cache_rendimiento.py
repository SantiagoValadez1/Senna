import time

from app.services.f1_service import analizarStint


if __name__ == "__main__":
    inicio = time.perf_counter()
    analizarStint(2024, 1, "VER")
    print(f"Primera llamada (puede usar red): {time.perf_counter() - inicio:.3f}s")

    inicio = time.perf_counter()
    analizarStint(2024, 1, "VER")
    duracion = time.perf_counter() - inicio
    print(f"Segunda llamada (debe ser caché): {duracion * 1000:.1f}ms")

    if duracion <= 0.4:
        print("RNF03 cumplido (<= 400ms)")
    else:
        print("RNF03 no cumplido")
