#!/bin/bash

# Local Development Startup Script
# Starts both nova-rag and nova-api services locally for testing

set -e

echo "=========================================="
echo "🚀 NOVA Local Development Setup"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -d "nova" ] || [ ! -d "nova-rag" ]; then
    echo "❌ Error: Must run from /automatizaciones directory"
    echo "   Current directory: $(pwd)"
    exit 1
fi

# Check if ports are available
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port 8001 already in use (nova-rag)"
    echo "   Killing existing process..."
    lsof -ti:8001 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port 8000 already in use (nova-api)"
    echo "   Killing existing process..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

echo "1️⃣  Starting nova-rag service (port 8001)..."
echo ""

# Start nova-rag in background
cd nova-rag
uvicorn src.api.main:app --port 8001 --reload > ../logs/nova-rag.log 2>&1 &
RAG_PID=$!
cd ..

echo "   ✅ nova-rag started (PID: $RAG_PID)"
echo "   📄 Logs: logs/nova-rag.log"
echo ""

# Wait for RAG service to be ready
echo "2️⃣  Waiting for nova-rag to initialize..."
for i in {1..30}; do
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo "   ✅ nova-rag is ready!"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# Check if RAG is healthy
HEALTH=$(curl -s http://localhost:8001/health | grep -o '"status":"healthy"' || echo "")
if [ -z "$HEALTH" ]; then
    echo "   ⚠️  Warning: nova-rag might not be fully ready yet"
    echo "   Check logs/nova-rag.log for details"
fi

echo ""
echo "3️⃣  Starting nova-api service (port 8000)..."
echo ""

# Set RAG_SERVICE_URL for nova-api
export RAG_SERVICE_URL="http://localhost:8001"

# Start nova-api in background
cd nova
uvicorn src.api.main:app --port 8000 --reload > ../logs/nova-api.log 2>&1 &
API_PID=$!
cd ..

echo "   ✅ nova-api started (PID: $API_PID)"
echo "   📄 Logs: logs/nova-api.log"
echo ""

# Wait for API service to be ready
echo "4️⃣  Waiting for nova-api to initialize..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ✅ nova-api is ready!"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

echo "=========================================="
echo "✅ Development Environment Ready!"
echo "=========================================="
echo ""
echo "Services running:"
echo "  🔹 nova-rag:  http://localhost:8001"
echo "  🔹 nova-api:  http://localhost:8000"
echo ""
echo "API Documentation:"
echo "  🔹 nova-rag docs:  http://localhost:8001/docs"
echo "  🔹 nova-api docs:  http://localhost:8000/docs"
echo ""
echo "Logs:"
echo "  🔹 nova-rag:  tail -f logs/nova-rag.log"
echo "  🔹 nova-api:  tail -f logs/nova-api.log"
echo ""
echo "PIDs (for stopping):"
echo "  🔹 nova-rag:  $RAG_PID"
echo "  🔹 nova-api:  $API_PID"
echo ""
echo "To stop all services:"
echo "  kill $RAG_PID $API_PID"
echo ""
echo "To run integration tests:"
echo "  python test_rag_integration.py"
echo ""
echo "Press Ctrl+C to stop watching logs (services will keep running)"
echo "=========================================="
echo ""

# Follow logs (can Ctrl+C to exit, services keep running)
tail -f logs/nova-rag.log logs/nova-api.log
