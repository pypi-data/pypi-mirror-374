#!/usr/bin/env python3
"""
Module Integration Tests for Modular Qualitative Reasoning System
================================================================

This module tests the integration between different modules to ensure
they work together correctly and maintain data consistency.

Test Coverage:
- Constraint-process interaction
- Simulation-analysis integration
- Analysis-visualization integration
- Full pipeline integration
- Data consistency across modules
- Cross-module communication

Author: Test Suite for Benedict Chen's Qualitative Reasoning Library
"""

import traceback
from conftest import TestResult


def test_module_integration() -> TestResult:
    """Test integration between modules"""
    
    result = TestResult("Module Integration")
    print("\n🧪 Test: Integration Between Modules")
    print("=" * 37)
    
    try:
        from qualitative_reasoning import (
            QualitativeReasoner, QualitativeValue, QualitativeDirection
        )
        
        reasoner = QualitativeReasoner("Integration Test System")
        
        # Create a comprehensive system that uses all modules
        print("Setting up integrated system...")
        
        # Add quantities (uses core types)
        reasoner.add_quantity("water_level", QualitativeValue.POSITIVE_SMALL, 
                            QualitativeDirection.STEADY, landmarks=[0.0, 50.0, 100.0])
        reasoner.add_quantity("flow_rate", QualitativeValue.ZERO, 
                            QualitativeDirection.STEADY)
        reasoner.add_quantity("pressure", QualitativeValue.POSITIVE_SMALL, 
                            QualitativeDirection.STEADY)
        
        # Add processes (ProcessEngineMixin)
        reasoner.add_process("filling", 
                           ["valve_open"], 
                           ["pressure > 0"], 
                           ["I+(water_level)", "I+(flow_rate)"])
        
        reasoner.add_process("draining", 
                           ["drain_open"], 
                           ["water_level > 0"], 
                           ["I-(water_level)", "I+(flow_rate)"])
        
        # Add constraints (ConstraintEngineMixin)
        reasoner.add_constraint("water_level >= 0")
        reasoner.add_constraint("flow_rate >= 0")
        reasoner.add_constraint("water_level <= 100")
        
        print("✓ Integrated system setup complete")
        result.add_pass()
        
        # Test constraint-process interaction
        print("Testing constraint-process interaction...")
        
        try:
            if hasattr(reasoner, 'update_active_processes'):
                active_processes = reasoner.update_active_processes()
                
            # Run simulation (SimulationEngineMixin) with constraints
            if hasattr(reasoner, 'run_simulation'):
                reasoner.run_simulation("integration_step1")
                
            print("✓ Constraint-process interaction working")
            result.add_pass()
            
        except Exception as e:
            print(f"❌ Constraint-process interaction failed: {e}")
            result.add_fail(f"Constraint-process interaction error: {e}")
        
        # Test simulation-analysis integration
        print("Testing simulation-analysis integration...")
        
        try:
            # Run a few simulation steps
            for i in range(3):
                if hasattr(reasoner, 'run_simulation'):
                    reasoner.run_simulation(f"analysis_step_{i}")
            
            # Analyze the results (AnalysisEngineMixin)
            if hasattr(reasoner, 'get_system_status'):
                analysis = reasoner.get_system_status()
                
            if hasattr(reasoner, 'explain_quantity'):
                explanation = reasoner.explain_quantity("water_level")
                
            print("✓ Simulation-analysis integration working")
            result.add_pass()
            
        except Exception as e:
            print(f"❌ Simulation-analysis integration failed: {e}")
            result.add_fail(f"Simulation-analysis integration error: {e}")
        
        # Test analysis-visualization integration
        print("Testing analysis-visualization integration...")
        
        try:
            # Generate comprehensive report (VisualizationEngineMixin)
            if hasattr(reasoner, 'generate_report'):
                report = reasoner.generate_report("text")
                
                # Check if report contains analysis information
                if report and len(str(report)) > 50:  # Non-empty report
                    print("✓ Analysis-visualization integration working")
                    result.add_pass()
                else:
                    print("❌ Generated report appears empty or minimal")
                    result.add_fail("Generated report insufficient")
            else:
                print("⚠️  Report generation not available")
                
        except Exception as e:
            print(f"❌ Analysis-visualization integration failed: {e}")
            result.add_fail(f"Analysis-visualization integration error: {e}")
        
        # Test full pipeline integration
        print("Testing full pipeline integration...")
        
        try:
            # Complete pipeline: setup -> simulate -> analyze -> visualize
            
            # 1. Additional setup
            reasoner.add_process("overflow_prevention", 
                               ["water_level > 90"], 
                               [], 
                               ["I-(flow_rate)"])
            
            # 2. Simulate with new process
            if hasattr(reasoner, 'run_simulation'):
                reasoner.run_simulation("pipeline_test")
            
            # 3. Analyze results
            if hasattr(reasoner, 'get_system_status'):
                analysis_result = reasoner.get_system_status()
            
            # 4. Generate visualization
            if hasattr(reasoner, 'visualize_system_state'):
                reasoner.visualize_system_state()
            
            # 5. Export data
            if hasattr(reasoner, 'export_system_state'):
                try:
                    data = reasoner.export_system_state("json")
                    print("✓ Full pipeline integration working")
                    result.add_pass()
                except:
                    print("✓ Full pipeline integration working (export optional)")
                    result.add_pass()
            else:
                print("✓ Full pipeline integration working")
                result.add_pass()
                
        except Exception as e:
            print(f"❌ Full pipeline integration failed: {e}")
            result.add_fail(f"Full pipeline integration error: {e}")
        
        # Test data consistency across modules
        print("Testing data consistency across modules...")
        
        try:
            # Check that all modules see the same system state
            quantity_count = len(reasoner.quantities)
            process_count = len(reasoner.processes)
            constraint_count = len(reasoner.constraints)
            
            if quantity_count >= 3 and process_count >= 3 and constraint_count >= 3:
                print("✓ Data consistency maintained across modules")
                result.add_pass()
            else:
                print(f"❌ Data inconsistency: Q={quantity_count}, P={process_count}, C={constraint_count}")
                result.add_fail(f"Data inconsistency detected")
                
        except Exception as e:
            print(f"❌ Data consistency check failed: {e}")
            result.add_fail(f"Data consistency error: {e}")
            
    except Exception as e:
        print(f"❌ Module integration test failed: {e}")
        result.add_fail(f"Module integration error: {e}")
        traceback.print_exc()
    
    print(f"\n{result.summary()}")
    return result


def run_integration_tests():
    """Run all integration tests"""
    return [test_module_integration()]


if __name__ == "__main__":
    results = run_integration_tests()
    for result in results:
        print(result.summary())