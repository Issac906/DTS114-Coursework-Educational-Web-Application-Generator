import importlib.util
import pathlib


def load_app_module():
    app_path = pathlib.Path(__file__).resolve().parents[1] / "flask" / "main.py"
    spec = importlib.util.spec_from_file_location("generated_app", app_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_course_library_has_required_ai_courses():
    module = load_app_module()
    assert len(module.COURSES) >= 8
    assert "Machine Learning" in {course["title"] for course in module.COURSES}


def test_health_and_course_api():
    module = load_app_module()
    client = module.app.test_client()
    assert client.get("/health").status_code == 200
    assert client.get("/api/courses?level=Beginner").get_json()["count"] >= 1


def test_manual_plan_endpoint_saves_student_entries():
    module = load_app_module()
    client = module.app.test_client()
    response = client.post("/api/plans", json={
        "course_ids": ["ai-foundations", "machine-learning"],
        "student_profile": {"name": "Test Student", "goal": "learn AI engineering"},
        "manual_entries": [
            {"week": 1, "course_id": "ai-foundations", "hours": 3, "task": "Review AI concepts"},
            {"week": 2, "course_id": "machine-learning", "hours": 4, "task": "Practice classification"},
        ],
    })
    assert response.status_code == 201
    plan = response.get_json()["plan"]
    assert plan["total_planned_hours"] == 7
    assert len(plan["weekly_plan"]) == 2
    assert plan["weekly_plan"][0]["task"] == "Review AI concepts"


def test_ai_advice_endpoint_uses_selected_courses(monkeypatch):
    module = load_app_module()
    monkeypatch.setattr(module, "request_ai_advice", lambda profile, courses: f"Study {courses[0]['title']} first.")
    client = module.app.test_client()
    response = client.post("/api/advice", json={
        "course_ids": ["ai-foundations"],
        "student_profile": {"name": "Test Student", "goal": "start learning AI"},
    })
    assert response.status_code == 200
    assert response.get_json()["source"] == "APIFree API"
    assert "AI Foundations" in response.get_json()["advice"]


def test_ai_advice_endpoint_requires_course_selection():
    module = load_app_module()
    client = module.app.test_client()
    response = client.post("/api/advice", json={"course_ids": []})
    assert response.status_code == 400


def test_edgeone_function_exposes_serverless_api_routes():
    app_path = pathlib.Path(__file__).resolve().parents[1] / "cloud-functions" / "api" / "[[default]].py"
    spec = importlib.util.spec_from_file_location("edgeone_generated_app", app_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    client = module.app.test_client()
    assert client.get("/courses").get_json()["count"] >= 8
    assert client.post("/advice", json={"course_ids": []}).status_code == 400
