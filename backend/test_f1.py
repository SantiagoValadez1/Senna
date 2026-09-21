from app.services.f1_service import analizarStint

if __name__ == "__main__":
    resultado = analizarStint(2024, 1, "VER")
    print(resultado)