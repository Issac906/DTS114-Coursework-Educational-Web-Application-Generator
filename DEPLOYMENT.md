# Deployment and CI/CD Notes

## Local run
```bash
cd artifacts/app/flask
python main.py
```
Open http://127.0.0.1:5005.

## Docker deployment
```bash
cd artifacts/app
docker compose up --build
```

## CI/CD workflow
The generated workflow is saved at `artifacts/app/.github/workflows/ci.yml`.
It installs dependencies and runs pytest against the generated Flask app.

## Coursework screenshots
For Task 2, capture screenshots of commit history, deployed website, and CI/CD workflow results after pushing to GitHub.
