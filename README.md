# transactsync
API for financial transaction synchronization from email alerts

## Docker Deployment

You can run the application using Docker:

```bash
# Pull the image from GitHub Container Registry
docker pull ghcr.io/manojmukkamala/transactsync:latest

# Run the container (set DATABASE_URL env variable to point to your DB, ex: `postgresql://transactsync:transactsync@postgres-hostname:5432/transactsync`)
docker run -p 8000:8000 -e API_KEY="super-secret" ghcr.io/manojmukkamala/transactsync:latest

# To run full stack instead (update volumes in docker-compose.yaml to persist data)
docker compose up
```

The application will be accessible at `http://localhost:8000`.

FastAPI swagger docs will be accessible at `http://localhost:8000/docs`.

## Local Development

```bash
export API_KEY=super-secret
uv sync && uv run main.py
```

#### Linting & Code Formatting

```bash
ruff check app
ruff format app
mypy app
```

## CI/CD

The application is automatically built and published to GitHub Container Registry on every tagged release on the main branch.