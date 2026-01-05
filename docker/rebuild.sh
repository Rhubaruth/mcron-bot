docker compose down
docker build -t rhubaruth/mcrcon . --no-cache
docker compose up -d
