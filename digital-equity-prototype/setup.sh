#!/bin/bash
# Setup script for Digital Equity Intelligence System

set -e  # Exit on error

echo "=========================================="
echo "Digital Equity Intelligence System Setup"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✓ Docker is installed"
echo ""

# Check if Python 3.9+ is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION is installed"
echo ""

# Step 1: Start Neo4j container
echo "Step 1: Starting Neo4j container..."
if docker ps -a | grep -q neo4j; then
    echo "  Neo4j container already exists. Starting it..."
    docker start neo4j
else
    echo "  Creating new Neo4j container..."
    docker run -d \
        --name neo4j \
        -p 7474:7474 \
        -p 7687:7687 \
        -e NEO4J_AUTH=neo4j/password \
        neo4j:latest
fi

echo "  Waiting for Neo4j to start (15 seconds)..."
sleep 15
echo "✓ Neo4j is running at http://localhost:7474"
echo ""

# Step 2: Create virtual environment
echo "Step 2: Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "  Virtual environment already exists"
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi
echo ""

# Step 3: Install dependencies
echo "Step 3: Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Step 4: Configure secrets
echo "Step 4: Configuring secrets..."
if [ ! -f ".streamlit/secrets.toml" ]; then
    cp .streamlit/secrets.toml.example .streamlit/secrets.toml
    echo "✓ Created .streamlit/secrets.toml from example"
    echo "  Default Neo4j credentials: neo4j/password"
    echo ""
    echo "  For GraphRAG features, add your OpenAI API key to .streamlit/secrets.toml"
else
    echo "  .streamlit/secrets.toml already exists"
fi
echo ""

# Step 5: Build knowledge graph
echo "Step 5: Building knowledge graph..."
python build_knowledge_graph.py
echo "✓ Knowledge graph created"
echo ""

# Step 6: Ingest Michigan data
echo "Step 6: Ingesting Michigan data..."
python ingest_michigan_data.py
echo "✓ Data ingestion complete"
echo ""

# Success message
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "To start the dashboard:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run: streamlit run app.py"
echo "  3. Open: http://localhost:8501"
echo ""
echo "Neo4j browser: http://localhost:7474"
echo "  Username: neo4j"
echo "  Password: password"
echo ""
echo "Optional: Add OpenAI API key to .streamlit/secrets.toml for GraphRAG features"
echo ""
