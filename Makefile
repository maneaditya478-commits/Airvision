.PHONY: up down build logs backend frontend seed

up:
	docker compose up --build -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

celery:
	cd backend && celery -A app.tasks.celery_app worker --loglevel=info

celery-beat:
	cd backend && celery -A app.tasks.celery_app beat --loglevel=info

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install
