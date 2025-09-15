# Running Ollama locally for Chat2DB

This project can use a local Ollama model via HTTP for AI-assisted chat features. The backend expects a local Ollama HTTP API at `http://localhost:11434` by default and a model name configured via `OLLAMA_MODEL` environment variable.

Quick start (host)

1. Install Ollama following official instructions: https://ollama.com/docs
2. Start an Ollama model (example):

```bash
# pull and run a model (replace <model> with your chosen model name)
ollama pull ollama/<model>
ollama run <model>
```

3. Verify the HTTP API is available:

```bash
curl http://localhost:11434/api/models
```

4. Configure backend environment (optional):

```bash
export OLLAMA_URL=http://localhost:11434
export OLLAMA_MODEL=<model>
# restart backend container or set env in docker-compose
```

Alternative: run Ollama outside this repo (recommended for local development), or deploy a dedicated model service.

Notes
- Ollama is required to use the `/api/chat` endpoint. If Ollama isn't running, the endpoint will return an error.
- Depending on your model choice, resource requirements (RAM/CPU) can be significant.
