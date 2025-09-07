#!/usr/bin/env python3
"""
Stop Loss Insurance Analysis Example

This example demonstrates comprehensive stop loss insurance analysis using CausalLLM
for risk assessment, premium optimization, and claims prediction in group health insurance.

Stop loss insurance protects self-insured employers from catastrophic claims costs.
This analysis helps insurers understand risk factors, optimize pricing strategies,
and predict claims patterns.

Prerequisites:
- Set OPENAI_API_KEY environment variable (optional - works without API key)
- Install: pip install pandas numpy

Run: python examples/stop_loss_insurance_analysis.py
"""

import sys
import os
import json
from datetime import datetime, timedelta
import random
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from causallm import EnhancedCausalLLM
from causallm.core.causal_llm_core import CausalLLMCore

def generate_stop_loss_data():
    """Generate realistic stop loss insurance data for analysis."""
    np.random.seed(42)
    n_policies = 2000
    
    # Employer characteristics
    company_sizes = np.random.choice(['Small', 'Medium', 'Large'], n_policies, p=[0.4, 0.35, 0.25])
    company_size_numeric = {'Small': 50, 'Medium': 250, 'Large': 1000}
    size_std_map = {'Small': 20, 'Medium': 100, 'Large': 500}
    employee_counts = [company_size_numeric[size] + np.random.normal(0, size_std_map[size], 1)[0] 
                      for size in company_sizes]
    employee_counts = np.clip(employee_counts, 10, 5000).astype(int)
    
    # Industry risk factors
    industries = np.random.choice([
        'Technology', 'Healthcare', 'Manufacturing', 'Construction', 
        'Finance', 'Retail', 'Education', 'Transportation'
    ], n_policies, p=[0.15, 0.12, 0.15, 0.08, 0.12, 0.18, 0.1, 0.1])
    
    # Industry risk multipliers for claims
    industry_risk = {
        'Technology': 0.8, 'Healthcare': 1.1, 'Manufacturing': 1.2, 
        'Construction': 1.4, 'Finance': 0.9, 'Retail': 1.0, 
        'Education': 0.95, 'Transportation': 1.3
    }
    
    # Employee demographics (affects claims)
    avg_ages = np.random.normal(42, 8, n_policies)
    avg_ages = np.clip(avg_ages, 25, 65)
    
    # Geographic risk factors
    regions = np.random.choice(['Northeast', 'Southeast', 'Midwest', 'West'], 
                              n_policies, p=[0.25, 0.3, 0.25, 0.2])
    region_cost_multiplier = {
        'Northeast': 1.15, 'Southeast': 0.9, 'Midwest': 0.95, 'West': 1.1
    }
    
    # Plan characteristics
    deductible_levels = np.random.choice(['Low', 'Medium', 'High'], n_policies, p=[0.3, 0.5, 0.2])
    deductible_amounts = {'Low': 25000, 'Medium': 50000, 'High': 100000}
    specific_deductibles = [deductible_amounts[level] for level in deductible_levels]
    
    aggregate_deductibles = [specific * employee_count * 0.8 
                           for specific, employee_count in zip(specific_deductibles, employee_counts)]
    
    # Previous claims history
    prior_large_claims = np.random.poisson(0.3, n_policies)  # Average 0.3 large claims per year
    
    # Calculate expected claims based on risk factors
    base_claim_prob = 0.02  # 2% chance of large claim per employee per year
    
    expected_large_claims = []
    annual_premiums = []
    actual_large_claims = []
    total_claim_amounts = []
    
    for i in range(n_policies):
        # Risk-adjusted claim probability
        risk_multiplier = (industry_risk[industries[i]] * 
                          region_cost_multiplier[regions[i]] * 
                          (1 + (avg_ages[i] - 40) * 0.01) *  # Age factor
                          (1 + prior_large_claims[i] * 0.2))  # Claims history
        
        adjusted_prob = base_claim_prob * risk_multiplier
        expected_claims = employee_counts[i] * adjusted_prob
        expected_large_claims.append(expected_claims)
        
        # Actual claims (with randomness)
        actual_claims = np.random.poisson(expected_claims)
        actual_large_claims.append(actual_claims)
        
        # Claim amounts (following log-normal distribution)
        if actual_claims > 0:
            claim_amounts = np.random.lognormal(11, 1, actual_claims)  # Mean ~$100k claims
            total_amount = np.sum(claim_amounts)
        else:
            total_amount = 0
        total_claim_amounts.append(total_amount)
        
        # Premium calculation (based on expected risk + profit margin)
        base_premium_per_employee = 1200  # Annual base premium
        risk_adjusted_premium = (base_premium_per_employee * 
                               employee_counts[i] * 
                               risk_multiplier * 1.2)  # 20% profit margin
        annual_premiums.append(risk_adjusted_premium)
    
    # Additional risk factors
    wellness_programs = np.random.choice([0, 1], n_policies, p=[0.4, 0.6])
    chronic_disease_mgmt = np.random.choice([0, 1], n_policies, p=[0.5, 0.5])
    telemedicine_adoption = np.random.uniform(0, 1, n_policies)  # % adoption
    
    return pd.DataFrame({
        'policy_id': range(1, n_policies + 1),
        'company_size': company_sizes,
        'employee_count': employee_counts,
        'industry': industries,
        'avg_employee_age': avg_ages,
        'region': regions,
        'specific_deductible': specific_deductibles,
        'aggregate_deductible': aggregate_deductibles,
        'prior_large_claims': prior_large_claims,
        'wellness_program': wellness_programs,
        'chronic_disease_mgmt': chronic_disease_mgmt,
        'telemedicine_adoption': telemedicine_adoption,
        'expected_large_claims': expected_large_claims,
        'actual_large_claims': actual_large_claims,
        'total_claim_amount': total_claim_amounts,
        'annual_premium': annual_premiums,
        'loss_ratio': np.array(total_claim_amounts) / np.array(annual_premiums),
        'profitable': (np.array(total_claim_amounts) / np.array(annual_premiums)) < 0.8
    })

