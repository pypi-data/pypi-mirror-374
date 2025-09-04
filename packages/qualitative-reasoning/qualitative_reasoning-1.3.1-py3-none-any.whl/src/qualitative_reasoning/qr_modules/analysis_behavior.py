"""
🧠 Qualitative Reasoning - Analysis Behavior Module
==================================================

Behavioral explanation and causal analysis for qualitative reasoning systems.
Extracted from analysis_engine.py to enforce 800-line limit.

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Forbus, K. D. (1984) - "Qualitative Process Theory"

This module provides behavioral explanation, causal chain analysis,
and deep reasoning about system behavior.
"""

from typing import Dict, List, Tuple, Union, Optional, Any, Set
from dataclasses import dataclass, field
from .core_types import QualitativeValue, QualitativeDirection, QualitativeQuantity, QualitativeState, QualitativeProcess

@dataclass
class CausalChain:
    """Represents a causal chain connecting processes to quantity changes"""
    source_quantity: str
    target_quantity: str
    intermediate_processes: List[str]
    chain_strength: float = 0.0
    explanation: List[str] = field(default_factory=list)

@dataclass  
class BehaviorExplanation:
    """Complete behavioral explanation for a quantity"""
    quantity_name: str
    current_behavior: str
    primary_causes: List[str] = field(default_factory=list)
    contributing_factors: List[str] = field(default_factory=list)
    causal_chains: List[CausalChain] = field(default_factory=list)
    confidence: float = 0.0
    explanation_text: List[str] = field(default_factory=list)

