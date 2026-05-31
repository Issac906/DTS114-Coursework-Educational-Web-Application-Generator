import json
import os
import sys
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def load_env_file():
    candidates = [PROJECT_ROOT / ".env", Path.cwd() / ".env"]
    candidates.extend(parent / ".env" for parent in PROJECT_ROOT.parents)
    env_path = next((path for path in candidates if path.exists()), None)
    if not env_path:
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env_file()
app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app)

COURSES = [
    {
        "id": "ai-foundations",
        "title": "AI Foundations",
        "level": "Beginner",
        "weeks": 2,
        "hours_per_week": 4,
        "category": "Core AI",
        "description": "AI history, core vocabulary, search, knowledge representation, and modern AI use cases.",
        "skills": [
            "AI vocabulary",
            "problem framing",
            "search"
        ]
    },
    {
        "id": "python-data",
        "title": "Python for Data and AI",
        "level": "Beginner",
        "weeks": 3,
        "hours_per_week": 5,
        "category": "Programming",
        "description": "Python, NumPy, pandas, notebooks, data cleaning, and reproducible experiments.",
        "skills": [
            "Python",
            "pandas",
            "notebooks"
        ]
    },
    {
        "id": "statistics-ml",
        "title": "Statistics for Machine Learning",
        "level": "Beginner",
        "weeks": 3,
        "hours_per_week": 4,
        "category": "Mathematics",
        "description": "Probability, distributions, hypothesis testing, correlation, and evaluation basics.",
        "skills": [
            "probability",
            "evaluation",
            "experiments"
        ]
    },
    {
        "id": "machine-learning",
        "title": "Machine Learning",
        "level": "Intermediate",
        "weeks": 4,
        "hours_per_week": 6,
        "category": "Core AI",
        "description": "Supervised and unsupervised learning, regression, classification, trees, and validation.",
        "skills": [
            "classification",
            "regression",
            "validation"
        ]
    },
    {
        "id": "deep-learning",
        "title": "Deep Learning",
        "level": "Intermediate",
        "weeks": 4,
        "hours_per_week": 6,
        "category": "Core AI",
        "description": "Neural networks, optimization, CNNs, RNNs, transformers, and training workflows.",
        "skills": [
            "neural networks",
            "optimization",
            "transformers"
        ]
    },
    {
        "id": "nlp-llms",
        "title": "Natural Language Processing and LLMs",
        "level": "Intermediate",
        "weeks": 4,
        "hours_per_week": 5,
        "category": "Language AI",
        "description": "Text processing, embeddings, transformers, prompting, retrieval, and LLM apps.",
        "skills": [
            "NLP",
            "embeddings",
            "RAG"
        ]
    },
    {
        "id": "computer-vision",
        "title": "Computer Vision",
        "level": "Intermediate",
        "weeks": 3,
        "hours_per_week": 5,
        "category": "Vision AI",
        "description": "Image classification, object detection, segmentation, and responsible visual AI.",
        "skills": [
            "image models",
            "detection",
            "segmentation"
        ]
    },
    {
        "id": "generative-ai",
        "title": "Generative AI Product Studio",
        "level": "Advanced",
        "weeks": 3,
        "hours_per_week": 6,
        "category": "Applied AI",
        "description": "Prompt design, tool use, evaluation, safety, and user-centered AI product workflows.",
        "skills": [
            "product design",
            "evaluation",
            "AI safety"
        ]
    },
    {
        "id": "mlops",
        "title": "MLOps and Deployment",
        "level": "Advanced",
        "weeks": 4,
        "hours_per_week": 5,
        "category": "Engineering",
        "description": "Experiment tracking, APIs, containers, monitoring, model serving, and delivery.",
        "skills": [
            "Flask APIs",
            "Docker",
            "monitoring"
        ]
    },
    {
        "id": "responsible-ai",
        "title": "Responsible AI and Ethics",
        "level": "All Levels",
        "weeks": 2,
        "hours_per_week": 3,
        "category": "Governance",
        "description": "Bias, privacy, transparency, explainability, risk controls, and AI governance.",
        "skills": [
            "ethics",
            "bias analysis",
            "governance"
        ]
    }
]
PLANS = []
ADVICE_MODEL = os.getenv("APIFREE_TEXT_MODEL", "openai/gpt-5.2")


def selected_courses(course_ids):
    lookup = {course["id"]: course for course in COURSES}
    return [lookup[cid] for cid in course_ids if cid in lookup]


