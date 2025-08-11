#!/bin/bash
set -e

echo "Deploying to production environment..."

# Pull latest image
docker pull ghcr.io/$GITHUB_REPOSITORY:main

# Create backup
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U root goods_store > backup_$(date +%Y%m%d_%H%M%S).sql

# Stop existing containers
docker-compose -f docker-compose.prod.yml down

# Start new containers
docker-compose -f docker-compose.prod.yml up -d

# Run database migrations
docker-compose -f docker-compose.prod.yml exec app python migrate.py

# Health check
sleep 30
curl -f http://localhost:8000/health || exit 1

echo "Production deployment completed"