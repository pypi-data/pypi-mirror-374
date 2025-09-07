#!/usr/bin/env python3
"""
Educational Outcomes Causal Analysis - CausalLLM Comprehensive Example

This example demonstrates CausalLLM's capabilities in the education domain,
analyzing factors that causally influence student learning outcomes and 
educational interventions effectiveness.

Features showcased:
- Automated causal discovery in educational data
- Multi-method statistical inference for intervention effects  
- Domain-specific educational insights and recommendations
- Policy intervention recommendations with expected impact
- Heterogeneous treatment effects across student subgroups
- Cost-effectiveness analysis for educational programs

Domain: Education Policy & Student Outcomes
Use Case: Analyzing causal factors affecting student performance and 
         evaluating educational interventions

Run: python examples/educational_outcomes_analysis.py
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
from typing import Dict, List, Tuple

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import enhanced CausalLLM components
from causallm.enhanced_causallm import EnhancedCausalLLM

# Suppress warnings for cleaner demo output
warnings.filterwarnings('ignore')

def generate_educational_dataset(n_students: int = 3000) -> pd.DataFrame:
    """
    Generate realistic educational dataset with complex causal relationships.
    
    This dataset simulates factors affecting student outcomes including:
    - Student demographics and background
    - School resources and quality indicators  
    - Educational interventions and programs
    - Learning outcomes and achievements
    
    Known causal structure:
    - Socioeconomic factors → School choice → Resources available
    - Prior achievement → Program participation → Learning gains
    - Teacher quality → Student engagement → Academic outcomes
    - Class size → Individual attention → Performance improvements
    """
    
    np.random.seed(2024)  # For reproducibility
    
    print(f"🎓 Generating educational dataset with {n_students:,} students...")
    print("   Simulating complex educational causal relationships...")
    
    # === STUDENT DEMOGRAPHICS & BACKGROUND ===
    
    # Age/grade level
    grade_level = np.random.choice([9, 10, 11, 12], n_students, p=[0.27, 0.26, 0.25, 0.22])
    student_age = grade_level + np.random.normal(0, 0.5, n_students)
    student_age = np.clip(student_age, 13, 19)
    
    # Socioeconomic status (fundamental confounder)
    parent_education = np.random.choice(
        ['high_school', 'some_college', 'bachelors', 'graduate'], 
        n_students, p=[0.25, 0.35, 0.25, 0.15]
    )
    
    # Family income (correlated with parent education)
    income_mapping = {
        'high_school': np.random.lognormal(np.log(35000), 0.6, n_students),
        'some_college': np.random.lognormal(np.log(45000), 0.5, n_students), 
        'bachelors': np.random.lognormal(np.log(70000), 0.4, n_students),
        'graduate': np.random.lognormal(np.log(95000), 0.4, n_students)
    }
    
    family_income = np.array([
        income_mapping[edu][i] if edu in income_mapping else 40000
        for i, edu in enumerate(parent_education)
    ])
    family_income = np.clip(family_income, 20000, 250000)
    
    # Demographics
    gender = np.random.choice(['female', 'male', 'non_binary'], n_students, p=[0.51, 0.47, 0.02])
    ethnicity = np.random.choice(
        ['white', 'hispanic', 'black', 'asian', 'other'], 
        n_students, p=[0.45, 0.25, 0.15, 0.10, 0.05]
    )
    
    # Special populations
    english_learner = np.random.binomial(1, 0.12, n_students)  # 12% EL students
    special_education = np.random.binomial(1, 0.13, n_students)  # 13% special ed
    free_lunch_eligible = np.random.binomial(
        1, np.clip(0.8 - (family_income - 20000) / 100000, 0.1, 0.9), n_students
    )
    
    # === PRIOR ACADEMIC ACHIEVEMENT ===
    
    # Prior test scores (influenced by demographics and SES)
    prior_achievement_base = (
        80 +  # Base score
        (family_income - 50000) / 5000 +  # SES effect
        np.random.normal(0, 15, n_students)  # Individual variation
    )
    
    # Demographic adjustments (reflecting systemic inequities)
    ethnicity_effects = {
        'white': 0, 'asian': 8, 'hispanic': -6, 'black': -8, 'other': -2
    }
    prior_achievement = prior_achievement_base + np.array([
        ethnicity_effects.get(eth, 0) for eth in ethnicity
    ])
    
    # Special population adjustments
    prior_achievement -= english_learner * 12  # EL gap
    prior_achievement -= special_education * 8  # Special ed gap
    prior_achievement = np.clip(prior_achievement, 40, 100)
    
    # === SCHOOL CHARACTERISTICS ===
    
    # School type (influenced by SES and demographics)
    school_choice_prob = np.clip(
        0.7 + (family_income - 50000) / 100000 + 
        (prior_achievement - 80) / 50, 0.1, 0.95
    )
    
    school_type = np.array([
        np.random.choice(['public', 'charter', 'private'], 
                        p=[1-p, p*0.6, p*0.4] if p < 0.8 else [0.2, 0.5, 0.3])
        for p in school_choice_prob
    ])
    
    # School quality indicators
    # Teacher experience (varies by school type and location)
    teacher_experience_base = np.random.normal(8, 4, n_students)
    school_effects = {'public': 0, 'charter': -1, 'private': 2}
    teacher_experience = teacher_experience_base + np.array([
        school_effects.get(school, 0) for school in school_type
    ])
    teacher_experience = np.clip(teacher_experience, 1, 25)
    
    # Class size (smaller in private schools, varies by funding)
    class_size_base = 25 + np.random.normal(0, 5, n_students)
    class_size = class_size_base - np.array([
        school_effects.get(school, 0) * 3 for school in school_type
    ])
    class_size = np.clip(class_size, 12, 35)
    
    # School resources (funding per student)
    school_funding_base = 8000 + (family_income.mean() / 10)  # Property tax effect
    school_funding = school_funding_base + np.array([
        {'public': 0, 'charter': 500, 'private': 2000}.get(school, 0)
        for school in school_type
    ]) + np.random.normal(0, 1000, n_students)
    school_funding = np.clip(school_funding, 5000, 20000)
    
    # === EDUCATIONAL INTERVENTIONS ===
    
    # Tutorial program participation (targeted based on prior achievement)
    tutoring_eligibility = (prior_achievement < 75) | (free_lunch_eligible == 1)
    tutoring_participation = np.where(
        tutoring_eligibility,
        np.random.binomial(1, 0.4, n_students),  # 40% participation among eligible
        np.random.binomial(1, 0.1, n_students)   # 10% among non-eligible
    )
    
    # Advanced coursework participation (selective based on achievement)
    advanced_course_eligibility = (prior_achievement > 85) & (grade_level >= 10)
    advanced_courses = np.where(
        advanced_course_eligibility,
        np.random.binomial(1, 0.6, n_students),  # 60% of eligible take advanced courses
        np.random.binomial(1, 0.05, n_students)  # 5% of non-eligible
    )
    
    # Technology integration (varies by school resources)
    tech_integration_prob = np.clip(
        0.3 + (school_funding - 8000) / 10000 + 
        np.random.normal(0, 0.2, n_students), 0.1, 0.9
    )
    tech_integration = np.random.binomial(1, tech_integration_prob, n_students)
    
    # Mentoring program (targeted support)
    mentoring_prob = np.clip(
        0.2 + (prior_achievement < 70) * 0.3 + 
        free_lunch_eligible * 0.2 + 
        english_learner * 0.25, 0.1, 0.7
    )
    mentoring_program = np.random.binomial(1, mentoring_prob, n_students)
    
    # === INTERMEDIATE OUTCOMES ===
    
    # Student engagement (influenced by multiple factors)
    engagement_score = (
        70 +  # Base engagement
        (prior_achievement - 80) * 0.3 +  # Higher achievers more engaged
        tutoring_participation * 5 +
        advanced_courses * 8 +
        mentoring_program * 6 +
        tech_integration * 4 +
        -class_size * 0.5 +  # Smaller classes improve engagement
        teacher_experience * 0.3 +
        np.random.normal(0, 12, n_students)
    )
    engagement_score = np.clip(engagement_score, 30, 100)
    
    # School attendance (influenced by engagement and support)
    attendance_rate = (
        90 +  # Base attendance
        engagement_score * 0.1 +
        mentoring_program * 2 +
        -free_lunch_eligible * 3 +  # SES challenges
        np.random.normal(0, 5, n_students)
    )
    attendance_rate = np.clip(attendance_rate, 60, 99)
    
    # === FINAL OUTCOMES ===
    
    # Test score improvement (learning gains)
    learning_gains = (
        5 +  # Base improvement
        tutoring_participation * 8 +  # Tutoring effect
        advanced_courses * 6 +  # Challenging coursework
        mentoring_program * 4 +
        tech_integration * 3 +
        engagement_score * 0.15 +
        attendance_rate * 0.1 +
        teacher_experience * 0.2 +
        -class_size * 0.3 +  # Smaller classes help
        (school_funding - 8000) / 1000 +  # Resource effect
        np.random.normal(0, 8, n_students)
    )
    learning_gains = np.clip(learning_gains, -10, 25)
    
    # Final achievement (prior + gains)
    final_achievement = prior_achievement + learning_gains
    final_achievement = np.clip(final_achievement, 35, 105)
    
    # College readiness (based on final achievement and coursework)
    college_ready_prob = np.clip(
        (final_achievement - 70) / 30 +
        advanced_courses * 0.2 +
        engagement_score / 500,
        0.1, 0.95
    )
    college_ready = np.random.binomial(1, college_ready_prob, n_students)
    
    # Graduation likelihood
    graduation_prob = np.clip(
        0.7 + (final_achievement - 80) / 100 +
        attendance_rate / 500 +
        engagement_score / 500 +
        mentoring_program * 0.1,
        0.4, 0.98
    )
    graduated = np.random.binomial(1, graduation_prob, n_students)
    
    # === CREATE DATAFRAME ===
    
    educational_data = pd.DataFrame({
        # Demographics
        'student_id': range(1, n_students + 1),
        'grade_level': grade_level,
        'student_age': student_age.round(1),
        'gender': gender,
        'ethnicity': ethnicity,
        'family_income': family_income.round(0),
        'parent_education': parent_education,
        'english_learner': english_learner,
        'special_education': special_education,
        'free_lunch_eligible': free_lunch_eligible,
        
        # Prior achievement
        'prior_achievement': prior_achievement.round(1),
        
        # School characteristics
        'school_type': school_type,
        'teacher_experience': teacher_experience.round(1),
        'class_size': class_size.round(0),
        'school_funding': school_funding.round(0),
        
        # Interventions (treatments)
        'tutoring_participation': tutoring_participation,
        'advanced_courses': advanced_courses,
        'tech_integration': tech_integration,
        'mentoring_program': mentoring_program,
        
        # Intermediate outcomes
        'engagement_score': engagement_score.round(1),
        'attendance_rate': attendance_rate.round(1),
        
        # Final outcomes
        'learning_gains': learning_gains.round(1),
        'final_achievement': final_achievement.round(1),
        'college_ready': college_ready,
        'graduated': graduated
    })
    
    print("   ✅ Educational dataset generated with realistic causal structure")
    print(f"   • Students: {n_students:,} across grades 9-12")
    print(f"   • Interventions: Tutoring ({tutoring_participation.mean()*100:.1f}%), "
          f"Advanced courses ({advanced_courses.mean()*100:.1f}%), "
          f"Tech integration ({tech_integration.mean()*100:.1f}%), "
          f"Mentoring ({mentoring_program.mean()*100:.1f}%)")
    print(f"   • Outcomes: Learning gains (μ={learning_gains.mean():.1f}), "
          f"College ready ({college_ready.mean()*100:.1f}%), "
          f"Graduation ({graduated.mean()*100:.1f}%)")
    print()
    
    return educational_data

def demonstrate_causal_discovery_education():
    """Demonstrate causal discovery in educational context."""
    
    print("🔍 " + "="*80)
    print("   EDUCATIONAL CAUSAL DISCOVERY - Identifying Key Relationships")
    print("="*83)
    print()
    
    # Generate educational data
    edu_data = generate_educational_dataset(2500)
    
    # Initialize Enhanced CausalLLM for education domain
    enhanced_causallm = EnhancedCausalLLM(llm_provider="grok", significance_level=0.01)
    
    # Focus on key educational variables
    key_variables = [
        'prior_achievement', 'family_income', 'class_size', 'teacher_experience',
        'tutoring_participation', 'advanced_courses', 'tech_integration',
        'engagement_score', 'attendance_rate', 'learning_gains', 'college_ready'
    ]
    
    # Discover causal relationships
    print("🎯 Discovering causal relationships in educational data...")
    discovery_results = enhanced_causallm.discover_causal_relationships(
        data=edu_data[key_variables],
        variables=key_variables,
        domain='education'
    )
    
    # Display discovered relationships
    print("📚 DISCOVERED EDUCATIONAL CAUSAL RELATIONSHIPS")
    print("-" * 55)
    
    # Group by outcome type
    learning_edges = [e for e in discovery_results.discovered_edges 
                     if e.effect in ['learning_gains', 'college_ready']]
    engagement_edges = [e for e in discovery_results.discovered_edges 
                       if e.effect in ['engagement_score', 'attendance_rate']]
    
    print("🎓 Learning Outcomes:")
    for edge in sorted(learning_edges, key=lambda x: x.confidence, reverse=True)[:8]:
        print(f"  • {edge.cause} → {edge.effect}")
        print(f"    Confidence: {edge.confidence:.3f} | Effect: {edge.effect_size:.3f}")
        print(f"    {edge.interpretation[:80]}...")
        print()
    
    print("📈 Student Engagement:")
    for edge in sorted(engagement_edges, key=lambda x: x.confidence, reverse=True)[:5]:
        print(f"  • {edge.cause} → {edge.effect}")
        print(f"    Confidence: {edge.confidence:.3f} | Effect: {edge.effect_size:.3f}")
        print()
    
    # Domain insights
    print("🧠 EDUCATIONAL DOMAIN INSIGHTS")
    print("-" * 35)
    print(discovery_results.domain_insights)
    
    return discovery_results, edu_data

def analyze_intervention_effectiveness():
    """Analyze effectiveness of educational interventions using multiple methods."""
    
    print("📊 " + "="*80)
    print("   INTERVENTION EFFECTIVENESS ANALYSIS - Multi-Method Causal Inference")
    print("="*83)
    print()
    
    # Generate fresh educational data
    edu_data = generate_educational_dataset(2000)
    
    # Initialize Enhanced CausalLLM
    enhanced_causallm = EnhancedCausalLLM(llm_provider="grok")
    
    # Analyze tutoring program effectiveness
    print("🎯 ANALYZING TUTORING PROGRAM EFFECTIVENESS")
    print("-" * 50)
    
    tutoring_analysis = enhanced_causallm.estimate_causal_effect(
        data=edu_data,
        treatment='tutoring_participation',
        outcome='learning_gains',
        covariates=['prior_achievement', 'family_income', 'class_size', 
                   'free_lunch_eligible', 'english_learner'],
        method='comprehensive'
    )
    
    print("📈 Tutoring Program Results:")
    print(f"  • Effect on learning gains: {tutoring_analysis.primary_effect.effect_estimate:.2f} points")
    print(f"  • 95% Confidence Interval: [{tutoring_analysis.primary_effect.confidence_interval[0]:.2f}, "
          f"{tutoring_analysis.primary_effect.confidence_interval[1]:.2f}]")
    print(f"  • Statistical significance: p = {tutoring_analysis.primary_effect.p_value:.6f}")
    print(f"  • Sample size: {tutoring_analysis.primary_effect.sample_size:,} students")
    print(f"  • Analysis confidence: {tutoring_analysis.confidence_level}")
    print()
    print("Interpretation:")
    print(tutoring_analysis.primary_effect.interpretation)
    print()
    
    if tutoring_analysis.robustness_checks:
        print("🔄 Robustness Validation:")
        for i, check in enumerate(tutoring_analysis.robustness_checks, 1):
            print(f"  Method {i} ({check.method}): Effect = {check.effect_estimate:.2f}, p = {check.p_value:.4f}")
        print()
    
    # Analyze advanced coursework impact
    print("🎓 ANALYZING ADVANCED COURSEWORK IMPACT")
    print("-" * 45)
    
    advanced_analysis = enhanced_causallm.estimate_causal_effect(
        data=edu_data,
        treatment='advanced_courses',
        outcome='college_ready',
        covariates=['prior_achievement', 'family_income', 'grade_level', 
                   'parent_education', 'engagement_score'],
        method='comprehensive'
    )
    
    print("📊 Advanced Coursework Results:")
    college_ready_effect = advanced_analysis.primary_effect.effect_estimate
    print(f"  • Effect on college readiness: {college_ready_effect:.3f} probability increase")
    print(f"  • Percentage point increase: {college_ready_effect*100:.1f}%")
    print(f"  • Statistical significance: p = {advanced_analysis.primary_effect.p_value:.6f}")
    print(f"  • Analysis confidence: {advanced_analysis.confidence_level}")
    print()
    
    return tutoring_analysis, advanced_analysis, edu_data

def comprehensive_educational_policy_analysis():
    """Perform comprehensive analysis for educational policy recommendations."""
    
    print("🚀 " + "="*80)
    print("   COMPREHENSIVE EDUCATIONAL POLICY ANALYSIS")
    print("="*83)
    print("   Combining Discovery + Inference + Policy Recommendations")
    print("="*83)
    print()
    
    # Generate comprehensive educational dataset
    edu_data = generate_educational_dataset(3500)
    
    # Initialize Enhanced CausalLLM
    enhanced_causallm = EnhancedCausalLLM(llm_provider="grok")
    
    # Perform comprehensive analysis focusing on learning gains
    comprehensive_results = enhanced_causallm.comprehensive_analysis(
        data=edu_data,
        treatment='tutoring_participation',  # Primary intervention of interest
        outcome='learning_gains',           # Key educational outcome
        variables=[
            'prior_achievement', 'family_income', 'class_size', 'teacher_experience',
            'tutoring_participation', 'advanced_courses', 'tech_integration', 
            'mentoring_program', 'engagement_score', 'attendance_rate', 
            'learning_gains', 'college_ready'
        ],
        domain='education',
        covariates=['prior_achievement', 'family_income', 'free_lunch_eligible', 'class_size']
    )
    
    # Display comprehensive results
    print("🎯 COMPREHENSIVE ANALYSIS SUMMARY")
    print("-" * 40)
    print(f"Overall Analysis Confidence: {comprehensive_results.confidence_score:.3f}")
    print(f"Causal Relationships Discovered: {len(comprehensive_results.discovery_results.discovered_edges)}")
    print(f"Statistical Analyses Performed: {len(comprehensive_results.inference_results)}")
    print(f"Policy Insights Generated: {len(comprehensive_results.actionable_insights)}")
    print()
    
    # Key findings
    print("🔍 KEY EDUCATIONAL FINDINGS")
    print("-" * 30)
    for analysis_name, result in comprehensive_results.inference_results.items():
        if result.primary_effect.p_value < 0.05:
            effect = result.primary_effect.effect_estimate
            treatment = result.primary_effect.treatment
            outcome = result.primary_effect.outcome
            
            print(f"✅ {treatment.replace('_', ' ').title()} → {outcome.replace('_', ' ').title()}")
            print(f"   Effect: {effect:.2f} units (p = {result.primary_effect.p_value:.4f})")
            print(f"   Confidence: {result.confidence_level}")
            print()
    
    # Actionable policy insights
    print("💡 ACTIONABLE POLICY INSIGHTS")
    print("-" * 35)
    for i, insight in enumerate(comprehensive_results.actionable_insights[:8], 1):
        print(f"{i}. {insight}")
    print()
    
    # Generate specific intervention recommendations
    print("🎯 POLICY INTERVENTION RECOMMENDATIONS")
    print("-" * 45)
    
    interventions = enhanced_causallm.generate_intervention_recommendations(
        comprehensive_results,
        target_outcome='learning_gains',
        budget_constraint=1000000  # $1M education budget
    )
    
    print("🏆 Priority Interventions:")
    for i, intervention in enumerate(interventions['primary_interventions'][:3], 1):
        print(f"\n{i}. {intervention['target_variable'].replace('_', ' ').title()} Program")
        print(f"   Expected Impact: {intervention['expected_outcome_change']}")
        print(f"   Confidence Level: {intervention['confidence_level']:.3f}")
        print(f"   Implementation Timeline: {intervention['timeline']}")
        print(f"   Success Metrics: {', '.join(intervention['success_metrics'])}")
    
    print("\n🔬 Supporting Interventions:")
    for i, intervention in enumerate(interventions['secondary_interventions'][:2], 1):
        print(f"{i}. {intervention['target_variable'].replace('_', ' ').title()}")
        print(f"   Impact: {intervention['expected_outcome_change']}")
    
    return comprehensive_results

def analyze_equity_and_heterogeneous_effects():
    """Analyze how intervention effects vary across different student subgroups."""
    
    print("⚖️ " + "="*80)
    print("   EDUCATIONAL EQUITY ANALYSIS - Heterogeneous Treatment Effects")
    print("="*83)
    print()
    
    # Generate educational data
    edu_data = generate_educational_dataset(2800)
    
    # Initialize Enhanced CausalLLM
    enhanced_causallm = EnhancedCausalLLM(llm_provider="grok")
    
    print("🎯 ANALYZING TUTORING EFFECTS BY STUDENT SUBGROUPS")
    print("-" * 55)
    
    # Define subgroups for analysis
    subgroups = {
        'Low Income': edu_data['free_lunch_eligible'] == 1,
        'Higher Income': edu_data['free_lunch_eligible'] == 0,
        'English Learners': edu_data['english_learner'] == 1,
        'Native English': edu_data['english_learner'] == 0,
        'Low Prior Achievement': edu_data['prior_achievement'] < 70,
        'High Prior Achievement': edu_data['prior_achievement'] >= 80,
        'Underrepresented': edu_data['ethnicity'].isin(['hispanic', 'black']),
        'Traditional': edu_data['ethnicity'].isin(['white', 'asian'])
    }
    
    subgroup_effects = {}
    
    for group_name, group_mask in subgroups.items():
        if group_mask.sum() < 100:  # Skip if too few observations
            continue
            
        group_data = edu_data[group_mask]
        
        try:
            # Analyze tutoring effect for this subgroup
            group_analysis = enhanced_causallm.estimate_causal_effect(
                data=group_data,
                treatment='tutoring_participation',
                outcome='learning_gains',
                covariates=['prior_achievement', 'class_size', 'teacher_experience'],
                method='regression'  # Use faster method for subgroup analysis
            )
            
            subgroup_effects[group_name] = {
                'effect': group_analysis.primary_effect.effect_estimate,
                'p_value': group_analysis.primary_effect.p_value,
                'sample_size': len(group_data),
                'ci_lower': group_analysis.primary_effect.confidence_interval[0],
                'ci_upper': group_analysis.primary_effect.confidence_interval[1]
            }
            
        except Exception as e:
            print(f"Warning: Could not analyze {group_name}: {e}")
    
    # Display subgroup effects
    print("📊 TUTORING EFFECTS BY STUDENT SUBGROUP")
    print("-" * 45)
    print(f"{'Group':<20} {'Effect':<8} {'95% CI':<20} {'P-value':<10} {'N':<6}")
    print("-" * 70)
    
    for group, results in subgroup_effects.items():
        if results['p_value'] < 0.05:
            significance = "***" if results['p_value'] < 0.001 else "**" if results['p_value'] < 0.01 else "*"
        else:
            significance = ""
            
        ci_str = f"[{results['ci_lower']:.2f}, {results['ci_upper']:.2f}]"
        print(f"{group:<20} {results['effect']:<8.2f} {ci_str:<20} "
              f"{results['p_value']:<10.4f} {results['sample_size']:<6} {significance}")
    
    print("\n*** p<0.001, ** p<0.01, * p<0.05")
    print()
    
    # Identify equity implications
    print("⚖️ EQUITY IMPLICATIONS")
    print("-" * 25)
    
    # Compare effects for equity-relevant groups
    equity_comparisons = [
        ('Low Income', 'Higher Income'),
        ('English Learners', 'Native English'),
        ('Low Prior Achievement', 'High Prior Achievement'),
        ('Underrepresented', 'Traditional')
    ]
    
    for group1, group2 in equity_comparisons:
        if group1 in subgroup_effects and group2 in subgroup_effects:
            effect1 = subgroup_effects[group1]['effect']
            effect2 = subgroup_effects[group2]['effect']
            difference = effect1 - effect2
            
            if abs(difference) > 1.0:  # Meaningful difference threshold
                equity_implication = "reduces" if difference > 0 else "may increase"
                print(f"• Tutoring {equity_implication} gaps between {group1} and {group2}")
                print(f"  Effect difference: {difference:.2f} points")
                print()
    
    return subgroup_effects

def estimate_cost_effectiveness():
    """Estimate cost-effectiveness of educational interventions."""
    
    print("💰 " + "="*80)
    print("   COST-EFFECTIVENESS ANALYSIS - ROI of Educational Interventions")
    print("="*83)
    print()
    
    # Generate data and get intervention effects
    edu_data = generate_educational_dataset(2200)
    enhanced_causallm = EnhancedCausalLLM(llm_provider="grok")
    
    # Define intervention costs (annual per student)
    intervention_costs = {
        'tutoring_participation': 1200,      # $1,200 per student per year
        'mentoring_program': 800,            # $800 per student per year  
        'tech_integration': 400,             # $400 per student per year
        'advanced_courses': 300              # $300 additional per student
    }
    
    # Estimate effects and calculate ROI
    intervention_analysis = {}
    
    for intervention, cost in intervention_costs.items():
        if intervention in edu_data.columns:
            print(f"📈 Analyzing {intervention.replace('_', ' ').title()}")
            
            try:
                analysis = enhanced_causallm.estimate_causal_effect(
                    data=edu_data,
                    treatment=intervention,
                    outcome='learning_gains',
                    covariates=['prior_achievement', 'family_income', 'class_size'],
                    method='regression'
                )
                
                if analysis.primary_effect.p_value < 0.1:  # Significant effect
                    effect_size = analysis.primary_effect.effect_estimate
                    
                    # Estimate long-term value (simplified model)
                    # Each point of learning gain worth ~$2,000 in lifetime earnings
                    lifetime_value = effect_size * 2000
                    roi = (lifetime_value - cost) / cost * 100
                    
                    intervention_analysis[intervention] = {
                        'effect_size': effect_size,
                        'p_value': analysis.primary_effect.p_value,
                        'cost': cost,
                        'lifetime_value': lifetime_value,
                        'roi': roi,
                        'confidence': analysis.confidence_level
                    }
                    
                    print(f"   Effect: {effect_size:.2f} learning gain points")
                    print(f"   Estimated lifetime value: ${lifetime_value:,.0f}")
                    print(f"   Annual cost: ${cost:,.0f}")
                    print(f"   ROI: {roi:.0f}%")
                    print(f"   Confidence: {analysis.confidence_level}")
                    print()
                    
            except Exception as e:
                print(f"   Could not analyze {intervention}: {e}")
                print()
    
    # Rank interventions by ROI
    if intervention_analysis:
        print("🏆 INTERVENTION RANKING BY ROI")
        print("-" * 35)
        
        sorted_interventions = sorted(
            intervention_analysis.items(), 
            key=lambda x: x[1]['roi'], 
            reverse=True
        )
        
        print(f"{'Rank':<5} {'Intervention':<20} {'Effect':<8} {'ROI':<8} {'Confidence'}")
        print("-" * 60)
        
        for i, (intervention, results) in enumerate(sorted_interventions, 1):
            name = intervention.replace('_', ' ').title()[:18]
            print(f"{i:<5} {name:<20} {results['effect_size']:<8.2f} "
                  f"{results['roi']:<8.0f}% {results['confidence']}")
        
        print()
        print("💡 INVESTMENT RECOMMENDATIONS")
        print("-" * 35)
        
        top_intervention = sorted_interventions[0]
        print(f"🥇 Highest ROI: {top_intervention[0].replace('_', ' ').title()}")
        print(f"   Return on Investment: {top_intervention[1]['roi']:.0f}%")
        print(f"   For every $1 invested, expect ${top_intervention[1]['roi']/100 + 1:.2f} in returns")
        print()
        
        if len(sorted_interventions) > 1:
            print("📊 Portfolio Approach Recommended:")
            print("   Combine high-ROI interventions for maximum impact")
            total_effect = sum(r[1]['effect_size'] for r in sorted_interventions[:2])
            total_cost = sum(r[1]['cost'] for r in sorted_interventions[:2])
            print(f"   Combined effect: {total_effect:.2f} learning gain points")
            print(f"   Combined annual cost: ${total_cost:,.0f} per student")
    
    return intervention_analysis

def main():
    """Run the comprehensive educational outcomes causal analysis demonstration."""
    
    print("🌟 " + "="*80)
    print("   ENHANCED CAUSALLM: EDUCATIONAL OUTCOMES ANALYSIS")
    print("="*83)
    print("   Comprehensive Causal Analysis for Educational Policy & Interventions")
    print("="*83)
    print()
    
    print("🎯 ANALYSIS OVERVIEW")
    print("-" * 22)
    print("This demonstration showcases CausalLLM's capabilities for:")
    print("• Automated discovery of educational causal relationships")
    print("• Rigorous evaluation of intervention effectiveness")  
    print("• Policy recommendations based on causal evidence")
    print("• Equity analysis across different student subgroups")
    print("• Cost-effectiveness and ROI calculations")
    print("• Multi-method statistical validation")
    print()
    
    try:
        # Analysis 1: Causal Discovery
        print("PHASE 1: Causal Structure Discovery in Education")
        print("="*50)
        discovery_results, edu_data = demonstrate_causal_discovery_education()
        print("\n" + "="*83 + "\n")
        
        # Analysis 2: Intervention Effectiveness
        print("PHASE 2: Educational Intervention Effectiveness Analysis")
        print("="*55)
        tutoring_analysis, advanced_analysis, _ = analyze_intervention_effectiveness()
        print("\n" + "="*83 + "\n")
        
        # Analysis 3: Comprehensive Policy Analysis
        print("PHASE 3: Comprehensive Educational Policy Analysis")
        print("="*50)
        comprehensive_results = comprehensive_educational_policy_analysis()
        print("\n" + "="*83 + "\n")
        
        # Analysis 4: Equity Analysis
        print("PHASE 4: Educational Equity and Heterogeneous Effects")
        print("="*52)
        subgroup_effects = analyze_equity_and_heterogeneous_effects()
        print("\n" + "="*83 + "\n")
        
        # Analysis 5: Cost-Effectiveness
        print("PHASE 5: Cost-Effectiveness and Return on Investment")
        print("="*52)
        cost_analysis = estimate_cost_effectiveness()
        print("\n" + "="*83 + "\n")
        
        # Summary and Impact
        print("🎯 EDUCATIONAL ANALYSIS COMPLETE")
        print("="*35)
        print("✅ Comprehensive causal discovery in educational domain")
        print("✅ Multi-method intervention effectiveness evaluation")
        print("✅ Evidence-based policy recommendations generated")
        print("✅ Educational equity implications identified")
        print("✅ Cost-effectiveness analysis with ROI calculations")
        print("✅ Actionable insights for educational leaders")
        print()
        
        print("🚀 KEY INSIGHTS FOR EDUCATIONAL POLICY:")
        print("-" * 45)
        print("1. CausalLLM enables data-driven educational decision making")
        print("2. Rigorous causal analysis identifies effective interventions")
        print("3. Equity analysis ensures interventions benefit all students")
        print("4. Cost-effectiveness analysis maximizes educational ROI")
        print("5. Multi-method validation provides robust evidence base")
        print()
        
        print("📚 IMPACT ON EDUCATION SECTOR:")
        print("-" * 35)
        print("• Transform educational research from correlational to causal")
        print("• Enable evidence-based resource allocation decisions")
        print("• Identify interventions that reduce achievement gaps")
        print("• Optimize limited educational budgets for maximum student impact")
        print("• Support educators with data-driven insights")
        print()
        
        print("🔬 FRAMEWORK CAPABILITIES DEMONSTRATED:")
        print("-" * 45)
        print("✅ Domain-Specific Intelligence: Educational context and expertise")
        print("✅ Automated Discovery: Found key relationships without prior specification")
        print("✅ Statistical Rigor: Multiple methods with robustness validation")
        print("✅ Heterogeneous Effects: Subgroup analysis for equity insights")
        print("✅ Business Value: ROI and cost-effectiveness calculations")
        print("✅ Actionable Insights: Specific policy recommendations with confidence levels")
        
    except Exception as e:
        print(f"❌ Analysis failed with error: {e}")
        print("This may be due to missing dependencies or computational issues.")
        print("Please check requirements and try again.")

if __name__ == "__main__":
    main()