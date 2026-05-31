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
$env:APIFREE_API_KEY="your-key"  # PowerShell
docker compose up --build
```

For an online deployment platform, configure `APIFREE_API_KEY` as a server-side environment variable. Do not commit the key to GitHub.

## Render deployment
1. Push the generated `artifacts/app` repository to GitHub.
2. In Render, create a Web Service and connect the GitHub repository.
3. Select the Docker runtime. Render will build `docker/Dockerfile`.
4. Add `APIFREE_API_KEY` as a server-side environment variable.
5. Deploy and open the generated `onrender.com` URL.

## CI/CD workflow
The generated workflow is saved at `artifacts/app/.github/workflows/ci.yml`.
It installs dependencies, runs pytest against the generated Flask app, and verifies the Docker build.

## Coursework screenshots
For Task 2, capture screenshots of commit history, deployed website, and CI/CD workflow results after pushing to GitHub.
