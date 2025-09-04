"""
📅 Qualitative Reasoning - Visualization History Module
====================================================

History rendering and timeline visualization for qualitative reasoning systems.
Extracted from visualization_engine.py to enforce 800-line limit.

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Forbus & de Kleer (1993) - Building Problem Solvers

This module provides history visualization, timeline rendering,
and temporal state analysis functionality.
"""

from typing import Dict, List, Any, Optional
from ..qr_modules.core_types import QualitativeState

class VisualizationHistoryMixin:
    """
    History visualization and timeline rendering for qualitative reasoning.
    
    Provides comprehensive temporal visualization capabilities including
    timeline rendering, state change detection, and historical analysis.
    """
    
    def _visualize_relationships(self) -> str:
        """
        🔗 Visualize derived relationships between quantities
        
        Shows mathematical and causal relationships that have been
        derived or inferred in the current system state.
        """
        
        relationships = getattr(self, 'derived_relationships', {})
        if not relationships:
            return "🔗 No derived relationships currently available."
            
        lines = ["🔗 DERIVED RELATIONSHIPS", "" + "-" * 30]
        
        for rel_name, relationship in relationships.items():
            rel_type = getattr(relationship, 'type', 'unknown')
            description = getattr(relationship, 'description', rel_name)
            
            # Format relationship based on type
            if rel_type == 'proportional':
                lines.append(f"   ↔️ {description} (proportional)")
            elif rel_type == 'inverse':
                lines.append(f"   ⇆ {description} (inverse)")
            elif rel_type == 'causal':
                lines.append(f"   ➡️ {description} (causal)")
            else:
                lines.append(f"   🔗 {description} ({rel_type})")
                
            # Add details if available
            if hasattr(relationship, 'quantities_involved'):
                quantities = getattr(relationship, 'quantities_involved', [])
                if len(quantities) >= 2:
                    lines.append(f"      Involves: {', '.join(quantities[:3])}{'...' if len(quantities) > 3 else ''}")
                    
        return "\n".join(lines)
        
    def _visualize_state_history(self, detail_level: str) -> str:
        """
        📅 Visualize historical state evolution
        
        Shows how the system state has evolved over time with
        key changes and transitions highlighted.
        
        Args:
            detail_level: Level of detail for history display
        """
        
        if not hasattr(self, 'state_history') or len(self.state_history) <= 1:
            return "📅 No state history available (need 2+ states)."
            
        history = self.state_history[-self._viz_config.max_history_length:]
        
        lines = ["📅 STATE EVOLUTION HISTORY", "" + "-" * 35]
        
        for i, state in enumerate(history):
            state_time = getattr(state, 'time', f'State {i}')
            state_desc = getattr(state, 'description', 'System state')
            
            if detail_level == "basic":
                lines.append(f"   {i+1:2}. {state_time} - {state_desc}")
            else:
                # Detailed history with change detection
                lines.append(f"   ⏰ Time: {state_time}")
                lines.append(f"   📏 {state_desc}")
                
                # Detect changes from previous state
                if i > 0:
                    prev_state = history[i-1]
                    changes = self._detect_state_changes(prev_state, state)
                    if changes:
                        lines.append("   🔄 Changes:")
                        for change in changes[:3]:  # Limit to 3 changes
                            lines.append(f"      • {change}")
                            
                lines.append("")  # Spacing between states
                
        return "\n".join(lines)
        
    def _visualize_constraints(self) -> str:
        """
        ⚖️ Visualize system constraints and any violations
        
        Shows all active constraints and highlights any that
        are currently being violated.
        """
        
        if not hasattr(self, 'constraints'):
            return "⚖️ No constraints defined for this system."
            
        constraints = self.constraints
        if not constraints:
            return "⚖️ No constraints currently active."
            
        lines = ["⚖️ SYSTEM CONSTRAINTS", "" + "-" * 25]
        
        satisfied_constraints = []
        violated_constraints = []
        
        for constraint in constraints:
            constraint_name = getattr(constraint, 'name', 'Unnamed Constraint')
            is_satisfied = getattr(constraint, 'is_satisfied', True)
            
            if is_satisfied:
                satisfied_constraints.append(constraint)
            else:
                violated_constraints.append(constraint)
                
        # Show violations first (more important)
        if violated_constraints:
            lines.extend(["   ⚠️ VIOLATIONS:", ""])
            for constraint in violated_constraints:
                constraint_name = getattr(constraint, 'name', 'Unnamed')
                description = getattr(constraint, 'description', '')
                lines.append(f"      ❌ {constraint_name}")
                if description:
                    lines.append(f"         {description[:60]}{'...' if len(description) > 60 else ''}")
            lines.append("")
            
        # Show satisfied constraints
        if satisfied_constraints:
            lines.extend(["   ✅ SATISFIED:", ""])
            for constraint in satisfied_constraints[:5]:  # Limit display
                constraint_name = getattr(constraint, 'name', 'Unnamed')
                lines.append(f"      ✓ {constraint_name}")
                
            if len(satisfied_constraints) > 5:
                remaining = len(satisfied_constraints) - 5
                lines.append(f"      ... and {remaining} more")
                
        return "\n".join(lines)
        
    def _generate_analysis_summary(self) -> str:
        """
        📊 Generate comprehensive analysis summary
        
        Creates an analytical overview highlighting key insights,
        patterns, and important system behaviors.
        """
        
        lines = ["📊 ANALYSIS INSIGHTS", "" + "-" * 25]
        
        # System stability analysis
        if hasattr(self, 'state_history') and len(self.state_history) >= 3:
            recent_states = self.state_history[-3:]
            
            # Detect stability patterns
            if self._is_system_stable(recent_states):
                lines.append("   🟢 System appears stable (minimal changes)")
            else:
                lines.append("   🟡 System shows dynamic behavior (active changes)")
                
        # Process activity analysis
        processes = getattr(self, 'processes', [])
        active_count = len([p for p in processes if getattr(p, 'is_active', False)])
        
        if active_count == 0:
            lines.append("   ⚙️ System in equilibrium (no active processes)")
        elif active_count == 1:
            lines.append("   ⚙️ Single process driving system behavior")
        else:
            lines.append(f"   ⚙️ Multiple processes active ({active_count} concurrent)")
            
        # Constraint health
        if hasattr(self, 'constraints') and self.constraints:
            violations = [c for c in self.constraints if not getattr(c, 'is_satisfied', True)]
            if not violations:
                lines.append("   ✅ All constraints satisfied (healthy state)")
            else:
                lines.append(f"   ⚠️ {len(violations)} constraint violations detected")
                
        # Quantity trend analysis
        quantities = getattr(self, 'quantities', {})
        if quantities:
            increasing = [q for q in quantities.values() if getattr(q, 'derivative', '') == 'increasing']
            decreasing = [q for q in quantities.values() if getattr(q, 'derivative', '') == 'decreasing']
            
            if len(increasing) > len(decreasing):
                lines.append(f"   ↗️ Predominantly increasing trends ({len(increasing)} quantities)")
            elif len(decreasing) > len(increasing):
                lines.append(f"   ↘️ Predominantly decreasing trends ({len(decreasing)} quantities)")
            else:
                lines.append("   → Balanced trend distribution")
                
        # Add domain-specific insights if available
        domain_insights = getattr(self, '_generate_domain_insights', lambda: [])() 
        for insight in domain_insights[:3]:  # Limit to 3 insights
            lines.append(f"   🔍 {insight}")
            
        return "\n".join(lines)
        
    def _detect_state_changes(self, prev_state: QualitativeState, curr_state: QualitativeState) -> List[str]:
        """
        🔍 Detect changes between two qualitative states
        
        Analyzes two states to identify what quantities, processes,
        or relationships have changed.
        
        Args:
            prev_state: Previous system state
            curr_state: Current system state
            
        Returns:
            List[str]: Descriptions of detected changes
        """
        
        changes = []
        
        # Compare quantities if available
        prev_quantities = getattr(prev_state, 'quantities', {})
        curr_quantities = getattr(curr_state, 'quantities', {})
        
        for qty_name in set(prev_quantities.keys()) | set(curr_quantities.keys()):
            if qty_name not in prev_quantities:
                changes.append(f"New quantity appeared: {qty_name}")
            elif qty_name not in curr_quantities:
                changes.append(f"Quantity disappeared: {qty_name}")
            else:
                # Check for magnitude or trend changes
                prev_mag = getattr(prev_quantities[qty_name], 'magnitude', 'unknown')
                curr_mag = getattr(curr_quantities[qty_name], 'magnitude', 'unknown')
                prev_trend = getattr(prev_quantities[qty_name], 'derivative', 'unknown')
                curr_trend = getattr(curr_quantities[qty_name], 'derivative', 'unknown')
                
                if prev_mag != curr_mag:
                    changes.append(f"{qty_name} magnitude: {prev_mag} → {curr_mag}")
                if prev_trend != curr_trend:
                    changes.append(f"{qty_name} trend: {prev_trend} → {curr_trend}")
                    
        # Compare active processes
        prev_active = getattr(prev_state, 'active_processes', [])
        curr_active = getattr(curr_state, 'active_processes', [])
        
        prev_names = set(getattr(p, 'name', str(p)) for p in prev_active)
        curr_names = set(getattr(p, 'name', str(p)) for p in curr_active)
        
        for process_name in curr_names - prev_names:
            changes.append(f"Process activated: {process_name}")
        for process_name in prev_names - curr_names:
            changes.append(f"Process deactivated: {process_name}")
            
        return changes[:5]  # Limit to 5 most important changes
        
    def _format_console_output(self, report) -> str:
        """
        🖥️ Format report for console display
        
        Creates a clean, readable console version of the visualization report
        with appropriate spacing and formatting.
        
        Args:
            report: VisualizationReport to format
            
        Returns:
            str: Console-formatted report
        """
        
        if self._viz_config.detail_level == "silent":
            return ""
            
        # Use the report's built-in text formatting
        console_output = report.to_text()
        
        # Add terminal-specific enhancements if color support is available
        if self._color_support and self._viz_config.color_support:
            # Simple color enhancements (could be expanded)
            console_output = console_output.replace("⚠️", "\033[93m⚠️\033[0m")  # Yellow warning
            console_output = console_output.replace("✅", "\033[92m✅\033[0m")  # Green check
            console_output = console_output.replace("❌", "\033[91m❌\033[0m")  # Red X
            
        return console_output
        
    def render_state_history(self, format_type: str = "timeline") -> str:
        """
        📊 Render state history in specified format
        
        Provides multiple visualization formats for historical data.
        
        Args:
            format_type: "timeline", "table", "chart", "summary"
            
        Returns:
            str: Formatted history visualization
        """
        
        if not hasattr(self, 'state_history') or not self.state_history:
            return "No state history available for rendering."
            
        if format_type == "timeline":
            return self._render_timeline_history()
        elif format_type == "table":
            return self._render_tabular_history()
        elif format_type == "chart":
            return self._render_chart_history()
        elif format_type == "summary":
            return self._render_summary_history()
        else:
            return f"Unknown format type '{format_type}'. Use: timeline, table, chart, summary"
            
    def _render_timeline_history(self) -> str:
        """
        📊 Render history as timeline visualization
        """
        
        history = self.state_history[-10:]  # Last 10 states
        lines = ["📅 STATE TIMELINE", "=" * 20, ""]
        
        for i, state in enumerate(history):
            time_stamp = getattr(state, 'time', f'T{i}')
            description = getattr(state, 'description', 'State')
            
            # Timeline formatting
            connector = "│" if i < len(history) - 1 else " "
            lines.extend([
                f"│",
                f"├── {time_stamp}: {description}",
                f"│"
            ])
            
        return "\n".join(lines)
        
    def _render_tabular_history(self) -> str:
        """
        📊 Render history as structured table
        """
        
        history = self.state_history[-8:]  # Last 8 states for table width
        
        lines = [
            "📊 STATE HISTORY TABLE",
            "=" * 50,
            f"{'Time':<10} {'Active Processes':<15} {'Key Changes':<25}",
            "-" * 50
        ]
        
        for i, state in enumerate(history):
            time_stamp = str(getattr(state, 'time', f'T{i}'))[:9]
            
            # Count active processes
            active_processes = getattr(state, 'active_processes', [])
            process_count = len(active_processes)
            
            # Detect major changes (simplified)
            changes = "Stable" if i == 0 else "Changes"
            
            lines.append(f"{time_stamp:<10} {process_count:<15} {changes:<25}")
            
        return "\n".join(lines)
        
    def _render_chart_history(self) -> str:
        """
        📊 Render history as ASCII chart visualization
        """
        
        # Simple ASCII chart showing process activity over time
        history = self.state_history[-20:]  # Last 20 states
        
        lines = [
            "📊 PROCESS ACTIVITY CHART",
            "=" * 40,
            "Activity Level  |  Timeline",
            "               |"
        ]
        
        # Build chart
        for i, state in enumerate(history):
            active_count = len(getattr(state, 'active_processes', []))
            
            # Scale activity to chart width (0-10)
            activity_level = min(10, active_count)
            bar = "█" * activity_level + "░" * (10 - activity_level)
            
            time_label = str(getattr(state, 'time', i))[:6]
            lines.append(f"{time_label:>6} {activity_level:>2}   |{bar}")
            
        lines.extend([
            "               |",
            "Legend: █ = Active Process, ░ = Inactive"
        ])
        
        return "\n".join(lines)
        
    def _render_summary_history(self) -> str:
        """
        📊 Render condensed history summary
        """
        
        if len(self.state_history) < 2:
            return "Insufficient history for summary (need 2+ states)."
            
        recent_states = self.state_history[-5:]  # Last 5 states
        
        lines = [
            "📊 HISTORY SUMMARY",
            "=" * 25,
            f"Total States: {len(self.state_history)}",
            f"Time Span: {getattr(self.state_history[0], 'time', 'Start')} → {getattr(self.state_history[-1], 'time', 'Now')}",
            "",
            "Recent Activity:"
        ]
        
        # Analyze recent patterns
        total_processes = 0
        for state in recent_states:
            total_processes += len(getattr(state, 'active_processes', []))
            
        avg_activity = total_processes / len(recent_states) if recent_states else 0
        
        lines.extend([
            f"  Average Processes Active: {avg_activity:.1f}",
            f"  Recent Stability: {'High' if avg_activity < 1 else 'Medium' if avg_activity < 3 else 'Low'}",
            f"  Last Update: {getattr(self.state_history[-1], 'time', 'Unknown')}"
        ])
        
        return "\n".join(lines)
        
    def _is_system_stable(self, recent_states: List) -> bool:
        """
        🔍 Determine if system appears stable based on recent states
        
        Simple heuristic for system stability assessment.
        """
        
        if len(recent_states) < 2:
            return True  # Default to stable
            
        # Check if active process count is consistent
        process_counts = []
        for state in recent_states:
            count = len(getattr(state, 'active_processes', []))
            process_counts.append(count)
            
        # System is stable if process activity is consistent
        return max(process_counts) - min(process_counts) <= 1
