# transactsync
API for financial transaction synchronization from email alerts

## Docker Deployment

You can run the application using Docker:

```bash
# Pull the image from GitHub Container Registry
docker pull ghcr.io/manojmukkamala/transactsync:latest

# Run the container
docker run -p 8000:8000 -e API_KEY="super-secret" ghcr.io/manojmukkamala/transactsync:latest
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