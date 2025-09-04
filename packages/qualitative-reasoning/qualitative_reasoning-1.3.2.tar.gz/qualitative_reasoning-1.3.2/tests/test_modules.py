#!/usr/bin/env python3
"""
Individual Module Tests for Modular Qualitative Reasoning System
==================================================================

This module tests each mixin module's functionality individually
to ensure proper method availability and basic operation.

Test Coverage:
- ConstraintEngineMixin methods and functionality
- ProcessEngineMixin methods and functionality
- SimulationEngineMixin methods and functionality
- AnalysisEngineMixin methods and functionality
- VisualizationEngineMixin methods and functionality
- Method Resolution Order (MRO) validation

Author: Test Suite for Benedict Chen's Qualitative Reasoning Library
"""

import traceback
from conftest import TestResult


def test_individual_modules() -> TestResult:
    """Test each module's functionality individually"""
    
    result = TestResult("Individual Modules")
    print("\n🧪 Test: Individual Module Functionality")
    print("=" * 40)
    
    try:
        from qualitative_reasoning import QualitativeReasoner, QualitativeValue
        
        reasoner = QualitativeReasoner("Module Test System")
        
        # Set up basic system for module testing
        reasoner.add_quantity("temp", QualitativeValue.POSITIVE_SMALL)
        reasoner.add_quantity("pressure", QualitativeValue.ZERO)
        reasoner.add_process("heating", ["heat_on"], ["temp >= 0"], ["I+(temp)"])
        reasoner.add_constraint("temp > 0")
        
        # Test ConstraintEngineMixin
        print("Testing ConstraintEngineMixin...")
        
        constraint_methods = ['add_constraint', 'configure_security']
        constraint_working = True
        
        for method_name in constraint_methods:
            if not hasattr(reasoner, method_name):
                print(f"   ❌ Missing method: {method_name}")
                constraint_working = False
        
        if constraint_working:
            try:
                reasoner.add_constraint("pressure >= 0")
                print("✓ ConstraintEngineMixin working correctly")
                result.add_pass()
            except Exception as e:
                print(f"❌ ConstraintEngineMixin failed: {e}")
                result.add_fail(f"ConstraintEngineMixin error: {e}")
        else:
            print("❌ ConstraintEngineMixin missing methods")
            result.add_fail("ConstraintEngineMixin missing methods")
        
        # Test ProcessEngineMixin
        print("Testing ProcessEngineMixin...")
        
        process_methods = ['add_process', 'update_active_processes']
        process_working = True
        
        for method_name in process_methods:
            if not hasattr(reasoner, method_name):
                print(f"   ❌ Missing method: {method_name}")
                process_working = False
        
        if process_working:
            try:
                reasoner.add_process("cooling", ["heat_off"], ["temp > 0"], ["I-(temp)"])
                if hasattr(reasoner, 'update_active_processes'):
                    reasoner.update_active_processes()
                print("✓ ProcessEngineMixin working correctly")
                result.add_pass()
            except Exception as e:
                print(f"❌ ProcessEngineMixin failed: {e}")
                result.add_fail(f"ProcessEngineMixin error: {e}")
        else:
            print("❌ ProcessEngineMixin missing methods")
            result.add_fail("ProcessEngineMixin missing methods")
        
        # Test SimulationEngineMixin
        print("Testing SimulationEngineMixin...")
        
        simulation_methods = ['run_simulation']
        simulation_working = True
        
        for method_name in simulation_methods:
            if not hasattr(reasoner, method_name):
                print(f"   ❌ Missing method: {method_name}")
                simulation_working = False
        
        if simulation_working:
            try:
                reasoner.run_simulation("module_test")
                print("✓ SimulationEngineMixin working correctly")
                result.add_pass()
            except Exception as e:
                print(f"❌ SimulationEngineMixin failed: {e}")
                result.add_fail(f"SimulationEngineMixin error: {e}")
        else:
            print("❌ SimulationEngineMixin missing methods")
            result.add_fail("SimulationEngineMixin missing methods")
        
        # Test AnalysisEngineMixin
        print("Testing AnalysisEngineMixin...")
        
        analysis_methods = ['get_system_status', 'explain_quantity']
        analysis_working = True
        
        for method_name in analysis_methods:
            if not hasattr(reasoner, method_name):
                print(f"   ❌ Missing method: {method_name}")
                analysis_working = False
        
        if analysis_working:
            try:
                if hasattr(reasoner, 'get_system_status'):
                    reasoner.get_system_status()
                if hasattr(reasoner, 'explain_quantity'):
                    reasoner.explain_quantity("temp")
                print("✓ AnalysisEngineMixin working correctly")
                result.add_pass()
            except Exception as e:
                print(f"❌ AnalysisEngineMixin failed: {e}")
                result.add_fail(f"AnalysisEngineMixin error: {e}")
        else:
            print("❌ AnalysisEngineMixin missing methods")
            result.add_fail("AnalysisEngineMixin missing methods")
        
        # Test VisualizationEngineMixin
        print("Testing VisualizationEngineMixin...")
        
        viz_methods = ['generate_report', 'visualize_system_state']
        viz_working = True
        
        for method_name in viz_methods:
            if not hasattr(reasoner, method_name):
                print(f"   ❌ Missing method: {method_name}")
                viz_working = False
        
        if viz_working:
            try:
                if hasattr(reasoner, 'generate_report'):
                    reasoner.generate_report("text")
                if hasattr(reasoner, 'visualize_system_state'):
                    reasoner.visualize_system_state()
                print("✓ VisualizationEngineMixin working correctly")
                result.add_pass()
            except Exception as e:
                print(f"❌ VisualizationEngineMixin failed: {e}")
                result.add_fail(f"VisualizationEngineMixin error: {e}")
        else:
            print("❌ VisualizationEngineMixin missing methods")
            result.add_fail("VisualizationEngineMixin missing methods")
        
        # Test method resolution order (MRO)
        print("Testing method resolution order...")
        
        mro = QualitativeReasoner.__mro__
        expected_mixins = [
            'ConstraintEngineMixin',
            'ProcessEngineMixin', 
            'SimulationEngineMixin',
            'AnalysisEngineMixin',
            'VisualizationEngineMixin'
        ]
        
        mro_names = [cls.__name__ for cls in mro]
        missing_mixins = [name for name in expected_mixins if name not in mro_names]
        
        if not missing_mixins:
            print("✓ Method resolution order correct - all mixins present")
            result.add_pass()
        else:
            print(f"❌ Missing mixins in MRO: {missing_mixins}")
            result.add_fail(f"Missing mixins in MRO: {missing_mixins}")
            
    except Exception as e:
        print(f"❌ Individual modules test failed: {e}")
        result.add_fail(f"Individual modules error: {e}")
        traceback.print_exc()
    
    print(f"\n{result.summary()}")
    return result


def run_module_tests():
    """Run all module tests"""
    return [test_individual_modules()]


if __name__ == "__main__":
    results = run_module_tests()
    for result in results:
        print(result.summary())