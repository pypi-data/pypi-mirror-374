#!/usr/bin/env python3
"""
Basic Initialization Tests for Modular Qualitative Reasoning System
==================================================================

This module tests the basic initialization and import functionality
of the modular qualitative reasoning system.

Test Coverage:
- Core type imports
- Factory function imports  
- Analysis and visualization type imports
- Basic reasoner creation
- Configured reasoner creation
- Attribute validation
- Mixin method availability

Author: Test Suite for Benedict Chen's Qualitative Reasoning Library
"""

import traceback
from conftest import TestResult


def test_basic_initialization() -> TestResult:
    """Test basic initialization of the modular QR system"""
    
    result = TestResult("Basic Initialization")
    print("\n🧪 Test: Basic Initialization of Modular QR System")
    print("=" * 55)
    
    try:
        # Test imports from main module
        print("Testing imports...")
        from qualitative_reasoning import (
            QualitativeReasoner, 
            QualitativeValue, 
            QualitativeDirection,
            QualitativeQuantity,
            QualitativeState,
            QualitativeProcess,
            ConstraintEvaluationMethod,
            ConstraintEvaluationConfig
        )
        print("✓ Core types imported")
        result.add_pass()
        
        # Test factory functions import
        from qualitative_reasoning import (
            create_educational_reasoner,
            create_research_reasoner,
            create_production_reasoner,
            create_demo_reasoner
        )
        print("✓ Factory functions imported")
        result.add_pass()
        
        # Test analysis and visualization imports
        from qualitative_reasoning import (
            CausalChain,
            RelationshipAnalysis,
            BehaviorExplanation,
            VisualizationConfig,
            VisualizationReport
        )
        print("✓ Analysis and visualization types imported successfully")
        result.add_pass()
        
        # Test basic reasoner creation
        reasoner = QualitativeReasoner("Test System")
        if reasoner.domain_name == "Test System":
            print("✓ Basic reasoner creation successful")
            result.add_pass()
        else:
            print("❌ Basic reasoner creation failed - incorrect domain name")
            result.add_fail("Reasoner domain name mismatch")
        
        # Test reasoner with configuration
        config = ConstraintEvaluationConfig(
            evaluation_method=ConstraintEvaluationMethod.AST_SAFE,
            strict_mode=False
        )
        config_reasoner = QualitativeReasoner("Configured System", constraint_config=config)
        if hasattr(config_reasoner, 'constraint_config'):
            print("✓ Configured reasoner creation successful")
            result.add_pass()
        else:
            print("❌ Configured reasoner creation failed")
            result.add_fail("Configured reasoner missing constraint_config")
        
        # Test that all expected attributes are present
        expected_attrs = [
            'domain_name', 'quantities', 'processes', 'constraints', 
            'state_history', 'current_state', 'causal_graph'
        ]
        
        missing_attrs = []
        for attr in expected_attrs:
            if not hasattr(reasoner, attr):
                missing_attrs.append(attr)
        
        if not missing_attrs:
            print("✓ All expected attributes present")
            result.add_pass()
        else:
            print(f"❌ Missing attributes: {missing_attrs}")
            result.add_fail(f"Missing attributes: {missing_attrs}")
            
        # Test mixin inheritance - using actual available methods
        mixin_methods = [
            'add_constraint',                          # ConstraintEngineMixin
            'add_process', 'update_active_processes',  # ProcessEngineMixin
            'run_simulation', 'qualitative_simulation_step',  # SimulationEngineMixin
            'explain_quantity', 'get_system_status',   # AnalysisEngineMixin
            'generate_report', 'visualize_system_state'  # VisualizationEngineMixin
        ]
        
        missing_methods = []
        for method in mixin_methods:
            if not hasattr(reasoner, method):
                missing_methods.append(method)
        
        if not missing_methods:
            print("✓ All mixin methods available")
            result.add_pass()
        else:
            print(f"❌ Missing mixin methods: {missing_methods}")
            result.add_fail(f"Missing mixin methods: {missing_methods}")
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        result.add_fail(f"Import error: {e}")
    except Exception as e:
        print(f"❌ Initialization test failed: {e}")
        result.add_fail(f"Initialization error: {e}")
    
    print(f"\n{result.summary()}")
    return result


def run_initialization_tests():
    """Run all initialization tests"""
    return [test_basic_initialization()]


if __name__ == "__main__":
    results = run_initialization_tests()
    for result in results:
        print(result.summary())