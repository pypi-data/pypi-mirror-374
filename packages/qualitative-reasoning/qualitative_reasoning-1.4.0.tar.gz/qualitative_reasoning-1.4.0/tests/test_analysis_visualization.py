#!/usr/bin/env python3
"""
Analysis & Visualization Tests for Modular Qualitative Reasoning System
======================================================================

This module tests the analysis and visualization capabilities including
system analysis, quantity explanation, behavior prediction, report generation,
and data export functionality.

Test Coverage:
- System analysis and status reporting
- Quantity explanation functionality
- Behavior prediction capabilities
- Report generation in multiple formats
- System visualization
- Data export in different formats
- Causal chain analysis

Author: Test Suite for Benedict Chen's Qualitative Reasoning Library
"""

import traceback
from conftest import TestResult


def test_analysis_visualization() -> TestResult:
    """Test analysis and visualization capabilities"""
    
    result = TestResult("Analysis & Visualization")
    print("\n🧪 Test: Analysis and Visualization Capabilities")
    print("=" * 50)
    
    try:
        from qualitative_reasoning import (
            QualitativeReasoner, QualitativeValue, QualitativeDirection
        )
        
        # Create a reasoner with rich system for analysis
        reasoner = QualitativeReasoner("Analysis Test System")
        
        # Set up a complex system
        print("Setting up complex system for analysis...")
        
        # Add multiple quantities
        reasoner.add_quantity("temperature", QualitativeValue.POSITIVE_SMALL, 
                            QualitativeDirection.INCREASING, landmarks=[0, 25, 50, 100])
        reasoner.add_quantity("pressure", QualitativeValue.POSITIVE_LARGE, 
                            QualitativeDirection.DECREASING)
        reasoner.add_quantity("volume", QualitativeValue.POSITIVE_LARGE, 
                            QualitativeDirection.STEADY)
        reasoner.add_quantity("energy", QualitativeValue.POSITIVE_SMALL, 
                            QualitativeDirection.INCREASING)
        
        # Add multiple processes with complex relationships
        reasoner.add_process("heating", 
                           ["heater_on", "power_available"], 
                           ["energy > 0"], 
                           ["I+(temperature)", "I+(energy)"])
        
        reasoner.add_process("expansion", 
                           ["temperature > 25"], 
                           ["pressure > 0"], 
                           ["I+(volume)", "I-(pressure)"])
        
        reasoner.add_process("compression", 
                           ["external_pressure"], 
                           ["volume > 0"], 
                           ["I-(volume)", "I+(pressure)"])
        
        # Add constraints
        reasoner.add_constraint("temperature >= 0")
        reasoner.add_constraint("pressure > 0")
        reasoner.add_constraint("volume > 0")
        reasoner.add_constraint("temperature > 50 => pressure > 10")
        
        print("✓ Complex system setup complete")
        result.add_pass()
        
        # Run simulation to generate data for analysis
        for i in range(5):
            if hasattr(reasoner, 'run_simulation'):
                reasoner.run_simulation(f"analysis_data_{i}")
        
        # Test system analysis
        print("Testing system analysis...")
        
        try:
            if hasattr(reasoner, 'get_system_status'):
                analysis = reasoner.get_system_status()
                print("✓ System analysis completed successfully")
                result.add_pass()
                
                # Check if analysis contains meaningful information
                if analysis and len(str(analysis)) > 20:
                    print("✓ Analysis contains substantial information")
                    result.add_pass()
                else:
                    print("⚠️  Analysis appears minimal")
                    
            else:
                print("❌ System analysis method not available")
                result.add_fail("get_system_status method missing")
                
        except Exception as e:
            print(f"❌ System analysis failed: {e}")
            result.add_fail(f"System analysis error: {e}")
        
        # Test quantity explanation
        print("Testing quantity explanation...")
        
        try:
            if hasattr(reasoner, 'explain_quantity'):
                explanation = reasoner.explain_quantity("temperature")
                print("✓ Quantity explanation generated successfully")
                result.add_pass()
                
                # Test multiple quantities
                for qty in ["pressure", "volume", "energy"]:
                    if qty in reasoner.quantities:
                        reasoner.explain_quantity(qty)
                        
                print("✓ Multiple quantity explanations generated")
                result.add_pass()
                
            else:
                print("❌ Quantity explanation method not available")
                result.add_fail("explain_quantity method missing")
                
        except Exception as e:
            print(f"❌ Quantity explanation failed: {e}")
            result.add_fail(f"Quantity explanation error: {e}")
        
        # Test behavior prediction
        print("Testing behavior prediction...")
        
        try:
            if hasattr(reasoner, 'predict_future'):
                predictions = reasoner.predict_future(n_steps=3)
                print("✓ Behavior prediction completed successfully")
                result.add_pass()
                
                if predictions and len(predictions) > 0:
                    print(f"✓ Generated {len(predictions)} prediction steps")
                    result.add_pass()
                else:
                    print("⚠️  Predictions appear empty")
                    
            else:
                print("⚠️  Behavior prediction method not available (optional)")
                
        except Exception as e:
            print(f"❌ Behavior prediction failed: {e}")
            result.add_fail(f"Behavior prediction error: {e}")
        
        # Test report generation in different formats
        print("Testing report generation...")
        
        formats_to_test = ["text", "json", "markdown"]
        
        for report_format in formats_to_test:
            try:
                if hasattr(reasoner, 'generate_report'):
                    report = reasoner.generate_report(report_format)
                    
                    if report and len(str(report)) > 10:
                        print(f"✓ {report_format.upper()} report generated successfully")
                        result.add_pass()
                    else:
                        print(f"❌ {report_format.upper()} report appears empty")
                        result.add_fail(f"{report_format} report empty")
                        
                else:
                    print("❌ Report generation method not available")
                    result.add_fail("generate_report method missing")
                    break
                    
            except Exception as e:
                print(f"❌ {report_format.upper()} report generation failed: {e}")
                result.add_fail(f"{report_format} report error: {e}")
        
        # Test system visualization
        print("Testing system visualization...")
        
        try:
            if hasattr(reasoner, 'visualize_system_state'):
                reasoner.visualize_system_state()
                print("✓ System visualization completed successfully")
                result.add_pass()
                
            else:
                print("❌ System visualization method not available")
                result.add_fail("visualize_system_state method missing")
                
        except Exception as e:
            print(f"❌ System visualization failed: {e}")
            result.add_fail(f"System visualization error: {e}")
        
        # Test data export
        print("Testing data export...")
        
        export_formats = ["json", "csv"]
        
        for export_format in export_formats:
            try:
                if hasattr(reasoner, 'export_system_state'):
                    data = reasoner.export_system_state(export_format)
                    
                    if data and len(str(data)) > 10:
                        print(f"✓ {export_format.upper()} export completed successfully")
                        result.add_pass()
                    else:
                        print(f"❌ {export_format.upper()} export appears empty")
                        result.add_fail(f"{export_format} export empty")
                        
                else:
                    print("⚠️  Data export method not available (optional)")
                    break
                    
            except Exception as e:
                print(f"❌ {export_format.upper()} export failed: {e}")
                result.add_fail(f"{export_format} export error: {e}")
        
        # Test system status reporting
        print("Testing system status reporting...")
        
        try:
            if hasattr(reasoner, 'get_system_status'):
                status = reasoner.get_system_status()
                
                if status and isinstance(status, dict):
                    print("✓ System status reporting working")
                    result.add_pass()
                    
                    # Check for expected status fields
                    expected_fields = ['health', 'quantities', 'processes']
                    present_fields = [field for field in expected_fields if field in status]
                    
                    if len(present_fields) >= 2:
                        print(f"✓ System status contains expected fields: {present_fields}")
                        result.add_pass()
                    else:
                        print(f"⚠️  System status missing some fields: {expected_fields}")
                        
                else:
                    print("❌ System status reporting failed - invalid return")
                    result.add_fail("System status invalid return type")
                    
            else:
                print("⚠️  System status method not available (optional)")
                
        except Exception as e:
            print(f"❌ System status reporting failed: {e}")
            result.add_fail(f"System status error: {e}")
        
        # Test causal chain analysis
        print("Testing causal chain analysis...")
        
        try:
            # This tests if the system can trace cause-effect relationships
            if hasattr(reasoner, 'trace_causal_chain'):
                chain = reasoner.trace_causal_chain("temperature", "pressure")
                print("✓ Causal chain analysis completed")
                result.add_pass()
            elif hasattr(reasoner, 'analyze_system'):
                # Use general analysis as fallback
                analysis = reasoner.analyze_system()
                print("✓ Causal analysis via system analysis completed")
                result.add_pass()
            else:
                print("⚠️  Causal chain analysis not available (optional)")
                
        except Exception as e:
            print(f"❌ Causal chain analysis failed: {e}")
            result.add_fail(f"Causal chain analysis error: {e}")
            
    except Exception as e:
        print(f"❌ Analysis and visualization test failed: {e}")
        result.add_fail(f"Analysis and visualization error: {e}")
        traceback.print_exc()
    
    print(f"\n{result.summary()}")
    return result


def run_analysis_viz_tests():
    """Run all analysis and visualization tests"""
    return [test_analysis_visualization()]


if __name__ == "__main__":
    results = run_analysis_viz_tests()
    for result in results:
        print(result.summary())