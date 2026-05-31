# AI Learning Path Generator

Run with `python main.py` and open http://127.0.0.1:5005.

## API endpoints
- `GET /health`
- `GET /api/courses`
- `POST /api/plans`
- `GET /api/plans`
- `GET /api/plans/<plan_id>`
- `POST /api/advice`

The optional AI advice endpoint requires `APIFREE_API_KEY` in the server environment. Never expose this key in frontend code or commit it to GitHub.
