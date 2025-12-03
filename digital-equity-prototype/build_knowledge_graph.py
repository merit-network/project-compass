#!/usr/bin/env python3
"""
Build Knowledge Graph for Digital Equity Intelligence System
Combines ontologies from:
- Digital Compass Navigator
- Human Infrastructure of Broadband
- Finding Digital Divide (Bayesian factors)
"""

from owlready2 import *
from neo4j import GraphDatabase
import pandas as pd

class DigitalEquityKG:
    def __init__(self, neo4j_uri, neo4j_user, neo4j_password):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.onto = get_ontology("http://example.org/digital_equity.owl")
        
    def create_ontology(self):
        """Create the combined ontology from all three documents"""
        with self.onto:
            # From Digital Compass Navigator
            class DigitalNavigator(Thing): pass
            class Service(Thing): pass
            class Population(Thing): pass
            class Skill(Thing): pass
            class Program(Thing): pass
            
            # From Human Infrastructure
            class Organization(Thing): pass
            class CoreOrganization(Organization): pass
            class Library(CoreOrganization): pass
            class DigitalEquityNonprofit(CoreOrganization): pass
            class ComplementaryOrganization(Organization): pass
            class CoalitionOrganization(Organization): pass
            
            # Infrastructure (from Digital Compass)
            class Infrastructure(Thing): pass
            class Road(Infrastructure): pass
            class FiberOpticCable(Infrastructure): pass
            class AccessPoint(Infrastructure): pass
            class Household(Thing): pass
            class GeographicRegion(Thing): pass
            
            # Bayesian Network Factors (from Finding Digital Divide)
            class DigitalDivideFactor(Thing): pass
            class Availability(DigitalDivideFactor): pass
            class Aspiration(DigitalDivideFactor): pass
            class Relevance(DigitalDivideFactor): pass
            class Quality(DigitalDivideFactor): pass
            class Affordability(DigitalDivideFactor): pass
            
            # Research
            class ResearchDocument(Thing): pass
            class Author(Thing): pass
            class Publication(Thing): pass
            
            # Properties
            class provides_service(ObjectProperty):
                domain = [DigitalNavigator, Organization]
                range = [Service]
            
            class serves_population(ObjectProperty):
                domain = [DigitalNavigator, Organization]
                range = [Population]
            
            class has_skill(ObjectProperty):
                domain = [DigitalNavigator]
                range = [Skill]
            
            class located_in(ObjectProperty):
                domain = [Household, Organization, Infrastructure]
                range = [GeographicRegion]
            
            class connected_to(ObjectProperty):
                domain = [Road, AccessPoint]
                range = [FiberOpticCable, Household]
            
            class influences_factor(ObjectProperty):
                domain = [Infrastructure, Service, Program]
                range = [DigitalDivideFactor]
            
            class has_score(DataProperty):
                domain = [DigitalDivideFactor, GeographicRegion]
                range = [float]
            
            class collaborates_with(ObjectProperty):
                domain = [Organization]
                range = [Organization]
            
            class supports_navigator(ObjectProperty):
                domain = [ResearchDocument]
                range = [DigitalNavigator]
        
        self.onto.save(file="digital_equity.owl")
        print("✓ Ontology created and saved")
    
    def load_to_neo4j(self):
        """Load ontology into Neo4j"""
        with self.driver.session() as session:
            # Clear existing data
            print("Clearing existing Neo4j data...")
            session.run("MATCH (n) DETACH DELETE n")
            
            # Create constraints
            session.run("""
                CREATE CONSTRAINT IF NOT EXISTS FOR (n:Organization) 
                REQUIRE n.name IS UNIQUE
            """)
            session.run("""
                CREATE CONSTRAINT IF NOT EXISTS FOR (n:GeographicRegion) 
                REQUIRE n.name IS UNIQUE
            """)
            
            print("✓ Neo4j constraints created")
    
    def import_michigan_data(self):
        """Import sample Michigan data"""
        with self.driver.session() as session:
            # Create geographic regions
            print("Creating geographic regions...")
            session.run("""
                CREATE (up:GeographicRegion {
                    name: 'Upper Peninsula',
                    type: 'region',
                    population: 301000,
                    rural_percentage: 0.85
                })
                CREATE (detroit:GeographicRegion {
                    name: 'Detroit Metro',
                    type: 'metro',
                    population: 4300000,
                    rural_percentage: 0.15
                })
            """)
            
            # Create sample library (from Salt Lake City example)
            print("Creating organizations...")
            session.run("""
                CREATE (lib:Library:Organization {
                    name: 'Upper Peninsula Library System',
                    type: 'Library'
                })
                CREATE (service1:Service {name: 'Digital Navigation'})
                CREATE (service2:Service {name: 'WiFi Access'})
                CREATE (service3:Service {name: 'Device Lending'})
                CREATE (lib)-[:PROVIDES_SERVICE]->(service1)
                CREATE (lib)-[:PROVIDES_SERVICE]->(service2)
                CREATE (lib)-[:PROVIDES_SERVICE]->(service3)
            """)
            
            # Create populations
            print("Creating populations...")
            session.run("""
                CREATE (pop1:Population {name: 'Seniors', description: 'Older adults 65+'})
                CREATE (pop2:Population {name: 'Low-Income Families', description: 'Households below poverty line'})
                CREATE (pop3:Population {name: 'Rural Residents', description: 'Residents in rural areas'})
            """)
            
            # Link library to populations
            session.run("""
                MATCH (lib:Library {name: 'Upper Peninsula Library System'})
                MATCH (pop:Population)
                WHERE pop.name IN ['Seniors', 'Low-Income Families', 'Rural Residents']
                CREATE (lib)-[:SERVES_POPULATION]->(pop)
            """)
            
            print("✓ Sample Michigan data imported")
    
    def close(self):
        self.driver.close()

# Usage
if __name__ == "__main__":
    print("=" * 60)
    print("Digital Equity Knowledge Graph Builder")
    print("=" * 60)
    print()
    
    # Default Neo4j connection
    kg = DigitalEquityKG(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password"  # Change this!
    )
    
    try:
        print("Step 1: Creating ontology...")
        kg.create_ontology()
        print()
        
        print("Step 2: Loading to Neo4j...")
        kg.load_to_neo4j()
        print()
        
        print("Step 3: Importing Michigan data...")
        kg.import_michigan_data()
        print()
        
        print("✓ Knowledge Graph built successfully!")
        print()
        print("Access Neo4j Browser at: http://localhost:7474")
        print("Username: neo4j")
        print("Password: password")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Make sure Neo4j is running:")
        print("  docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest")
    finally:
        kg.close()
