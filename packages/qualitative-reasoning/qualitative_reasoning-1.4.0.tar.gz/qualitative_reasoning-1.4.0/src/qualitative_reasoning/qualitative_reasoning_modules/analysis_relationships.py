"""
📋 Analysis Relationships
==========================

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
🔗 Qualitative Reasoning - Analysis Relationships Module
========================================================

Relationship analysis and derivation for qualitative reasoning systems.
Extracted from analysis_engine.py to enforce 800-line limit.

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Forbus, K. D. (1984) - "Qualitative Process Theory"

This module provides relationship derivation, correlation analysis,
and intelligent relationship inference for qualitative systems.
"""

from typing import Dict, List, Tuple, Union, Optional, Any, Set
from dataclasses import dataclass, field
from .core_types import QualitativeValue, QualitativeDirection, QualitativeQuantity, QualitativeState, QualitativeProcess

@dataclass  
class RelationshipAnalysis:
    """Results of relationship analysis between quantities"""
    quantity_pair: Tuple[str, str]
    relationship_type: str
    strength: float = 0.0
    confidence: float = 0.0
    evidence: List[str] = field(default_factory=list)
    temporal_consistency: float = 0.0

class AnalysisRelationshipsMixin:
    """
    Relationship analysis and derivation for qualitative reasoning.
    
    Provides sophisticated relationship detection through multiple analytical
    approaches including directional correlation, causal analysis, and temporal patterns.
    """
    
    def derive_relationships(self) -> Dict[str, str]:
        """
        🔗 Derive relationships between quantities using multiple analytical approaches
        
        This implements sophisticated relationship inference by combining:
        1. **Directional Analysis**: Examines how quantities change together
        2. **Causal Analysis**: Traces process-mediated causation
        3. **Temporal Analysis**: Analyzes patterns over time  
        4. **Domain Knowledge**: Applies physics/domain-specific rules
        
        Returns:
            Dict[str, str]: Mapping from quantity pairs to relationship descriptions
            
        🔗 Relationship Types Detected:
        - **Proportional**: "quantity A increases when quantity B increases"
        - **Inverse**: "quantity A decreases when quantity B increases"
        - **Causal**: "quantity A directly causes changes in quantity B"
        - **Correlated**: "quantity A and B tend to change together"
        - **Independent**: "no significant relationship detected"
        
        🔍 Analysis Methods:
        The relationship derivation uses a multi-method approach:
        - Process-based causal tracing (most reliable)
        - Statistical correlation over time (requires history)
        - Instantaneous directional analysis (current state)
        - Domain-specific pattern matching (knowledge-based)
        """
        
        # Check cache for recent analysis
        if 'relationships' in self._analysis_cache:
            cache_time = self._analysis_cache.get('relationships_timestamp', 0)
            current_time = len(getattr(self, 'state_history', []))
            if abs(current_time - cache_time) < 5:  # Cache valid for 5 time steps
                return self._analysis_cache['relationships']
                
        relationships = {}
        quantity_names = list(self.quantities.keys())
        
        if len(quantity_names) < 2:
            return relationships
            
        # Method 1: Analyze directional correlations (current state)
        directional_relationships = self._analyze_directional_correlations(quantity_names)
        relationships.update(directional_relationships)
        
        # Method 2: Analyze causal relationships (process-based)
        causal_relationships = self._analyze_causal_relationships(quantity_names)
        relationships.update(causal_relationships)
        
        # Method 3: Analyze temporal correlations (requires history)
        if hasattr(self, 'state_history') and len(self.state_history) > 3:
            temporal_relationships = self._analyze_temporal_correlations(quantity_names)
            relationships.update(temporal_relationships)
            
        # Method 4: Infer domain-specific relationships
        domain_relationships = self._infer_domain_relationships(quantity_names)
        relationships.update(domain_relationships)
        
        # Cache results
        self._analysis_cache['relationships'] = relationships
        self._analysis_cache['relationships_timestamp'] = len(getattr(self, 'state_history', []))
        
        return relationships
        
    def _analyze_directional_correlations(self, qty_names: List[str]) -> Dict[str, str]:
        """
        Analyze directional correlations in current system state
        
        Examines how quantities are currently changing and infers relationships
        from synchronized directional patterns.
        
        Args:
            qty_names: List of quantity names to analyze
            
        Returns:
            Dict[str, str]: Directional relationship descriptions
        """
        
        relationships = {}
        
        for i, qty1_name in enumerate(qty_names):
            for qty2_name in qty_names[i+1:]:
                qty1 = self.quantities[qty1_name]
                qty2 = self.quantities[qty2_name]
                
                # Analyze current derivatives
                deriv1 = qty1.derivative
                deriv2 = qty2.derivative
                
                # Skip if either quantity is not changing
                if deriv1 == QualitativeDirection.ZERO or deriv2 == QualitativeDirection.ZERO:
                    continue
                    
                relationship_key = f"{qty1_name} <-> {qty2_name}"
                
                # Determine relationship type
                if deriv1 == deriv2:  # Both increasing or both decreasing
                    if deriv1 == QualitativeDirection.POSITIVE:
                        relationships[relationship_key] = f"proportional (both increasing)"
                    else:
                        relationships[relationship_key] = f"proportional (both decreasing)"
                elif deriv1 != deriv2:  # Opposite directions
                    if deriv1 == QualitativeDirection.POSITIVE:
                        relationships[relationship_key] = f"inverse ({qty1_name} increasing, {qty2_name} decreasing)"
                    else:
                        relationships[relationship_key] = f"inverse ({qty1_name} decreasing, {qty2_name} increasing)"
                        
        return relationships
        
    def _analyze_causal_relationships(self, qty_names: List[str]) -> Dict[str, str]:
        """
        Analyze causal relationships mediated by processes
        
        Traces how processes create causal connections between quantities,
        providing the most reliable relationship inferences.
        
        Args:
            qty_names: List of quantity names to analyze
            
        Returns:
            Dict[str, str]: Causal relationship descriptions
        """
        
        relationships = {}
        
        # Build causal graph from active processes
        causal_graph = {}  # qty1 -> [(qty2, process_name, influence_type)]
        
        for process_name, process in self.processes.items():
            if not process.active:
                continue
                
            # Find quantities this process influences
            influenced_quantities = []
            for influence_str in process.influences:
                if hasattr(self, '_parse_influence_target'):
                    target_qty = self._parse_influence_target(influence_str)
                    if target_qty and target_qty in qty_names:
                        influence_type = "positive" if influence_str.strip().startswith("I+") else "negative"
                        influenced_quantities.append((target_qty, influence_type))
                        
            # Find quantities this process depends on (via conditions)
            dependent_quantities = []
            for condition in process.quantity_conditions:
                if hasattr(self, 'get_condition_dependencies'):
                    dependencies = self.get_condition_dependencies(condition)
                    for dep_qty in dependencies:
                        if dep_qty in qty_names:
                            dependent_quantities.append(dep_qty)
                            
            # Create causal links: dependent -> influenced
            for dep_qty in dependent_quantities:
                if dep_qty not in causal_graph:
                    causal_graph[dep_qty] = []
                    
                for influenced_qty, influence_type in influenced_quantities:
                    if dep_qty != influenced_qty:  # Avoid self-loops
                        causal_graph[dep_qty].append((influenced_qty, process_name, influence_type))
                        
        # Generate relationship descriptions from causal graph
        for source_qty, connections in causal_graph.items():
            for target_qty, process_name, influence_type in connections:
                relationship_key = f"{source_qty} -> {target_qty}"
                
                if influence_type == "positive":
                    relationships[relationship_key] = f"causal positive (via {process_name})"
                else:
                    relationships[relationship_key] = f"causal negative (via {process_name})"
                    
        return relationships
        
    def _analyze_temporal_correlations(self, qty_names: List[str]) -> Dict[str, str]:
        """
        Analyze temporal correlations using historical data
        
        Uses time series analysis to detect correlation patterns that may not
        be visible in instantaneous analysis.
        
        Args:
            qty_names: List of quantity names to analyze
            
        Returns:
            Dict[str, str]: Temporal relationship descriptions
        """
        
        relationships = {}
        
        if not hasattr(self, 'state_history') or len(self.state_history) < 4:
            return relationships
            
        # Extract derivative histories for each quantity
        derivative_histories = {}
        for qty_name in qty_names:
            history = []
            for state in self.state_history[-10:]:  # Last 10 states
                if hasattr(state, 'quantities') and qty_name in state.quantities:
                    qty = state.quantities[qty_name]
                    history.append(qty.derivative)
                    
            if len(history) >= 3:  # Need minimum history
                derivative_histories[qty_name] = history
                
        # Compute pairwise correlations
        for i, qty1_name in enumerate(qty_names):
            for qty2_name in qty_names[i+1:]:
                if qty1_name in derivative_histories and qty2_name in derivative_histories:
                    hist1 = derivative_histories[qty1_name]
                    hist2 = derivative_histories[qty2_name]
                    
                    if len(hist1) == len(hist2) and len(hist1) >= 3:
                        correlation = self._compute_temporal_correlation(hist1, hist2)
                        
                        relationship_key = f"{qty1_name} <~> {qty2_name}"
                        
                        if abs(correlation) > 0.7:  # Strong correlation
                            if correlation > 0:
                                relationships[relationship_key] = f"strong positive temporal correlation ({correlation:.2f})"
                            else:
                                relationships[relationship_key] = f"strong negative temporal correlation ({correlation:.2f})"
                        elif abs(correlation) > 0.4:  # Moderate correlation
                            if correlation > 0:
                                relationships[relationship_key] = f"moderate positive temporal correlation ({correlation:.2f})"
                            else:
                                relationships[relationship_key] = f"moderate negative temporal correlation ({correlation:.2f})"
                                
        return relationships
        
    def _compute_temporal_correlation(self, hist1: List[QualitativeDirection], 
                                    hist2: List[QualitativeDirection]) -> float:
        """
        Compute correlation coefficient between two qualitative time series
        
        Converts qualitative directions to numeric values for correlation analysis.
        """
        
        def direction_to_numeric(direction):
            mapping = {
                QualitativeDirection.POSITIVE: 1.0,
                QualitativeDirection.ZERO: 0.0,
                QualitativeDirection.NEGATIVE: -1.0
            }
            return mapping.get(direction, 0.0)
            
        # Convert to numeric sequences
        seq1 = [direction_to_numeric(d) for d in hist1]
        seq2 = [direction_to_numeric(d) for d in hist2]
        
        if len(seq1) != len(seq2) or len(seq1) < 2:
            return 0.0
            
        # Compute correlation coefficient
        n = len(seq1)
        mean1 = sum(seq1) / n
        mean2 = sum(seq2) / n
        
        numerator = sum((seq1[i] - mean1) * (seq2[i] - mean2) for i in range(n))
        denom1 = sum((seq1[i] - mean1) ** 2 for i in range(n))
        denom2 = sum((seq2[i] - mean2) ** 2 for i in range(n))
        
        if denom1 == 0 or denom2 == 0:
            return 0.0
            
        correlation = numerator / (denom1 * denom2) ** 0.5
        return max(-1.0, min(1.0, correlation))  # Clamp to [-1, 1]
        
    def _infer_domain_relationships(self, qty_names: List[str]) -> Dict[str, str]:
        """
        Infer relationships using domain knowledge patterns
        
        Applies physics and domain-specific knowledge to identify
        well-known relationship patterns.
        
        Args:
            qty_names: List of quantity names to analyze
            
        Returns:
            Dict[str, str]: Domain-based relationship descriptions
        """
        
        relationships = {}
        
        # Common physics relationships (pattern matching)
        physics_patterns = [
            # Thermodynamics
            (r'temperature.*hot', r'temperature.*cold', 'thermal_gradient'),
            (r'heat.*flow', r'temperature.*difference', 'heat_transfer'),
            
            # Fluid dynamics
            (r'pressure.*high', r'pressure.*low', 'pressure_gradient'),
            (r'flow.*rate', r'pressure.*difference', 'flow_relationship'),
            
            # Mechanics  
            (r'force', r'acceleration', 'newtons_second_law'),
            (r'velocity', r'displacement', 'kinematic_relationship'),
            
            # Economics/General systems
            (r'supply', r'demand', 'market_relationship'),
            (r'input', r'output', 'production_relationship')
        ]
        
        for i, qty1_name in enumerate(qty_names):
            for qty2_name in qty_names[i+1:]:
                # Check for pattern matches
                for pattern1, pattern2, relationship_type in physics_patterns:
                    import re
                    
                    if (re.search(pattern1, qty1_name.lower()) and 
                        re.search(pattern2, qty2_name.lower())) or \
                       (re.search(pattern2, qty1_name.lower()) and 
                        re.search(pattern1, qty2_name.lower())):
                        
                        relationship_key = f"{qty1_name} <=> {qty2_name}"
                        relationships[relationship_key] = f"domain: {relationship_type}"
                        
        # Conservation law relationships
        conservation_patterns = ['energy', 'mass', 'momentum', 'charge']
        for pattern in conservation_patterns:
            matching_quantities = [qty for qty in qty_names if pattern in qty.lower()]
            
            if len(matching_quantities) >= 2:
                for i, qty1 in enumerate(matching_quantities):
                    for qty2 in matching_quantities[i+1:]:
                        relationship_key = f"{qty1} <=> {qty2}"
                        relationships[relationship_key] = f"conservation: {pattern} conservation law"
                        
        return relationships
        
    def analyze_relationship_strength(self, qty1_name: str, qty2_name: str) -> RelationshipAnalysis:
        """
        Perform detailed analysis of relationship strength between two quantities
        
        Args:
            qty1_name: First quantity name
            qty2_name: Second quantity name
            
        Returns:
            RelationshipAnalysis: Detailed relationship analysis
        """
        
        if qty1_name not in self.quantities or qty2_name not in self.quantities:
            return RelationshipAnalysis(
                quantity_pair=(qty1_name, qty2_name),
                relationship_type="undefined",
                strength=0.0,
                confidence=0.0,
                evidence=["One or both quantities not found"]
            )
            
        evidence = []
        strength_factors = []
        
        # Factor 1: Causal connection strength
        causal_strength = self._assess_causal_connection(qty1_name, qty2_name)
        if causal_strength > 0:
            strength_factors.append(causal_strength)
            evidence.append(f"Causal connection strength: {causal_strength:.2f}")
            
        # Factor 2: Directional correlation
        directional_correlation = self._assess_directional_correlation(qty1_name, qty2_name)
        if directional_correlation > 0:
            strength_factors.append(directional_correlation)
            evidence.append(f"Directional correlation: {directional_correlation:.2f}")
            
        # Factor 3: Temporal consistency (if history available)
        temporal_consistency = 0.0
        if hasattr(self, 'state_history') and len(self.state_history) > 3:
            temporal_consistency = self._assess_temporal_consistency(qty1_name, qty2_name)
            if temporal_consistency > 0:
                strength_factors.append(temporal_consistency)
                evidence.append(f"Temporal consistency: {temporal_consistency:.2f}")
                
        # Factor 4: Domain knowledge support
        domain_support = self._assess_domain_support(qty1_name, qty2_name)
        if domain_support > 0:
            strength_factors.append(domain_support)
            evidence.append(f"Domain knowledge support: {domain_support:.2f}")
            
        # Calculate overall strength and confidence
        overall_strength = sum(strength_factors) / len(strength_factors) if strength_factors else 0.0
        confidence = min(1.0, len(strength_factors) / 4.0)  # Higher confidence with more evidence
        
        # Determine relationship type
        relationship_type = self._classify_relationship_type(qty1_name, qty2_name, evidence)
        
        return RelationshipAnalysis(
            quantity_pair=(qty1_name, qty2_name),
            relationship_type=relationship_type,
            strength=overall_strength,
            confidence=confidence,
            evidence=evidence,
            temporal_consistency=temporal_consistency
        )
        
    def _assess_causal_connection(self, qty1_name: str, qty2_name: str) -> float:
        """
        Assess strength of causal connection between quantities
        
        Returns value between 0.0 (no connection) and 1.0 (strong direct connection)
        """
        
        # Check for direct process-mediated causation
        for process_name, process in self.processes.items():
            if not process.active:
                continue
                
            # Check if process is influenced by qty1 and influences qty2
            influences_qty2 = False
            depends_on_qty1 = False
            
            # Check influences
            for influence_str in process.influences:
                if hasattr(self, '_parse_influence_target'):
                    target = self._parse_influence_target(influence_str)
                    if target == qty2_name:
                        influences_qty2 = True
                        break
                        
            # Check dependencies
            for condition in process.quantity_conditions:
                if hasattr(self, 'get_condition_dependencies'):
                    deps = self.get_condition_dependencies(condition)
                    if qty1_name in deps:
                        depends_on_qty1 = True
                        break
                        
            if influences_qty2 and depends_on_qty1:
                return 1.0  # Strong direct causal connection
                
        return 0.0  # No direct causal connection found
        
    def _assess_directional_correlation(self, qty1_name: str, qty2_name: str) -> float:
        """
        Assess directional correlation in current state
        
        Returns value between 0.0 (no correlation) and 1.0 (perfect correlation)
        """
        
        qty1 = self.quantities[qty1_name]
        qty2 = self.quantities[qty2_name]
        
        deriv1 = qty1.derivative
        deriv2 = qty2.derivative
        
        # Both changing in same direction
        if deriv1 == deriv2 and deriv1 != QualitativeDirection.ZERO:
            return 0.8
            
        # Both changing in opposite directions
        if ((deriv1 == QualitativeDirection.POSITIVE and deriv2 == QualitativeDirection.NEGATIVE) or
            (deriv1 == QualitativeDirection.NEGATIVE and deriv2 == QualitativeDirection.POSITIVE)):
            return 0.6  # Negative correlation
            
        return 0.0  # No clear directional relationship
        
    def _assess_temporal_consistency(self, qty1_name: str, qty2_name: str) -> float:
        """
        Assess temporal consistency of relationship over time
        
        Returns value between 0.0 (inconsistent) and 1.0 (perfectly consistent)
        """
        
        if not hasattr(self, 'state_history') or len(self.state_history) < 4:
            return 0.0
            
        # Extract derivative patterns
        patterns = []
        for state in self.state_history[-8:]:  # Last 8 states
            if hasattr(state, 'quantities'):
                if qty1_name in state.quantities and qty2_name in state.quantities:
                    qty1_deriv = state.quantities[qty1_name].derivative
                    qty2_deriv = state.quantities[qty2_name].derivative
                    
                    if qty1_deriv == qty2_deriv:
                        patterns.append('same')
                    elif ((qty1_deriv == QualitativeDirection.POSITIVE and qty2_deriv == QualitativeDirection.NEGATIVE) or
                          (qty1_deriv == QualitativeDirection.NEGATIVE and qty2_deriv == QualitativeDirection.POSITIVE)):
                        patterns.append('opposite')
                    else:
                        patterns.append('mixed')
                        
        if not patterns:
            return 0.0
            
        # Calculate consistency (how often the same pattern appears)
        most_common_pattern = max(set(patterns), key=patterns.count)
        consistency = patterns.count(most_common_pattern) / len(patterns)
        
        return consistency
        
    def _assess_domain_support(self, qty1_name: str, qty2_name: str) -> float:
        """
        Assess domain knowledge support for relationship
        
        Returns value between 0.0 (no support) and 1.0 (strong domain support)
        """
        
        # Simple pattern matching for common domain relationships
        qty1_lower = qty1_name.lower()
        qty2_lower = qty2_name.lower()
        
        # Physics relationships
        physics_pairs = [
            ('temperature', 'heat'),
            ('pressure', 'flow'),
            ('force', 'acceleration'),
            ('voltage', 'current'),
            ('supply', 'demand')
        ]
        
        for term1, term2 in physics_pairs:
            if ((term1 in qty1_lower and term2 in qty2_lower) or
                (term2 in qty1_lower and term1 in qty2_lower)):
                return 0.7
                
        return 0.0
        
    def _classify_relationship_type(self, qty1_name: str, qty2_name: str, evidence: List[str]) -> str:
        """
        Classify the type of relationship based on evidence
        
        Args:
            qty1_name: First quantity
            qty2_name: Second quantity
            evidence: List of evidence strings
            
        Returns:
            str: Relationship type classification
        """
        
        evidence_text = ' '.join(evidence).lower()
        
        if 'causal connection' in evidence_text and 'strength: 1.0' in evidence_text:
            return 'direct_causal'
        elif 'causal connection' in evidence_text:
            return 'indirect_causal'
        elif 'directional correlation' in evidence_text and 'temporal consistency' in evidence_text:
            return 'correlated'
        elif 'domain knowledge' in evidence_text:
            return 'domain_related'
        elif 'directional correlation' in evidence_text:
            return 'directionally_related'
        elif 'temporal consistency' in evidence_text:
            return 'temporally_related'
        else:
            return 'weak_or_unknown'
            
    def get_relationship_network(self) -> Dict[str, Any]:
        """
        Get network representation of all quantity relationships
        
        Returns:
            Dict: Network structure with nodes and edges
        """
        
        relationships = self.derive_relationships()
        
        # Build network structure
        nodes = list(self.quantities.keys())
        edges = []
        
        for relationship_key, relationship_desc in relationships.items():
            # Parse relationship key to extract quantity names
            if ' -> ' in relationship_key:  # Directed relationship
                source, target = relationship_key.split(' -> ')
                edges.append({
                    'source': source.strip(),
                    'target': target.strip(),
                    'type': 'directed',
                    'description': relationship_desc
                })
            elif ' <-> ' in relationship_key or ' <~> ' in relationship_key or ' <=> ' in relationship_key:
                # Undirected relationship
                separator = ' <-> ' if ' <-> ' in relationship_key else ' <~> ' if ' <~> ' in relationship_key else ' <=> '
                qty1, qty2 = relationship_key.split(separator)
                edges.append({
                    'source': qty1.strip(),
                    'target': qty2.strip(),
                    'type': 'undirected',
                    'description': relationship_desc
                })
                
        return {
            'nodes': nodes,
            'edges': edges,
            'total_relationships': len(relationships),
            'network_density': len(edges) / max(1, len(nodes) * (len(nodes) - 1) / 2)
        }
