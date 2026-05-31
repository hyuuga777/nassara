import os
import sys
from fastapi.testclient import TestClient

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"
    assert "Buscador" in response.json()["app"]

def test_profile():
    response = client.get("/api/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Dra. Nassara Mesquita"
    assert "Farmacêutica" in data["bio"]

def test_timeline():
    response = client.get("/api/timeline")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    # First item should be chronological (year 2026 since we sort descending)
    assert data[0]["year"] == 2026

def test_relevance():
    response = client.get("/api/relevance")
    assert response.status_code == 200
    data = response.json()
    assert data["total_timeline_items"] > 0
    assert data["total_courses"] > 0
    assert data["total_appearances"] > 0

if __name__ == "__main__":
    print("[TESTS] Iniciando bateria de testes rápidos da API...")
    try:
        test_root()
        print("  [PASS] Endpoint raiz '/' respondendo online.")
        test_profile()
        print("  [PASS] Endpoint '/api/profile' retornando perfil com sucesso.")
        test_timeline()
        print("  [PASS] Endpoint '/api/timeline' retornando itens em ordem decrescente.")
        test_relevance()
        print("  [PASS] Endpoint '/api/relevance' retornando métricas do Dashboard.")
        print("[TESTS] Todos os testes passaram com sucesso absoluto!")
    except AssertionError as e:
        print(f"  [FAIL] Teste falhou por asserção: {e}")
    except Exception as e:
        print(f"  [FAIL] Teste falhou por exceção: {e}")
