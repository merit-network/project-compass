#!/usr/bin/env python3
"""
Data Ingestion for Michigan Digital Equity Data
Ingests FCC broadband data, library data, digital navigator programs, and census data
"""

import pandas as pd
import requests
from neo4j import GraphDatabase
import json

class MichiganDataIngester:
    def __init__(self, neo4j_uri, neo4j_user, neo4j_password):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    
    def ingest_fcc_broadband_data(self, fcc_data_path=None):
        """Ingest FCC broadband availability data"""
        print("Ingesting FCC broadband data...")
        
        # For demo, use sample data
        sample_data = pd.DataFrame({
            'county': ['Marquette', 'Wayne', 'Kent', 'Chippewa'],
            'fiber_coverage_pct': [45.0, 85.0, 75.0, 30.0],
            'cable_coverage_pct': [60.0, 95.0, 90.0, 40.0],
            'dsl_coverage_pct': [75.0, 98.0, 95.0, 70.0],
            'median_download_mbps': [50.0, 100.0, 100.0, 25.0],
            'population': [67000, 1750000, 650000, 37000]
        })
        
        with self.driver.session() as session:
            for _, row in sample_data.iterrows():
                session.run("""
                    MERGE (r:GeographicRegion {name: $county})
                    SET r.population = $population,
                        r.fiber_coverage = $fiber,
                        r.cable_coverage = $cable,
                        r.dsl_coverage = $dsl,
                        r.median_speed_mbps = $speed,
                        r.type = 'county'
                """, {
                    'county': f"{row['county']} County",
                    'population': int(row['population']),
                    'fiber': row['fiber_coverage_pct'],
                    'cable': row['cable_coverage_pct'],
                    'dsl': row['dsl_coverage_pct'],
                    'speed': row['median_download_mbps']
                })
        
        print(f"  ✓ Ingested FCC data for {len(sample_data)} counties")
    
    def ingest_library_data(self):
        """Ingest Michigan library system data"""
        print("Ingesting library data...")
        
        # Sample Michigan library data
        libraries = [
            {
                'name': 'Upper Peninsula District Library',
                'county': 'Marquette County',
                'services': ['Digital Navigation', 'WiFi Access', 'Device Lending', 'Digital Literacy Training'],
                'populations': ['Seniors', 'Rural Residents', 'Low-Income Families']
            },
            {
                'name': 'Detroit Public Library',
                'county': 'Wayne County',
                'services': ['WiFi Access', 'Computer Access', 'Digital Literacy Training', 'Job Search Assistance'],
                'populations': ['Low-Income Families', 'Job Seekers', 'Students']
            },
            {
                'name': 'Grand Rapids Public Library',
                'county': 'Kent County',
                'services': ['WiFi Access', 'Device Lending', 'Digital Literacy Training', 'Tech Help Desk'],
                'populations': ['Seniors', 'Students', 'Low-Income Families']
            }
        ]
        
        with self.driver.session() as session:
            for lib in libraries:
                # Create library
                session.run("""
                    MERGE (l:Library:Organization {name: $name})
                    SET l.type = 'Library'
                """, {'name': lib['name']})
                
                # Link to region
                session.run("""
                    MATCH (l:Library {name: $lib_name})
                    MATCH (r:GeographicRegion {name: $county})
                    MERGE (l)-[:LOCATED_IN]->(r)
                """, {'lib_name': lib['name'], 'county': lib['county']})
                
                # Create services
                for service in lib['services']:
                    session.run("""
                        MATCH (l:Library {name: $lib_name})
                        MERGE (s:Service {name: $service})
                        MERGE (l)-[:PROVIDES_SERVICE]->(s)
                    """, {'lib_name': lib['name'], 'service': service})
                
                # Link populations
                for pop in lib['populations']:
                    session.run("""
                        MATCH (l:Library {name: $lib_name})
                        MERGE (p:Population {name: $pop})
                        MERGE (l)-[:SERVES_POPULATION]->(p)
                    """, {'lib_name': lib['name'], 'pop': pop})
        
        print(f"  ✓ Ingested {len(libraries)} libraries")
    
    def ingest_digital_navigator_programs(self):
        """Ingest digital navigator program data"""
        print("Ingesting digital navigator programs...")
        
        programs = [
            {
                'name': 'Michigan Works! Digital Navigator',
                'organization': 'Michigan Works!',
                'type': 'Workforce Development',
                'county': 'Multiple',
                'services': ['Job Search Assistance', 'Digital Skills Training', 'Device Access'],
                'populations': ['Job Seekers', 'Low-Income Families']
            },
            {
                'name': 'AARP Digital Skills Program',
                'organization': 'AARP Michigan',
                'type': 'Senior Services',
                'county': 'Multiple',
                'services': ['Digital Literacy Training', 'Online Safety', 'Tech Support'],
                'populations': ['Seniors']
            }
        ]
        
        with self.driver.session() as session:
            for prog in programs:
                # Create organization
                session.run("""
                    MERGE (o:DigitalEquityNonprofit:Organization {name: $org_name})
                    SET o.type = $type
                """, {'org_name': prog['organization'], 'type': prog['type']})
                
                # Create program
                session.run("""
                    MATCH (o:Organization {name: $org_name})
                    MERGE (pr:Program {name: $prog_name})
                    MERGE (o)-[:OPERATES]->(pr)
                """, {'org_name': prog['organization'], 'prog_name': prog['name']})
                
                # Link services and populations
                for service in prog['services']:
                    session.run("""
                        MATCH (o:Organization {name: $org_name})
                        MERGE (s:Service {name: $service})
                        MERGE (o)-[:PROVIDES_SERVICE]->(s)
                    """, {'org_name': prog['organization'], 'service': service})
                
                for pop in prog['populations']:
                    session.run("""
                        MATCH (o:Organization {name: $org_name})
                        MERGE (p:Population {name: $pop})
                        MERGE (o)-[:SERVES_POPULATION]->(p)
                    """, {'org_name': prog['organization'], 'pop': pop})
        
        print(f"  ✓ Ingested {len(programs)} digital navigator programs")
    
    def ingest_census_data(self):
        """Ingest relevant US Census data for Michigan"""
        print("Ingesting census data...")
        
        # Sample census data
        census_data = pd.DataFrame({
            'county': ['Marquette County', 'Wayne County', 'Kent County', 'Chippewa County'],
            'median_income': [45000, 52000, 58000, 42000],
            'poverty_rate': [0.18, 0.22, 0.15, 0.19],
            'senior_population_pct': [0.20, 0.15, 0.13, 0.22],
            'rural_percentage': [0.75, 0.10, 0.25, 0.85]
        })
        
        with self.driver.session() as session:
            for _, row in census_data.iterrows():
                session.run("""
                    MATCH (r:GeographicRegion {name: $county})
                    SET r.median_income = $income,
                        r.poverty_rate = $poverty,
                        r.senior_population_pct = $seniors,
                        r.rural_percentage = $rural
                """, {
                    'county': row['county'],
                    'income': row['median_income'],
                    'poverty': row['poverty_rate'],
                    'seniors': row['senior_population_pct'],
                    'rural': row['rural_percentage']
                })
        
        print(f"  ✓ Ingested census data for {len(census_data)} counties")
    
    def calculate_bayesian_factors(self):
        """Calculate Bayesian factor scores for each region"""
        print("Calculating Bayesian factor scores...")
        
        with self.driver.session() as session:
            # Calculate Availability score
            session.run("""
                MATCH (r:GeographicRegion)
                SET r.availability_score = 
                    CASE 
                        WHEN r.fiber_coverage >= 70 THEN 1.0
                        WHEN r.fiber_coverage >= 40 THEN 0.7
                        ELSE 0.3
                    END
            """)
            
            # Calculate Affordability score
            session.run("""
                MATCH (r:GeographicRegion)
                SET r.affordability_score = 
                    CASE 
                        WHEN r.median_income >= 55000 THEN 1.0
                        WHEN r.median_income >= 45000 THEN 0.7
                        ELSE 0.3
                    END
            """)
            
            # Calculate Aspiration score (based on education proxy)
            session.run("""
                MATCH (r:GeographicRegion)
                SET r.aspiration_score = 
                    CASE 
                        WHEN r.rural_percentage < 0.3 THEN 0.8
                        WHEN r.rural_percentage < 0.6 THEN 0.6
                        ELSE 0.4
                    END
            """)
            
            # Calculate Service Quality score
            session.run("""
                MATCH (r:GeographicRegion)<-[:LOCATED_IN]-(o:Organization)
                WITH r, count(o) as org_count
                SET r.service_quality_score = 
                    CASE 
                        WHEN org_count >= 3 THEN 1.0
                        WHEN org_count >= 1 THEN 0.6
                        ELSE 0.2
                    END
            """)
        
        print("  ✓ Calculated Bayesian factor scores for all regions")
    
    def close(self):
        self.driver.close()

# Main ingestion script
if __name__ == "__main__":
    print("=" * 60)
    print("Michigan Digital Equity Data Ingestion")
    print("=" * 60)
    print()
    
    ingester = MichiganDataIngester(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password"
    )
    
    try:
        print("Starting data ingestion...")
        print()
        
        ingester.ingest_fcc_broadband_data()
        ingester.ingest_library_data()
        ingester.ingest_digital_navigator_programs()
        ingester.ingest_census_data()
        ingester.calculate_bayesian_factors()
        
        print()
        print("=" * 60)
        print("✓ All data ingested successfully!")
        print("=" * 60)
        print()
        print("Next step: Run 'streamlit run app.py' to launch the dashboard")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure Neo4j is running:")
        print("  docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest")
    finally:
        ingester.close()
