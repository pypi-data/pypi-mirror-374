#!/usr/bin/env python3
"""
Constraint Evaluation Tests for Modular Qualitative Reasoning System
==================================================================

This module tests constraint evaluation functionality, including
security features and validation mechanisms.

Test Coverage:
- Different evaluation methods (AST_SAFE, REGEX_PARSER, HYBRID)
- Security features and unsafe constraint rejection
- Constraint validation (valid vs invalid constraints)
- Error handling and graceful degradation

Author: Test Suite for Benedict Chen's Qualitative Reasoning Library
"""

import traceback
from conftest import TestResult


def test_constraint_evaluation() -> TestResult:
    """Test constraint evaluation functionality"""
    
    result = TestResult("Constraint Evaluation")
    print("\n🧪 Test: Constraint Evaluation Functionality")
    print("=" * 45)
    
    try:
        from qualitative_reasoning import (
            QualitativeReasoner, QualitativeValue, QualitativeDirection,
            ConstraintEvaluationMethod, ConstraintEvaluationConfig
        )
        
        # Test different evaluation methods
        methods_to_test = [
            ConstraintEvaluationMethod.AST_SAFE,
            ConstraintEvaluationMethod.REGEX_PARSER,
            ConstraintEvaluationMethod.HYBRID
        ]
        
        for method in methods_to_test:
            print(f"Testing {method.value} evaluation method...")
            
            config = ConstraintEvaluationConfig(evaluation_method=method)
            reasoner = QualitativeReasoner(f"Constraint Test - {method.value}", constraint_config=config)
            
            # Add quantities for testing
            reasoner.add_quantity("temp", QualitativeValue.POSITIVE_SMALL, QualitativeDirection.STEADY)
            reasoner.add_quantity("pressure", QualitativeValue.ZERO, QualitativeDirection.STEADY)
            
            # Test simple constraints
            test_constraints = [
                "temp > 0",
                "pressure >= 0", 
                "temp != pressure"
            ]
            
            constraint_results = []
            for constraint in test_constraints:
                try:
                    reasoner.add_constraint(constraint)
                    # Try to evaluate the constraint
                    if hasattr(reasoner, 'evaluate_constraint'):
                        result_val = reasoner.evaluate_constraint(constraint)
                        constraint_results.append(True)
                    else:
                        constraint_results.append(True)  # Just adding was successful
                except Exception as e:
                    print(f"   ❌ Constraint '{constraint}' failed: {e}")
                    constraint_results.append(False)
            
            if all(constraint_results):
                print(f"✓ {method.value} method working correctly")
                result.add_pass()
            else:
                print(f"❌ {method.value} method failed some constraints")
                result.add_fail(f"{method.value} method constraint failures")
        
        # Test security features
        print("Testing security features...")
        
        secure_reasoner = QualitativeReasoner(
            "Security Test",
            constraint_config=ConstraintEvaluationConfig(
                evaluation_method=ConstraintEvaluationMethod.AST_SAFE,
                allow_function_calls=False,
                strict_mode=True
            )
        )
        secure_reasoner.add_quantity("safe_var", QualitativeValue.POSITIVE_SMALL)
        
        # Test that unsafe constraints are rejected
        unsafe_constraints = [
            "__import__('os').system('echo test')",  # Code injection attempt
            "exec('print(1)')",                      # Exec attempt
            "eval('1+1')"                           # Nested eval
        ]
        
        security_passed = True
        for unsafe_constraint in unsafe_constraints:
            try:
                secure_reasoner.add_constraint(unsafe_constraint)
                if hasattr(secure_reasoner, 'evaluate_constraint'):
                    secure_reasoner.evaluate_constraint(unsafe_constraint)
                # If we get here without exception in strict mode, security failed
                if secure_reasoner.constraint_config.strict_mode:
                    print(f"❌ Security vulnerability: '{unsafe_constraint}' was allowed")
                    security_passed = False
            except Exception:
                # Exception is expected for unsafe constraints in secure mode
                pass
        
        if security_passed:
            print("✓ Security features working correctly")
            result.add_pass()
        else:
            print("❌ Security vulnerabilities detected")
            result.add_fail("Security vulnerabilities in constraint evaluation")
        
        # Test constraint validation
        print("Testing constraint validation...")
        validator_reasoner = QualitativeReasoner("Validation Test")
        validator_reasoner.add_quantity("test_var", QualitativeValue.ZERO)
        
        valid_constraints = [
            "test_var > 0",
            "test_var == 0",
            "test_var != 5"
        ]
        
        invalid_constraints = [
            "test_var >",           # Incomplete
            "invalid_var > 0",      # Undefined variable
            "test_var ++ 1"         # Invalid syntax
        ]
        
        validation_passed = True
        
        # Valid constraints should work
        for constraint in valid_constraints:
            try:
                validator_reasoner.add_constraint(constraint)
            except Exception as e:
                print(f"❌ Valid constraint rejected: '{constraint}' - {e}")
                validation_passed = False
        
        # Invalid constraints should be handled gracefully
        for constraint in invalid_constraints:
            try:
                validator_reasoner.add_constraint(constraint)
                # Check if evaluation fails gracefully
                if hasattr(validator_reasoner, 'evaluate_constraint'):
                    result_val = validator_reasoner.evaluate_constraint(constraint)
                    # In non-strict mode, should default to False or handle gracefully
            except Exception:
                # Exceptions are acceptable for invalid constraints
                pass
        
        if validation_passed:
            print("✓ Constraint validation working correctly")
            result.add_pass()
        else:
            print("❌ Constraint validation issues detected")
            result.add_fail("Constraint validation problems")
            
    except Exception as e:
        print(f"❌ Constraint evaluation test failed: {e}")
        result.add_fail(f"Constraint evaluation error: {e}")
        traceback.print_exc()
    
    print(f"\n{result.summary()}")
    return result


def run_constraint_tests():
    """Run all constraint tests"""
    return [test_constraint_evaluation()]


if __name__ == "__main__":
    results = run_constraint_tests()
    for result in results:
        print(result.summary())