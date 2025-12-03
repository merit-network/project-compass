#!/usr/bin/env python3
"""
Digital Equity Intelligence System Dashboard
Streamlit application for exploring Michigan's digital divide
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from neo4j import GraphDatabase
from bayesian_model import DigitalDivideBayesianModel
from graphrag_engine import GraphRAGEngine
import os

# Page configuration
st.set_page_config(
    page_title="Digital Equity Intelligence System",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #F0F9FF;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3B82F6;
    }
    .insight-box {
        background-color: #FFF7ED;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #F59E0B;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize connections
@st.cache_resource
def init_neo4j():
    """Initialize Neo4j connection"""
    uri = st.secrets.get("neo4j", {}).get("uri", "bolt://localhost:7687")
    user = st.secrets.get("neo4j", {}).get("username", "neo4j")
    password = st.secrets.get("neo4j", {}).get("password", "password")
    return GraphDatabase.driver(uri, auth=(user, password))

@st.cache_resource
def init_bayesian_model():
    """Initialize Bayesian network model"""
    return DigitalDivideBayesianModel()

@st.cache_resource
def init_graphrag():
    """Initialize GraphRAG engine"""
    uri = st.secrets.get("neo4j", {}).get("uri", "bolt://localhost:7687")
    user = st.secrets.get("neo4j", {}).get("username", "neo4j")
    password = st.secrets.get("neo4j", {}).get("password", "password")
    api_key = st.secrets.get("openai", {}).get("api_key", os.getenv("OPENAI_API_KEY"))
    
    if api_key:
        return GraphRAGEngine(uri, user, password, api_key)
    return None

# Initialize resources
driver = init_neo4j()
bayesian_model = init_bayesian_model()
graphrag_engine = init_graphrag()

# Sidebar navigation
st.sidebar.title("🌐 Digital Equity Navigator")
page = st.sidebar.radio(
    "Navigation",
    ["📊 Overview", "🕸️ Knowledge Graph Explorer", "🎲 Bayesian Analysis", 
     "🎯 Intervention Planner", "💬 GraphRAG Query"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
### About
This system combines:
- **Knowledge Graphs** (Neo4j)
- **Bayesian Networks** (pgmpy)
- **GraphRAG** (LangChain)

to analyze Michigan's digital divide.
""")

