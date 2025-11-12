#!/bin/bash

set -e

echo "MyGuardian Demo Script"
echo "========================"
echo ""

cd "$(dirname "$0")/../backend" || exit 1

if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "Starting services with Docker Compose..."
docker compose up -d --build

echo "Waiting for services to be ready..."
sleep 10

for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "API is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "Error: API did not become ready in time"
        exit 1
    fi
    sleep 1
done

echo ""
echo "Running example requests..."
echo ""

echo "Example 1: ALLOW (Good Answer)"
curl -s -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key-change-in-production" \
  -d '{
    "question": "What are side-effects of metformin?",
    "answer": "Common side-effects include nausea and diarrhea.",
    "passages": [
      {"id":"p1","text":"Common side-effects are nausea and diarrhea.","source":"med-guide"}
    ]
  }' | jq -r '.decision, .scores'
echo ""

echo "Example 2: REPAIR (Missing Parts)"
curl -s -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key-change-in-production" \
  -d '{
    "question": "What are side-effects, dosage, and interactions?",
    "answer": "Side-effects include nausea and diarrhea.",
    "passages": [
      {"id":"p1","text":"Common side-effects are nausea and diarrhea.","source":"med-guide"},
      {"id":"p2","text":"Typical adult dosage starts at 500 mg once or twice daily with meals.","source":"dose-guide"}
    ]
  }' | jq -r '.decision, .scores, .repaired_answer[:100]'
echo ""

echo "Example 3: BLOCK (PII Detected)"
curl -s -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key-change-in-production" \
  -d '{
    "question": "How to contact support?",
    "answer": "Email me at user@example.com.",
    "passages": [{"id":"p1","text":"Use official support channels only.","source":"policy"}]
  }' | jq -r '.decision, .scores, .explanations'
echo ""

echo "Opening dashboards..."
echo ""

if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:16686
    open http://localhost:9090
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open http://localhost:16686 2>/dev/null || true
    xdg-open http://localhost:9090 2>/dev/null || true
fi

echo "Demo complete!"
echo ""
echo "View metrics: http://localhost:9090"
echo "View traces: http://localhost:16686"
echo "Health check: http://localhost:8000/health"
echo "Version info: http://localhost:8000/version"
echo ""
echo "Run eval harness:"
echo "   cd backend && python eval/run_eval.py --report md"
echo ""
echo "Stop services: docker compose down"

