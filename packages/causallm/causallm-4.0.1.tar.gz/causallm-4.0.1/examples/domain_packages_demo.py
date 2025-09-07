#!/usr/bin/env python3
"""
Domain Packages Demonstration

This example shows how to use the new domain packages for healthcare
and insurance analysis with CausalLLM.

The domain packages provide:
1. Realistic synthetic data generators
2. Domain-specific knowledge and expertise
3. Pre-configured analysis templates
4. Business-ready interpretations

Run: python examples/domain_packages_demo.py
"""

import sys
import os
import pandas as pd
import numpy as np

# Add causallm to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from causallm import EnhancedCausalLLM
from causallm.domains.healthcare import HealthcareDomain
from causallm.domains.insurance import InsuranceDomain


def demo_healthcare_domain():
    """Demonstrate healthcare domain package."""
    print("🏥 Healthcare Domain Package Demo")
    print("=" * 50)
    
    # Initialize healthcare domain
    healthcare = HealthcareDomain()
    
    # Generate clinical trial data
    print("📊 Generating clinical trial data...")
    clinical_data = healthcare.generate_clinical_trial_data(
        n_patients=500,
        treatment_arms=['control', 'new_treatment'],
        randomization_ratio=[0.5, 0.5]
    )
    print(f"Generated {len(clinical_data)} patient records")
    print(f"Columns: {list(clinical_data.columns)}")
    print()
    
    # Show data sample
    print("📋 Sample of clinical data:")
    print(clinical_data[['age', 'gender', 'treatment', 'recovery_time', 'complications']].head())
    print()
    
    # Get domain-specific confounders
    print("🔍 Getting medical confounders for treatment effectiveness analysis...")
    confounders = healthcare.get_medical_confounders(
        treatment='treatment', 
        outcome='recovery_time',
        available_vars=list(clinical_data.columns)
    )
    print(f"Recommended confounders: {confounders}")
    print()
    
    # Run treatment effectiveness analysis
    print("📈 Running treatment effectiveness analysis...")
    try:
        causal_llm = EnhancedCausalLLM()
        
        # Use domain template for analysis
        treatment_result = healthcare.treatment_template.run_analysis(
            'treatment_effectiveness',
            clinical_data,
            causal_llm,
            treatment='treatment',
            outcome='recovery_time'
        )
        
        print("✅ Treatment Effectiveness Results:")
        print(f"   Effect Estimate: {treatment_result.effect_estimate:.2f} days")
        print(f"   95% CI: [{treatment_result.confidence_interval[0]:.2f}, {treatment_result.confidence_interval[1]:.2f}]")
        print(f"   P-value: {treatment_result.p_value:.4f}")
        print(f"   Sample Size: {treatment_result.sample_size}")
        print()
        
        print("🎯 Domain Interpretation:")
        print(f"   {treatment_result.domain_interpretation}")
        print()
        
        print("💰 Business Impact:")
        for key, value in treatment_result.business_impact.items():
            print(f"   {key}: {value}")
        print()
        
        print("📋 Recommendations:")
        for i, rec in enumerate(treatment_result.recommendations, 1):
            print(f"   {i}. {rec}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        # Show basic statistics instead
        control_recovery = clinical_data[clinical_data['treatment'] == 'control']['recovery_time'].mean()
        treatment_recovery = clinical_data[clinical_data['treatment'] == 'new_treatment']['recovery_time'].mean()
        difference = treatment_recovery - control_recovery
        
        print(f"📊 Basic Statistics:")
        print(f"   Control group recovery time: {control_recovery:.2f} days")
        print(f"   Treatment group recovery time: {treatment_recovery:.2f} days") 
        print(f"   Difference: {difference:.2f} days")
    
    print()


def demo_insurance_domain():
    """Demonstrate insurance domain package."""
    print("💼 Insurance Domain Package Demo")
    print("=" * 50)
    
    # Initialize insurance domain
    insurance = InsuranceDomain()
    
    # Generate stop loss insurance data
    print("📊 Generating stop loss insurance data...")
    insurance_data = insurance.generate_stop_loss_data(n_policies=800)
    print(f"Generated {len(insurance_data)} policy records")
    print(f"Columns: {list(insurance_data.columns)}")
    print()
    
    # Show data sample
    print("📋 Sample of insurance data:")
    sample_cols = ['company_size', 'industry', 'employee_count', 'total_claim_amount', 'loss_ratio']
    print(insurance_data[sample_cols].head())
    print()
    
    # Basic statistics
    print("📈 Key Insurance Metrics:")
    print(f"   Average Loss Ratio: {insurance_data['loss_ratio'].mean():.3f}")
    print(f"   Profitable Policies: {(insurance_data['loss_ratio'] < 0.8).sum()}/{len(insurance_data)}")
    print(f"   High-Risk Policies: {(insurance_data['loss_ratio'] > 1.2).sum()}/{len(insurance_data)}")
    print()
    
    # Industry analysis
    industry_stats = insurance_data.groupby('industry').agg({
        'loss_ratio': 'mean',
        'total_claim_amount': 'mean'
    }).round(3)
    
    print("🏭 Risk by Industry:")
    print(industry_stats)
    print()
    
    # Get domain-specific confounders
    print("🔍 Getting actuarial confounders for risk analysis...")
    confounders = insurance.get_insurance_confounders(
        treatment='industry',
        outcome='total_claim_amount', 
        available_vars=list(insurance_data.columns)
    )
    print(f"Recommended confounders: {confounders}")
    print()
    
    # Run risk analysis
    print("📊 Running insurance risk analysis...")
    try:
        risk_result = insurance.risk_template.run_analysis(
            'risk_assessment',
            insurance_data,
            causal_engine=None  # Use template's built-in analysis
        )
        
        print("✅ Risk Analysis Results:")
        print(f"   Risk Factor Effect: ${risk_result.effect_estimate:,.0f}")
        print(f"   95% CI: [${risk_result.confidence_interval[0]:,.0f}, ${risk_result.confidence_interval[1]:,.0f}]")
        print(f"   P-value: {risk_result.p_value:.4f}")
        print()
        
        print("🎯 Domain Interpretation:")
        print(f"   {risk_result.domain_interpretation}")
        print()
        
        print("💼 Business Impact:")
        for key, value in risk_result.business_impact.items():
            print(f"   {key}: {value}")
        print()
        
        print("📋 Recommendations:")
        for i, rec in enumerate(risk_result.recommendations, 1):
            print(f"   {i}. {rec}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        print("📊 Showing descriptive analysis instead...")
    
    print()


def demo_comparison():
    """Compare domain-specific vs generic analysis."""
    print("⚖️ Domain-Specific vs Generic Analysis Comparison")
    print("=" * 55)
    
    # Generate healthcare data
    healthcare = HealthcareDomain()
    clinical_data = healthcare.generate_clinical_trial_data(n_patients=400)
    
    print("🧬 Healthcare Analysis Comparison:")
    print("-" * 35)
    
    # Domain-specific approach
    print("1. Domain-Specific Approach:")
    medical_confounders = healthcare.get_medical_confounders(
        'treatment', 'recovery_time', list(clinical_data.columns)
    )
    print(f"   • Medical confounders identified: {len(medical_confounders)}")
    print(f"   • Confounders: {medical_confounders[:3]}...")
    print("   • Uses medical knowledge and clinical expertise")
    print("   • Provides clinical interpretation and recommendations")
    print()
    
    # Generic approach  
    print("2. Generic Approach:")
    print("   • Would use all available variables as potential confounders")
    print("   • No domain-specific knowledge")
    print("   • Generic statistical interpretation")
    print("   • Limited actionable insights")
    print()
    
    print("🏆 Domain Package Advantages:")
    print("   ✅ Expert knowledge built-in")
    print("   ✅ Realistic synthetic data with proper causal structure")
    print("   ✅ Domain-specific interpretation")
    print("   ✅ Business-ready recommendations")
    print("   ✅ Faster time to insights")
    print("   ✅ Reduced expertise requirement")
    print()


def main():
    """Run the complete domain packages demonstration."""
    print("🚀 CausalLLM Domain Packages Demonstration")
    print("=" * 60)
    print("This demo showcases the new domain-specific packages that make")
    print("causal analysis easier and more accurate for specific industries.")
    print()
    
    try:
        # Healthcare domain demo
        demo_healthcare_domain()
        print()
        
        # Insurance domain demo  
        demo_insurance_domain()
        print()
        
        # Comparison
        demo_comparison()
        
        print("🎉 Domain Packages Demo Complete!")
        print()
        print("💡 Next Steps:")
        print("   • Explore other domain packages (marketing, education, experimentation)")
        print("   • Customize domain knowledge for your specific use case")
        print("   • Integrate domain packages into your analysis workflows")
        print("   • Contribute domain expertise to expand the packages")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()