#!/usr/bin/env python3
"""
Component Management Tests for Modular Qualitative Reasoning System
==================================================================

This module tests adding and managing quantities, states, and processes
in the modular qualitative reasoning system.

Test Coverage:
- Basic quantity addition
- Quantity with landmarks
- Multiple quantity management
- Basic process addition  
- Complex process creation
- Causal graph building
- State creation functionality

Author: Test Suite for Benedict Chen's Qualitative Reasoning Library
"""

import traceback
from conftest import TestResult


def test_adding_components() -> TestResult:
    """Test adding quantities, states, and processes"""
    
    result = TestResult("Adding Components")
    print("\n🧪 Test: Adding Quantities, States, and Processes")
    print("=" * 50)
    
    try:
        from qualitative_reasoning import (
            QualitativeReasoner, QualitativeValue, QualitativeDirection
        )
        
        reasoner = QualitativeReasoner("Component Test System")
        
        # Test adding quantities
        print("Testing quantity addition...")
        
        # Basic quantity
        temp_qty = reasoner.add_quantity(
            "temperature", 
            QualitativeValue.POSITIVE_SMALL, 
            QualitativeDirection.INCREASING
        )
        
        if "temperature" in reasoner.quantities:
            print("✓ Basic quantity added successfully")
            result.add_pass()
        else:
            print("❌ Basic quantity addition failed")
            result.add_fail("Basic quantity not found in reasoner.quantities")
        
        # Quantity with landmarks
        pressure_qty = reasoner.add_quantity(
            "pressure",
            QualitativeValue.ZERO,
            QualitativeDirection.STEADY,
            landmarks=[0.0, 1.0, 2.0, 5.0]
        )
        
        if "pressure" in reasoner.quantities and reasoner.quantities["pressure"].landmark_values:
            print("✓ Quantity with landmarks added successfully")
            result.add_pass()
        else:
            print("❌ Quantity with landmarks addition failed")
            result.add_fail("Quantity with landmarks not properly stored")
        
        # Multiple quantities
        for qty_name in ["flow_rate", "volume", "energy"]:
            reasoner.add_quantity(qty_name, QualitativeValue.ZERO, QualitativeDirection.STEADY)
        
        if len(reasoner.quantities) == 5:  # temperature, pressure, flow_rate, volume, energy
            print("✓ Multiple quantities added successfully")
            result.add_pass()
        else:
            print(f"❌ Expected 5 quantities, found {len(reasoner.quantities)}")
            result.add_fail(f"Incorrect quantity count: {len(reasoner.quantities)}")
        
        # Test adding processes
        print("Testing process addition...")
        
        # Basic process
        heating_process = reasoner.add_process(
            "heating",
            preconditions=["heat_source_present"],
            quantity_conditions=["temperature >= 0"],
            influences=["I+(temperature)", "I+(energy)"]
        )
        
        if "heating" in reasoner.processes:
            print("✓ Basic process added successfully")
            result.add_pass()
        else:
            print("❌ Basic process addition failed")
            result.add_fail("Basic process not found in reasoner.processes")
        
        # Complex process
        flow_process = reasoner.add_process(
            "fluid_flow",
            preconditions=["valve_open", "pressure_gradient_exists"],
            quantity_conditions=["pressure > 0", "volume > 0"],
            influences=["I+(flow_rate)", "I-(pressure)", "I-(volume)"]
        )
        
        if "fluid_flow" in reasoner.processes:
            process = reasoner.processes["fluid_flow"]
            if (len(process.preconditions) == 2 and 
                len(process.quantity_conditions) == 2 and
                len(process.influences) == 3):
                print("✓ Complex process added successfully")
                result.add_pass()
            else:
                print("❌ Complex process structure incorrect")
                result.add_fail("Complex process conditions/influences count mismatch")
        else:
            print("❌ Complex process addition failed")
            result.add_fail("Complex process not found")
        
        # Test causal graph building
        if reasoner.causal_graph and "heating" in reasoner.causal_graph:
            influenced = reasoner.causal_graph["heating"]
            if "temperature" in influenced and "energy" in influenced:
                print("✓ Causal graph built correctly")
                result.add_pass()
            else:
                print(f"❌ Causal graph incomplete: {influenced}")
                result.add_fail(f"Causal graph missing influences: {influenced}")
        else:
            print("❌ Causal graph not built")
            result.add_fail("Causal graph missing or incomplete")
        
        # Test current state creation
        if hasattr(reasoner, 'create_current_state'):
            state = reasoner.create_current_state("test_state")
            if hasattr(state, 'quantities') and len(state.quantities) > 0:
                print("✓ State creation successful")
                result.add_pass()
            else:
                print("❌ State creation failed - empty quantities")
                result.add_fail("Created state has empty quantities")
        else:
            print("⚠️  State creation method not available, skipping test")
        
    except Exception as e:
        print(f"❌ Component addition test failed: {e}")
        result.add_fail(f"Component addition error: {e}")
        traceback.print_exc()
    
    print(f"\n{result.summary()}")
    return result


def run_component_tests():
    """Run all component tests"""
    return [test_adding_components()]


if __name__ == "__main__":
    results = run_component_tests()
    for result in results:
        print(result.summary())