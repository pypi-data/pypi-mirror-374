#!/usr/bin/env python3
"""
Master Test Suite for Modular Qualitative Reasoning System
==========================================================

This is the main test runner that executes all modularized test modules
and provides comprehensive reporting on the system's functionality.

Test Modules Included:
- test_initialization.py - Core imports and basic reasoner creation
- test_components.py - Component addition and management
- test_constraints.py - Constraint evaluation and security
- test_simulation.py - Simulation engine functionality
- test_modules.py - Individual module testing
- test_integration.py - Cross-module integration testing
- test_factories.py - Factory function testing
- test_analysis_viz.py - Analysis and visualization testing

Usage:
    python test_suite.py                    # Run all tests
    python test_suite.py --module <name>    # Run specific test module
    python test_suite.py --verbose          # Detailed output
    python test_suite.py --summary-only     # Just show summary

Author: Test Suite for Benedict Chen's Qualitative Reasoning Library
"""

import sys
import os
import traceback
import argparse
from typing import List

# Import test modules
from conftest import TestResult, generate_test_summary
from test_initialization import run_initialization_tests
from test_components import run_component_tests
from test_constraints import run_constraint_tests
from test_simulation import run_simulation_tests
from test_modules import run_module_tests
from test_integration import run_integration_tests
from test_factories import run_factory_tests
from test_analysis_viz import run_analysis_viz_tests


def run_all_tests(verbose: bool = True) -> List[TestResult]:
    """Run all test modules and return aggregated results"""
    
    if verbose:
        print("🧠 Comprehensive Modular Qualitative Reasoning Test Suite")
        print("=" * 65)
        print("Testing the complete modular QR system for correctness and integration")
        print()
    
    # Define all test modules with their runners
    test_modules = [
        ("Initialization", run_initialization_tests),
        ("Components", run_component_tests),
        ("Constraints", run_constraint_tests),
        ("Simulation", run_simulation_tests),
        ("Modules", run_module_tests),
        ("Integration", run_integration_tests),
        ("Factories", run_factory_tests),
        ("Analysis & Visualization", run_analysis_viz_tests)
    ]
    
    all_results = []
    
    # Run each test module
    for module_name, test_runner in test_modules:
        if verbose:
            print(f"\n{'='*60}")
            print(f"🚀 Running {module_name} Tests")
            print(f"{'='*60}")
        
        try:
            module_results = test_runner()
            all_results.extend(module_results)
            
            if verbose:
                for result in module_results:
                    status_icon = "✅" if result.failed == 0 else "❌"
                    print(f"{status_icon} {result.summary()}")
                    
        except Exception as e:
            # Create failed result for crashed test module
            crashed_result = TestResult(f"{module_name} (CRASHED)")
            crashed_result.add_fail(f"Test module crashed: {e}")
            all_results.append(crashed_result)
            
            if verbose:
                print(f"❌ {module_name} test module crashed: {e}")
                traceback.print_exc()
    
    return all_results


def run_specific_module(module_name: str, verbose: bool = True) -> List[TestResult]:
    """Run a specific test module"""
    
    module_runners = {
        "initialization": run_initialization_tests,
        "components": run_component_tests,
        "constraints": run_constraint_tests,
        "simulation": run_simulation_tests,
        "modules": run_module_tests,
        "integration": run_integration_tests,
        "factories": run_factory_tests,
        "analysis_viz": run_analysis_viz_tests
    }
    
    if module_name.lower() not in module_runners:
        print(f"❌ Unknown test module: {module_name}")
        print(f"Available modules: {', '.join(module_runners.keys())}")
        return []
    
    if verbose:
        print(f"🧪 Running {module_name.title()} Tests Only")
        print("=" * 50)
    
    try:
        results = module_runners[module_name.lower()]()
        return results
    except Exception as e:
        print(f"❌ Test module {module_name} crashed: {e}")
        traceback.print_exc()
        return []


def main():
    """Main test execution function"""
    
    parser = argparse.ArgumentParser(description="Modular QR Test Suite")
    parser.add_argument("--module", "-m", type=str, help="Run specific test module")
    parser.add_argument("--verbose", "-v", action="store_true", default=True, help="Verbose output")
    parser.add_argument("--summary-only", "-s", action="store_true", help="Show summary only")
    parser.add_argument("--quiet", "-q", action="store_true", help="Minimal output")
    
    args = parser.parse_args()
    
    # Determine verbosity level
    verbose = args.verbose and not args.summary_only and not args.quiet
    
    try:
        if args.module:
            # Run specific module
            results = run_specific_module(args.module, verbose)
        else:
            # Run all tests
            results = run_all_tests(verbose)
        
        # Generate and display summary
        if not args.quiet:
            summary = generate_test_summary(results)
            print(summary)
        
        # Return exit code based on results
        total_failed = sum(r.failed for r in results)
        
        if not args.quiet:
            if total_failed == 0:
                print("\n🎉 All tests passed! The modular QR system is working correctly.")
            else:
                print(f"\n❌ {total_failed} test(s) failed. Review the details above.")
        
        return 0 if total_failed == 0 else 1
        
    except Exception as e:
        print(f"💥 Test suite execution failed: {e}")
        if verbose:
            traceback.print_exc()
        return 2


def run_comprehensive_tests():
    """Legacy function to maintain compatibility with original test file"""
    return run_all_tests(verbose=True)


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)