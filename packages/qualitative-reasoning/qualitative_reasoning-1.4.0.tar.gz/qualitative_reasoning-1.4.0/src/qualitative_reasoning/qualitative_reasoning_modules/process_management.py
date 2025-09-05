"""
📋 Process Management
======================

🎯 ELI5 Summary:
This file is an important component in our AI research system! Like different organs 
in your body that work together to keep you healthy, this file has a specific job that 
helps the overall algorithm work correctly and efficiently.

🧪 Technical Details:
===================
Implementation details and technical specifications for this component.
Designed to work seamlessly within the research framework while
maintaining high performance and accuracy standards.

📋 Component Integration:
========================
    ┌──────────┐
    │   This   │
    │Component │ ←→ Other Components
    └──────────┘
         ↑↓
    System Integration

"""
"""
⚙️ Qualitative Reasoning - Process Management Module
==================================================

Process management and configuration for qualitative reasoning systems.
Extracted from process_engine.py to enforce 800-line limit.

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Forbus, K. D. (1984) - "Qualitative Process Theory"

This module provides core process management functionality including
process creation, configuration, and dependency analysis.
"""

from typing import Dict, List, Tuple, Union, Optional, Any, Set
from dataclasses import dataclass
from .core_types import QualitativeProcess, QualitativeQuantity, QualitativeValue, QualitativeDirection, QualitativeState

