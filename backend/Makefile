run:
	uvicorn app.main:app --reload --port 8000

worker:
	rq worker eval

test:
	python tests/run_goldens.py

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-scale:
	docker compose up --scale worker=3 -d

eval:
	python eval/generate_cases.py && python eval/run_eval.py

lint:
	python -m flake8 app/ worker/ --max-line-length=100 --ignore=E501,W503 || true

