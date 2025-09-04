"""
💾 Qualitative Reasoning - Visualization Exports Module
=====================================================

Data export and formatting for qualitative reasoning systems.
Extracted from visualization_engine.py to enforce 800-line limit.

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Forbus & de Kleer (1993) - Building Problem Solvers

This module provides comprehensive data export functionality in multiple
formats including JSON, CSV, Markdown, and plain text.
"""

import json
import csv
import os
from io import StringIO
from typing import Dict, List, Any, Optional
from datetime import datetime

class VisualizationExportsMixin:
    """
    Data export and formatting for qualitative reasoning visualization.
    
    Provides comprehensive export capabilities in multiple formats with
    proper data serialization and file management.
    """
    
    def export_data(self, format_type: str = "json", filename: Optional[str] = None) -> str:
        """
        💾 Export visualization data in specified format
        
        Exports current system state and visualization data to various formats
        suitable for external analysis, reporting, or integration.
        
        Args:
            format_type: Export format ("json", "csv", "markdown", "text")
            filename: Optional filename for file export
            
        Returns:
            str: Exported data as string or filename if file was created
            
        💾 Supported Export Formats:
        - **JSON**: Structured data for programmatic processing
        - **CSV**: Tabular data for spreadsheet analysis
        - **Markdown**: Documentation-ready format
        - **Text**: Human-readable plain text report
        """
        
        if format_type.lower() == "json":
            return self._export_json(filename)
        elif format_type.lower() == "csv":
            return self._export_csv(filename)
        elif format_type.lower() == "markdown":
            return self._export_markdown(filename)
        elif format_type.lower() == "text":
            return self._export_text(filename)
        else:
            available_formats = "json, csv, markdown, text"
            raise ValueError(f"Unsupported format '{format_type}'. Available: {available_formats}")
            
    def _export_json(self, filename: Optional[str] = None) -> str:
        """
        💾 Export system state as JSON format
        
        Creates comprehensive JSON export suitable for programmatic processing
        and integration with external systems.
        """
        
        export_data = {
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "domain_name": getattr(self, 'domain_name', 'Unknown'),
                "export_version": "1.0",
                "exporter": "QualitativeReasoning.VisualizationEngine"
            },
            "current_state": {
                "quantities": self._export_quantities_data(),
                "processes": self._export_processes_data(),
                "relationships": self._export_relationships_data(),
                "constraints": self._export_constraints_data()
            },
            "history": self._export_history_data(),
            "performance": self._export_performance_data(),
            "analysis": {
                "system_health": self._calculate_system_health_score(),
                "efficiency_metrics": self._calculate_efficiency_metrics(),
                "recommendations": self._get_export_recommendations()
            }
        }
        
        json_output = json.dumps(export_data, indent=2, default=self._json_serializer)
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(json_output)
            self._log_export('json', filename)
            return f"Data exported to {filename}"
        else:
            return json_output
            
    def _export_csv(self, filename: Optional[str] = None) -> str:
        """
        💾 Export system state as CSV format
        
        Creates CSV exports of key system data suitable for spreadsheet
        analysis and statistical processing.
        """
        
        output = StringIO()
        
        # Export quantities data
        output.write("=== QUANTITIES ===\n")
        quantities = self._export_quantities_data()
        if quantities:
            writer = csv.DictWriter(output, fieldnames=['name', 'magnitude', 'derivative', 'unit', 'description'])
            writer.writeheader()
            
            for qty_name, qty_data in quantities.items():
                writer.writerow({
                    'name': qty_name,
                    'magnitude': qty_data.get('magnitude', 'unknown'),
                    'derivative': qty_data.get('derivative', 'unknown'),
                    'unit': qty_data.get('unit', ''),
                    'description': qty_data.get('description', '')
                })
                
        output.write("\n=== PROCESSES ===\n")
        processes = self._export_processes_data()
        if processes:
            writer = csv.DictWriter(output, fieldnames=['name', 'is_active', 'influence_count', 'description'])
            writer.writeheader()
            
            for proc_name, proc_data in processes.items():
                writer.writerow({
                    'name': proc_name,
                    'is_active': proc_data.get('is_active', False),
                    'influence_count': len(proc_data.get('influences', [])),
                    'description': proc_data.get('description', '')
                })
                
        # Export historical data if available
        if hasattr(self, 'state_history') and self.state_history:
            output.write("\n=== HISTORY ===\n")
            writer = csv.DictWriter(output, fieldnames=['time', 'active_processes', 'total_quantities', 'description'])
            writer.writeheader()
            
            for state in self.state_history[-10:]:  # Last 10 states
                writer.writerow({
                    'time': getattr(state, 'time', 'Unknown'),
                    'active_processes': len(getattr(state, 'active_processes', [])),
                    'total_quantities': len(getattr(state, 'quantities', {})),
                    'description': getattr(state, 'description', '')
                })
                
        csv_output = output.getvalue()
        output.close()
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(csv_output)
            self._log_export('csv', filename)
            return f"Data exported to {filename}"
        else:
            return csv_output
            
    def _export_markdown(self, filename: Optional[str] = None) -> str:
        """
        💾 Export system state as Markdown format
        
        Creates documentation-ready Markdown export suitable for
        reports, documentation, and presentation.
        """
        
        lines = [
            f"# Qualitative Reasoning System Export",
            f"",
            f"**Export Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**Domain**: {getattr(self, 'domain_name', 'Unknown Domain')}  ",
            f"**System Health**: {self._calculate_system_health_score():.1%}  ",
            f"",
            "## Current System State",
            ""
        ]
        
        # Quantities section
        quantities = self._export_quantities_data()
        if quantities:
            lines.extend([
                "### Quantities",
                "",
                "| Name | Magnitude | Trend | Unit | Description |",
                "|------|-----------|--------|------|-------------|"
            ])
            
            for qty_name, qty_data in quantities.items():
                magnitude = qty_data.get('magnitude', 'unknown')
                derivative = qty_data.get('derivative', 'unknown')
                unit = qty_data.get('unit', '-')
                description = qty_data.get('description', '')[:50]
                
                lines.append(f"| {qty_name} | {magnitude} | {derivative} | {unit} | {description} |")
                
            lines.append("")
            
        # Processes section
        processes = self._export_processes_data()
        if processes:
            lines.extend([
                "### Active Processes",
                ""
            ])
            
            active_processes = {name: data for name, data in processes.items() if data.get('is_active', False)}
            
            if active_processes:
                for proc_name, proc_data in active_processes.items():
                    description = proc_data.get('description', 'No description')
                    influences = proc_data.get('influences', [])
                    
                    lines.extend([
                        f"#### {proc_name}",
                        f"{description}",
                        f"**Influences**: {len(influences)} quantities",
                        ""
                    ])
            else:
                lines.extend(["*No processes currently active.*", ""])
                
        # Constraints section
        if hasattr(self, 'constraints') and self.constraints:
            violations = [c for c in self.constraints if not getattr(c, 'is_satisfied', True)]
            
            lines.extend([
                "### Constraints",
                f"**Total**: {len(self.constraints)}  ",
                f"**Satisfied**: {len(self.constraints) - len(violations)}  ",
                f"**Violations**: {len(violations)}  ",
                ""
            ])
            
            if violations:
                lines.extend(["#### Violations", ""])
                for violation in violations:
                    name = getattr(violation, 'name', 'Unnamed')
                    description = getattr(violation, 'description', 'No description')
                    lines.extend([f"- **{name}**: {description}", ""])
                    
        # Analysis section
        lines.extend([
            "## System Analysis",
            "",
            "### Performance Metrics",
            ""
        ])
        
        efficiency = self._calculate_efficiency_metrics()
        for metric_name, metric_value in efficiency.items():
            if isinstance(metric_value, float):
                lines.append(f"- **{metric_name.replace('_', ' ').title()}**: {metric_value:.1%}")
            else:
                lines.append(f"- **{metric_name.replace('_', ' ').title()}**: {metric_value}")
                
        # Recommendations
        recommendations = self._get_export_recommendations()
        if recommendations:
            lines.extend([
                "",
                "### Recommendations",
                ""
            ])
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"{i}. {rec}")
                
        markdown_output = "\n".join(lines)
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(markdown_output)
            self._log_export('markdown', filename)
            return f"Data exported to {filename}"
        else:
            return markdown_output
            
    def _export_text(self, filename: Optional[str] = None) -> str:
        """
        💾 Export system state as plain text format
        
        Creates human-readable plain text export suitable for
        console display and simple text processing.
        """
        
        # Reuse the existing visualization report functionality
        report = self.visualize_system_state(include_history=True, detail_level="comprehensive")
        text_output = report.to_text()
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(text_output)
            self._log_export('text', filename)
            return f"Data exported to {filename}"
        else:
            return text_output
            
    def _export_quantities_data(self) -> Dict[str, Any]:
        """
        📏 Export quantities data in structured format
        
        Creates structured export of all quantity information
        suitable for external processing.
        """
        
        quantities = getattr(self, 'quantities', {})
        export_data = {}
        
        for qty_name, quantity in quantities.items():
            export_data[qty_name] = {
                'magnitude': getattr(quantity, 'magnitude', 'unknown'),
                'derivative': getattr(quantity, 'derivative', 'unknown'),
                'unit': getattr(quantity, 'unit', ''),
                'description': getattr(quantity, 'description', ''),
                'value_type': getattr(quantity, 'value_type', 'qualitative'),
                'last_updated': getattr(quantity, 'last_updated', None)
            }
            
        return export_data
        
    def _export_processes_data(self) -> Dict[str, Any]:
        """
        ⚙️ Export processes data in structured format
        
        Creates structured export of all process information
        including activation status and influences.
        """
        
        processes = getattr(self, 'processes', [])
        export_data = {}
        
        for process in processes:
            process_name = getattr(process, 'name', f'Process_{id(process)}')
            export_data[process_name] = {
                'is_active': getattr(process, 'is_active', False),
                'description': getattr(process, 'description', ''),
                'preconditions': [str(p) for p in getattr(process, 'preconditions', [])],
                'influences': [
                    {
                        'quantity': getattr(inf, 'quantity_name', 'Unknown'),
                        'direction': getattr(inf, 'direction', 'unknown'),
                        'strength': getattr(inf, 'strength', 'unknown')
                    }
                    for inf in getattr(process, 'influences', [])
                ],
                'activation_count': getattr(process, 'activation_count', 0)
            }
            
        return export_data
        
    def _export_relationships_data(self) -> Dict[str, str]:
        """
        🔗 Export relationships data in structured format
        
        Creates structured export of derived relationships
        between quantities.
        """
        
        relationships = getattr(self, 'derived_relationships', {})
        export_data = {}
        
        for rel_name, relationship in relationships.items():
            export_data[rel_name] = {
                'type': getattr(relationship, 'type', 'unknown'),
                'description': getattr(relationship, 'description', ''),
                'quantities_involved': getattr(relationship, 'quantities_involved', []),
                'strength': getattr(relationship, 'strength', 'unknown'),
                'confidence': getattr(relationship, 'confidence', 0.5)
            }
            
        return export_data
        
    def _export_constraints_data(self) -> List[Dict[str, Any]]:
        """
        ⚖️ Export constraints data in structured format
        
        Creates structured export of system constraints
        and their satisfaction status.
        """
        
        if not hasattr(self, 'constraints'):
            return []
            
        export_data = []
        for constraint in self.constraints:
            export_data.append({
                'name': getattr(constraint, 'name', 'Unnamed'),
                'description': getattr(constraint, 'description', ''),
                'is_satisfied': getattr(constraint, 'is_satisfied', True),
                'severity': getattr(constraint, 'severity', 'medium'),
                'type': getattr(constraint, 'type', 'unknown'),
                'violation_count': getattr(constraint, 'violation_count', 0)
            })
            
        return export_data
        
    def _export_history_data(self) -> List[Dict[str, Any]]:
        """
        📅 Export historical state data
        
        Creates structured export of state evolution history.
        """
        
        if not hasattr(self, 'state_history'):
            return []
            
        export_data = []
        for state in self.state_history[-20:]:  # Last 20 states
            export_data.append({
                'timestamp': getattr(state, 'time', 'Unknown'),
                'description': getattr(state, 'description', ''),
                'active_process_count': len(getattr(state, 'active_processes', [])),
                'quantity_count': len(getattr(state, 'quantities', {})),
                'constraint_violations': len([
                    c for c in getattr(state, 'constraints', [])
                    if not getattr(c, 'is_satisfied', True)
                ])
            })
            
        return export_data
        
    def _export_performance_data(self) -> Dict[str, Any]:
        """
        📊 Export performance metrics data
        
        Creates structured export of system performance
        and health indicators.
        """
        
        return {
            'system_health_score': self._calculate_system_health_score(),
            'efficiency_metrics': self._calculate_efficiency_metrics(),
            'stability_metrics': self._calculate_stability_metrics(),
            'capacity_metrics': self._calculate_capacity_metrics(),
            'export_timestamp': datetime.now().isoformat()
        }
        
    def _get_export_recommendations(self) -> List[str]:
        """
        🎯 Get actionable recommendations for export
        
        Generates list of actionable recommendations based on
        current system analysis.
        """
        
        recommendations = []
        
        # System health recommendations
        health = self._calculate_system_health_score()
        if health < 0.7:
            recommendations.append("System health below optimal - investigate constraint violations and process conflicts")
            
        # Efficiency recommendations
        efficiency = self._calculate_efficiency_metrics()
        if efficiency.get('process_utilization', 0.5) < 0.3:
            recommendations.append("Low process utilization - consider activating additional processes")
            
        # Constraint recommendations
        if hasattr(self, 'constraints') and self.constraints:
            violations = [c for c in self.constraints if not getattr(c, 'is_satisfied', True)]
            if violations:
                recommendations.append(f"Address {len(violations)} active constraint violations")
                
        # Data quality recommendations
        quantities = getattr(self, 'quantities', {})
        if quantities:
            unknown_count = len([q for q in quantities.values() if getattr(q, 'derivative', 'unknown') == 'unknown'])
            if unknown_count > len(quantities) * 0.4:
                recommendations.append("Improve quantity trend monitoring - high number of unknown derivatives")
                
        return recommendations[:5]  # Limit to top 5 recommendations
        
    def _json_serializer(self, obj):
        """
        💾 Custom JSON serializer for complex objects
        
        Handles serialization of objects that are not JSON-serializable by default.
        """
        
        if hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):  # Custom objects
            return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        else:
            return str(obj)
            
    def _log_export(self, format_type: str, filename: str):
        """
        📝 Log export activity for tracking
        
        Records export activity for audit and usage tracking.
        """
        
        export_record = {
            'timestamp': datetime.now().isoformat(),
            'format': format_type,
            'filename': filename,
            'file_size': os.path.getsize(filename) if os.path.exists(filename) else 0
        }
        
        self._export_history.append(export_record)
        
        # Keep only last 50 export records
        if len(self._export_history) > 50:
            self._export_history = self._export_history[-50:]
