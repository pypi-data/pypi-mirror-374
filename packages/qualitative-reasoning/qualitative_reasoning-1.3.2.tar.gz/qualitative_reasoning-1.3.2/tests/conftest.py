#!/usr/bin/env python3
"""
Shared Test Utilities for Modular Qualitative Reasoning Test Suite
================================================================

This file contains shared test utilities, fixtures, and helper classes
used across all test modules in the qualitative reasoning test suite.

Author: Test Suite for Benedict Chen's Qualitative Reasoning Library
"""

import sys
import os
import traceback
from typing import Dict, List, Any, Optional


class TestResult:
    """Helper class for tracking test results across test modules"""
    
    def __init__(self, name: str):
        self.name = name
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self):
        self.passed += 1
        
    def add_fail(self, error: str):
        self.failed += 1
        self.errors.append(error)
    
    def success_rate(self) -> float:
        total = self.passed + self.failed
        return (self.passed / total * 100) if total > 0 else 0.0
    
    def summary(self) -> str:
        return f"{self.name}: {self.passed} passed, {self.failed} failed ({self.success_rate():.1f}%)"


def generate_test_summary(results: List[TestResult]) -> str:
    """Generate a comprehensive test summary"""
    
    total_passed = sum(r.passed for r in results)
    total_failed = sum(r.failed for r in results)
    total_tests = total_passed + total_failed
    
    overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0.0
    
    summary = []
    summary.append("\n" + "=" * 65)
    summary.append("📊 COMPREHENSIVE TEST SUMMARY")
    summary.append("=" * 65)
    summary.append(f"Total Tests Run: {total_tests}")
    summary.append(f"Tests Passed: {total_passed}")
    summary.append(f"Tests Failed: {total_failed}")
    summary.append(f"Overall Success Rate: {overall_success_rate:.1f}%")
    summary.append("")
    
    # Individual test results
    summary.append("📋 Individual Test Results:")
    summary.append("-" * 40)
    
    for result in results:
        status_icon = "✅" if result.failed == 0 else "❌"
        summary.append(f"{status_icon} {result.summary()}")
    
    # Failed test details
    failed_results = [r for r in results if r.failed > 0]
    if failed_results:
        summary.append("")
        summary.append("🔍 Failed Test Details:")
        summary.append("-" * 25)
        
        for result in failed_results:
            summary.append(f"\n❌ {result.name}:")
            for error in result.errors:
                summary.append(f"   • {error}")
    
    # System health assessment
    summary.append("")
    summary.append("🏥 System Health Assessment:")
    summary.append("-" * 30)
    
    if overall_success_rate >= 95:
        summary.append("🎉 EXCELLENT - System is working correctly!")
        summary.append("   All core functionality appears to be intact.")
    elif overall_success_rate >= 85:
        summary.append("✅ GOOD - System is mostly working correctly.")
        summary.append("   Minor issues detected, but core functionality intact.")
    elif overall_success_rate >= 70:
        summary.append("⚠️  FAIR - System has some issues but basic functionality works.")
        summary.append("   Some modules may need attention.")
    elif overall_success_rate >= 50:
        summary.append("❌ POOR - System has significant issues.")
        summary.append("   Major functionality problems detected.")
    else:
        summary.append("💥 CRITICAL - System has major failures.")
        summary.append("   Extensive debugging and fixes needed.")
    
    # Recommendations
    summary.append("")
    summary.append("💡 Recommendations:")
    summary.append("-" * 20)
    
    if total_failed == 0:
        summary.append("• System is working correctly - no action needed!")
        summary.append("• Consider adding more advanced test cases for edge cases.")
    elif total_failed <= 3:
        summary.append("• Address the few failing tests to achieve perfect score.")
        summary.append("• Review error details above for specific issues.")
    else:
        summary.append("• Focus on fixing core integration issues first.")
        summary.append("• Check module imports and method availability.")
        summary.append("• Review the modular architecture implementation.")
        summary.append("• Consider running tests individually for detailed debugging.")
    
    summary.append("")
    summary.append("=" * 65)
    
    return "\n".join(summary)