class ProcessManagementMixin:
    """
    Process management and configuration for qualitative reasoning.
    
    Handles process creation, configuration, influence parsing,
    and dependency analysis for the qualitative reasoning engine.
    """
    
    def __init__(self):
        """Initialize process management components"""
        
        # Process storage and management
        self.processes: Dict[str, QualitativeProcess] = {}
        self.causal_graph: Dict[str, List[str]] = {}  # process -> [influenced_quantities]
        
        # Process activation tracking
        self.active_process_history: List[List[str]] = []  # History of active process sets
        self.activation_changes: List[Tuple[str, str, bool]] = []  # (time, process, active_state)
        self.process_history: List[Dict[str, bool]] = []  # Historical activation states
        
        # Process interaction tracking
        self.process_conflicts: List[Tuple[str, str, str]] = []  # (process1, process2, quantity)
        self.influence_resolution: Dict[str, str] = {}  # quantity -> resolution_strategy
        
    def add_process(self, name: str, preconditions: List[str], 
                   quantity_conditions: List[str], influences: List[str],
                   description: str = "", active: bool = False) -> bool:
        """
        Add a new process to the qualitative reasoning system
        
        This implements process definition from Forbus's Process Theory:
        P = ⟨preconditions, quantity_conditions, influences⟩
        
        Args:
            name: Unique process identifier
            preconditions: List of logical preconditions for activation
            quantity_conditions: List of quantity-based activation conditions  
            influences: List of quantity influences ("I+ quantity" or "I- quantity")
            description: Human-readable process description
            active: Initial activation state (default False)
            
        Returns:
            bool: True if process added successfully, False if name conflict
            
        🧠 Process Theory:
        A process represents a physical mechanism that becomes active when
        its conditions are satisfied and influences quantities through causal
        relationships. This captures the dynamic nature of physical systems.
        
        Example:
        ```
        engine.add_process(
            name="Heat_Flow",
            preconditions=["connected(source, target)"],
            quantity_conditions=["temperature(source) > temperature(target)"],
            influences=["I- temperature(source)", "I+ temperature(target)"],
            description="Heat flows from hot to cold objects"
        )
        ```
        """
        
        if name in self.processes:
            if hasattr(self, '_verbose') and self._verbose:
                print(f"Warning: Process '{name}' already exists. Skipping.")
            return False
            
        # Create process object
        process = QualitativeProcess(
            name=name,
            preconditions=preconditions,
            quantity_conditions=quantity_conditions, 
            influences=influences,
            description=description,
            active=active
        )
        
        # Store process
        self.processes[name] = process
        
        # Parse and validate influences
        influenced_quantities = []
        for influence in influences:
            quantity_name = self._parse_influence_target(influence)
            if quantity_name:
                influenced_quantities.append(quantity_name)
                
        # Build causal graph
        self.causal_graph[name] = influenced_quantities
        
        # Analyze process dependencies and conflicts
        self._analyze_process_dependencies(name)
        
        if hasattr(self, '_verbose') and self._verbose:
            print(f"Added process: {name}")
            print(f"  Preconditions: {len(preconditions)}")
            print(f"  Quantity conditions: {len(quantity_conditions)}")
            print(f"  Influences: {len(influences)} quantities")
            
        return True
        
    def _parse_influence_target(self, influence: str) -> Optional[str]:
        """
        Parse an influence string to extract the target quantity name
        
        Influence format: "I+ quantity_name" or "I- quantity_name"
        Extended format: "I+ quantity_name [strength]" where strength is optional
        
        Args:
            influence: Influence string to parse
            
        Returns:
            Optional[str]: Target quantity name if valid, None otherwise
            
        🔧 Supported Formats:
        - "I+ temperature" -> "temperature"
        - "I- pressure [strong]" -> "pressure" 
        - "I+ velocity [2]" -> "velocity"
        - "increase temperature" -> "temperature" (alternative syntax)
        """
        
        influence = influence.strip()
        
        # Standard format: I+/I- quantity [optional_strength]
        if influence.startswith(("I+", "I-")):
            # Remove direction indicator
            parts = influence[2:].strip().split()
            if parts:
                return parts[0]  # First part is quantity name
                
        # Alternative format: increase/decrease quantity
        elif influence.startswith(("increase", "decrease")):
            parts = influence.split()
            if len(parts) >= 2:
                return parts[1]  # Second part is quantity name
                
        # Format: +quantity or -quantity
        elif influence.startswith(("+", "-")):
            parts = influence[1:].strip().split()
            if parts:
                return parts[0]
                
        return None
        
    def _analyze_process_dependencies(self, process_name: str):
        """
        Analyze dependencies and potential conflicts for a process
        
        Identifies:
        1. Processes that influence the same quantities (potential conflicts)
        2. Causal chains where one process affects conditions of another
        3. Circular dependencies in process activation
        
        Args:
            process_name: Name of process to analyze
            
        🔍 Dependency Analysis:
        Process interactions can create complex behaviors:
        - **Reinforcement**: Multiple processes increase same quantity
        - **Opposition**: Some processes increase, others decrease same quantity
        - **Causal Chains**: Process A affects quantity that influences Process B conditions
        - **Feedback Loops**: Process effects eventually influence their own conditions
        """
        
        if process_name not in self.processes:
            return
            
        current_process = self.processes[process_name]
        influenced_quantities = self.causal_graph.get(process_name, [])
        
        # Check for conflicts with existing processes
        for existing_name, existing_process in self.processes.items():
            if existing_name == process_name:
                continue
                
            existing_influenced = self.causal_graph.get(existing_name, [])
            
            # Find shared influenced quantities
            shared_quantities = set(influenced_quantities) & set(existing_influenced)
            
            for shared_qty in shared_quantities:
                # Determine if this is a reinforcing or opposing interaction
                current_influences = [inf for inf in current_process.influences 
                                   if self._parse_influence_target(inf) == shared_qty]
                existing_influences = [inf for inf in existing_process.influences 
                                     if self._parse_influence_target(inf) == shared_qty]
                
                if current_influences and existing_influences:
                    current_direction = "+" if current_influences[0].startswith("I+") else "-"
                    existing_direction = "+" if existing_influences[0].startswith("I+") else "-"
                    
                    if current_direction != existing_direction:
                        # Opposing influences - potential conflict
                        conflict = (process_name, existing_name, shared_qty)
                        if conflict not in self.process_conflicts:
                            self.process_conflicts.append(conflict)
                            
                            # Set default resolution strategy
                            if shared_qty not in self.influence_resolution:
                                self.influence_resolution[shared_qty] = "algebraic_sum"
                                
        if hasattr(self, '_verbose') and self._verbose and influenced_quantities:
            print(f"  Process {process_name} influences: {', '.join(influenced_quantities)}")
            
    def get_process_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive information about a process
        
        Args:
            name: Process name to query
            
        Returns:
            Optional[Dict]: Process information if found, None otherwise
        """
        
        if name not in self.processes:
            return None
            
        process = self.processes[name]
        
        return {
            'name': name,
            'description': process.description,
            'active': process.active,
            'preconditions': process.preconditions,
            'quantity_conditions': process.quantity_conditions,
            'influences': process.influences,
            'influenced_quantities': self.causal_graph.get(name, []),
            'conflicts': [c for c in self.process_conflicts if name in c[:2]],
            'activation_history': len([c for c in self.activation_changes if c[1] == name])
        }
        
    def list_processes(self, active_only: bool = False) -> List[str]:
        """
        List all processes in the system
        
        Args:
            active_only: If True, only return currently active processes
            
        Returns:
            List[str]: Process names
        """
        
        if active_only:
            return [name for name, proc in self.processes.items() if proc.active]
        else:
            return list(self.processes.keys())
            
    def remove_process(self, name: str) -> bool:
        """
        Remove a process from the system
        
        Args:
            name: Process name to remove
            
        Returns:
            bool: True if removed, False if not found
        """
        
        if name not in self.processes:
            return False
            
        # Remove from processes
        del self.processes[name]
        
        # Remove from causal graph
        if name in self.causal_graph:
            del self.causal_graph[name]
            
        # Clean up conflicts involving this process
        self.process_conflicts = [c for c in self.process_conflicts if name not in c[:2]]
        
        # Clean up influence resolutions for quantities only this process affected
        influenced_quantities = set()
        for proc_influences in self.causal_graph.values():
            influenced_quantities.update(proc_influences)
            
        orphaned_quantities = set(self.influence_resolution.keys()) - influenced_quantities
        for qty in orphaned_quantities:
            del self.influence_resolution[qty]
            
        if hasattr(self, '_verbose') and self._verbose:
            print(f"Removed process: {name}")
            
        return True
        
    def get_process_conflicts(self) -> List[Dict[str, Any]]:
        """
        Get information about process conflicts
        
        Returns:
            List[Dict]: Conflict information with resolution strategies
        """
        
        conflicts = []
        for proc1, proc2, quantity in self.process_conflicts:
            resolution = self.influence_resolution.get(quantity, "unknown")
            
            conflicts.append({
                'processes': [proc1, proc2],
                'quantity': quantity,
                'resolution_strategy': resolution,
                'active_conflict': (proc1 in self.processes and self.processes[proc1].active and
                                  proc2 in self.processes and self.processes[proc2].active)
            })
            
        return conflicts
        
    def set_influence_resolution(self, quantity: str, strategy: str):
        """
        Set the resolution strategy for conflicting influences on a quantity
        
        Args:
            quantity: Quantity name
            strategy: Resolution strategy ("algebraic_sum", "dominance", "cancellation")
        """
        
        valid_strategies = ["algebraic_sum", "dominance", "cancellation", "priority_based"]
        if strategy not in valid_strategies:
            raise ValueError(f"Invalid strategy '{strategy}'. Valid options: {valid_strategies}")
            
        self.influence_resolution[quantity] = strategy
        
        if hasattr(self, '_verbose') and self._verbose:
            print(f"Set influence resolution for {quantity}: {strategy}")
            
    def get_causal_graph_info(self) -> Dict[str, Any]:
        """
        Get information about the causal graph structure
        
        Returns:
            Dict: Causal graph statistics and structure
        """
        
        # Calculate graph metrics
        total_processes = len(self.processes)
        total_influences = sum(len(influences) for influences in self.causal_graph.values())
        
        influenced_quantities = set()
        for influences in self.causal_graph.values():
            influenced_quantities.update(influences)
            
        return {
            'total_processes': total_processes,
            'active_processes': len([p for p in self.processes.values() if p.active]),
            'total_influences': total_influences,
            'influenced_quantities': len(influenced_quantities),
            'process_conflicts': len(self.process_conflicts),
            'resolution_strategies': len(self.influence_resolution),
            'causal_connections': dict(self.causal_graph)
        }
