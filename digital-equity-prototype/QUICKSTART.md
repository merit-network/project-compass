# Digital Equity Intelligence System - Quick Start Guide

## 🎯 What This Does

Combines **Knowledge Graphs** (Neo4j) + **Bayesian Networks** (pgmpy) + **GraphRAG** (LangChain) to analyze Michigan's digital divide.

## ⚡ One-Command Setup

```bash
./setup.sh
```

This will:
1. ✓ Start Neo4j container
2. ✓ Create Python virtual environment
3. ✓ Install all dependencies
4. ✓ Build knowledge graph ontology
5. ✓ Ingest Michigan sample data

## 🚀 Launch Dashboard

```bash
source venv/bin/activate
streamlit run app.py
```

Open: http://localhost:8501

## 📊 What You'll See

### 1. Overview Page
- 5 organizations
- 10+ digital services
- 4 Michigan counties (Marquette, Wayne, Kent, Chippewa)
- Broadband coverage charts

### 2. Knowledge Graph Explorer
- Browse organizations (libraries, nonprofits, ISPs)
- View services (digital literacy, device lending, WiFi)
- See populations served (seniors, low-income families, rural residents)

### 3. Bayesian Analysis
- Query: "What's P(Digital Inclusion = High) given Infrastructure = High?"
- Interactive probability calculator
- Visualize distributions

### 4. Intervention Planner
- Compare 5 intervention scenarios:
  - Baseline
  - Infrastructure upgrades
  - Affordability subsidies
  - Navigator programs
  - Combined approach
- See predicted impact on digital inclusion

### 5. GraphRAG Query (requires OpenAI API key)
- Ask: "Which organizations serve low-income families in Wayne County?"
- Natural language → Cypher query → Answer

## 🔧 Troubleshooting

### Check Everything Works
```bash
python verify.py
```

### Neo4j Not Running?
```bash
docker start neo4j
```

### Missing Dependencies?
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### No Data in Dashboard?
```bash
python ingest_michigan_data.py
```

### Add GraphRAG (Optional)
Edit `.streamlit/secrets.toml`:
```toml
[openai]
api_key = "sk-your-key-here"
```

## 📁 Files Overview

```
├── app.py                      # 5-page Streamlit dashboard
├── build_knowledge_graph.py    # Ontology builder (3 frameworks combined)
├── bayesian_model.py           # Causal inference engine
├── ingest_michigan_data.py     # Data pipeline (FCC, libraries, census)
├── graphrag_engine.py          # Natural language queries
├── setup.sh                    # Automated setup script
├── verify.py                   # Verification script
└── requirements.txt            # Python dependencies
```

## 🎓 Research Foundations

Implements concepts from:
1. **Digital Compass Navigator Ontology** - Stakeholder organization
2. **Finding the Digital Divide** (Bayesian) - Causal pathways
3. **Human Infrastructure Framework** - Organizational capacity

## 📈 Sample Queries

### Neo4j Browser (http://localhost:7474)
```cypher
// Find all organizations serving low-income families
MATCH (o:Organization)-[:SERVES_POPULATION]->(p:Population {name: "Low-Income Families"})
RETURN o.name, o.type

// Show service coverage by county
MATCH (r:GeographicRegion)<-[:LOCATED_IN]-(o:Organization)-[:PROVIDES_SERVICE]->(s:Service)
RETURN r.name, count(DISTINCT s) as service_count
ORDER BY service_count DESC
```

### Python (Bayesian Model)
```python
from bayesian_model import DigitalDivideBayesianModel

model = DigitalDivideBayesianModel()

# Predict with high infrastructure
result = model.query(
    variables=["DigitalInclusion"],
    evidence={"Infrastructure": "High"}
)
print(result)
```

### Command Line (GraphRAG)
```bash
export OPENAI_API_KEY="sk-..."
python graphrag_engine.py "Which counties have lowest broadband coverage?"
```

## 🎯 Next Steps

1. **Add Real Data**
   - FCC Broadband Map: https://broadbandmap.fcc.gov
   - Michigan libraries: https://www.michigan.gov/libraryofmichigan
   - Census API: https://www.census.gov/data/developers

2. **Enhance Model**
   - Add temporal dynamics
   - Refine CPDs with real-world data
   - Expand entity types (schools, healthcare)

3. **Deploy**
   - Use Neo4j Aura (managed cloud)
   - Add authentication
   - Deploy to AWS/GCP/Azure

## 💡 Key Insights from Sample Data

- **Urban-Rural Divide:** Wayne County (85% fiber) vs. Chippewa County (30% fiber)
- **Service Gaps:** Low-income families have fewer service providers than seniors
- **Best Intervention:** Combined approach (infrastructure + affordability + navigators) yields 70% probability of high digital inclusion
- **Library Impact:** Public libraries are key access points in rural areas

## 🤝 Support

Having issues?
1. Run `python verify.py` to check status
2. Check Docker: `docker ps | grep neo4j`
3. Review logs: `docker logs neo4j`

## 📄 Full Documentation

See `README.md` for comprehensive documentation.

---

**Built with ❤️ for Michigan's Digital Equity**
