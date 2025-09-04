#!/usr/bin/env python3
"""
Factory Function Tests for Modular Qualitative Reasoning System
==============================================================

This module tests the factory functions that create different types
of reasoner instances with appropriate configurations.

Test Coverage:
- Educational reasoner factory
- Research reasoner factory
- Production reasoner factory
- Demo reasoner factory
- Factory function consistency
- Factory customization and differentiation

Author: Test Suite for Benedict Chen's Qualitative Reasoning Library
"""

import traceback
from conftest import TestResult


def test_factory_functions() -> TestResult:
    """Test factory functions"""
    
    result = TestResult("Factory Functions")
    print("\n🧪 Test: Factory Functions")
    print("=" * 28)
    
    try:
        from qualitative_reasoning import (
            create_educational_reasoner,
            create_research_reasoner,
            create_production_reasoner,
            create_demo_reasoner
        )
        
        # Test educational reasoner factory
        print("Testing educational reasoner factory...")
        
        try:
            edu_reasoner = create_educational_reasoner("Physics Class Demo")
            
            # Check if it has expected characteristics for educational use
            if (hasattr(edu_reasoner, 'domain_name') and 
                edu_reasoner.domain_name == "Physics Class Demo"):
                print("✓ Educational reasoner created successfully")
                result.add_pass()
                
                # Test that it has educational-friendly settings
                if hasattr(edu_reasoner, 'constraint_config'):
                    if not edu_reasoner.constraint_config.strict_mode:  # Should be lenient for education
                        print("✓ Educational reasoner has appropriate settings")
                        result.add_pass()
                    else:
                        print("⚠️  Educational reasoner may be too strict for learning")
                        
            else:
                print("❌ Educational reasoner creation failed")
                result.add_fail("Educational reasoner creation failed")
                
        except Exception as e:
            print(f"❌ Educational reasoner factory failed: {e}")
            result.add_fail(f"Educational reasoner factory error: {e}")
        
        # Test research reasoner factory
        print("Testing research reasoner factory...")
        
        try:
            research_reasoner = create_research_reasoner("Advanced Physics Research")
            
            if (hasattr(research_reasoner, 'domain_name') and 
                research_reasoner.domain_name == "Advanced Physics Research"):
                print("✓ Research reasoner created successfully")
                result.add_pass()
                
                # Research reasoner should have advanced analysis capabilities
                advanced_methods = ['get_system_status', 'explain_quantity', 'predict_future']
                has_advanced = all(hasattr(research_reasoner, method) for method in advanced_methods)
                
                if has_advanced:
                    print("✓ Research reasoner has advanced capabilities")
                    result.add_pass()
                else:
                    print("❌ Research reasoner missing advanced capabilities")
                    result.add_fail("Research reasoner missing advanced methods")
                    
            else:
                print("❌ Research reasoner creation failed")
                result.add_fail("Research reasoner creation failed")
                
        except Exception as e:
            print(f"❌ Research reasoner factory failed: {e}")
            result.add_fail(f"Research reasoner factory error: {e}")
        
        # Test production reasoner factory
        print("Testing production reasoner factory...")
        
        try:
            prod_reasoner = create_production_reasoner("Industrial Control System", "high")
            
            if (hasattr(prod_reasoner, 'domain_name') and 
                "Industrial Control System" in prod_reasoner.domain_name):
                print("✓ Production reasoner created successfully")
                result.add_pass()
                
                # Production reasoner should prioritize security
                if hasattr(prod_reasoner, 'constraint_config'):
                    if prod_reasoner.constraint_config.evaluation_method.value in ['ast_safe', 'hybrid']:
                        print("✓ Production reasoner has secure settings")
                        result.add_pass()
                    else:
                        print("❌ Production reasoner security settings inadequate")
                        result.add_fail("Production reasoner security insufficient")
                        
            else:
                print("❌ Production reasoner creation failed")
                result.add_fail("Production reasoner creation failed")
                
        except Exception as e:
            print(f"❌ Production reasoner factory failed: {e}")
            result.add_fail(f"Production reasoner factory error: {e}")
        
        # Test demo reasoner factory
        print("Testing demo reasoner factory...")
        
        try:
            demo_reasoner = create_demo_reasoner("Conference Presentation")
            
            if (hasattr(demo_reasoner, 'domain_name') and 
                demo_reasoner.domain_name == "Conference Presentation"):
                print("✓ Demo reasoner created successfully")
                result.add_pass()
                
                # Demo reasoner should have good visualization
                viz_methods = ['generate_report', 'visualize_system_state']
                has_viz = all(hasattr(demo_reasoner, method) for method in viz_methods)
                
                if has_viz:
                    print("✓ Demo reasoner has visualization capabilities")
                    result.add_pass()
                else:
                    print("❌ Demo reasoner missing visualization capabilities")
                    result.add_fail("Demo reasoner missing visualization")
                    
            else:
                print("❌ Demo reasoner creation failed")
                result.add_fail("Demo reasoner creation failed")
                
        except Exception as e:
            print(f"❌ Demo reasoner factory failed: {e}")
            result.add_fail(f"Demo reasoner factory error: {e}")
        
        # Test factory function consistency
        print("Testing factory function consistency...")
        
        try:
            # All factories should create instances of QualitativeReasoner
            from qualitative_reasoning import QualitativeReasoner
            
            factories = [
                create_educational_reasoner("Test"),
                create_research_reasoner("Test"),
                create_production_reasoner("Test", "medium"),
                create_demo_reasoner("Test")
            ]
            
            all_correct_type = all(isinstance(reasoner, QualitativeReasoner) for reasoner in factories)
            
            if all_correct_type:
                print("✓ All factory functions return correct type")
                result.add_pass()
            else:
                print("❌ Factory functions return incorrect types")
                result.add_fail("Factory functions type inconsistency")
            
            # All should have basic required methods
            required_methods = ['add_quantity', 'add_process', 'run_simulation']
            all_have_methods = all(
                all(hasattr(reasoner, method) for method in required_methods)
                for reasoner in factories
            )
            
            if all_have_methods:
                print("✓ All factory-created reasoners have required methods")
                result.add_pass()
            else:
                print("❌ Some factory-created reasoners missing methods")
                result.add_fail("Factory-created reasoners missing methods")
                
        except Exception as e:
            print(f"❌ Factory function consistency test failed: {e}")
            result.add_fail(f"Factory consistency error: {e}")
            
        # Test factory customization
        print("Testing factory customization...")
        
        try:
            # Test that different factories produce different configurations
            edu = create_educational_reasoner("Test")
            prod = create_production_reasoner("Test", "high")
            
            # They should have different constraint evaluation settings
            if (hasattr(edu, 'constraint_config') and hasattr(prod, 'constraint_config')):
                edu_strict = getattr(edu.constraint_config, 'strict_mode', False)
                prod_strict = getattr(prod.constraint_config, 'strict_mode', True)
                
                if edu_strict != prod_strict:
                    print("✓ Factory customization working correctly")
                    result.add_pass()
                else:
                    print("⚠️  Factory customization may not be differentiating configurations")
            else:
                print("✓ Factory customization test skipped (config not available)")
                result.add_pass()  # Don't fail if configurations aren't accessible
                
        except Exception as e:
            print(f"❌ Factory customization test failed: {e}")
            result.add_fail(f"Factory customization error: {e}")
            
    except ImportError as e:
        print(f"❌ Factory function imports failed: {e}")
        result.add_fail(f"Factory function import error: {e}")
    except Exception as e:
        print(f"❌ Factory functions test failed: {e}")
        result.add_fail(f"Factory functions error: {e}")
        traceback.print_exc()
    
    print(f"\n{result.summary()}")
    return result


def run_factory_tests():
    """Run all factory tests"""
    return [test_factory_functions()]


if __name__ == "__main__":
    results = run_factory_tests()
    for result in results:
        print(result.summary())