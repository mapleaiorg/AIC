#!/bin/bash

echo "🚀 Deploying Maple AI Companion to production..."

# Build and start with Docker Compose
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check health
echo "🏥 Checking service health..."
curl -f http://localhost:8000/health || {
    echo "❌ Health check failed!"
    docker-compose logs api
    exit 1
}

echo "✅ Deployment successful!"
echo "📊 Access Grafana dashboard at: http://localhost:3000 (admin/admin123)"
echo "📈 Access Prometheus at: http://localhost:9090"
echo "🍁 API available at: http://localhost:8000"
