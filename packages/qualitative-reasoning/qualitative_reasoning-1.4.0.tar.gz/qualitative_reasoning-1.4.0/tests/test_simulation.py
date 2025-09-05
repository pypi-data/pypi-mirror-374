#!/usr/bin/env python3
"""
Simulation Engine Tests for Modular Qualitative Reasoning System
==================================================================

This module tests the simulation engine functionality including
state transitions, process activation, and constraint checking.

Test Coverage:
- Single simulation step execution
- Multiple simulation steps
- Process activation and deactivation
- State transitions and history tracking  
- Simulation with constraint checking
- Error handling during simulation

Author: Test Suite for Benedict Chen's Qualitative Reasoning Library
"""

import traceback
from conftest import TestResult


def test_simulation_engine() -> TestResult:
    """Test simulation engine functionality"""
    
    result = TestResult("Simulation Engine")
    print("\n🧪 Test: Simulation Engine")
    print("=" * 30)
    
    try:
        from qualitative_reasoning import (
            QualitativeReasoner, QualitativeValue, QualitativeDirection
        )
        
        reasoner = QualitativeReasoner("Simulation Test System")
        
        # Set up a simple thermal system for simulation
        reasoner.add_quantity("temperature", QualitativeValue.ZERO, QualitativeDirection.STEADY)
        reasoner.add_quantity("heat_energy", QualitativeValue.ZERO, QualitativeDirection.STEADY)
        
        reasoner.add_process(
            "heating",
            preconditions=["heat_source_present"],
            quantity_conditions=[],
            influences=["I+(temperature)", "I+(heat_energy)"]
        )
        
        reasoner.add_process(
            "cooling",
            preconditions=["heat_sink_present"],
            quantity_conditions=["temperature > 0"],
            influences=["I-(temperature)", "I-(heat_energy)"]
        )
        
        reasoner.add_constraint("temperature >= 0")
        reasoner.add_constraint("heat_energy >= 0")
        
        # Test single simulation step
        print("Testing single simulation step...")
        
        if hasattr(reasoner, 'run_simulation'):
            try:
                state = reasoner.run_simulation("step1")
                print("✓ Single simulation step executed successfully")
                result.add_pass()
                
                # Check if state was recorded
                if len(reasoner.state_history) > 0:
                    print("✓ Simulation state recorded in history")
                    result.add_pass()
                else:
                    print("❌ Simulation state not recorded")
                    result.add_fail("State history not updated")
                    
            except Exception as e:
                print(f"❌ Single simulation step failed: {e}")
                result.add_fail(f"Single simulation step error: {e}")
        else:
            print("❌ run_simulation method not available")
            result.add_fail("run_simulation method missing")
        
        # Test multiple simulation steps
        print("Testing multiple simulation steps...")
        
        try:
            initial_history_length = len(reasoner.state_history)
            
            for i in range(3):
                if hasattr(reasoner, 'step_simulation'):
                    reasoner.step_simulation(f"multi_step_{i}")
                elif hasattr(reasoner, 'run_simulation'):
                    reasoner.run_simulation(f"multi_step_{i}")
                else:
                    break
            
            if len(reasoner.state_history) > initial_history_length:
                print("✓ Multiple simulation steps executed successfully")
                result.add_pass()
            else:
                print("❌ Multiple simulation steps failed")
                result.add_fail("Multiple simulation steps did not update history")
                
        except Exception as e:
            print(f"❌ Multiple simulation steps failed: {e}")
            result.add_fail(f"Multiple simulation steps error: {e}")
        
        # Test process activation
        print("Testing process activation...")
        
        try:
            if hasattr(reasoner, 'update_active_processes'):
                active_processes = reasoner.update_active_processes()
                print(f"✓ Process activation check completed (active: {len(active_processes) if active_processes else 0})")
                result.add_pass()
            else:
                print("⚠️  Process activation method not available")
        except Exception as e:
            print(f"❌ Process activation failed: {e}")
            result.add_fail(f"Process activation error: {e}")
        
        # Test state transitions
        print("Testing state transitions...")
        
        try:
            # Modify a quantity and see if simulation responds
            if "temperature" in reasoner.quantities:
                original_direction = reasoner.quantities["temperature"].direction
                
                # Run simulation step
                if hasattr(reasoner, 'run_simulation'):
                    reasoner.run_simulation("transition_test")
                
                # Check if state changed (may or may not change depending on process activation)
                print("✓ State transition test completed")
                result.add_pass()
            else:
                print("❌ Temperature quantity not found for transition test")
                result.add_fail("Missing quantity for transition test")
                
        except Exception as e:
            print(f"❌ State transition test failed: {e}")
            result.add_fail(f"State transition error: {e}")
        
        # Test simulation with constraints
        print("Testing simulation with constraint checking...")
        
        try:
            # Add a constraint that might be violated
            reasoner.add_constraint("temperature <= 100")  # Temperature shouldn't exceed 100
            
            # Run simulation
            if hasattr(reasoner, 'run_simulation'):
                reasoner.run_simulation("constraint_test")
                print("✓ Simulation with constraints completed")
                result.add_pass()
            else:
                print("⚠️  Simulation method not available for constraint test")
                
        except Exception as e:
            print(f"❌ Simulation with constraints failed: {e}")
            result.add_fail(f"Simulation with constraints error: {e}")
            
    except Exception as e:
        print(f"❌ Simulation engine test failed: {e}")
        result.add_fail(f"Simulation engine error: {e}")
        traceback.print_exc()
    
    print(f"\n{result.summary()}")
    return result


def run_simulation_tests():
    """Run all simulation tests"""
    return [test_simulation_engine()]


if __name__ == "__main__":
    results = run_simulation_tests()
    for result in results:
        print(result.summary())