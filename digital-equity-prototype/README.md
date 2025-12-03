# Digital Equity Intelligence Network

A prototype system combining **Knowledge Graphs**, **Bayesian Networks**, and **GraphRAG** to analyze Michigan's digital divide.

## 🎯 Overview

This system integrates three research frameworks:
1. **Digital Compass Navigator Ontology** - Organizing digital equity stakeholders
2. **Human Infrastructure Framework** - Understanding organizational capacity  
3. **Bayesian Causal Model** - Analyzing intervention effectiveness

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard                      │
│                         (app.py)                            │
└───────────────────┬─────────────────┬───────────────────────┘
                    │                 │
        ┌───────────▼──────┐    ┌────▼──────────────┐
        │  Knowledge Graph │    │  Bayesian Network │
        │     (Neo4j)      │    │     (pgmpy)       │
        └───────────┬──────┘    └────┬──────────────┘
                    │                │
        ┌───────────▼────────────────▼──────────┐
        │         GraphRAG Engine               │
        │   (LangChain + GPT-3.5-turbo)        │
        └───────────────────────────────────────┘
```

## 📦 Components

### 1. Knowledge Graph (`build_knowledge_graph.py`)
- **Technology:** Neo4j 5.14.0, owlready2
- **Purpose:** Store and query digital equity ecosystem
- **Entities:** Organizations, Services, Populations, Geographic Regions, Infrastructure
- **Relationships:** PROVIDES_SERVICE, SERVES_POPULATION, LOCATED_IN, ENABLES

### 2. Bayesian Network (`bayesian_model.py`)
- **Technology:** pgmpy 0.1.23
- **Purpose:** Causal inference and intervention prediction
- **DAG Structure:** Infrastructure → Availability → InternetAccess → DigitalInclusion
- **Interventions:** Infrastructure upgrades, affordability programs, navigator services

### 3. Data Ingestion (`ingest_michigan_data.py`)
- **Sources:** FCC broadband data, library systems, digital navigator programs, census data
- **Process:** Extract → Transform → Load to Neo4j
- **Bayesian Factors:** Calculates availability, affordability, aspiration scores

### 4. GraphRAG Engine (`graphrag_engine.py`)
- **Technology:** LangChain, OpenAI GPT-3.5-turbo
- **Purpose:** Natural language queries over knowledge graph
- **Features:** Question → Cypher translation, entity extraction, sample questions

### 5. Dashboard (`app.py`)
- **Technology:** Streamlit 1.29.0, Plotly 5.18.0
- **Pages:**
  - 📊 Overview: Summary statistics and regional comparison
  - 🕸️ Knowledge Graph Explorer: Browse organizations, services, populations
  - 🎲 Bayesian Analysis: Probability queries with evidence
  - 🎯 Intervention Planner: Compare intervention effectiveness
  - 💬 GraphRAG Query: Ask questions in natural language

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Docker (for Neo4j)
- OpenAI API key (optional, for GraphRAG)

### 1. Install Neo4j

```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

Verify it's running: http://localhost:7474

### 2. Install Python Dependencies

```bash
cd digital-equity-prototype
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Secrets

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml with your credentials
```

**Minimum configuration:**
```toml
[neo4j]
uri = "bolt://localhost:7687"
username = "neo4j"
password = "password"
```

**For GraphRAG (optional):**
```toml
[openai]
api_key = "sk-your-api-key-here"
```

### 4. Build Knowledge Graph

```bash
python build_knowledge_graph.py
```

This creates the ontology and loads it into Neo4j.

### 5. Ingest Michigan Data

```bash
python ingest_michigan_data.py
```

This populates the graph with:
- 4 Michigan counties (Marquette, Wayne, Kent, Chippewa)
- 3 library systems
- 2 digital navigator programs
- FCC broadband coverage data
- Census demographic data

### 6. Launch Dashboard

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## 📊 Sample Data

The prototype includes sample data for demonstration:

**Counties:**
- **Marquette County** (Upper Peninsula) - Rural, 45% fiber coverage
- **Wayne County** (Detroit Metro) - Urban, 85% fiber coverage
- **Kent County** (Grand Rapids) - Urban, 75% fiber coverage
- **Chippewa County** (Sault Ste. Marie) - Rural, 30% fiber coverage

