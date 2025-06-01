#!/bin/sh

echo "Dowload OpenAPI schema"
docker-compose -f docker-compose.local.yml exec django /entrypoint python3 manage.py spectacular --format openapi-json --file frontend/src/generated/flash_api.json

echo "Convert OpenAPI schema to TypeScript types"
./frontend/node_modules/.bin/openapi-typescript frontend/src/generated/flash_api.json -o frontend/src/generated/schema.d.ts

echo "Format schema"
./frontend/node_modules/.bin/prettier --write frontend/src/generated/flash_api.json frontend/src/generated/schema.d.ts
