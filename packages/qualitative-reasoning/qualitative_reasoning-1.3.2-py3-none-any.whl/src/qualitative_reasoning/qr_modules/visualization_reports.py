"""
📊 Qualitative Reasoning - Visualization Reports Module
=====================================================

Report generation and analysis for qualitative reasoning systems.
Extracted from visualization_engine.py to enforce 800-line limit.

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Forbus & de Kleer (1993) - Building Problem Solvers

This module provides report generation, analysis summaries,
and prediction visualization functionality.
"""

from typing import Dict, List, Any, Optional
from ..qr_modules.visualization_core import VisualizationReport

class VisualizationReportsMixin:
    """
    Report generation and analysis for qualitative reasoning.
    
    Provides reporting capabilities including executive summaries,
    prediction visualization, and system analysis.
    """
    
    def generate_comprehensive_report(self, include_predictions: bool = False) -> VisualizationReport:
        """
        📊 Generate system analysis report
        
        Creates a detailed report covering all aspects of the system including
        current state, historical analysis, predictions, and executive summary.
        
        Args:
            include_predictions: Whether to include future state predictions
            
        Returns:
            VisualizationReport: Complete comprehensive report
            
        🎯 Report Components:
        1. **Executive Summary**: High-level insights for decision makers
        2. **Current State Analysis**: Detailed current system state
        3. **Historical Trends**: Analysis of system evolution patterns
        4. **Process Analysis**: Deep dive into process behavior
        5. **Constraint Assessment**: Constraint satisfaction analysis
        6. **Performance Metrics**: System performance indicators
        7. **Predictions**: Future state predictions (if requested)
        8. **Recommendations**: Actionable insights and suggestions
        """
        
        # Create comprehensive report
        report = VisualizationReport(
            title=f"Comprehensive Analysis: {getattr(self, 'domain_name', 'QR System')}",
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            summary=self._generate_executive_summary()
        )
        
        # Add detailed sections
        report.add_section("Executive Summary", self._generate_executive_summary())
        report.add_section("Current State", self._visualize_system_overview())
        report.add_section("Quantity Analysis", self._visualize_quantities("comprehensive"))
        report.add_section("Process Analysis", self._visualize_active_processes("comprehensive"))
        report.add_section("Relationship Analysis", self._visualize_relationships())
        
        # Historical analysis if available
        if hasattr(self, 'state_history') and len(self.state_history) > 1:
            report.add_section("Historical Trends", self._visualize_state_history("comprehensive"))
            report.add_section("Pattern Analysis", self._analyze_historical_patterns())
            
        # Constraint analysis
        if hasattr(self, 'constraints'):
            report.add_section("Constraint Assessment", self._analyze_constraint_satisfaction())
            
        # Performance metrics
        report.add_section("Performance Metrics", self._generate_performance_metrics())
        
        # Predictions if requested
        if include_predictions:
            predictions = self._generate_system_predictions()
            if predictions:
                report.add_section("Future Predictions", self._visualize_predictions(predictions))
                
        # Recommendations
        report.add_section("Recommendations", self._generate_system_recommendations())
        
        # Add comprehensive data exports
        report.add_data("complete_state", self._export_complete_system_state())
        report.add_data("historical_data", self._export_history_data())
        report.add_data("performance_metrics", self._export_performance_data())
        
        # Cache the report
        self._viz_cache['comprehensive_report'] = report
        self._export_history.append({
            'type': 'comprehensive_report',
            'timestamp': report.timestamp,
            'sections': len(report.sections)
        })
        
        return report
        
    def _generate_executive_summary(self) -> str:
        """
        🏆 Generate executive summary for leadership consumption
        
        Creates a high-level summary focusing on business value,
        key insights, and actionable information for decision makers.
        """
        
        lines = [
            "🏆 EXECUTIVE SUMMARY",
            "=" * 30,
            ""
        ]
        
        # System health assessment
        health_score = self._calculate_system_health_score()
        health_status = "Excellent" if health_score >= 0.8 else "Good" if health_score >= 0.6 else "Needs Attention"
        
        lines.extend([
            f"🎯 System Health: {health_status} ({health_score:.1%})",
            ""
        ])
        
        # Key performance indicators
        quantities = getattr(self, 'quantities', {})
        processes = getattr(self, 'processes', [])
        active_processes = [p for p in processes if getattr(p, 'is_active', False)]
        
        lines.extend([
            "📊 Key Metrics:",
            f"  • {len(quantities)} quantities under management",
            f"  • {len(active_processes)} processes currently active",
            f"  • {len(getattr(self, 'constraints', []))} constraints enforced",
            ""
        ])
        
        # Critical issues (if any)
        violations = []
        if hasattr(self, 'constraints'):
            violations = [c for c in self.constraints if not getattr(c, 'is_satisfied', True)]
            
        if violations:
            lines.extend([
                "⚠️ Critical Issues:",
                f"  • {len(violations)} constraint violations detected",
                "  • Immediate attention recommended",
                ""
            ])
            
        # System trends
        if hasattr(self, 'state_history') and len(self.state_history) >= 3:
            trend = self._assess_system_trend()
            trend_desc = {
                'improving': '↗️ System performance improving',
                'stable': '→ System operating in stable state',
                'declining': '↘️ System showing performance decline',
                'volatile': '🌊 System exhibiting volatile behavior'
            }.get(trend, '🔄 System trend unclear')
            
            lines.extend([
                "📈 Performance Trend:",
                f"  • {trend_desc}",
                ""
            ])
            
        # Strategic recommendations
        recommendations = self._get_strategic_recommendations()
        if recommendations:
            lines.extend([
                "🎤 Strategic Recommendations:",
            ])
            for i, rec in enumerate(recommendations[:3], 1):
                lines.append(f"  {i}. {rec}")
                
        # Business impact assessment
        impact = self._assess_business_impact()
        if impact:
            lines.extend([
                "",
                "🏢 Business Impact:",
                f"  {impact}"
            ])
            
        return "\n".join(lines)
        
    def _visualize_predictions(self, predictions: List) -> str:
        """
        🔮 Visualize future state predictions
        
        Shows predicted future states and their likelihood based on
        current system trajectory and process activations.
        
        Args:
            predictions: List of predicted future states
            
        Returns:
            str: Formatted predictions visualization
        """
        
        if not predictions:
            return "🔮 No predictions available (insufficient data or inactive system)."
            
        lines = [
            "🔮 FUTURE STATE PREDICTIONS",
            "=" * 35,
            ""
        ]
        
        for i, prediction in enumerate(predictions[:5], 1):  # Limit to 5 predictions
            time_horizon = getattr(prediction, 'time_horizon', f'Future {i}')
            confidence = getattr(prediction, 'confidence', 0.5)
            description = getattr(prediction, 'description', 'Predicted state')
            
            # Format confidence indicator
            confidence_bar = "█" * int(confidence * 10) + "░" * (10 - int(confidence * 10))
            confidence_desc = "High" if confidence >= 0.7 else "Medium" if confidence >= 0.4 else "Low"
            
            lines.extend([
                f"🕰️ {time_horizon}:",
                f"   Description: {description}",
                f"   Confidence:  {confidence_desc} ({confidence:.1%}) |{confidence_bar}|",
                ""
            ])
            
            # Add key predicted changes
            if hasattr(prediction, 'predicted_changes'):
                changes = getattr(prediction, 'predicted_changes', [])
                if changes:
                    lines.append("   Key Changes:")
                    for change in changes[:3]:  # Limit to 3 changes
                        lines.append(f"     • {change}")
                    lines.append("")
                    
        # Add prediction methodology note
        lines.extend([
            "📊 Prediction Methodology:",
            "   Based on current process activations, historical patterns,",
            "   and qualitative differential equations. Confidence reflects",
            "   model uncertainty and time horizon."
        ])
        
        return "\n".join(lines)
        
    def _analyze_historical_patterns(self) -> str:
        """
        📈 Analyze patterns in historical state evolution
        
        Identifies recurring patterns, cycles, and trends in the
        system's historical behavior.
        """
        
        if not hasattr(self, 'state_history') or len(self.state_history) < 5:
            return "📈 Insufficient history for pattern analysis (need 5+ states)."
            
        history = self.state_history
        lines = [
            "📈 HISTORICAL PATTERN ANALYSIS",
            "=" * 40,
            ""
        ]
        
        # Analyze process activation patterns
        process_activity = []
        for state in history:
            active_count = len(getattr(state, 'active_processes', []))
            process_activity.append(active_count)
            
        # Detect patterns in activity
        if self._is_cyclic_pattern(process_activity):
            lines.append("🔄 Cyclic Pattern Detected:")
            lines.append("   System shows repeating activity cycles")
            cycle_length = self._estimate_cycle_length(process_activity)
            lines.append(f"   Estimated cycle length: {cycle_length} states")
        elif self._is_trending_pattern(process_activity):
            trend_dir = self._get_trend_direction(process_activity)
            lines.append(f"📈 Trending Pattern Detected:")
            lines.append(f"   System activity is {trend_dir} over time")
        else:
            lines.append("🌲 Random/Complex Pattern:")
            lines.append("   No clear cyclical or trending patterns detected")
            
        lines.append("")
        
        # Analyze quantity evolution patterns
        lines.extend([
            "📊 Quantity Evolution Patterns:",
            ""
        ])
        
        # Track specific quantities if available
        if len(history) >= 3 and hasattr(history[0], 'quantities'):
            sample_quantities = list(getattr(history[0], 'quantities', {}).keys())[:3]
            
            for qty_name in sample_quantities:
                qty_pattern = self._analyze_quantity_pattern(history, qty_name)
                if qty_pattern:
                    lines.append(f"   • {qty_name}: {qty_pattern}")
                    
        # Stability assessment
        stability = self._assess_historical_stability(history)
        lines.extend([
            "",
            "⚖️ System Stability Assessment:",
            f"   Overall Stability: {stability['level']}",
            f"   Volatility Index: {stability['volatility']:.2f}",
            f"   Predictability: {stability['predictability']}"
        ])
        
        return "\n".join(lines)
        
    def _analyze_constraint_satisfaction(self) -> str:
        """
        ⚖️ Analyze constraint satisfaction over time
        
        Provides detailed analysis of constraint behavior including
        violation patterns and satisfaction trends.
        """
        
        if not hasattr(self, 'constraints') or not self.constraints:
            return "⚖️ No constraints defined for analysis."
            
        lines = [
            "⚖️ CONSTRAINT SATISFACTION ANALYSIS",
            "=" * 45,
            ""
        ]
        
        constraints = self.constraints
        total_constraints = len(constraints)
        satisfied = [c for c in constraints if getattr(c, 'is_satisfied', True)]
        violated = [c for c in constraints if not getattr(c, 'is_satisfied', True)]
        
        # Overall satisfaction metrics
        satisfaction_rate = len(satisfied) / total_constraints if total_constraints > 0 else 1.0
        
        lines.extend([
            f"📊 Overall Constraint Health:",
            f"   Total Constraints: {total_constraints}",
            f"   Currently Satisfied: {len(satisfied)} ({satisfaction_rate:.1%})",
            f"   Current Violations: {len(violated)}",
            ""
        ])
        
        # Detailed violation analysis
        if violated:
            lines.extend([
                "⚠️ Constraint Violations (Detailed):",
                ""
            ])
            
            for constraint in violated:
                constraint_name = getattr(constraint, 'name', 'Unnamed')
                severity = getattr(constraint, 'severity', 'medium')
                description = getattr(constraint, 'description', 'No description')
                
                severity_symbol = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(severity, '🟡')
                
                lines.extend([
                    f"   {severity_symbol} {constraint_name} ({severity} severity)",
                    f"      {description[:70]}{'...' if len(description) > 70 else ''}",
                    ""
                ])
                
        # Constraint satisfaction trends (if history available)
        if hasattr(self, 'state_history') and len(self.state_history) >= 3:
            trend = self._analyze_constraint_trends()
            lines.extend([
                "📈 Constraint Satisfaction Trends:",
                f"   Recent Trend: {trend['direction']}",
                f"   Average Satisfaction: {trend['average']:.1%}",
                f"   Trend Stability: {trend['stability']}",
                ""
            ])
            
        # Recommendations for constraint issues
        if violated:
            recommendations = self._generate_constraint_recommendations(violated)
            lines.extend([
                "🎯 Recommendations:",
            ])
            for rec in recommendations:
                lines.append(f"   • {rec}")
                
        return "\n".join(lines)
        
    def _generate_performance_metrics(self) -> str:
        """
        📊 Generate system performance metrics and KPIs
        
        Calculates and displays key performance indicators for
        system health, efficiency, and operational status.
        """
        
        lines = [
            "📊 PERFORMANCE METRICS & KPIs",
            "=" * 35,
            ""
        ]
        
        # System efficiency metrics
        efficiency_metrics = self._calculate_efficiency_metrics()
        
        lines.extend([
            "⚙️ System Efficiency:",
            f"   Process Utilization: {efficiency_metrics.get('process_utilization', 0):.1%}",
            f"   Constraint Compliance: {efficiency_metrics.get('constraint_compliance', 1):.1%}",
            f"   Resource Efficiency: {efficiency_metrics.get('resource_efficiency', 0.8):.1%}",
            ""
        ])
        
        # Response time metrics (if available)
        if hasattr(self, '_performance_history'):
            response_metrics = self._calculate_response_metrics()
            lines.extend([
                "⏱️ Response Performance:",
                f"   Average Processing Time: {response_metrics.get('avg_time', 'N/A')}ms",
                f"   Peak Response Time: {response_metrics.get('peak_time', 'N/A')}ms",
                f"   Success Rate: {response_metrics.get('success_rate', 1):.1%}",
                ""
            ])
            
        # System stability metrics
        stability_metrics = self._calculate_stability_metrics()
        
        lines.extend([
            "⚖️ System Stability:",
            f"   State Consistency: {stability_metrics.get('consistency', 0.9):.1%}",
            f"   Process Reliability: {stability_metrics.get('reliability', 0.95):.1%}",
            f"   Error Rate: {stability_metrics.get('error_rate', 0.01):.1%}",
            ""
        ])
        
        # Capacity and scaling metrics
        capacity_metrics = self._calculate_capacity_metrics()
        
        lines.extend([
            "📈 Capacity & Scaling:",
            f"   Current Load: {capacity_metrics.get('current_load', 0.5):.1%}",
            f"   Peak Load Handling: {capacity_metrics.get('peak_capacity', 'Unknown')}",
            f"   Scalability Index: {capacity_metrics.get('scalability', 0.8):.1f}/10",
            ""
        ])
        
        # Historical performance comparison (if available)
        if hasattr(self, 'state_history') and len(self.state_history) >= 10:
            historical_comparison = self._compare_historical_performance()
            lines.extend([
                "📅 Historical Comparison (vs last 10 states):",
                f"   Performance Change: {historical_comparison.get('performance_delta', 0):+.1%}",
                f"   Efficiency Trend: {historical_comparison.get('efficiency_trend', 'stable').title()}",
                f"   Quality Improvement: {historical_comparison.get('quality_delta', 0):+.1%}",
                ""
            ])
            
        return "\n".join(lines)
        
    def _generate_system_recommendations(self) -> str:
        """
        🎯 Generate actionable system recommendations
        
        Provides specific, actionable recommendations based on
        current system state, performance, and identified issues.
        """
        
        lines = [
            "🎯 SYSTEM RECOMMENDATIONS",
            "=" * 30,
            ""
        ]
        
        recommendations = []
        
        # Constraint-based recommendations
        if hasattr(self, 'constraints'):
            violated = [c for c in self.constraints if not getattr(c, 'is_satisfied', True)]
            if violated:
                recommendations.append(
                    f"Address {len(violated)} constraint violations to improve system stability"
                )
                
        # Performance-based recommendations
        efficiency = self._calculate_efficiency_metrics().get('process_utilization', 0.5)
        if efficiency < 0.3:
            recommendations.append(
                "Low process utilization detected - consider activating dormant processes"
            )
        elif efficiency > 0.9:
            recommendations.append(
                "High process utilization - monitor for potential resource conflicts"
            )
            
        # Stability recommendations
        if hasattr(self, 'state_history') and len(self.state_history) >= 5:
            stability = self._assess_historical_stability(self.state_history)
            if stability['level'] == 'Low':
                recommendations.append(
                    "System instability detected - review process interaction patterns"
                )
                
        # Data quality recommendations
        quantities = getattr(self, 'quantities', {})
        unknown_trends = [q for q in quantities.values() if getattr(q, 'derivative', 'unknown') == 'unknown']
        if len(unknown_trends) > len(quantities) * 0.3:
            recommendations.append(
                "High number of quantities with unknown trends - improve monitoring coverage"
            )
            
        # Historical trend recommendations
        if hasattr(self, 'state_history') and len(self.state_history) >= 8:
            trend = self._assess_system_trend()
            if trend == 'declining':
                recommendations.append(
                    "Declining performance trend - investigate root causes and implement corrective actions"
                )
            elif trend == 'volatile':
                recommendations.append(
                    "Volatile system behavior - consider implementing stabilization measures"
                )
                
        # Capacity and scaling recommendations
        capacity = self._calculate_capacity_metrics().get('current_load', 0.5)
        if capacity > 0.8:
            recommendations.append(
                "High system load detected - prepare for scaling or load distribution"
            )
        elif capacity < 0.2:
            recommendations.append(
                "Low system utilization - consider consolidating or optimizing resources"
            )
            
        # Format recommendations
        if recommendations:
            lines.append("🎯 Priority Actions:")
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"   {i}. {rec}")
        else:
            lines.append("✅ No immediate actions required - system operating within normal parameters.")
            
        lines.extend([
            "",
            "📅 Next Review Recommendation:",
            "   Schedule next comprehensive analysis based on system activity level",
            "   and constraint satisfaction trends."
        ])
        
        return "\n".join(lines)
        
    # Helper methods for metrics and analysis
    
    def _calculate_system_health_score(self) -> float:
        """Calculate overall system health score (0.0 to 1.0)"""
        health_factors = []
        
        # Constraint satisfaction factor
        if hasattr(self, 'constraints') and self.constraints:
            satisfied = len([c for c in self.constraints if getattr(c, 'is_satisfied', True)])
            health_factors.append(satisfied / len(self.constraints))
        else:
            health_factors.append(1.0)  # No constraints = healthy
            
        # Process activity factor (balanced activity is healthy)
        processes = getattr(self, 'processes', [])
        active_count = len([p for p in processes if getattr(p, 'is_active', False)])
        if processes:
            activity_ratio = active_count / len(processes)
            # Optimal activity is around 30-70%
            activity_health = 1.0 - abs(activity_ratio - 0.5) * 2
            health_factors.append(max(0, activity_health))
            
        # Data quality factor
        quantities = getattr(self, 'quantities', {})
        if quantities:
            known_trends = [q for q in quantities.values() if getattr(q, 'derivative', 'unknown') != 'unknown']
            health_factors.append(len(known_trends) / len(quantities))
            
        return sum(health_factors) / len(health_factors) if health_factors else 0.5
        
    def _calculate_efficiency_metrics(self) -> Dict[str, float]:
        """Calculate various efficiency metrics"""
        processes = getattr(self, 'processes', [])
        active_processes = [p for p in processes if getattr(p, 'is_active', False)]
        
        return {
            'process_utilization': len(active_processes) / max(len(processes), 1),
            'constraint_compliance': self._calculate_constraint_compliance(),
            'resource_efficiency': self._compute_resource_efficiency()
        }
        
    def _calculate_constraint_compliance(self) -> float:
        """Calculate constraint compliance rate"""
        if not hasattr(self, 'constraints') or not self.constraints:
            return 1.0
            
        satisfied = len([c for c in self.constraints if getattr(c, 'is_satisfied', True)])
        return satisfied / len(self.constraints)
        
    def _calculate_stability_metrics(self) -> Dict[str, float]:
        """Calculate system stability metrics based on Forbus (1984) qualitative physics principles"""
        # Consistency: measure of contradiction-free reasoning
        consistency_score = self._compute_consistency_score()
        
        # Reliability: measure of reproducible qualitative states  
        reliability_score = self._compute_reliability_score()
        
        # Error rate: based on constraint violations and invalid transitions
        error_rate = self._compute_error_rate()
        
        return {
            'consistency': consistency_score,
            'reliability': reliability_score,
            'error_rate': error_rate
        }
    
    def _compute_resource_efficiency(self) -> float:
        """Compute resource efficiency based on active processes and constraints"""
        if not hasattr(self, 'processes') or not self.processes:
            return 0.8  # Default moderate efficiency
        
        # Efficiency based on constraint satisfaction and process utilization
        constraint_ratio = self._calculate_constraint_compliance()
        
        # Process efficiency: ratio of useful vs total processes
        active_processes = len([p for p in self.processes if getattr(p, 'is_active', False)])
        total_processes = len(self.processes)
        process_efficiency = active_processes / max(total_processes, 1)
        
        # Combined efficiency score
        return (constraint_ratio * 0.6 + process_efficiency * 0.4)
    
    def _compute_consistency_score(self) -> float:
        """Compute consistency based on contradictory qualitative states"""
        if not hasattr(self, 'qualitative_states') or not self.qualitative_states:
            return 0.95  # High default if no states to check
        
        # Check for contradictory qualitative relationships
        contradictions = 0
        total_relationships = 0
        
        for state in self.qualitative_states:
            if hasattr(state, 'relationships'):
                for rel in state.relationships:
                    total_relationships += 1
                    # Check for logical contradictions (e.g., A > B and B > A simultaneously)
                    if hasattr(rel, 'is_contradictory') and rel.is_contradictory:
                        contradictions += 1
        
        if total_relationships == 0:
            return 0.95
        
        return max(0.0, 1.0 - (contradictions / total_relationships))
    
    def _compute_reliability_score(self) -> float:
        """Compute reliability based on state transition stability"""
        if not hasattr(self, 'state_history') or len(self.state_history) < 2:
            return 0.90  # Default if insufficient history
        
        # Measure stability of qualitative state transitions
        stable_transitions = 0
        total_transitions = len(self.state_history) - 1
        
        for i in range(1, len(self.state_history)):
            prev_state = self.state_history[i-1]
            curr_state = self.state_history[i]
            
            # Check if transition follows qualitative physics rules
            if self._is_valid_transition(prev_state, curr_state):
                stable_transitions += 1
        
        if total_transitions == 0:
            return 0.90
            
        return stable_transitions / total_transitions
    
    def _compute_error_rate(self) -> float:
        """Compute error rate based on constraint violations"""
        if not hasattr(self, 'constraints') or not self.constraints:
            return 0.02  # Low default error rate
        
        violations = len([c for c in self.constraints if not getattr(c, 'is_satisfied', True)])
        total_constraints = len(self.constraints)
        
        return violations / max(total_constraints, 1)
    
    def _is_valid_transition(self, prev_state: Any, curr_state: Any) -> bool:
        """Check if qualitative state transition is valid according to physics rules"""
        # Basic validation - in full implementation would check continuity principles
        if not hasattr(prev_state, 'qualitative_value') or not hasattr(curr_state, 'qualitative_value'):
            return True  # Cannot validate without proper state structure
        
        # Example: check for continuity (no jumping between non-adjacent qualitative values)
        prev_val = getattr(prev_state, 'qualitative_value', 0)
        curr_val = getattr(curr_state, 'qualitative_value', 0)
        
        # Allow transitions between adjacent or same qualitative regions
        return abs(prev_val - curr_val) <= 1
        
    def _calculate_capacity_metrics(self) -> Dict[str, Any]:
        """Calculate system capacity and load metrics"""
        # Simplified capacity calculation based on process activity
        processes = getattr(self, 'processes', [])
        active_count = len([p for p in processes if getattr(p, 'is_active', False)])
        
        current_load = active_count / max(len(processes), 1) if processes else 0
        
        return {
            'current_load': current_load,
            'peak_capacity': 'Unknown',  # Would need historical peak data
            'scalability': min(10, max(1, 8 - current_load * 5))  # Simple heuristic
        }
