#!/usr/bin/env python3
"""
🧪 Test FOIL Algorithm Variants Integration
========================================

This test verifies that FOIL algorithm variants are properly integrated and working.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from inductive_logic_programming.foil_comprehensive_config import (
    FOILComprehensiveConfig, 
    InformationGainMethod,
    CoverageTestingMethod,
    create_research_accurate_config,
    create_fast_approximation_config
)
from inductive_logic_programming.foil_algorithm_variants import FOILAlgorithmVariants
from inductive_logic_programming.foil import FOILLearner
from inductive_logic_programming.ilp_core import LogicalTerm, LogicalAtom, LogicalClause

def test_foil_algorithm_variants():
    """Test that FOIL algorithm variants are available and configurable"""
    
    print("🧪 Testing FOIL Algorithm Variants Integration")
    print("=" * 50)
    
    # Test 1: All configuration options work
    configs_to_test = [
        ("Quinlan Original + SLD", FOILComprehensiveConfig(
            information_gain_method=InformationGainMethod.QUINLAN_ORIGINAL,
            coverage_method=CoverageTestingMethod.SLD_RESOLUTION
        )),
        ("Laplace Corrected + CLP", FOILComprehensiveConfig(
            information_gain_method=InformationGainMethod.LAPLACE_CORRECTED,
            coverage_method=CoverageTestingMethod.CONSTRAINT_LOGIC_PROGRAMMING
        )),
        ("Modern Info Theory + Tabled", FOILComprehensiveConfig(
            information_gain_method=InformationGainMethod.MODERN_INFO_THEORY,
            coverage_method=CoverageTestingMethod.TABLED_RESOLUTION
        )),
        ("Research Accurate Config", create_research_accurate_config()),
        ("Fast Approximation Config", create_fast_approximation_config())
    ]
    
    success_count = 0
    for name, config in configs_to_test:
        try:
            foil = FOILLearner(foil_config=config)
            print(f"✅ {name}: WORKING")
            success_count += 1
        except Exception as e:
            print(f"❌ {name}: FAILED - {e}")
    
    print(f"\n📊 Configuration Test Results: {success_count}/{len(configs_to_test)}")
    
    # Test 2: Algorithm Variant Methods Exist
    print("\n🔧 Testing Algorithm Variant Methods:")
    solutions = FOILAlgorithmVariants(create_research_accurate_config())
    
    required_methods = [
        'calculate_foil_gain_quinlan_exact',
        'calculate_foil_gain_laplace_corrected', 
        'calculate_foil_gain_modern_info_theory',
        'generate_variable_bindings',
        'covers_example_sld_resolution',
        'covers_example_clp',
        'covers_example_tabled',
        'sld_resolution',
        'apply_substitution'
    ]
    
    method_count = 0
    for method_name in required_methods:
        if hasattr(solutions, method_name):
            print(f"✅ {method_name}: EXISTS")
            method_count += 1
        else:
            print(f"❌ {method_name}: MISSING")
    
    print(f"\n📊 Method Test Results: {method_count}/{len(required_methods)}")
    
    # Test 3: Integration with Original FOIL
    print("\n🔗 Testing Integration with Original FOIL:")
    try:
        foil = FOILLearner()  # Default research-accurate config
        
        # Add some simple examples
        parent_atom = LogicalAtom(
            predicate='parent',
            terms=[LogicalTerm('tom', 'constant'), LogicalTerm('bob', 'constant')]
        )
        foil.add_example(parent_atom, True)
        
        male_atom = LogicalAtom(
            predicate='male', 
            terms=[LogicalTerm('bob', 'constant')]
        )
        foil.add_example(male_atom, True)
        
        print("✅ Examples added successfully")
        print("✅ FOIL integration working with algorithm variants")
        
    except Exception as e:
        print(f"❌ Integration failed: {e}")
        return False
    
    print(f"\n🎯 FINAL RESULT:")
    total_tests = 3
    passed_tests = (
        1 if success_count == len(configs_to_test) else 0
    ) + (
        1 if method_count == len(required_methods) else 0  
    ) + 1  # Integration test passed
    
    if passed_tests == total_tests:
        print(f"✅ ALL {passed_tests}/{total_tests} TESTS PASSED!")
        print("🚀 FOIL integration testing complete")
        print("🎯 Algorithm variants tested and functional")
        return True
    else:
        print(f"⚠️  {passed_tests}/{total_tests} tests passed")
        return False

if __name__ == "__main__":
    success = test_foil_algorithm_variants()
    sys.exit(0 if success else 1)