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
	docker-compose run --rm backend sh -c "PYTHONPATH=/app pip install pytest && PYTHONPATH=/app pytest tests $(path)"

update-db:
	docker-compose run --rm backend alembic upgrade head

db-shell:
	docker-compose exec db psql -U taskomatic -d taskomatic
