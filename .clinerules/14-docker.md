# Docker Compose Rules

## Purpose
Docker Compose orchestrates all services in the NewsMill project: Queue (RabbitMQ), Database (PostgreSQL), Monitor (FastAPI), and Worker (FastStream).

## Service Definitions
- Define all services in `docker-compose.yml` at the project root.
- Services to include:
  - **queue** — RabbitMQ message broker (image: `rabbitmq:4-management`)
  - **db** — PostgreSQL database (image: `postgres:17`)
  - **monitor** — FastAPI application (Monitor service)
  - **worker** — FastStream application (Worker service)

## Queue Service
- Use `rabbitmq:4-management` image.
- Expose ports: `5672:5672` (AMQP), `15672:15672` (management UI).
- Set environment variables: `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS`.
- Use a named volume for persistent data (optional).

## Database Service
- Use `postgres:17` image.
- Expose port: `5432:5432` (or omit for internal-only access).
- Set environment variables: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`.
- Use a named volume for persistent data storage.

## Monitor Service
- Build from the project root (or a `monitor/` subdirectory if structured that way).
- Dependencies: `depends_on` — queue, db.
- Expose port: `8000:8000` for the FastAPI HTTP server.
- Mount `.env` file or pass environment variables for configuration.
- Command: `uvicorn src.app:app --host 0.0.0.0 --port 8000`

## Worker Service
- Build from the project root (or a `worker/` subdirectory).
- Dependencies: `depends_on` — queue, db.
- Do not expose any ports (internal-only consumer).
- Mount `.env` file or pass environment variables.
- Command: `python -m src.worker` (or equivalent FastStream run command).

## Networking
- Use a custom network (e.g., `newsmill-network`) for inter-service communication.
- All services should be on the same network.
- Use service names as hostnames for connection (e.g., `queue`, `db`).

## Volumes
- Use named volumes for PostgreSQL data persistence.
- Use named volumes for RabbitMQ data persistence (optional).
- Do not use bind mounts for application code in production.

## Environment Variables
- Load sensitive configuration from `.env` file using `env_file` directive.
- Required variables: `RABBITMQ_HOST`, `RABBITMQ_PORT`, `RABBITMQ_USER`, `RABBITMQ_PASS`, `DATABASE_URL`.
- Default values should work for local development (e.g., `queue` as hostname).

## Error Handling
- Configure `restart: unless-stopped` for all services.
- Set health checks for queue and db services.
- Monitor and worker should handle dependency unavailability gracefully.