# ===== PAGE 1: OVERVIEW =====
if page == "📊 Overview":
    st.markdown('<p class="main-header">📊 Digital Equity Overview</p>', unsafe_allow_html=True)
    
    st.markdown("""
    This intelligence system integrates three research frameworks to analyze Michigan's digital divide:
    1. **Digital Compass Navigator Ontology** - Organizing digital equity stakeholders
    2. **Human Infrastructure Framework** - Understanding organizational capacity
    3. **Bayesian Causal Model** - Analyzing intervention effectiveness
    """)
    
    # Fetch summary statistics from Neo4j
    with driver.session() as session:
        # Count organizations
        org_result = session.run("MATCH (o:Organization) RETURN count(o) as count")
        org_count = org_result.single()["count"]
        
        # Count services
        service_result = session.run("MATCH (s:Service) RETURN count(s) as count")
        service_count = service_result.single()["count"]
        
        # Count populations
        pop_result = session.run("MATCH (p:Population) RETURN count(p) as count")
        pop_count = pop_result.single()["count"]
        
        # Count regions
        region_result = session.run("MATCH (r:GeographicRegion) RETURN count(r) as count")
        region_count = region_result.single()["count"]
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Organizations", org_count)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Digital Services", service_count)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Populations Served", pop_count)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Counties", region_count)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Regional comparison
    st.subheader("📍 Regional Broadband Coverage")
    
    with driver.session() as session:
        region_data = session.run("""
            MATCH (r:GeographicRegion)
            RETURN r.name as county, 
                   r.fiber_coverage as fiber,
                   r.cable_coverage as cable,
                   r.median_speed_mbps as speed
            ORDER BY r.fiber_coverage DESC
        """)
        df_regions = pd.DataFrame([dict(record) for record in region_data])
    
    if not df_regions.empty:
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Fiber', x=df_regions['county'], y=df_regions['fiber']))
        fig.add_trace(go.Bar(name='Cable', x=df_regions['county'], y=df_regions['cable']))
        fig.update_layout(
            barmode='group',
            title="Broadband Coverage by County (%)",
            xaxis_title="County",
            yaxis_title="Coverage Percentage",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

# ===== PAGE 2: KNOWLEDGE GRAPH EXPLORER =====
elif page == "🕸️ Knowledge Graph Explorer":
    st.markdown('<p class="main-header">🕸️ Knowledge Graph Explorer</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Organizations", "Services", "Populations"])
    
    with tab1:
        st.subheader("Organizations in the Digital Equity Ecosystem")
        
        with driver.session() as session:
            org_data = session.run("""
                MATCH (o:Organization)
                OPTIONAL MATCH (o)-[:PROVIDES_SERVICE]->(s:Service)
                OPTIONAL MATCH (o)-[:SERVES_POPULATION]->(p:Population)
                OPTIONAL MATCH (o)-[:LOCATED_IN]->(r:GeographicRegion)
                RETURN o.name as name, 
                       labels(o) as types,
                       collect(DISTINCT s.name) as services,
                       collect(DISTINCT p.name) as populations,
                       r.name as region
            """)
            df_orgs = pd.DataFrame([dict(record) for record in org_data])
        
        if not df_orgs.empty:
            for _, row in df_orgs.iterrows():
                with st.expander(f"**{row['name']}**"):
                    st.write(f"**Type:** {', '.join(row['types'])}")
                    if row['region']:
                        st.write(f"**Location:** {row['region']}")
                    if row['services']:
                        st.write(f"**Services:** {', '.join(row['services'])}")
                    if row['populations']:
                        st.write(f"**Populations Served:** {', '.join(row['populations'])}")
    
    with tab2:
        st.subheader("Digital Services Catalog")
        
        with driver.session() as session:
            service_data = session.run("""
                MATCH (s:Service)<-[:PROVIDES_SERVICE]-(o:Organization)
                RETURN s.name as service, 
                       count(o) as provider_count,
                       collect(o.name) as providers
                ORDER BY provider_count DESC
            """)
            df_services = pd.DataFrame([dict(record) for record in service_data])
        
        if not df_services.empty:
            fig = px.bar(
                df_services,
                x='service',
                y='provider_count',
                title="Service Availability (Number of Providers)",
                labels={'service': 'Service Type', 'provider_count': 'Number of Providers'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df_services, use_container_width=True)
    
    with tab3:
        st.subheader("Populations Served")
        
        with driver.session() as session:
            pop_data = session.run("""
                MATCH (p:Population)<-[:SERVES_POPULATION]-(o:Organization)
                RETURN p.name as population,
                       count(o) as org_count,
                       collect(o.name) as organizations
                ORDER BY org_count DESC
            """)
            df_pops = pd.DataFrame([dict(record) for record in pop_data])
        
        if not df_pops.empty:
            fig = px.pie(
                df_pops,
                names='population',
                values='org_count',
                title="Population Coverage by Organizations"
            )
            st.plotly_chart(fig, use_container_width=True)

# ===== PAGE 3: BAYESIAN ANALYSIS =====
elif page == "🎲 Bayesian Analysis":
    st.markdown('<p class="main-header">🎲 Bayesian Causal Analysis</p>', unsafe_allow_html=True)
    
    st.markdown("""
    The Bayesian network models causal relationships in digital equity:
    **Infrastructure → Availability → Internet Access → Digital Inclusion**
    """)
    
    st.subheader("Query Probability")
    
    col1, col2 = st.columns(2)
    
    with col1:
        variables = st.multiselect(
            "Select variables to query",
            ["Infrastructure", "Availability", "Affordability", "Aspiration", 
             "InternetAccess", "ServiceQuality", "DigitalInclusion"],
            default=["DigitalInclusion"]
        )
    
    with col2:
        evidence_var = st.selectbox(
            "Evidence variable (optional)",
            ["None", "Infrastructure", "Availability", "Affordability", "Aspiration"]
        )
        
        if evidence_var != "None":
            evidence_value = st.selectbox(f"{evidence_var} value", ["Low", "Medium", "High"])
    
    if st.button("Run Query"):
        evidence = {}
        if evidence_var != "None":
            evidence[evidence_var] = evidence_value
        
        result = bayesian_model.query(variables, evidence)
        
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.subheader("Results")
        
        for var in variables:
            st.write(f"**{var}:**")
            df_result = pd.DataFrame(
                result[var].values,
                columns=[result[var].state_names[var][i] for i in range(len(result[var].values))]
            )
            st.dataframe(df_result.T, use_container_width=True)
            
            # Visualization
            fig = px.bar(
                x=df_result.columns,
                y=df_result.values[0],
                title=f"Probability Distribution: {var}",
                labels={'x': 'State', 'y': 'Probability'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ===== PAGE 4: INTERVENTION PLANNER =====
elif page == "🎯 Intervention Planner":
    st.markdown('<p class="main-header">🎯 Intervention Planning</p>', unsafe_allow_html=True)
    
    st.markdown("""
    Compare the predicted impact of different digital equity interventions using the Bayesian model.
    """)
    
    if st.button("Run Intervention Analysis"):
        with st.spinner("Calculating intervention impacts..."):
            results = bayesian_model.predict_intervention_impact()
        
        # Create comparison table
        comparison_data = []
        for intervention, probs in results.items():
            comparison_data.append({
                'Intervention': intervention,
                'P(Digital Inclusion = High)': probs['High'],
                'P(Digital Inclusion = Medium)': probs['Medium'],
                'P(Digital Inclusion = Low)': probs['Low']
            })
        
        df_comparison = pd.DataFrame(comparison_data)
        
        st.subheader("📊 Intervention Effectiveness Comparison")
        st.dataframe(df_comparison, use_container_width=True)
        
        # Visualization
        fig = px.bar(
            df_comparison,
            x='Intervention',
            y='P(Digital Inclusion = High)',
            title="Predicted Probability of High Digital Inclusion by Intervention",
            labels={'P(Digital Inclusion = High)': 'Probability', 'Intervention': 'Intervention Type'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Insights
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.subheader("💡 Key Insights")
        
        best_intervention = df_comparison.loc[df_comparison['P(Digital Inclusion = High)'].idxmax(), 'Intervention']
        best_prob = df_comparison['P(Digital Inclusion = High)'].max()
        
        st.write(f"""
        - **Most effective intervention:** {best_intervention} ({best_prob:.1%} probability of high inclusion)
        - **Combined approach:** Addresses multiple causal pathways simultaneously
        - **Infrastructure investments:** Enable downstream improvements in availability and access
        - **Navigator programs:** Help translate access into actual digital inclusion
        """)
        st.markdown('</div>', unsafe_allow_html=True)

# ===== PAGE 5: GRAPHRAG QUERY =====
elif page == "💬 GraphRAG Query":
    st.markdown('<p class="main-header">💬 Natural Language Query</p>', unsafe_allow_html=True)
    
    if graphrag_engine is None:
        st.warning("⚠️ GraphRAG requires an OpenAI API key. Please add it to `.streamlit/secrets.toml`")
        st.code("""
# .streamlit/secrets.toml
[openai]
api_key = "sk-..."
        """)
    else:
        st.markdown("Ask questions about Michigan's digital equity ecosystem in natural language.")
        
        # Sample questions
        with st.expander("📝 Sample Questions"):
            for i, q in enumerate(graphrag_engine.get_sample_questions(), 1):
                st.write(f"{i}. {q}")
        
        # Query input
        question = st.text_input("Enter your question:", placeholder="Which organizations serve low-income families?")
        
        if st.button("Search") and question:
            with st.spinner("Querying knowledge graph..."):
                result = graphrag_engine.query(question)
            
            st.markdown('<div class="insight-box">', unsafe_allow_html=True)
            st.subheader("Answer")
            st.write(result['answer'])
            
            if result['cypher_query']:
                with st.expander("🔍 View Generated Cypher Query"):
                    st.code(result['cypher_query'], language="cypher")
            
            st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Built with ❤️ for Michigan's Digital Equity")
