"""
⚡ Qualitative Reasoning - Process Activation Module
=================================================

Process activation and influence application for qualitative reasoning systems.
Extracted from process_engine.py to enforce 800-line limit.

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Forbus, K. D. (1984) - "Qualitative Process Theory"

This module provides process activation logic, influence application,
and causal effect computation for qualitative processes.
"""

from typing import Dict, List, Tuple, Union, Optional, Any, Set
from .core_types import QualitativeProcess, QualitativeQuantity, QualitativeValue, QualitativeDirection, QualitativeState

class ProcessActivationMixin:
    """
    Process activation and influence application for qualitative reasoning.
    
    Handles the dynamic activation of processes and application of their
    causal influences to quantity derivatives.
    """
    
    def update_active_processes(self) -> List[str]:
        """
        Update which processes are currently active based on current system state
        
        This implements the process activation cycle from Process Theory:
        1. Evaluate each process's activation conditions
        2. Track activation state changes
        3. Record process activation history
        4. Return list of currently active processes
        
        Returns:
            List[str]: Names of currently active processes
            
        🧠 Process Theory:
        Process activation is dynamic - processes can become active or inactive
        as system conditions change. This creates the temporal dynamics that
        drive qualitative simulation and behavioral prediction.
        """
        
        active_processes = []
        activation_changes = []
        current_time = len(self.process_history)  # Simple time counter
        
        for process_name, process in self.processes.items():
            was_active = process.active
            
            # Evaluate current activation conditions
            process.active = self.evaluate_process_conditions(process)
            
            if process.active:
                active_processes.append(process_name)
                
            # Track activation changes
            if process.active != was_active:
                status = "ACTIVATED" if process.active else "DEACTIVATED"
                activation_changes.append((process_name, status))
                
                # Record in activation history
                self.activation_changes.append((f"t_{current_time}", process_name, process.active))
                
                if hasattr(self, '_verbose') and self._verbose:
                    print(f"   Process {process_name}: {status}")
                    
        # Store activation state snapshot
        current_activation_state = {name: proc.active for name, proc in self.processes.items()}
        self.process_history.append(current_activation_state)
        
        # Store active process list for history
        self.active_process_history.append(active_processes.copy())
        
        return active_processes
        
    def apply_process_influences(self, active_processes: List[str]):
        """
        Apply influences from active processes to quantity derivatives
        
        This implements the core causal mechanism from Process Theory:
        Active processes influence quantities through I+ and I- relations,
        which are combined to determine the net qualitative derivative.
        
        Args:
            active_processes: List of currently active process names
            
        ⚡ Influence Application:
        For each quantity, we collect all influences from active processes
        and resolve them using the configured resolution strategy:
        - **Algebraic Sum**: I+ and I- cancel, multiple I+ sum to stronger influence
        - **Dominance**: Strongest influence wins, others ignored
        - **Cancellation**: Any opposing influences result in zero net effect
        """
        
        if not active_processes:
            # No active processes - reset all derivatives to zero
            for quantity in self.quantities.values():
                quantity.derivative = QualitativeDirection.ZERO
            return
            
        # Collect influences for each quantity
        quantity_influences: Dict[str, List[Tuple[str, str, int]]] = {}  # qty -> [(process, direction, strength)]
        
        for process_name in active_processes:
            if process_name not in self.processes:
                continue
                
            process = self.processes[process_name]
            
            for influence_str in process.influences:
                # Parse influence string
                quantity_name = self._parse_influence_target(influence_str)
                if not quantity_name or quantity_name not in self.quantities:
                    continue
                    
                direction = "positive" if influence_str.strip().startswith("I+") else "negative"
                strength = self._parse_influence_strength(influence_str)
                
                if quantity_name not in quantity_influences:
                    quantity_influences[quantity_name] = []
                    
                quantity_influences[quantity_name].append((process_name, direction, strength))
                
        # Apply resolved influences to quantities
        for quantity_name, influences in quantity_influences.items():
            if quantity_name not in self.quantities:
                continue
                
            quantity = self.quantities[quantity_name]
            
            # Resolve conflicting influences
            resolution_strategy = self.influence_resolution.get(quantity_name, "algebraic_sum")
            net_derivative = self._resolve_influences(influences, resolution_strategy)
            
            # Apply to quantity derivative
            quantity.derivative = net_derivative
            
            if hasattr(self, '_verbose') and self._verbose and len(influences) > 1:
                print(f"   {quantity_name}: {len(influences)} influences -> {net_derivative}")
                
        # Reset derivatives for quantities with no influences
        influenced_quantities = set(quantity_influences.keys())
        for quantity_name, quantity in self.quantities.items():
            if quantity_name not in influenced_quantities:
                quantity.derivative = QualitativeDirection.ZERO
                
    def _resolve_influences(self, influences: List[Tuple[str, str, int]], 
                          strategy: str) -> QualitativeDirection:
        """
        Resolve multiple influences on a quantity using specified strategy
        
        Args:
            influences: List of (process_name, direction, strength) tuples
            strategy: Resolution strategy to use
            
        Returns:
            QualitativeDirection: Net resolved influence
        """
        
        if not influences:
            return QualitativeDirection.ZERO
            
        if len(influences) == 1:
            # Single influence - direct application
            _, direction, strength = influences[0]
            if direction == "positive":
                return QualitativeDirection.POSITIVE if strength >= 0 else QualitativeDirection.ZERO
            else:
                return QualitativeDirection.NEGATIVE if strength >= 0 else QualitativeDirection.ZERO
                
        # Multiple influences - apply resolution strategy
        if strategy == "algebraic_sum":
            return self._resolve_algebraic_sum(influences)
        elif strategy == "dominance":
            return self._resolve_dominance(influences)
        elif strategy == "cancellation":
            return self._resolve_cancellation(influences)
        elif strategy == "priority_based":
            return self._resolve_priority_based(influences)
        else:
            # Default to algebraic sum
            return self._resolve_algebraic_sum(influences)
            
    def _resolve_algebraic_sum(self, influences: List[Tuple[str, str, int]]) -> QualitativeDirection:
        """
        Resolve influences using algebraic summation
        
        Positive influences add together, negative influences add together,
        then they are combined to get net effect.
        """
        
        positive_strength = 0
        negative_strength = 0
        
        for _, direction, strength in influences:
            if direction == "positive":
                positive_strength += max(strength, 1)  # Minimum strength 1
            else:
                negative_strength += max(strength, 1)
                
        net_strength = positive_strength - negative_strength
        
        if net_strength > 0:
            return QualitativeDirection.POSITIVE
        elif net_strength < 0:
            return QualitativeDirection.NEGATIVE
        else:
            return QualitativeDirection.ZERO
            
    def _resolve_dominance(self, influences: List[Tuple[str, str, int]]) -> QualitativeDirection:
        """
        Resolve influences using dominance strategy
        
        The strongest influence wins, others are ignored.
        """
        
        max_strength = 0
        dominant_direction = "positive"
        
        for _, direction, strength in influences:
            if strength > max_strength:
                max_strength = strength
                dominant_direction = direction
                
        if max_strength > 0:
            return QualitativeDirection.POSITIVE if dominant_direction == "positive" else QualitativeDirection.NEGATIVE
        else:
            return QualitativeDirection.ZERO
            
    def _resolve_cancellation(self, influences: List[Tuple[str, str, int]]) -> QualitativeDirection:
        """
        Resolve influences using cancellation strategy
        
        Any opposing influences result in zero net effect.
        """
        
        has_positive = any(direction == "positive" for _, direction, _ in influences)
        has_negative = any(direction == "negative" for _, direction, _ in influences)
        
        if has_positive and has_negative:
            return QualitativeDirection.ZERO  # Opposing influences cancel
        elif has_positive:
            return QualitativeDirection.POSITIVE
        elif has_negative:
            return QualitativeDirection.NEGATIVE
        else:
            return QualitativeDirection.ZERO
            
    def _resolve_priority_based(self, influences: List[Tuple[str, str, int]]) -> QualitativeDirection:
        """
        Resolve influences using process priority
        
        Higher priority processes override lower priority ones.
        """
        
        # Get process priorities (if defined)
        priorities = getattr(self, 'process_priorities', {})
        
        highest_priority = -1
        priority_direction = "positive"
        
        for process_name, direction, strength in influences:
            priority = priorities.get(process_name, 0)
            if priority > highest_priority:
                highest_priority = priority
                priority_direction = direction
                
        return QualitativeDirection.POSITIVE if priority_direction == "positive" else QualitativeDirection.NEGATIVE
        
    def _parse_influence_strength(self, influence: str) -> int:
        """
        Parse influence strength from influence string
        
        Args:
            influence: Influence string (e.g., "I+ temperature [3]")
            
        Returns:
            int: Influence strength (default 1)
        """
        
        # Look for strength specification in brackets
        if '[' in influence and ']' in influence:
            try:
                start = influence.find('[') + 1
                end = influence.find(']')
                strength_str = influence[start:end].strip()
                
                # Try to parse as integer
                return int(strength_str)
            except (ValueError, IndexError):
                pass
                
        # Look for strength keywords
        influence_lower = influence.lower()
        if 'strong' in influence_lower or 'high' in influence_lower:
            return 3
        elif 'medium' in influence_lower or 'moderate' in influence_lower:
            return 2
        elif 'weak' in influence_lower or 'low' in influence_lower:
            return 1
            
        # Default strength
        return 1
        
    def get_activation_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about process activation patterns
        
        Returns:
            Dict: Activation statistics and metrics
        """
        
        if not self.process_history:
            return {
                'total_processes': len(self.processes),
                'activation_cycles': 0,
                'average_active': 0,
                'most_active_process': None,
                'activation_changes': 0
            }
            
        # Calculate statistics
        total_processes = len(self.processes)
        activation_cycles = len(self.process_history)
        
        # Average number of active processes
        active_counts = [len(active_set) for active_set in self.active_process_history]
        average_active = sum(active_counts) / len(active_counts) if active_counts else 0
        
        # Most frequently active process
        process_activation_counts = {}
        for active_set in self.active_process_history:
            for process_name in active_set:
                process_activation_counts[process_name] = process_activation_counts.get(process_name, 0) + 1
                
        most_active_process = None
        if process_activation_counts:
            most_active_process = max(process_activation_counts.keys(), 
                                   key=lambda p: process_activation_counts[p])
            
        return {
            'total_processes': total_processes,
            'activation_cycles': activation_cycles,
            'average_active': round(average_active, 2),
            'max_simultaneous': max(active_counts) if active_counts else 0,
            'min_simultaneous': min(active_counts) if active_counts else 0,
            'most_active_process': most_active_process,
            'activation_changes': len(self.activation_changes),
            'process_activation_counts': process_activation_counts
        }
        
    def get_influence_summary(self) -> Dict[str, Any]:
        """
        Get summary of influence patterns and conflicts
        
        Returns:
            Dict: Influence analysis summary
        """
        
        # Get currently active processes
        active_processes = [name for name, proc in self.processes.items() if proc.active]
        
        # Analyze current influences
        influenced_quantities = set()
        influence_conflicts = 0
        
        for process_name in active_processes:
            if process_name not in self.processes:
                continue
                
            process = self.processes[process_name]
            for influence_str in process.influences:
                quantity_name = self._parse_influence_target(influence_str)
                if quantity_name:
                    influenced_quantities.add(quantity_name)
                    
        # Count conflicts (quantities with opposing influences)
        for quantity_name in influenced_quantities:
            influences = []
            for process_name in active_processes:
                if process_name in self.processes:
                    process = self.processes[process_name]
                    for influence_str in process.influences:
                        if self._parse_influence_target(influence_str) == quantity_name:
                            direction = "positive" if influence_str.strip().startswith("I+") else "negative"
                            influences.append(direction)
                            
            # Check for opposing influences
            if "positive" in influences and "negative" in influences:
                influence_conflicts += 1
                
        return {
            'active_processes': len(active_processes),
            'influenced_quantities': len(influenced_quantities),
            'influence_conflicts': influence_conflicts,
            'resolution_strategies': len(self.influence_resolution),
            'total_influences': sum(len(proc.influences) for proc in self.processes.values() if proc.active)
        }
        
    def reset_activation_history(self):
        """
        Reset all activation history and statistics
        
        Useful for starting fresh simulations or clearing old data.
        """
        
        self.active_process_history.clear()
        self.activation_changes.clear()
        self.process_history.clear()
        
        if hasattr(self, '_verbose') and self._verbose:
            print("Reset process activation history")
            
    def set_process_priorities(self, priorities: Dict[str, int]):
        """
        Set priority levels for processes (used in priority-based resolution)
        
        Args:
            priorities: Dictionary mapping process names to priority levels
        """
        
        if not hasattr(self, 'process_priorities'):
            self.process_priorities = {}
            
        self.process_priorities.update(priorities)
        
        if hasattr(self, '_verbose') and self._verbose:
            print(f"Updated process priorities: {priorities}")
