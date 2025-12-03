#!/usr/bin/env python3
"""
Verification script to check all components are working correctly
"""

import sys

def check_imports():
    """Check all required packages are installed"""
    print("Checking Python packages...")
    required_packages = [
        'streamlit',
        'neo4j',
        'owlready2',
        'pgmpy',
        'pandas',
        'numpy',
        'networkx',
        'plotly',
        'langchain',
        'openai'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✓ All packages installed\n")
    return True

def check_neo4j():
    """Check Neo4j connection"""
    print("Checking Neo4j connection...")
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
        with driver.session() as session:
            result = session.run("RETURN 1")
            result.single()
        driver.close()
        print("✓ Neo4j is accessible\n")
        return True
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        print("Make sure Neo4j is running:")
        print("  docker ps | grep neo4j")
        print("Or start it:")
        print("  docker start neo4j\n")
        return False

def check_knowledge_graph():
    """Check if knowledge graph has data"""
    print("Checking knowledge graph data...")
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
        with driver.session() as session:
            org_count = session.run("MATCH (o:Organization) RETURN count(o) as count").single()["count"]
            service_count = session.run("MATCH (s:Service) RETURN count(s) as count").single()["count"]
            region_count = session.run("MATCH (r:GeographicRegion) RETURN count(r) as count").single()["count"]
        
        driver.close()
        
        print(f"  Organizations: {org_count}")
        print(f"  Services: {service_count}")
        print(f"  Regions: {region_count}")
        
        if org_count > 0 and service_count > 0 and region_count > 0:
            print("✓ Knowledge graph has data\n")
            return True
        else:
            print("❌ Knowledge graph is empty")
            print("Run: python ingest_michigan_data.py\n")
            return False
    except Exception as e:
        print(f"❌ Error checking knowledge graph: {e}\n")
        return False

def check_bayesian_model():
    """Check Bayesian model"""
    print("Checking Bayesian model...")
    try:
        from bayesian_model import DigitalDivideBayesianModel
        model = DigitalDivideBayesianModel()
        result = model.query(["DigitalInclusion"], {})
        print("✓ Bayesian model is working\n")
        return True
    except Exception as e:
        print(f"❌ Bayesian model error: {e}\n")
        return False

def check_graphrag():
    """Check GraphRAG (optional)"""
    print("Checking GraphRAG (optional)...")
    try:
        import os
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠️  OPENAI_API_KEY not set (optional feature)")
            print("   Add to .streamlit/secrets.toml for natural language queries\n")
            return True
        
        from graphrag_engine import GraphRAGEngine
        engine = GraphRAGEngine("bolt://localhost:7687", "neo4j", "password")
        print("✓ GraphRAG is configured\n")
        return True
    except Exception as e:
        print(f"⚠️  GraphRAG setup issue (optional): {e}\n")
        return True  # Don't fail on optional feature

def main():
    print("=" * 60)
    print("Digital Equity Intelligence System - Verification")
    print("=" * 60)
    print()
    
    checks = [
        check_imports(),
        check_neo4j(),
        check_knowledge_graph(),
        check_bayesian_model(),
        check_graphrag()
    ]
    
    print("=" * 60)
    if all(checks[:4]):  # First 4 are required
        print("✓ All core components are working!")
        print("=" * 60)
        print()
        print("Ready to launch:")
        print("  streamlit run app.py")
        print()
        return 0
    else:
        print("❌ Some components need attention")
        print("=" * 60)
        print()
        print("Try running:")
        print("  ./setup.sh")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