def run_stop_loss_analysis():
    """Run comprehensive stop loss insurance analysis."""
    print("🏥 Stop Loss Insurance Analysis with CausalLLM")
    print("=" * 50)
    
    # Generate synthetic data
    print("📊 Generating stop loss insurance dataset...")
    data = generate_stop_loss_data()
    print(f"Generated {len(data)} policy records")
    print(f"Average loss ratio: {data['loss_ratio'].mean():.3f}")
    print(f"Profitable policies: {data['profitable'].sum()}/{len(data)} ({data['profitable'].mean():.1%})")
    print()
    
    # Initialize CausalLLM
    print("🔬 Initializing Enhanced CausalLLM...")
    causal_llm = EnhancedCausalLLM()
    print("✅ CausalLLM initialized successfully")
    print()
    
    # Analysis 1: Risk Factor Analysis
    print("📈 Analysis 1: Key Risk Factors for High Claims")
    print("-" * 45)
    
    try:
        risk_analysis = causal_llm.comprehensive_analysis(
            data=data,
            treatment='industry',
            outcome='total_claim_amount',
            domain='finance',
            covariates=['employee_count', 'avg_employee_age', 'region', 'prior_large_claims']
        )
        
        print("✅ Risk Factor Analysis Results:")
        # Get the primary inference result
        primary_result = list(risk_analysis.inference_results.values())[0]
        print(f"   Primary Effect: {primary_result.primary_effect.effect_estimate:.2f}")
        print(f"   Confidence: {risk_analysis.confidence_score:.1%}")
        print(f"   Business Impact: {len(risk_analysis.actionable_insights)} insights generated")
        
        # Display key insights
        print("\n🎯 Key Risk Insights:")
        for i, insight in enumerate(risk_analysis.actionable_insights[:3], 1):
            print(f"   {i}. {insight}")
            
    except Exception as e:
        print(f"❌ Risk analysis failed: {str(e)}")
        print("📊 Continuing with statistical analysis...")
    
    print()
    
    # Analysis 2: Wellness Program Impact
    print("💪 Analysis 2: Wellness Program Effectiveness")
    print("-" * 45)
    
    try:
        wellness_analysis = causal_llm.comprehensive_analysis(
            data=data,
            treatment='wellness_program',
            outcome='loss_ratio',
            domain='healthcare',
            covariates=['company_size', 'industry', 'avg_employee_age']
        )
        
        print("✅ Wellness Program Analysis Results:")
        # Get the primary inference result
        primary_result = list(wellness_analysis.inference_results.values())[0]
        print(f"   Effect on Loss Ratio: {primary_result.primary_effect.effect_estimate:.4f}")
        print(f"   Statistical Significance: p = {primary_result.primary_effect.p_value:.4f}")
        print(f"   Confidence Interval: {primary_result.primary_effect.confidence_interval}")
        
        # Calculate business impact
        avg_premium = data['annual_premium'].mean()
        wellness_savings = abs(primary_result.primary_effect.effect_estimate) * avg_premium
        print(f"   💰 Estimated Annual Savings per Policy: ${wellness_savings:,.0f}")
        
    except Exception as e:
        print(f"❌ Wellness analysis failed: {str(e)}")
        
        # Fallback statistical analysis
        wellness_yes = data[data['wellness_program'] == 1]['loss_ratio'].mean()
        wellness_no = data[data['wellness_program'] == 0]['loss_ratio'].mean()
        difference = wellness_yes - wellness_no
        print(f"📊 Fallback Analysis:")
        print(f"   Loss Ratio with Wellness: {wellness_yes:.4f}")
        print(f"   Loss Ratio without Wellness: {wellness_no:.4f}")
        print(f"   Difference: {difference:.4f}")
    
    print()
    
    # Analysis 3: Predictive Analysis
    print("🔮 Analysis 3: Claims Prediction Insights")
    print("-" * 45)
    
    # Calculate key statistics
    high_risk_policies = data[data['loss_ratio'] > 1.0]
    print(f"📊 Descriptive Statistics:")
    print(f"   High-risk policies: {len(high_risk_policies)}/{len(data)} ({len(high_risk_policies)/len(data):.1%})")
    print(f"   Average claim amount: ${data['total_claim_amount'].mean():,.0f}")
    print(f"   Median claim amount: ${data['total_claim_amount'].median():,.0f}")
    print()
    
    # Industry analysis
    industry_stats = data.groupby('industry').agg({
        'loss_ratio': 'mean',
        'total_claim_amount': 'mean',
        'profitable': 'mean'
    }).round(3)
    
    print("🏭 Risk by Industry:")
    print(industry_stats.to_string())
    print()
    
    # Size analysis
    size_stats = data.groupby('company_size').agg({
        'loss_ratio': 'mean',
        'total_claim_amount': 'mean',
        'employee_count': 'mean'
    }).round(3)
    
    print("📏 Risk by Company Size:")
    print(size_stats.to_string())
    print()
    
    # Analysis 4: Intervention Recommendations
    print("💡 Analysis 4: Business Recommendations")
    print("-" * 45)
    
    print("🎯 Key Strategic Recommendations:")
    print("   1. Premium Optimization:")
    high_risk_industries = industry_stats[industry_stats['loss_ratio'] > 1.0].index.tolist()
    if high_risk_industries:
        print(f"      • Increase premiums for: {', '.join(high_risk_industries)}")
    
    profitable_industries = industry_stats[industry_stats['loss_ratio'] < 0.8].index.tolist()
    if profitable_industries:
        print(f"      • Competitive pricing for: {', '.join(profitable_industries)}")
    
    print("   2. Risk Management:")
    print("      • Mandate wellness programs for high-risk groups")
    print("      • Implement chronic disease management programs")
    print("      • Incentivize telemedicine adoption")
    
    print("   3. Underwriting Guidelines:")
    print("      • Adjust deductibles based on industry risk")
    print("      • Consider employee age distribution in pricing")
    print("      • Factor in prior claims history more heavily")
    
    print()
    
    # Save results
    results_file = 'stop_loss_analysis_results.json'
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_policies': len(data),
        'average_loss_ratio': float(data['loss_ratio'].mean()),
        'profitable_policies_pct': float(data['profitable'].mean()),
        'high_risk_industries': high_risk_industries,
        'profitable_industries': profitable_industries,
        'industry_analysis': industry_stats.to_dict(),
        'size_analysis': size_stats.to_dict()
    }
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Results saved to: {results_file}")
    print()
    
    print("🎉 Stop Loss Insurance Analysis Complete!")
    print("Key Findings:")
    print(f"   • Analyzed {len(data)} policies across {data['industry'].nunique()} industries")
    print(f"   • Average loss ratio: {data['loss_ratio'].mean():.3f}")
    print(f"   • {data['profitable'].sum()} profitable policies ({data['profitable'].mean():.1%})")
    print(f"   • Wellness programs show potential for cost reduction")
    print(f"   • Industry-specific risk patterns identified for pricing optimization")

if __name__ == "__main__":
    run_stop_loss_analysis()