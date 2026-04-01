#!/bin/bash

# Wait for Ollama to be ready
echo "Waiting for Ollama to be ready..."
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    sleep 2
done

echo "Ollama is ready. Pulling llama3.2:1b model..."
docker-compose exec ollama ollama pull llama3.2:1b

echo "Model pulled successfully!"
