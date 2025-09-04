up:
	docker-compose up --build

down:
	docker-compose down

backend:
	docker-compose up --build backend

frontend:
	docker-compose up --build frontend

db:
	docker-compose up --build db

redis:
	docker-compose up --build redis

logs:
	docker-compose logs -f

prune:
	docker system prune -af

install-docker-compose:
	curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(shell uname -s)-$(shell uname -m)" -o /usr/local/bin/docker-compose
	chmod +x /usr/local/bin/docker-compose
	docker-compose --version
	@echo "Adding current user to docker group for permissions..."
	sudo usermod -aG docker $(USER)
	@echo "You may need to log out and log back in, or run 'newgrp docker' for group changes to take effect."

test:
	docker-compose run --rm backend python -m pytest tests/ -v

test-coverage:
	docker-compose run --rm backend python -m pytest tests/ -v --cov=backend --cov-report=html --cov-report=term-missing

test-integration:
	docker-compose run --rm backend python -m pytest tests/test_task_integration.py -v

test-endpoints:
	docker-compose run --rm backend python -m pytest tests/test_task_endpoints.py -v

test-watch:
	docker-compose run --rm backend python -m pytest tests/ -v --tb=short -f

update-db:
	docker-compose run --rm backend alembic upgrade head

db-shell:
	docker-compose exec db psql -U taskomatic -d taskomatic