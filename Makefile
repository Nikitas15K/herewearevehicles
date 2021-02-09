install-deps:
	pip install -r requirements.txt

build-img:
	docker build -f Dockerfile .

compose-up:
	docker-compose up -d --build

compose-down:
	docker-compose down -v

make-migration:
	docker-compose exec server alembic revision -m "$(m)"

migrate:
	docker-compose exec server alembic upgrade head

rollback:
	docker-compose exec server alembic downgrade base

pipeline-step-tests:
	docker-compose run server pytest -v