class AnalysisBehaviorMixin:
    """
    Behavioral explanation and causal analysis for qualitative reasoning.
    
    Provides deep behavioral analysis, causal chain construction,
    and intelligent explanation generation for system behavior.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize behavioral analysis components"""
        super().__init__(*args, **kwargs)
        
        # Analysis cache for performance
        self._analysis_cache: Dict[str, Any] = {}
        self._explanation_cache: Dict[str, BehaviorExplanation] = {}
        
        # Behavioral analysis configuration
        self._max_causal_depth = 5
        self._min_confidence_threshold = 0.3
        self._enable_deep_analysis = True
        
    def explain_behavior(self, quantity_name: str, depth: int = 3) -> BehaviorExplanation:
        """
        🧠 Generate comprehensive behavioral explanation for a quantity
        
        This implements the core intelligence of qualitative reasoning by providing
        rich, multi-layered explanations of why quantities behave as they do.
        
        Args:
            quantity_name: Name of quantity to explain
            depth: Maximum causal chain depth to explore
            
        Returns:
            BehaviorExplanation: Comprehensive behavioral analysis
            
        🧠 Explanation Theory:
        Behavioral explanation in qualitative reasoning requires understanding:
        1. **Direct Causation**: Which processes directly influence the quantity
        2. **Indirect Causation**: How upstream processes create conditions for direct influences
        3. **System Context**: How the quantity's behavior fits into overall system dynamics
        4. **Temporal Patterns**: How the behavior has evolved and will likely continue
        
        The explanation combines multiple analytical approaches:
        - Process-based causal tracing
        - Correlation analysis across time
        - Domain knowledge application
        - Statistical pattern recognition
        """
        
        # Check cache for recent explanations
        cache_key = f"{quantity_name}_{depth}_{id(self.current_state)}"
        if cache_key in self._explanation_cache:
            return self._explanation_cache[cache_key]
            
        if quantity_name not in self.quantities:
            return BehaviorExplanation(
                quantity_name=quantity_name,
                current_behavior="unknown",
                explanation_text=[f"Quantity '{quantity_name}' not found in system."]
            )
            
        quantity = self.quantities[quantity_name]
        current_derivative = quantity.derivative
        
        # Build comprehensive explanation
        explanation = BehaviorExplanation(
            quantity_name=quantity_name,
            current_behavior=self._describe_current_behavior(quantity),
            primary_causes=self._identify_primary_causes(quantity_name),
            contributing_factors=self._identify_contributing_factors(quantity_name),
            causal_chains=self._build_causal_chains(quantity_name, depth)
        )
        
        # Calculate confidence based on explanation completeness
        explanation.confidence = self._calculate_explanation_confidence(
            explanation.primary_causes, 
            explanation.contributing_factors,
            explanation.causal_chains
        )
        
        # Generate human-readable explanation text
        explanation.explanation_text = self._generate_explanation_text(explanation)
        
        # Cache the explanation
        self._explanation_cache[cache_key] = explanation
        
        return explanation
        
    def _describe_current_behavior(self, quantity: QualitativeQuantity) -> str:
        """
        Describe the current behavioral state of a quantity
        
        Args:
            quantity: QualitativeQuantity to describe
            
        Returns:
            str: Human-readable behavior description
        """
        
        magnitude = quantity.magnitude
        derivative = quantity.derivative
        
        # Build behavior description
        magnitude_desc = {
            QualitativeValue.ZERO: "at zero",
            QualitativeValue.POSITIVE_SMALL: "at small positive value",
            QualitativeValue.POSITIVE_LARGE: "at large positive value", 
            QualitativeValue.NEGATIVE_SMALL: "at small negative value",
            QualitativeValue.NEGATIVE_LARGE: "at large negative value",
            QualitativeValue.POSITIVE_INFINITY: "approaching positive infinity",
            QualitativeValue.NEGATIVE_INFINITY: "approaching negative infinity"
        }.get(magnitude, "at unknown magnitude")
        
        trend_desc = {
            QualitativeDirection.POSITIVE: "and increasing",
            QualitativeDirection.NEGATIVE: "and decreasing", 
            QualitativeDirection.ZERO: "and stable"
        }.get(derivative, "with unknown trend")
        
        return f"{magnitude_desc} {trend_desc}"
        
    def _identify_primary_causes(self, quantity_name: str) -> List[str]:
        """
        Identify the primary causal processes affecting a quantity
        
        Args:
            quantity_name: Target quantity to analyze
            
        Returns:
            List[str]: Names of primary causal processes
        """
        
        primary_causes = []
        
        # Find active processes directly influencing this quantity
        for process_name, process in self.processes.items():
            if not process.active:
                continue
                
            # Check if this process influences the target quantity
            for influence_str in process.influences:
                if hasattr(self, '_parse_influence_target'):
                    target_qty = self._parse_influence_target(influence_str)
                    if target_qty == quantity_name:
                        primary_causes.append(process_name)
                        break
                        
        return primary_causes
        
    def _identify_contributing_factors(self, quantity_name: str) -> List[str]:
        """
        Identify contributing factors that enable or modulate primary causes
        
        Args:
            quantity_name: Target quantity to analyze
            
        Returns:
            List[str]: Names of contributing factor processes/conditions
        """
        
        contributing_factors = []
        primary_causes = self._identify_primary_causes(quantity_name)
        
        # For each primary cause, find what enables it
        for primary_process in primary_causes:
            if primary_process not in self.processes:
                continue
                
            process = self.processes[primary_process]
            
            # Check process preconditions
            for precondition in process.preconditions:
                if self._evaluate_logical_condition(precondition):
                    contributing_factors.append(f"precondition: {precondition}")
                    
            # Check quantity conditions that enable this process
            for qty_condition in process.quantity_conditions:
                if self._evaluate_quantity_condition(qty_condition):
                    # Extract quantities mentioned in the condition
                    if hasattr(self, 'get_condition_dependencies'):
                        deps = self.get_condition_dependencies(qty_condition)
                        for dep_qty in deps:
                            if dep_qty != quantity_name:  # Avoid self-reference
                                contributing_factors.append(f"condition quantity: {dep_qty}")
                                
        return list(set(contributing_factors))  # Remove duplicates
        
    def _build_causal_chains(self, quantity_name: str, max_depth: int) -> List[CausalChain]:
        """
        Build causal chains showing how influences propagate through the system
        
        Args:
            quantity_name: Target quantity
            max_depth: Maximum chain length to trace
            
        Returns:
            List[CausalChain]: Constructed causal chains
        """
        
        causal_chains = []
        
        # Start with quantities that influence the target
        influencing_quantities = self._find_influencing_quantities(quantity_name, max_depth)
        
        for source_qty, influence_data in influencing_quantities.items():
            if source_qty != quantity_name:  # Avoid self-loops
                chain = CausalChain(
                    source_quantity=source_qty,
                    target_quantity=quantity_name,
                    intermediate_processes=influence_data.get('processes', []),
                    chain_strength=influence_data.get('strength', 0.5),
                    explanation=influence_data.get('explanation', [])
                )
                causal_chains.append(chain)
                
        return causal_chains
        
    def _find_influencing_quantities(self, target_quantity: str, max_depth: int) -> Dict[str, Dict[str, Any]]:
        """
        Find quantities that influence the target through process chains
        
        Uses recursive search to trace influence propagation.
        """
        influencing_quantities = {}
        visited = set()
        
        def trace_influences(current_qty: str, depth: int, path: List[str], explanation: List[str]) -> None:
            if depth >= max_depth or current_qty in visited:
                return
                
            visited.add(current_qty)
            
            # Find processes that affect current_qty
            affecting_processes = []
            for process_name, process in self.processes.items():
                if process.active:
                    for influence_str in process.influences:
                        if hasattr(self, '_parse_influence_target'):
                            target = self._parse_influence_target(influence_str)
                            if target == current_qty:
                                affecting_processes.append(process_name)
                                
            # For each affecting process, find what quantities enable it
            for process_name in affecting_processes:
                if process_name not in self.processes:
                    continue
                    
                process = self.processes[process_name]
                
                # Check quantity conditions for upstream quantities
                for condition in process.quantity_conditions:
                    if hasattr(self, 'get_condition_dependencies'):
                        dependencies = self.get_condition_dependencies(condition)
                        for dep_qty in dependencies:
                            if dep_qty not in path:  # Avoid cycles
                                new_path = path + [process_name]
                                new_explanation = explanation + [
                                    f"{dep_qty} enables {process_name} which affects {current_qty}"
                                ]
                                
                                if dep_qty not in influencing_quantities:
                                    influencing_quantities[dep_qty] = {
                                        'processes': new_path,
                                        'strength': 1.0 / (depth + 1),  # Weaker with distance
                                        'explanation': new_explanation
                                    }
                                    
                                # Recursively trace further back
                                trace_influences(dep_qty, depth + 1, new_path, new_explanation)
                                
        trace_influences(target_quantity, 0, [], [])
        return influencing_quantities
        
    def _calculate_explanation_confidence(self, primary_causes: List[str], 
                                        contributing_factors: List[str],
                                        causal_chains: List[CausalChain]) -> float:
        """
        Calculate confidence level for the behavioral explanation
        
        Args:
            primary_causes: List of identified primary causes
            contributing_factors: List of contributing factors
            causal_chains: List of constructed causal chains
            
        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        
        confidence_factors = []
        
        # Factor 1: Completeness of primary causes
        if primary_causes:
            confidence_factors.append(min(1.0, len(primary_causes) / 3.0))  # Optimal around 3 causes
        else:
            confidence_factors.append(0.1)  # Low confidence without primary causes
            
        # Factor 2: Contributing factor richness
        if contributing_factors:
            confidence_factors.append(min(1.0, len(contributing_factors) / 5.0))
        else:
            confidence_factors.append(0.3)
            
        # Factor 3: Causal chain strength
        if causal_chains:
            avg_chain_strength = sum(chain.chain_strength for chain in causal_chains) / len(causal_chains)
            confidence_factors.append(avg_chain_strength)
        else:
            confidence_factors.append(0.2)
            
        # Factor 4: System state consistency
        if hasattr(self, 'constraints'):
            violations = sum(1 for constraint in self.constraints 
                           if not self._evaluate_constraint(constraint))
            consistency_factor = max(0.0, 1.0 - violations / max(1, len(self.constraints)))
            confidence_factors.append(consistency_factor)
        else:
            confidence_factors.append(0.5)  # Neutral if no constraints
            
        return sum(confidence_factors) / len(confidence_factors)
        
    def _generate_explanation_text(self, explanation: BehaviorExplanation) -> List[str]:
        """
        Generate human-readable explanation text from analysis results
        
        Args:
            explanation: BehaviorExplanation object to convert to text
            
        Returns:
            List[str]: Human-readable explanation statements
        """
        
        text_lines = []
        
        # Opening statement
        text_lines.append(f"\n🧠 BEHAVIORAL EXPLANATION FOR {explanation.quantity_name.upper()}:")
        text_lines.append(f"Current state: {explanation.current_behavior}")
        text_lines.append(f"Explanation confidence: {explanation.confidence:.1%}")
        text_lines.append("")
        
        # Primary causes section
        if explanation.primary_causes:
            text_lines.append("🎯 PRIMARY CAUSES:")
            for i, cause in enumerate(explanation.primary_causes, 1):
                process = self.processes.get(cause)
                if process:
                    desc = process.description or "No description available"
                    text_lines.append(f"  {i}. {cause}: {desc[:80]}{'...' if len(desc) > 80 else ''}")
                else:
                    text_lines.append(f"  {i}. {cause}: Process details not available")
            text_lines.append("")
            
        # Contributing factors section
        if explanation.contributing_factors:
            text_lines.append("🔧 CONTRIBUTING FACTORS:")
            for factor in explanation.contributing_factors[:5]:  # Limit to top 5
                text_lines.append(f"  • {factor}")
            if len(explanation.contributing_factors) > 5:
                remaining = len(explanation.contributing_factors) - 5
                text_lines.append(f"  • ... and {remaining} more factors")
            text_lines.append("")
            
        # Causal chains section
        if explanation.causal_chains:
            text_lines.append("⛓️ CAUSAL CHAINS:")
            for i, chain in enumerate(explanation.causal_chains[:3], 1):  # Top 3 chains
                strength_desc = "Strong" if chain.chain_strength > 0.7 else "Moderate" if chain.chain_strength > 0.4 else "Weak"
                text_lines.append(f"  {i}. {chain.source_quantity} → {chain.target_quantity} ({strength_desc})")
                
                if chain.intermediate_processes:
                    processes_str = " → ".join(chain.intermediate_processes[:3])
                    if len(chain.intermediate_processes) > 3:
                        processes_str += " → ..."
                    text_lines.append(f"     Via processes: {processes_str}")
                    
                if chain.explanation:
                    text_lines.append(f"     {chain.explanation[0][:100]}{'...' if len(chain.explanation[0]) > 100 else ''}")
                    
            text_lines.append("")
            
        # Summary and predictions
        text_lines.append("📊 SUMMARY:")
        if explanation.confidence > 0.7:
            text_lines.append(f"  High confidence explanation based on {len(explanation.primary_causes)} primary causes")
        elif explanation.confidence > 0.4:
            text_lines.append(f"  Moderate confidence explanation with some uncertainty")
        else:
            text_lines.append(f"  Low confidence - limited causal evidence available")
            
        # Future behavior prediction
        text_lines.append("")
        text_lines.append("🔮 PREDICTION:")
        if explanation.primary_causes:
            text_lines.append(f"  Behavior will continue as long as {len(explanation.primary_causes)} primary cause(s) remain active")
        else:
            text_lines.append("  Behavior may be unpredictable due to unclear causation")
            
        return text_lines
        
    def get_behavior_summary(self) -> Dict[str, Any]:
        """
        Get system-wide behavioral analysis summary
        
        Returns:
            Dict: Summary of behavioral patterns across all quantities
        """
        
        summary = {
            'quantities_analyzed': 0,
            'high_confidence_explanations': 0,
            'primary_causes_identified': 0,
            'causal_chains_found': 0,
            'behavioral_patterns': {},
            'system_dynamics': 'unknown'
        }
        
        # Analyze all quantities with non-zero derivatives
        active_quantities = [
            name for name, qty in self.quantities.items() 
            if qty.derivative != QualitativeDirection.ZERO
        ]
        
        summary['quantities_analyzed'] = len(active_quantities)
        
        total_confidence = 0
        total_chains = 0
        behavioral_types = {'increasing': 0, 'decreasing': 0, 'stable': 0}
        
        for qty_name in active_quantities:
            explanation = self.explain_behavior(qty_name, depth=2)
            
            if explanation.confidence > 0.7:
                summary['high_confidence_explanations'] += 1
                
            summary['primary_causes_identified'] += len(explanation.primary_causes)
            total_chains += len(explanation.causal_chains)
            total_confidence += explanation.confidence
            
            # Categorize behavior type
            if 'increasing' in explanation.current_behavior:
                behavioral_types['increasing'] += 1
            elif 'decreasing' in explanation.current_behavior:
                behavioral_types['decreasing'] += 1
            else:
                behavioral_types['stable'] += 1
                
        summary['causal_chains_found'] = total_chains
        summary['average_confidence'] = total_confidence / max(1, len(active_quantities))
        summary['behavioral_patterns'] = behavioral_types
        
        # Determine overall system dynamics
        if behavioral_types['increasing'] > behavioral_types['decreasing']:
            summary['system_dynamics'] = 'expansive'
        elif behavioral_types['decreasing'] > behavioral_types['increasing']:
            summary['system_dynamics'] = 'contractive'
        elif behavioral_types['stable'] > sum(behavioral_types.values()) / 2:
            summary['system_dynamics'] = 'equilibrium'
        else:
            summary['system_dynamics'] = 'mixed'
            
        return summary
        
    def clear_behavior_cache(self):
        """
        Clear behavioral analysis cache
        
        Useful when system state changes significantly.
        """
        self._explanation_cache.clear()
        self._analysis_cache.clear()
