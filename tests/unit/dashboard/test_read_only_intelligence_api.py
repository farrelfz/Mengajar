from fastapi.testclient import TestClient
from app.web.server import app

def test_intelligence_api_exposes_no_mutating_authority_routes():
    client=TestClient(app)
    response=client.get("/api/intelligence/jobs")
    assert response.status_code==200
    methods=[route.methods for route in app.routes if getattr(route, "path", "").startswith("/api/intelligence")]
    assert all(methods_set <= {"GET"} for methods_set in methods)
    paths={route.path for route in app.routes}
    assert not any("force-export" in path or "override-quality" in path or "approve-export" in path for path in paths)

def test_intelligence_cockpit_is_available():
    assert TestClient(app).get("/intelligence").status_code==200