**Organizations:**
- Upper Peninsula District Library
- Detroit Public Library
- Grand Rapids Public Library
- Michigan Works!
- AARP Michigan

**Services:**
- Digital Navigation
- WiFi Access
- Device Lending
- Digital Literacy Training
- Job Search Assistance

**Populations:**
- Low-Income Families
- Seniors
- Rural Residents
- Students
- Job Seekers

## 🧪 Testing the System

### Test Knowledge Graph
```bash
# Query organizations in Neo4j browser (http://localhost:7474)
MATCH (o:Organization)-[:PROVIDES_SERVICE]->(s:Service)
RETURN o.name, collect(s.name) as services
```

### Test Bayesian Model
```python
from bayesian_model import DigitalDivideBayesianModel

model = DigitalDivideBayesianModel()

# Query: What's the probability of digital inclusion given high infrastructure?
result = model.query(
    variables=["DigitalInclusion"],
    evidence={"Infrastructure": "High"}
)
print(result)
```

### Test GraphRAG (requires OpenAI API key)
```bash
export OPENAI_API_KEY="sk-your-key"
python graphrag_engine.py "Which organizations serve low-income families?"
```

## 📁 Project Structure

```
digital-equity-prototype/
├── app.py                      # Streamlit dashboard (main UI)
├── build_knowledge_graph.py    # Ontology builder + Neo4j loader
├── bayesian_model.py           # Bayesian network inference engine
├── ingest_michigan_data.py     # Data pipeline for Michigan data
├── graphrag_engine.py          # Natural language query interface
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── .streamlit/
    ├── secrets.toml            # Your credentials (git-ignored)
    └── secrets.toml.example    # Template
```

## 🔧 Troubleshooting

### Neo4j Connection Error
```
Error: Could not connect to Neo4j
```
**Solution:** 
1. Check Neo4j is running: `docker ps`
2. Verify credentials in `.streamlit/secrets.toml`
3. Test connection: `cypher-shell -a bolt://localhost:7687 -u neo4j -p password`

### GraphRAG Not Working
```
Warning: OPENAI_API_KEY not set
```
**Solution:** Add your OpenAI API key to `.streamlit/secrets.toml`:
```toml
[openai]
api_key = "sk-..."
```

### Import Errors
```
ModuleNotFoundError: No module named 'owlready2'
```
**Solution:** Install dependencies: `pip install -r requirements.txt`

### No Data in Dashboard
**Solution:** Run ingestion script: `python ingest_michigan_data.py`

## 🎯 Next Steps

### Add Real Data
Replace sample data with actual Michigan sources:
- **FCC Broadband Map:** https://broadbandmap.fcc.gov/data-download
- **Michigan Library Database:** https://www.michigan.gov/libraryofmichigan
- **US Census API:** https://www.census.gov/data/developers/data-sets.html

### Enhance Bayesian Model
- Add more variables (education, employment, health)
- Refine CPDs with real-world data
- Implement temporal dynamics

### Expand Knowledge Graph
- Add more entity types (schools, healthcare, community orgs)
- Import Michigan Workforce Development Board data
- Link to NTIA BEAD funding

### Deploy to Production
- Use managed Neo4j (Aura)
- Add authentication (Streamlit Auth)
- Containerize with Docker Compose
- Deploy to cloud (AWS/GCP/Azure)

## 📚 Research Foundations

This prototype implements concepts from:

1. **Digital Compass Navigator Ontology** (`dev/DigitalCompassNavigatorOntology.md`)
   - Organizing digital equity stakeholders
   - Mapping service relationships

2. **Finding the Digital Divide** (`papers/finding_digital_divide.md`)
   - Bayesian network structure
   - Infrastructure → Availability → Access → Inclusion pathway

3. **Human Infrastructure Framework** (`research/HumanInfrastructure.md`)
   - Organizational capacity modeling
   - Navigator program effectiveness

## 📄 License

Research prototype - For educational and policy analysis purposes.

## 🤝 Contributing

This is a research prototype. For questions or collaboration:
- Open an issue on GitHub
- Contact: jason@example.com

## 🙏 Acknowledgments

- Michigan digital equity stakeholders
- Neo4j community
- pgmpy developers
- LangChain team
- Streamlit creators

---

**Built with ❤️ for Michigan's Digital Equity**
