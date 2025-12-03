#!/usr/bin/env python3
"""
GraphRAG Engine for Digital Equity Intelligence System
Uses LangChain to enable natural language queries over the knowledge graph
"""

from langchain.chains import GraphCypherQAChain
from langchain.chat_models import ChatOpenAI
from langchain.graphs import Neo4jGraph
from typing import Dict, List
import os

class GraphRAGEngine:
    """
    Natural language query interface for the Digital Equity Knowledge Graph
    Uses GraphRAG (Graph-augmented Retrieval) with LangChain
    """
    
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str, openai_api_key: str = None):
        """
        Initialize the GraphRAG engine
        
        Args:
            neo4j_uri: Neo4j connection URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
            openai_api_key: Optional OpenAI API key (will use env var if not provided)
        """
        # Initialize Neo4j graph
        self.graph = Neo4jGraph(
            url=neo4j_uri,
            username=neo4j_user,
            password=neo4j_password
        )
        
        # Initialize LLM (use GPT-3.5 for cost-effectiveness)
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        
        self.llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
        
        # Create GraphCypherQAChain
        self.chain = GraphCypherQAChain.from_llm(
            llm=self.llm,
            graph=self.graph,
            verbose=True,
            return_intermediate_steps=True
        )
    
    def query(self, question: str) -> Dict:
        """
        Query the knowledge graph using natural language
        
        Args:
            question: Natural language question
            
        Returns:
            Dictionary with answer, cypher query, and context
        """
        try:
            result = self.chain(question)
            
            return {
                'question': question,
                'answer': result['result'],
                'cypher_query': result['intermediate_steps'][0]['query'] if result.get('intermediate_steps') else None,
                'context': result['intermediate_steps'][0]['context'] if result.get('intermediate_steps') else None
            }
        except Exception as e:
            return {
                'question': question,
                'answer': f"Error: {str(e)}",
                'cypher_query': None,
                'context': None
            }
    
    def get_sample_questions(self) -> List[str]:
        """Return sample questions users can ask"""
        return [
            "Which organizations serve low-income families in Wayne County?",
            "What digital services are provided by libraries in Michigan?",
            "Which counties have the lowest broadband availability?",
            "What populations are underserved by digital navigator programs?",
            "Show me organizations that provide device lending services",
            "Which regions need the most infrastructure investment?",
            "What services help seniors with digital access?",
            "Compare digital equity resources between rural and urban counties"
        ]
    
    def extract_entities(self, text: str) -> List[Dict]:
        """
        Extract entities from text that match knowledge graph nodes
        Useful for autocomplete and entity linking
        """
        query = """
        MATCH (n)
        WHERE toLower(n.name) CONTAINS toLower($text)
        RETURN labels(n) as type, n.name as name
        LIMIT 10
        """
        
        result = self.graph.query(query, {"text": text})
        return result
    
    def get_schema_context(self) -> str:
        """Get a human-readable description of the graph schema"""
        return """
        The Digital Equity Knowledge Graph contains:
        
        **Organizations:**
        - Libraries
        - Digital Equity Nonprofits
        - ISPs (Internet Service Providers)
        - Workforce Development Organizations
        
        **Infrastructure:**
        - Broadband Infrastructure
        - Community Access Points
        
        **Services:**
        - Digital Literacy Training
        - Device Lending
        - WiFi Access
        - Tech Support
        - Job Search Assistance
        
        **Populations:**
        - Low-Income Families
        - Seniors
        - Rural Residents
        - Students
        - Job Seekers
        
        **Geographic Regions:**
        - Counties in Michigan
        - Urban/Rural classifications
        
        **Relationships:**
        - Organizations PROVIDE_SERVICE to Services
        - Organizations SERVE_POPULATION to Populations
        - Organizations LOCATED_IN Geographic Regions
        - Infrastructure ENABLES Services
        """

# Example usage
if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("Digital Equity GraphRAG Query System")
    print("=" * 60)
    print()
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set")
        print("   Set it in .streamlit/secrets.toml or as environment variable")
        print()
        sys.exit(1)
    
    try:
        engine = GraphRAGEngine(
            neo4j_uri="bolt://localhost:7687",
            neo4j_user="neo4j",
            neo4j_password="password"
        )
        
        print("GraphRAG engine initialized successfully!")
        print()
        print("Sample questions you can ask:")
        print()
        
        for i, question in enumerate(engine.get_sample_questions(), 1):
            print(f"  {i}. {question}")
        
        print()
        print("=" * 60)
        print()
        
        # Interactive mode
        if len(sys.argv) > 1:
            question = " ".join(sys.argv[1:])
        else:
            question = input("Enter your question: ")
        
        if question:
            print()
            print(f"Question: {question}")
            print()
            
            result = engine.query(question)
            
            print("Answer:")
            print(result['answer'])
            print()
            
            if result['cypher_query']:
                print("Generated Cypher:")
                print(result['cypher_query'])
                print()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Make sure:")
        print("  1. Neo4j is running (docker ps)")
        print("  2. Data is ingested (python ingest_michigan_data.py)")
        print("  3. OPENAI_API_KEY is set")
