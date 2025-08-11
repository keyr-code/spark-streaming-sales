#!/bin/bash
set -e

echo "Deploying to staging environment..."

# Pull latest image
docker pull ghcr.io/$GITHUB_REPOSITORY:develop

# Stop existing containers
docker-compose -f docker-compose.staging.yml down

# Start new containers
docker-compose -f docker-compose.staging.yml up -d

# Run database migrations
docker-compose -f docker-compose.staging.yml exec app python migrate.py

echo "Staging deployment completed"