def build_plan_payload(student_profile, course_ids, manual_entries):
    courses = selected_courses(course_ids)
    lookup = {course["id"]: course for course in courses}
    weekly_plan = []
    for entry in manual_entries:
        course = lookup.get(entry.get("course_id"))
        if not course:
            continue
        weekly_plan.append({
            "week": max(1, int(entry.get("week") or 1)),
            "course_id": course["id"],
            "title": course["title"],
            "hours": max(1, int(entry.get("hours") or 1)),
            "task": str(entry.get("task") or "Study selected course content.").strip(),
        })
    weekly_plan.sort(key=lambda item: (item["week"], item["title"]))
    return {
        "id": str(uuid.uuid4())[:8],
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "student_profile": student_profile,
        "courses": courses,
        "total_planned_hours": sum(item["hours"] for item in weekly_plan),
        "weekly_plan": weekly_plan,
    }


def request_ai_advice(student_profile, courses):
    api_key = os.getenv("APIFREE_API_KEY")
    if not api_key:
        raise RuntimeError("APIFREE_API_KEY is not configured on the server")
    course_summary = "\n".join(
        f"- {course['title']} ({course['level']}, {course['weeks']} weeks): {course['description']}"
        for course in courses
    )
    prompt = f"""You are an academic advisor for AI education.
Create a concise study-plan suggestion for the learner below.
Use only the selected courses. Recommend a sensible order and practical weekly focus.
The suggestion is advisory: remind the learner to adjust it to their available time.

Learner name: {student_profile.get("name") or "Student"}
Learner goal: {student_profile.get("goal") or "Build AI knowledge"}
Selected courses:
{course_summary}
"""
    base_url = os.getenv("APIFREE_API_BASE", "https://api.apifree.ai").rstrip("/")
    payload = {
        "model": ADVICE_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 1200,
    }
    req = urllib.request.Request(
        f"{base_url}/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        data = json.loads(response.read().decode("utf-8"))
    choices = data.get("choices") or data.get("resp_data", {}).get("choices") or []
    content = choices[0].get("message", {}).get("content", "") if choices else ""
    if isinstance(content, list):
        content = "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content)
    if not str(content).strip():
        raise RuntimeError("APIFree returned an empty AI suggestion")
    return str(content).strip()


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "ai-learning-path-generator"})


@app.get("/api/courses")
def list_courses():
    level = request.args.get("level", "").lower()
    category = request.args.get("category", "").lower()
    courses = COURSES
    if level:
        courses = [course for course in courses if course["level"].lower() == level]
    if category:
        courses = [course for course in courses if course["category"].lower() == category]
    return jsonify({"courses": courses, "count": len(courses)})


@app.post("/api/plans")
def create_plan():
    data = request.get_json(silent=True) or {}
    profile = data.get("student_profile") or {}
    course_ids = data.get("course_ids") or []
    manual_entries = data.get("manual_entries") or []
    if not isinstance(course_ids, list) or not course_ids:
        return jsonify({"error": "course_ids must be a non-empty list"}), 400
    if not isinstance(manual_entries, list) or not manual_entries:
        return jsonify({"error": "add at least one manual study-plan item"}), 400
    courses = selected_courses(course_ids)
    if not courses:
        return jsonify({"error": "no valid course ids were provided"}), 400
    plan = build_plan_payload(profile, [course["id"] for course in courses], manual_entries)
    if not plan["weekly_plan"]:
        return jsonify({"error": "manual plan items must use selected courses"}), 400
    PLANS.append(plan)
    return jsonify({"plan": plan}), 201


@app.get("/api/plans")
def list_plans():
    return jsonify({"plans": PLANS, "count": len(PLANS)})


@app.get("/api/plans/<plan_id>")
def get_plan(plan_id):
    plan = next((item for item in PLANS if item["id"] == plan_id), None)
    if not plan:
        return jsonify({"error": "plan not found"}), 404
    return jsonify({"plan": plan})


@app.post("/api/advice")
def create_ai_advice():
    data = request.get_json(silent=True) or {}
    profile = data.get("student_profile") or {}
    course_ids = data.get("course_ids") or []
    if not isinstance(course_ids, list) or not course_ids:
        return jsonify({"error": "select at least one course before requesting AI advice"}), 400
    courses = selected_courses(course_ids)
    if not courses:
        return jsonify({"error": "no valid course ids were provided"}), 400
    try:
        advice = request_ai_advice(profile, courses)
    except Exception as exc:
        return jsonify({"error": f"AI advice is temporarily unavailable: {exc}"}), 503
    return jsonify({"advice": advice, "model": ADVICE_MODEL, "source": "APIFree API"})


@app.get("/")
def index():
    return send_from_directory(".", "index.html")


@app.get("/<path:filename>")
def serve_static_file(filename):
    return send_from_directory(".", filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5005")), debug=False)
