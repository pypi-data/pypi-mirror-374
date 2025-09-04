"""
🧠 Qualitative Reasoning - Process Causal Reasoning Module
===========================================================

Causal reasoning and explanation for qualitative reasoning systems.
Extracted from process_engine.py to enforce 800-line limit.

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Forbus, K. D. (1984) - "Qualitative Process Theory"

This module provides causal explanation, behavioral analysis,
and causal graph construction for qualitative processes.
"""

from typing import Dict, List, Tuple, Union, Optional, Any, Set
from collections import defaultdict, deque
from .core_types import QualitativeProcess, QualitativeQuantity, QualitativeValue, QualitativeDirection, QualitativeState

class ProcessCausalReasoningMixin:
    """
    Causal reasoning and explanation for qualitative processes.
    
    Provides behavioral explanation, causal chain analysis,
    and causal graph construction for understanding system behavior.
    """
    
    def explain_behavior(self, quantity_name: str) -> List[str]:
        """
        Generate causal explanation for a quantity's behavior
        
        This implements causal explanation from Process Theory by tracing
        the processes responsible for a quantity's current derivative.
        
        Args:
            quantity_name: Name of quantity to explain
            
        Returns:
            List[str]: Ordered list of explanation statements
            
        🧠 Causal Explanation:
        Process Theory enables rich causal explanations by identifying:
        1. Which processes are influencing the quantity
        2. Why those processes are active (their conditions)
        3. How the influences combine to produce the net effect
        4. What this means for future system behavior
        
        Example Explanation:
        "Temperature is increasing because:
         1. Heat_Flow process is active (source hotter than target)
         2. Heat_Flow applies I+ influence to temperature
         3. No opposing processes are active
         4. Therefore net effect is positive derivative"
        """
        
        explanations = []
        
        if quantity_name not in self.quantities:
            return [f"Quantity '{quantity_name}' not found in system."]
            
        quantity = self.quantities[quantity_name]
        current_derivative = quantity.derivative
        
        # Find processes influencing this quantity
        influencing_processes = []
        for process_name, process in self.processes.items():
            if process.active:
                for influence_str in process.influences:
                    target_qty = self._parse_influence_target(influence_str)
                    if target_qty == quantity_name:
                        direction = "increasing" if influence_str.strip().startswith("I+") else "decreasing"
                        strength = self._parse_influence_strength(influence_str)
                        influencing_processes.append((process_name, direction, strength, influence_str))
                        
        # Generate explanation based on current state
        if current_derivative == QualitativeDirection.ZERO:
            if not influencing_processes:
                explanations.append(f"{quantity_name} is stable (not changing) because no processes are currently influencing it.")
            else:
                explanations.append(f"{quantity_name} is stable despite {len(influencing_processes)} active influence(s):")
                
                # Explain why influences cancel out
                positive_influences = [p for p in influencing_processes if p[1] == "increasing"]
                negative_influences = [p for p in influencing_processes if p[1] == "decreasing"]
                
                if positive_influences and negative_influences:
                    explanations.append(f"  • {len(positive_influences)} process(es) trying to increase {quantity_name}")
                    explanations.append(f"  • {len(negative_influences)} process(es) trying to decrease {quantity_name}")
                    explanations.append(f"  • These influences balance each other, resulting in no net change")
                    
        elif current_derivative == QualitativeDirection.POSITIVE:
            explanations.append(f"{quantity_name} is increasing because:")
            
            increasing_processes = [p for p in influencing_processes if p[1] == "increasing"]
            decreasing_processes = [p for p in influencing_processes if p[1] == "decreasing"]
            
            if increasing_processes:
                explanations.append(f"  • {len(increasing_processes)} process(es) are actively increasing it:")
                for process_name, direction, strength, influence in increasing_processes:
                    process_desc = self.processes[process_name].description or "No description"
                    explanations.append(f"    - {process_name}: {process_desc[:60]}{'...' if len(process_desc) > 60 else ''}")
                    
            if decreasing_processes:
                explanations.append(f"  • Despite {len(decreasing_processes)} opposing process(es), the net effect is still positive")
                
        elif current_derivative == QualitativeDirection.NEGATIVE:
            explanations.append(f"{quantity_name} is decreasing because:")
            
            decreasing_processes = [p for p in influencing_processes if p[1] == "decreasing"]
            increasing_processes = [p for p in influencing_processes if p[1] == "increasing"]
            
            if decreasing_processes:
                explanations.append(f"  • {len(decreasing_processes)} process(es) are actively decreasing it:")
                for process_name, direction, strength, influence in decreasing_processes:
                    process_desc = self.processes[process_name].description or "No description"
                    explanations.append(f"    - {process_name}: {process_desc[:60]}{'...' if len(process_desc) > 60 else ''}")
                    
            if increasing_processes:
                explanations.append(f"  • Despite {len(increasing_processes)} opposing process(es), the net effect is still negative")
                
        # Explain why influencing processes are active
        if influencing_processes:
            explanations.append("")
            explanations.append("Process activation reasons:")
            
            for process_name, direction, strength, influence in influencing_processes[:3]:  # Limit to 3 for brevity
                process = self.processes[process_name]
                
                explanations.append(f"  • {process_name} is active because:")
                
                # Explain preconditions
                if process.preconditions:
                    satisfied_preconditions = []
                    for precondition in process.preconditions:
                        if self._evaluate_logical_condition(precondition):
                            satisfied_preconditions.append(precondition)
                            
                    if satisfied_preconditions:
                        explanations.append(f"    - Preconditions satisfied: {', '.join(satisfied_preconditions[:2])}")
                        
                # Explain quantity conditions
                if process.quantity_conditions:
                    satisfied_qty_conditions = []
                    for qty_condition in process.quantity_conditions:
                        if self._evaluate_quantity_condition(qty_condition):
                            satisfied_qty_conditions.append(qty_condition)
                            
                    if satisfied_qty_conditions:
                        explanations.append(f"    - Quantity conditions met: {', '.join(satisfied_qty_conditions[:2])}")
                        
        # Add predictive insight
        explanations.append("")
        if current_derivative == QualitativeDirection.ZERO:
            explanations.append(f"Prediction: {quantity_name} will remain stable unless process conditions change.")
        elif current_derivative == QualitativeDirection.POSITIVE:
            explanations.append(f"Prediction: {quantity_name} will continue increasing until process deactivation or opposing forces strengthen.")
        elif current_derivative == QualitativeDirection.NEGATIVE:
            explanations.append(f"Prediction: {quantity_name} will continue decreasing until process deactivation or opposing forces strengthen.")
            
        return explanations
        
    def get_causal_chain(self, quantity_name: str) -> Dict[str, Any]:
        """
        Construct causal chain leading to quantity's current state
        
        Traces the causal relationships from root causes (process activation conditions)
        through intermediate processes to the final effect on the target quantity.
        
        Args:
            quantity_name: Target quantity to analyze
            
        Returns:
            Dict: Causal chain structure with processes, conditions, and relationships
            
        🕰️ Causal Chain Structure:
        {
            "target_quantity": "temperature",
            "current_state": {"magnitude": "positive", "derivative": "increasing"},
            "direct_influences": [
                {
                    "process": "Heat_Flow",
                    "influence_type": "I+", 
                    "strength": 2,
                    "activation_reason": "temperature_difference > 0"
                }
            ],
            "causal_depth": 2,
            "feedback_loops": [],
            "root_causes": ["external_heat_source"]
        }
        """
        
        if quantity_name not in self.quantities:
            return {"error": f"Quantity '{quantity_name}' not found"}
            
        quantity = self.quantities[quantity_name]
        
        # Build causal chain structure
        causal_chain = {
            "target_quantity": quantity_name,
            "current_state": {
                "magnitude": str(quantity.magnitude),
                "derivative": str(quantity.derivative)
            },
            "direct_influences": [],
            "indirect_influences": [],
            "causal_depth": 0,
            "feedback_loops": [],
            "root_causes": [],
            "process_dependencies": {}
        }
        
        # Find direct influences (processes directly affecting this quantity)
        direct_influences = []
        for process_name, process in self.processes.items():
            if process.active:
                for influence_str in process.influences:
                    target_qty = self._parse_influence_target(influence_str)
                    if target_qty == quantity_name:
                        influence_info = {
                            "process": process_name,
                            "influence_type": "I+" if influence_str.strip().startswith("I+") else "I-",
                            "strength": self._parse_influence_strength(influence_str),
                            "activation_reason": self._get_activation_summary(process),
                            "process_description": process.description
                        }
                        direct_influences.append(influence_info)
                        
        causal_chain["direct_influences"] = direct_influences
        
        # Trace indirect influences (processes affecting conditions of direct processes)
        indirect_influences = []
        visited_processes = set()
        
        for direct_influence in direct_influences:
            process_name = direct_influence["process"]
            indirect_chain = self._trace_indirect_influences(process_name, visited_processes, depth=0, max_depth=3)
            indirect_influences.extend(indirect_chain)
            
        causal_chain["indirect_influences"] = indirect_influences
        causal_chain["causal_depth"] = max(len(indirect_influences), len(direct_influences))
        
        # Detect feedback loops
        feedback_loops = self._detect_feedback_loops(quantity_name, max_depth=4)
        causal_chain["feedback_loops"] = feedback_loops
        
        # Identify root causes (processes with no dependencies)
        root_causes = []
        all_processes = set(inf["process"] for inf in direct_influences + indirect_influences)
        
        for process_name in all_processes:
            if process_name in self.processes:
                dependencies = self._get_process_dependencies(process_name)
                if not dependencies:  # No dependencies = root cause
                    root_causes.append(process_name)
                    
        causal_chain["root_causes"] = root_causes
        
        # Build process dependency graph
        process_dependencies = {}
        for process_name in all_processes:
            if process_name in self.processes:
                dependencies = self._get_process_dependencies(process_name)
                process_dependencies[process_name] = dependencies
                
        causal_chain["process_dependencies"] = process_dependencies
        
        return causal_chain
        
    def _get_activation_summary(self, process: QualitativeProcess) -> str:
        """
        Get summary of why a process is active
        
        Args:
            process: QualitativeProcess to analyze
            
        Returns:
            str: Summary of activation conditions
        """
        
        reasons = []
        
        # Check preconditions
        satisfied_preconditions = []
        for precondition in process.preconditions:
            if self._evaluate_logical_condition(precondition):
                satisfied_preconditions.append(precondition)
                
        if satisfied_preconditions:
            reasons.append(f"{len(satisfied_preconditions)} precondition(s) met")
            
        # Check quantity conditions
        satisfied_qty_conditions = []
        for qty_condition in process.quantity_conditions:
            if self._evaluate_quantity_condition(qty_condition):
                satisfied_qty_conditions.append(qty_condition)
                
        if satisfied_qty_conditions:
            reasons.append(f"{len(satisfied_qty_conditions)} quantity condition(s) met")
            
        return "; ".join(reasons) if reasons else "Always active"
        
    def _trace_indirect_influences(self, process_name: str, visited: Set[str], 
                                  depth: int, max_depth: int) -> List[Dict[str, Any]]:
        """
        Trace indirect influences through causal chains
        
        Args:
            process_name: Starting process
            visited: Set of already visited processes (to avoid cycles)
            depth: Current depth in the search
            max_depth: Maximum depth to search
            
        Returns:
            List[Dict]: Indirect influence information
        """
        
        if depth >= max_depth or process_name in visited:
            return []
            
        visited.add(process_name)
        indirect_influences = []
        
        if process_name not in self.processes:
            return []
            
        process = self.processes[process_name]
        
        # Look at this process's conditions to find dependent quantities
        dependent_quantities = set()
        
        for condition in process.quantity_conditions:
            # Extract quantity names from conditions
            dependencies = self.get_condition_dependencies(condition)
            dependent_quantities.update(dependencies)
            
        # Find processes that influence these dependent quantities
        for dep_quantity in dependent_quantities:
            for other_process_name, other_process in self.processes.items():
                if other_process_name == process_name or other_process_name in visited:
                    continue
                    
                if other_process.active:
                    for influence_str in other_process.influences:
                        target_qty = self._parse_influence_target(influence_str)
                        if target_qty == dep_quantity:
                            # Found indirect influence
                            indirect_info = {
                                "process": other_process_name,
                                "influenced_quantity": dep_quantity,
                                "affects_process": process_name,
                                "depth": depth + 1,
                                "influence_type": "I+" if influence_str.strip().startswith("I+") else "I-"
                            }
                            indirect_influences.append(indirect_info)
                            
                            # Recursively trace further
                            deeper_influences = self._trace_indirect_influences(
                                other_process_name, visited.copy(), depth + 1, max_depth
                            )
                            indirect_influences.extend(deeper_influences)
                            
        return indirect_influences
        
    def _detect_feedback_loops(self, quantity_name: str, max_depth: int = 4) -> List[Dict[str, Any]]:
        """
        Detect feedback loops involving a quantity
        
        Args:
            quantity_name: Starting quantity
            max_depth: Maximum loop length to detect
            
        Returns:
            List[Dict]: Detected feedback loops
        """
        
        feedback_loops = []
        
        # Use breadth-first search to find cycles
        queue = deque([(quantity_name, [quantity_name])])
        visited_paths = set()
        
        while queue:
            current_qty, path = queue.popleft()
            
            if len(path) > max_depth:
                continue
                
            # Find processes that influence current quantity
            for process_name, process in self.processes.items():
                if not process.active:
                    continue
                    
                influences_current = any(
                    self._parse_influence_target(inf) == current_qty 
                    for inf in process.influences
                )
                
                if influences_current:
                    # Find quantities this process depends on
                    dependent_quantities = set()
                    for condition in process.quantity_conditions:
                        dependencies = self.get_condition_dependencies(condition)
                        dependent_quantities.update(dependencies)
                        
                    for dep_qty in dependent_quantities:
                        new_path = path + [process_name, dep_qty]
                        
                        # Check for cycle
                        if dep_qty == quantity_name and len(new_path) > 2:
                            # Found feedback loop
                            loop_info = {
                                "loop_path": new_path,
                                "loop_length": len(new_path) - 1,
                                "loop_type": "positive" if self._is_positive_feedback(new_path) else "negative"
                            }
                            feedback_loops.append(loop_info)
                        elif dep_qty not in path:  # Avoid infinite recursion
                            path_key = tuple(new_path)
                            if path_key not in visited_paths:
                                visited_paths.add(path_key)
                                queue.append((dep_qty, new_path))
                                
        return feedback_loops
        
    def _is_positive_feedback(self, loop_path: List[str]) -> bool:
        """
        Determine if a feedback loop is positive (reinforcing) or negative (balancing)
        
        Args:
            loop_path: Path through the feedback loop
            
        Returns:
            bool: True if positive feedback, False if negative
        """
        
        # Simplified heuristic: count negative influences
        negative_count = 0
        
        for i in range(0, len(loop_path) - 1, 2):  # Process names are at even indices
            if i + 1 < len(loop_path):
                process_name = loop_path[i + 1]
                if process_name in self.processes:
                    process = self.processes[process_name]
                    for influence in process.influences:
                        if influence.strip().startswith("I-"):
                            negative_count += 1
                            break
                            
        # Even number of negative influences = positive feedback
        return negative_count % 2 == 0
        
    def _get_process_dependencies(self, process_name: str) -> List[str]:
        """
        Get quantities that a process depends on
        
        Args:
            process_name: Process to analyze
            
        Returns:
            List[str]: Quantity names this process depends on
        """
        
        if process_name not in self.processes:
            return []
            
        process = self.processes[process_name]
        dependencies = set()
        
        # Extract dependencies from quantity conditions
        for condition in process.quantity_conditions:
            condition_deps = self.get_condition_dependencies(condition)
            dependencies.update(condition_deps)
            
        return list(dependencies)
        
    def generate_causal_summary(self) -> Dict[str, Any]:
        """
        Generate overall causal summary of the system
        
        Returns:
            Dict: System-wide causal analysis
        """
        
        # Get all active processes
        active_processes = [name for name, proc in self.processes.items() if proc.active]
        
        # Get all influenced quantities
        influenced_quantities = set()
        for process_name in active_processes:
            if process_name in self.processes:
                process = self.processes[process_name]
                for influence in process.influences:
                    qty_name = self._parse_influence_target(influence)
                    if qty_name:
                        influenced_quantities.add(qty_name)
                        
        # Analyze system-wide patterns
        feedback_loop_count = 0
        root_cause_processes = []
        
        for qty in influenced_quantities:
            loops = self._detect_feedback_loops(qty, max_depth=3)
            feedback_loop_count += len(loops)
            
        # Find root causes (processes with minimal dependencies)
        for process_name in active_processes:
            dependencies = self._get_process_dependencies(process_name)
            if len(dependencies) <= 1:  # Minimal dependencies
                root_cause_processes.append(process_name)
                
        return {
            "system_state": "dynamic" if active_processes else "static",
            "active_processes": len(active_processes),
            "influenced_quantities": len(influenced_quantities),
            "feedback_loops": feedback_loop_count,
            "root_causes": len(root_cause_processes),
            "causal_complexity": "high" if feedback_loop_count > 2 else "medium" if feedback_loop_count > 0 else "low",
            "process_conflicts": len(self.process_conflicts),
            "most_influential_processes": active_processes[:5]  # Top 5
        }
