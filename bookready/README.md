# BookReady

BookReady is a full-stack reference implementation for preparing print-ready PDFs for book interiors and full spread covers. The project demonstrates a FastAPI backend, a Next.js/Tailwind frontend, background processing with RQ, and containerised infrastructure for local development.

## Features

- Create and manage book projects with trim size, bleed, paper type, and colour settings.
- Upload interior and cover PDFs directly to S3-compatible storage using pre-signed POST requests.
- Validate PDFs for page size, embedded fonts, crop marks, transparency, and spine calculations.
- Generate cover templates with bleed, trim, safe area, and barcode guides.
- Produce proof images using Poppler and provide downloadable reports in JSON and PDF form.
- Queue long-running fix/export jobs via Redis + RQ workers.
- Secure APIs with JWT authentication and ClamAV file scanning hooks.

## Quick Start

```bash
cp .env.example .env
cd infra
docker compose up --build
```

The frontend is available at http://localhost:3000 and proxies API traffic through the nginx container.

## Development

- Backend (FastAPI): `http://localhost:8000/docs`
- Frontend (Next.js App Router): `http://localhost:3000`
- Worker dashboard: use `rq info --url redis://localhost:6379/0` inside the backend container.

Run the unit tests locally:

```bash
cd bookready/backend
pip install -r requirements.txt
pytest -q
```

## Environment Variables

Refer to `.env.example` for all tunables, including S3/MinIO credentials and Redis connection URLs. The default compose stack provisions PostgreSQL, Redis, MinIO, and ClamAV.

## Project Structure

```
bookready/
  backend/        # FastAPI app + RQ worker
  frontend/       # Next.js/Tailwind UI
  infra/          # Dockerfiles and compose stack
```

Happy printing!
