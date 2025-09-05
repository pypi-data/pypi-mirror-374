"""
🎨 Visualization Core
======================

🎯 ELI5 Summary:
This is like an artist's palette for our data! Just like how artists use different 
colors and brushes to paint pictures that help people understand their ideas, this file 
creates charts, graphs, and visual displays that help researchers see and understand 
what their algorithms are doing.

🧪 Technical Details:
===================
Implementation details and technical specifications for this component.
Designed to work seamlessly within the research framework while
maintaining high performance and accuracy standards.

🧠 Core Algorithm Architecture:
===============================
    Input → Processing → Output
      ↓         ↓         ↓
  [Data]  [Algorithm]  [Result]
      ↓         ↓         ↓
     📊        ⚙️        ✨
     
Mathematical Foundation → Implementation → Research Application

"""
"""
📊 Qualitative Reasoning - Visualization Core Module
=================================================

Core visualization functionality for qualitative reasoning systems.
Extracted from visualization_engine.py to enforce 800-line limit.

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Forbus & de Kleer (1993) - Building Problem Solvers

This module provides the core visualization mixin with state display
and system overview functionality.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from ..qualitative_reasoning_modules.core_types import QualitativeState

class VisualizationConfig:
    """
    📋 Configuration for visualization display options.
    
    Controls various aspects of visualization output including detail levels,
    formatting options, and feature toggles.
    """
    
    def __init__(self):
        self.detail_level = "medium"  # basic, medium, detailed, comprehensive
        self.include_history = True
        self.include_relationships = True  
        self.include_constraints = True
        self.max_history_length = 10
        self.color_support = True
        self.unicode_symbols = True
        self.export_format = "json"  # json, csv, markdown, text

class VisualizationReport:
    """
    📊 Container for visualization report data and formatting.
    
    Stores visualization content in structured format with multiple
    output options (text, JSON, markdown).
    """
    
    def __init__(self, title: str, timestamp: str, summary: str):
        self.title = title
        self.timestamp = timestamp
        self.summary = summary
        self.sections = {}
        self.data = {}
        
    def add_section(self, name: str, content: str):
        """Add a named section with content"""
        self.sections[name] = content
        
    def add_data(self, key: str, value: Any):
        """Add structured data for export"""
        self.data[key] = value
        
    def to_text(self) -> str:
        """Generate formatted text report"""
        lines = [
            "=" * 80,
            f"🎯 {self.title}", 
            f"⏰ Generated: {self.timestamp}",
            "=" * 80,
            "",
            "📋 SUMMARY",
            "-" * 20,
            self.summary,
            ""
        ]
        
        for section_name, content in self.sections.items():
            lines.extend([
                f"📊 {section_name.upper()}",
                "-" * (len(section_name) + 4),
                content,
                ""
            ])
            
        return "\n".join(lines)
        
    def to_json(self) -> str:
        """Export as JSON format"""
        export_data = {
            "title": self.title,
            "timestamp": self.timestamp, 
            "summary": self.summary,
            "sections": self.sections,
            "data": self.data
        }
        return json.dumps(export_data, indent=2, default=str)
        
    def to_markdown(self) -> str:
        """Generate markdown report"""
        lines = [
            f"# {self.title}",
            f"*Generated: {self.timestamp}*",
            "",
            "## Summary",
            self.summary,
            ""
        ]
        
        for section_name, content in self.sections.items():
            lines.extend([
                f"## {section_name}",
                f"```",
                content,
                f"```",
                ""
            ])
            
        return "\n".join(lines)

class VisualizationCoreMixin:
    """
    Core visualization functionality for qualitative reasoning systems.
    
    Provides basic state visualization, system overview, and quantity display.
    This is the foundation that other visualization mixins build upon.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize visualization core components"""
        super().__init__(*args, **kwargs)
        
        # Visualization configuration
        self._viz_config = VisualizationConfig()
        self._viz_cache = {}
        self._export_history = []
        
        # Symbol mappings for display
        self._trend_symbols = {
            "+" : "↗", "-": "↘", "0": "→", "?": "❓",
            "increasing": "↗", "decreasing": "↘", "steady": "→", "unknown": "❓"
        }
        
        self._magnitude_symbols = {
            "pos_inf": "∞+", "neg_inf": "∞-", "pos_large": "++", "neg_large": "--",
            "pos_small": "+", "neg_small": "-", "zero": "0", "increasing": "↗", "decreasing": "↘"
        }
        
        # Initialize color support (if available)
        self._color_support = self._detect_color_support()
        
    def visualize_system_state(self, include_history: bool = True, detail_level: str = None) -> VisualizationReport:
        """
        📊 Visualize current system state and optional history
        
        Creates a comprehensive visualization of the current qualitative state
        including quantities, processes, relationships, and temporal context.
        
        Args:
            include_history: Whether to include historical state information
            detail_level: Level of detail ("basic", "medium", "detailed", "comprehensive")
            
        Returns:
            VisualizationReport: Complete visualization report
        """
        
        detail_level = detail_level or self._viz_config.detail_level
        
        # Create visualization report
        report = VisualizationReport(
            title=f"System State: {getattr(self, 'domain_name', 'Qualitative Reasoning System')}",
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            summary=self._generate_system_summary()
        )
        
        # Add core sections
        report.add_section("System Overview", self._visualize_system_overview())
        report.add_section("Current Quantities", self._visualize_quantities(detail_level))
        report.add_section("Active Processes", self._visualize_active_processes(detail_level))
        
        if self._viz_config.include_relationships:
            report.add_section("Relationships", self._visualize_relationships())
            
        if include_history and hasattr(self, 'state_history') and len(self.state_history) > 1:
            report.add_section("State History", self._visualize_state_history(detail_level))
            
        if self._viz_config.include_constraints:
            report.add_section("Constraints", self._visualize_constraints())
            
        if detail_level in ["detailed", "comprehensive"]:
            report.add_section("Analysis Summary", self._generate_analysis_summary())
            
        # Add structured data
        report.add_data("quantities", self._export_quantities_data())
        report.add_data("processes", self._export_processes_data()) 
        report.add_data("relationships", self._export_relationships_data())
        
        # Cache results
        self._viz_cache['last_state_visualization'] = report
        
        # Print to console by default (preserving original behavior)
        if self._viz_config.detail_level != "silent":
            print(self._format_console_output(report))
            
        return report
        
    def _generate_system_summary(self) -> str:
        """
        📋 Generate high-level system summary
        
        Creates a concise overview of the current system state including
        basic statistics and status information.
        """
        
        quantities_count = len(getattr(self, 'quantities', {}))
        processes_count = len([p for p in getattr(self, 'processes', []) if getattr(p, 'is_active', False)])
        relationships_count = len(getattr(self, 'derived_relationships', {}))
        
        summary_lines = [
            f"🔢 Quantities: {quantities_count} tracked",
            f"⚙️ Active Processes: {processes_count} running",
            f"🔗 Relationships: {relationships_count} derived"
        ]
        
        # Add state history info if available
        if hasattr(self, 'state_history'):
            history_length = len(self.state_history)
            summary_lines.append(f"📚 History: {history_length} states recorded")
            
        # Add constraint info if available
        if hasattr(self, 'constraints'):
            constraint_count = len(self.constraints)
            summary_lines.append(f"⚖️ Constraints: {constraint_count} active")
            
        return "\n".join(summary_lines)
        
    def _visualize_system_overview(self) -> str:
        """
        🎯 Generate system overview visualization
        
        Provides a high-level view of the system state with key metrics
        and overall system health indicators.
        """
        
        lines = ["📊 SYSTEM STATUS", "" + "=" * 40]
        
        # System metadata
        domain = getattr(self, 'domain_name', 'Unknown Domain')
        lines.extend([f"Domain: {domain}", ""])
        
        # Current state summary
        if hasattr(self, 'current_state') and self.current_state:
            state_time = getattr(self.current_state, 'time', 'Unknown')
            lines.extend([f"Current Time: {state_time}", ""])
            
        # Component counts and status
        quantities = getattr(self, 'quantities', {})
        processes = getattr(self, 'processes', [])
        
        lines.extend([
            f"📊 Components:",
            f"   Quantities: {len(quantities):>3} tracked",
            f"   Processes:  {len(processes):>3} defined", 
            f"   Active:     {len([p for p in processes if getattr(p, 'is_active', False)]):>3} running",
            ""
        ])
        
        # System health indicators
        lines.append("🏥 System Health:")
        
        # Check for constraint violations
        violations = []
        if hasattr(self, 'constraints'):
            for constraint in self.constraints:
                if not getattr(constraint, 'is_satisfied', True):
                    violations.append(constraint)
                    
        if violations:
            lines.append(f"   ⚠️  {len(violations)} constraint violation(s) detected")
        else:
            lines.append("   ✅ No constraint violations")
            
        # Check for active processes
        active_processes = [p for p in processes if getattr(p, 'is_active', False)]
        if active_processes:
            lines.append(f"   ⚡ {len(active_processes)} process(es) actively influencing system")
        else:
            lines.append("   🔄 System in equilibrium (no active processes)")
            
        return "\n".join(lines)
        
    def _visualize_quantities(self, detail_level: str) -> str:
        """
        📊 Visualize current quantities and their states
        
        Shows all tracked quantities with their magnitudes, trends,
        and other qualitative properties.
        
        Args:
            detail_level: Level of detail for display
        """
        
        quantities = getattr(self, 'quantities', {})
        if not quantities:
            return "No quantities currently tracked."
            
        lines = []
        
        # Header
        if detail_level == "basic":
            lines.extend(["📊 QUANTITIES (Basic)", "" + "-" * 30])
        else:
            lines.extend(["📊 QUANTITIES (Detailed)", "" + "-" * 35])
            
        # Display quantities
        for qty_name, quantity in quantities.items():
            # Get quantity properties
            magnitude = getattr(quantity, 'magnitude', 'unknown')
            trend = getattr(quantity, 'derivative', 'unknown')
            
            # Format symbols
            mag_symbol = self._magnitude_symbols.get(str(magnitude), str(magnitude))
            trend_symbol = self._trend_symbols.get(str(trend), str(trend))
            
            if detail_level == "basic":
                lines.append(f"   {qty_name:20} {mag_symbol:>4} {trend_symbol}")
            else:
                # Detailed view with additional information
                unit = getattr(quantity, 'unit', '')
                description = getattr(quantity, 'description', '')
                
                lines.extend([
                    f"   📏 {qty_name}",
                    f"      Magnitude: {mag_symbol:>4} ({magnitude})",
                    f"      Trend:     {trend_symbol:>4} ({trend})"
                ])
                
                if unit:
                    lines.append(f"      Unit:      {unit}")
                if description:
                    lines.append(f"      Info:      {description[:50]}{'...' if len(description) > 50 else ''}")
                    
                lines.append("")  # Spacing between quantities
                
        return "\n".join(lines)
        
    def _visualize_active_processes(self, detail_level: str) -> str:
        """
        ⚙️ Visualize currently active processes and their influences
        
        Shows all processes that are currently active and influencing
        quantities in the system.
        
        Args:
            detail_level: Level of detail for display
        """
        
        processes = getattr(self, 'processes', [])
        active_processes = [p for p in processes if getattr(p, 'is_active', False)]
        
        if not active_processes:
            return "⚙️ No processes currently active.\n   System is in equilibrium."
            
        lines = ["⚙️ ACTIVE PROCESSES", "" + "-" * 25]
        
        for process in active_processes:
            process_name = getattr(process, 'name', 'Unnamed Process')
            influences = getattr(process, 'influences', [])
            
            if detail_level == "basic":
                influence_count = len(influences)
                lines.append(f"   🔄 {process_name} ({influence_count} influences)")
            else:
                # Detailed view
                lines.extend([
                    f"   🔄 {process_name}",
                    f"      Status: Active"
                ])
                
                # Show preconditions if available
                preconditions = getattr(process, 'preconditions', [])
                if preconditions:
                    lines.append(f"      Preconditions: {len(preconditions)} satisfied")
                    
                # Show influences in detail
                if influences:
                    lines.append("      Influences:")
                    for influence in influences:
                        qty_name = getattr(influence, 'quantity_name', 'Unknown')
                        direction = getattr(influence, 'direction', 'unknown')
                        symbol = "+" if direction == "positive" else "-" if direction == "negative" else "?"
                        lines.append(f"         {symbol} {qty_name}")
                        
                lines.append("")  # Spacing between processes
                
        return "\n".join(lines)
        
    def _detect_color_support(self) -> bool:
        """
        🎨 Detect if terminal supports color output
        
        Simple heuristic to determine color capability.
        """
        import os
        return 'TERM' in os.environ and os.environ['TERM'] != 'dumb'
        
    def configure_visualization(self, **config_options):
        """
        ⚙️ Configure visualization display options
        
        Updates visualization configuration with provided options.
        """
        for key, value in config_options.items():
            if hasattr(self._viz_config, key):
                setattr(self._viz_config, key, value)
            else:
                print(f"Warning: Unknown visualization config option '{key}'")
                
    def get_visualization_metrics(self) -> Dict[str, Any]:
        """
        📊 Get visualization system metrics and statistics
        
        Returns information about visualization performance and usage.
        """
        return {
            'cache_size': len(self._viz_cache),
            'export_count': len(self._export_history),
            'color_support': self._color_support,
            'last_render_time': self._viz_cache.get('last_render_time'),
            'config': {
                'detail_level': self._viz_config.detail_level,
                'include_history': self._viz_config.include_history,
                'include_relationships': self._viz_config.include_relationships
            }
        }
