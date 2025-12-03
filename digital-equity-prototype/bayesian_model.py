#!/usr/bin/env python3
"""
Bayesian Network Model for Digital Divide Analysis
Based on "Finding the Digital Divide" research
"""

from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
import pandas as pd

class DigitalDivideBayesianModel:
    def __init__(self):
        # Define the structure (DAG)
        self.model = BayesianNetwork([
            ('Infrastructure', 'Availability'),
            ('Income', 'Affordability'),
            ('Education', 'Aspiration'),
            ('Availability', 'InternetAccess'),
            ('Affordability', 'InternetAccess'),
            ('Aspiration', 'InternetAccess'),
            ('InternetAccess', 'DigitalInclusion'),
            ('Services', 'DigitalInclusion')
        ])
        
    def define_cpds(self):
        """Define Conditional Probability Distributions"""
        
        # Infrastructure -> Availability
        cpd_infra = TabularCPD('Infrastructure', 2, [[0.7], [0.3]])  # [No, Yes]
        
        cpd_avail = TabularCPD('Availability', 2,
            [[0.9, 0.2],   # P(Avail=Low | Infra)
             [0.1, 0.8]],  # P(Avail=High | Infra)
            evidence=['Infrastructure'],
            evidence_card=[2])
        
        # Income -> Affordability
        cpd_income = TabularCPD('Income', 2, [[0.6], [0.4]])  # [Low, High]
        
        cpd_afford = TabularCPD('Affordability', 2,
            [[0.8, 0.2],   # P(Afford=Low | Income)
             [0.2, 0.8]],  # P(Afford=High | Income)
            evidence=['Income'],
            evidence_card=[2])
        
        # Education -> Aspiration
        cpd_edu = TabularCPD('Education', 2, [[0.5], [0.5]])  # [Low, High]
        
        cpd_aspir = TabularCPD('Aspiration', 2,
            [[0.7, 0.3],   # P(Aspir=Low | Edu)
             [0.3, 0.7]],  # P(Aspir=High | Edu)
            evidence=['Education'],
            evidence_card=[2])
        
        # Combined effect on Internet Access
        cpd_access = TabularCPD('InternetAccess', 2,
            [[0.95, 0.8, 0.8, 0.6, 0.8, 0.6, 0.6, 0.3],  # P(Access=No | ...)
             [0.05, 0.2, 0.2, 0.4, 0.2, 0.4, 0.4, 0.7]], # P(Access=Yes | ...)
            evidence=['Availability', 'Affordability', 'Aspiration'],
            evidence_card=[2, 2, 2])
        
        # Services
        cpd_services = TabularCPD('Services', 2, [[0.6], [0.4]])  # [Weak, Strong]
        
        # Digital Inclusion
        cpd_inclusion = TabularCPD('DigitalInclusion', 2,
            [[0.9, 0.7, 0.6, 0.3],  # P(Inclusion=Low | ...)
             [0.1, 0.3, 0.4, 0.7]], # P(Inclusion=High | ...)
            evidence=['InternetAccess', 'Services'],
            evidence_card=[2, 2])
        
        self.model.add_cpds(cpd_infra, cpd_avail, cpd_income, cpd_afford,
                           cpd_edu, cpd_aspir, cpd_access, cpd_services, cpd_inclusion)
        
        assert self.model.check_model()
        print("✓ Bayesian model validated")
    
    def query(self, evidence):
        """Perform inference given evidence"""
        inference = VariableElimination(self.model)
        result = inference.query(['DigitalInclusion'], evidence=evidence)
        return result
    
    def predict_intervention_impact(self, intervention_type):
        """Predict impact of different interventions"""
        inference = VariableElimination(self.model)
        
        scenarios = {
            'baseline': {},
            'infrastructure': {'Infrastructure': 1},
            'affordability_subsidy': {'Income': 1},
            'digital_navigator': {'Services': 1},
            'combined': {'Infrastructure': 1, 'Services': 1}
        }
        
        results = {}
        for scenario_name, evidence in scenarios.items():
            result = inference.query(['DigitalInclusion'], evidence=evidence)
            results[scenario_name] = result.values[1]  # Probability of High inclusion
        
        return results

# Usage
if __name__ == "__main__":
    print("=" * 60)
    print("Digital Divide Bayesian Model")
    print("=" * 60)
    print()
    
    model = DigitalDivideBayesianModel()
    model.define_cpds()
    print()
    
    # Example query
    print("Example 1: No infrastructure, Low income")
    evidence = {'Infrastructure': 0, 'Income': 0}
    result = model.query(evidence)
    print(result)
    print()
    
    # Predict intervention impacts
    print("Intervention Impact Analysis:")
    print("-" * 60)
    impacts = model.predict_intervention_impact('all')
    for scenario, prob in impacts.items():
        print(f"{scenario:25s}: {prob:.2%} digital inclusion probability")
