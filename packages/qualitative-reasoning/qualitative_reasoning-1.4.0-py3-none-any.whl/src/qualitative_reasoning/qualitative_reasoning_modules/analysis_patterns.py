"""
📋 Analysis Patterns
=====================

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
🔍 Qualitative Reasoning - Analysis Patterns Module
================================================

Pattern recognition and trend analysis for qualitative reasoning systems.
Extracted from analysis_engine.py to enforce 800-line limit.

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Forbus, K. D. (1984) - "Qualitative Process Theory"

This module provides pattern recognition, trend analysis,
and system health assessment for qualitative systems.
"""

from typing import Dict, List, Tuple, Union, Optional, Any, Set
from dataclasses import dataclass, field
from collections import Counter, defaultdict
from .core_types import QualitativeValue, QualitativeDirection, QualitativeQuantity, QualitativeState, QualitativeProcess

@dataclass
class PatternAnalysis:
    """Results of pattern analysis"""
    pattern_type: str
    entities_involved: List[str] = field(default_factory=list)
    strength: float = 0.0
    confidence: float = 0.0
    description: str = ""
    temporal_span: int = 0

class AnalysisPatternsMixin:
    """
    Pattern recognition and trend analysis for qualitative reasoning.
    
    Provides sophisticated pattern detection, trend analysis,
    and system health assessment capabilities.
    """
    
    def recognize_patterns(self) -> List[PatternAnalysis]:
        """
        🔍 Recognize behavioral patterns in the qualitative system
        
        This implements pattern recognition across multiple dimensions:
        1. **Temporal Patterns**: Recurring behavioral sequences over time
        2. **Structural Patterns**: Common process activation patterns
        3. **Magnitude Patterns**: Quantity magnitude evolution patterns
        4. **Causal Patterns**: Recurring cause-effect chains
        5. **Domain Patterns**: Physics/domain-specific behavioral patterns
        
        Returns:
            List[PatternAnalysis]: Recognized patterns with confidence scores
            
        🔍 Pattern Recognition Theory:
        Pattern recognition in qualitative reasoning helps identify:
        - **Cyclic Behavior**: Systems that return to previous states
        - **Trend Patterns**: Consistent directional changes over time
        - **Oscillatory Patterns**: Regular alternating behaviors
        - **Threshold Patterns**: Behavior changes at critical points
        - **Conservation Patterns**: Behaviors consistent with physical laws
        
        The recognition process combines:
        - Statistical analysis of historical sequences
        - Process activation pattern matching
        - Domain knowledge application
        - Structural relationship analysis
        """
        
        patterns = []
        
        # Pattern Type 1: Temporal sequence patterns
        temporal_patterns = self._recognize_temporal_patterns()
        patterns.extend(temporal_patterns)
        
        # Pattern Type 2: Process activation patterns
        activation_patterns = self._recognize_activation_patterns()
        patterns.extend(activation_patterns)
        
        # Pattern Type 3: Magnitude evolution patterns
        magnitude_patterns = self._recognize_magnitude_patterns()
        patterns.extend(magnitude_patterns)
        
        # Pattern Type 4: Causal chain patterns
        causal_patterns = self._recognize_causal_patterns()
        patterns.extend(causal_patterns)
        
        # Pattern Type 5: Domain-specific patterns
        domain_patterns = self._recognize_domain_patterns()
        patterns.extend(domain_patterns)
        
        # Sort by confidence score
        patterns.sort(key=lambda p: p.confidence, reverse=True)
        
        return patterns[:20]  # Return top 20 patterns
        
    def _recognize_temporal_patterns(self) -> List[PatternAnalysis]:
        """
        Recognize temporal patterns in system behavior
        
        Analyzes historical state sequences to identify recurring patterns.
        """
        
        patterns = []
        
        if not hasattr(self, 'state_history') or len(self.state_history) < 6:
            return patterns
            
        # Extract derivative sequences for each quantity
        for qty_name, quantity in self.quantities.items():
            derivative_sequence = []
            
            for state in self.state_history[-12:]:  # Last 12 states
                if hasattr(state, 'quantities') and qty_name in state.quantities:
                    deriv = state.quantities[qty_name].derivative
                    derivative_sequence.append(deriv)
                    
            if len(derivative_sequence) >= 6:
                # Look for cyclic patterns
                cycle_pattern = self._detect_cycles(derivative_sequence)
                if cycle_pattern:
                    patterns.append(PatternAnalysis(
                        pattern_type="cyclic_behavior",
                        entities_involved=[qty_name],
                        strength=cycle_pattern['strength'],
                        confidence=cycle_pattern['confidence'],
                        description=f"{qty_name} shows cyclic behavior with period {cycle_pattern['period']}",
                        temporal_span=cycle_pattern['period']
                    ))
                    
                # Look for trend patterns
                trend_pattern = self._detect_trends(derivative_sequence)
                if trend_pattern:
                    patterns.append(PatternAnalysis(
                        pattern_type="trend_behavior",
                        entities_involved=[qty_name],
                        strength=trend_pattern['strength'],
                        confidence=trend_pattern['confidence'],
                        description=f"{qty_name} shows {trend_pattern['direction']} trend",
                        temporal_span=len(derivative_sequence)
                    ))
                    
        return patterns
        
    def _recognize_activation_patterns(self) -> List[PatternAnalysis]:
        """
        Recognize patterns in process activation sequences
        """
        
        patterns = []
        
        if not hasattr(self, 'active_process_history') or len(self.active_process_history) < 5:
            return patterns
            
        # Analyze process activation sequences
        activation_history = self.active_process_history[-10:]  # Last 10 activation states
        
        # Look for consistent activation patterns
        activation_sequences = []
        for i in range(len(activation_history) - 2):
            sequence = tuple(sorted(activation_history[i:i+3]))  # 3-step sequences
            activation_sequences.append(sequence)
            
        # Find recurring sequences
        sequence_counts = Counter(activation_sequences)
        for sequence, count in sequence_counts.items():
            if count >= 2:  # Appears at least twice
                confidence = min(1.0, count / len(activation_sequences))
                patterns.append(PatternAnalysis(
                    pattern_type="activation_sequence",
                    entities_involved=list(set().union(*sequence)) if sequence else [],
                    strength=count / len(activation_sequences),
                    confidence=confidence,
                    description=f"Recurring process activation pattern: {' -> '.join(map(str, sequence))}",
                    temporal_span=3
                ))
                
        return patterns
        
    def _recognize_magnitude_patterns(self) -> List[PatternAnalysis]:
        """
        Recognize patterns in quantity magnitude evolution
        """
        
        patterns = []
        
        if not hasattr(self, 'state_history') or len(self.state_history) < 5:
            return patterns
            
        # Analyze magnitude stability patterns
        for qty_name in self.quantities.keys():
            stability_analysis = self._analyze_magnitude_stability(qty_name)
            
            if stability_analysis in ['highly_stable', 'moderately_stable']:
                confidence = 0.9 if stability_analysis == 'highly_stable' else 0.7
                patterns.append(PatternAnalysis(
                    pattern_type="magnitude_stability",
                    entities_involved=[qty_name],
                    strength=confidence,
                    confidence=confidence,
                    description=f"{qty_name} maintains {stability_analysis} magnitude",
                    temporal_span=len(self.state_history)
                ))
                
        # Look for equilibrium patterns
        equilibrium_quantities = []
        for qty_name, quantity in self.quantities.items():
            if quantity.derivative == QualitativeDirection.ZERO:
                equilibrium_quantities.append(qty_name)
                
        if len(equilibrium_quantities) > len(self.quantities) / 2:
            patterns.append(PatternAnalysis(
                pattern_type="system_equilibrium",
                entities_involved=equilibrium_quantities,
                strength=len(equilibrium_quantities) / len(self.quantities),
                confidence=0.8,
                description=f"System approaching equilibrium ({len(equilibrium_quantities)} of {len(self.quantities)} quantities stable)",
                temporal_span=1
            ))
            
        return patterns
        
    def _recognize_causal_patterns(self) -> List[PatternAnalysis]:
        """
        Recognize recurring causal chain patterns
        """
        
        patterns = []
        
        # Analyze causal chain structures
        causal_chains = {}
        for qty_name in self.quantities.keys():
            if hasattr(self, 'get_causal_chain'):
                chain = self.get_causal_chain(qty_name)
                if 'direct_influences' in chain and chain['direct_influences']:
                    for influence in chain['direct_influences']:
                        process_name = influence.get('process', 'unknown')
                        if process_name not in causal_chains:
                            causal_chains[process_name] = []
                        causal_chains[process_name].append(qty_name)
                        
        # Look for processes that influence multiple quantities
        for process_name, influenced_quantities in causal_chains.items():
            if len(influenced_quantities) > 2:
                patterns.append(PatternAnalysis(
                    pattern_type="multi_influence_process",
                    entities_involved=[process_name] + influenced_quantities,
                    strength=len(influenced_quantities) / len(self.quantities),
                    confidence=0.8,
                    description=f"Process {process_name} influences {len(influenced_quantities)} quantities",
                    temporal_span=1
                ))
                
        return patterns
        
    def _recognize_domain_patterns(self) -> List[PatternAnalysis]:
        """
        Recognize domain-specific patterns (physics, etc.)
        """
        
        patterns = []
        
        # Conservation pattern detection
        conservation_keywords = ['energy', 'mass', 'momentum', 'charge']
        for keyword in conservation_keywords:
            matching_quantities = [qty for qty in self.quantities.keys() 
                                 if keyword.lower() in qty.lower()]
            
            if len(matching_quantities) >= 2:
                # Check if quantities show conservation behavior (sum of derivatives ≈ 0)
                total_change = 0
                for qty_name in matching_quantities:
                    qty = self.quantities[qty_name]
                    if qty.derivative == QualitativeDirection.POSITIVE:
                        total_change += 1
                    elif qty.derivative == QualitativeDirection.NEGATIVE:
                        total_change -= 1
                        
                if abs(total_change) <= 1:  # Approximately conserved
                    patterns.append(PatternAnalysis(
                        pattern_type="conservation_law",
                        entities_involved=matching_quantities,
                        strength=0.8,
                        confidence=0.7,
                        description=f"{keyword.title()} conservation pattern detected",
                        temporal_span=1
                    ))
                    
        # Heat transfer patterns
        temperature_quantities = [qty for qty in self.quantities.keys() 
                                if 'temperature' in qty.lower()]
        
        if len(temperature_quantities) >= 2:
            # Check for heat flow patterns (high temp decreasing, low temp increasing)
            heat_flow_evidence = 0
            for qty_name in temperature_quantities:
                qty = self.quantities[qty_name]
                if qty.magnitude in [QualitativeValue.POSITIVE_LARGE, QualitativeValue.POSITIVE_SMALL]:
                    if qty.derivative == QualitativeDirection.NEGATIVE:
                        heat_flow_evidence += 1
                elif qty.magnitude in [QualitativeValue.NEGATIVE_SMALL, QualitativeValue.ZERO]:
                    if qty.derivative == QualitativeDirection.POSITIVE:
                        heat_flow_evidence += 1
                        
            if heat_flow_evidence >= 2:
                patterns.append(PatternAnalysis(
                    pattern_type="heat_transfer",
                    entities_involved=temperature_quantities,
                    strength=heat_flow_evidence / len(temperature_quantities),
                    confidence=0.8,
                    description="Heat transfer pattern: hot objects cooling, cold objects warming",
                    temporal_span=1
                ))
                
        return patterns
        
    def _detect_cycles(self, sequence: List[QualitativeDirection]) -> Optional[Dict[str, Any]]:
        """
        Detect cyclic patterns in a qualitative sequence
        
        Returns cycle information if found, None otherwise.
        """
        
        if len(sequence) < 4:
            return None
            
        # Try different cycle lengths
        for cycle_length in range(2, len(sequence) // 2 + 1):
            # Check if sequence repeats with this cycle length
            is_cyclic = True
            cycle_pattern = sequence[:cycle_length]
            
            for i in range(cycle_length, len(sequence)):
                if sequence[i] != cycle_pattern[i % cycle_length]:
                    is_cyclic = False
                    break
                    
            if is_cyclic:
                # Calculate confidence based on how many complete cycles we see
                complete_cycles = len(sequence) // cycle_length
                confidence = min(1.0, complete_cycles / 3.0)  # High confidence with 3+ cycles
                
                return {
                    'period': cycle_length,
                    'pattern': cycle_pattern,
                    'strength': 0.8,
                    'confidence': confidence,
                    'complete_cycles': complete_cycles
                }
                
        return None
        
    def _detect_trends(self, sequence: List[QualitativeDirection]) -> Optional[Dict[str, Any]]:
        """
        Detect trend patterns in a qualitative sequence
        
        Returns trend information if found, None otherwise.
        """
        
        if len(sequence) < 4:
            return None
            
        # Count directional changes
        positive_count = sequence.count(QualitativeDirection.POSITIVE)
        negative_count = sequence.count(QualitativeDirection.NEGATIVE)
        zero_count = sequence.count(QualitativeDirection.ZERO)
        
        total_count = len(sequence)
        
        # Determine if there's a clear trend
        if positive_count / total_count > 0.7:
            return {
                'direction': 'increasing',
                'strength': positive_count / total_count,
                'confidence': 0.8
            }
        elif negative_count / total_count > 0.7:
            return {
                'direction': 'decreasing',
                'strength': negative_count / total_count,
                'confidence': 0.8
            }
        elif zero_count / total_count > 0.7:
            return {
                'direction': 'stable',
                'strength': zero_count / total_count,
                'confidence': 0.8
            }
            
        return None
        
    def _analyze_magnitude_stability(self, qty_name: str) -> str:
        """
        Analyze magnitude stability of a quantity over time
        
        Args:
            qty_name: Quantity to analyze
            
        Returns:
            str: Stability classification
        """
        
        if not hasattr(self, 'state_history') or len(self.state_history) < 3:
            return 'insufficient_data'
            
        magnitude_history = []
        for state in self.state_history[-8:]:  # Last 8 states
            if hasattr(state, 'quantities') and qty_name in state.quantities:
                magnitude = state.quantities[qty_name].magnitude
                magnitude_history.append(magnitude)
                
        if len(magnitude_history) < 3:
            return 'insufficient_data'
            
        # Count magnitude changes
        changes = 0
        for i in range(1, len(magnitude_history)):
            if magnitude_history[i] != magnitude_history[i-1]:
                changes += 1
                
        change_rate = changes / (len(magnitude_history) - 1)
        
        if change_rate < 0.2:
            return 'highly_stable'
        elif change_rate < 0.4:
            return 'moderately_stable'
        elif change_rate < 0.7:
            return 'somewhat_unstable'
        else:
            return 'highly_unstable'
            
    def _assess_system_health(self) -> Dict[str, Any]:
        """Assess overall system health and stability"""
        
        health = {
            'constraint_violations': 0,
            'stability_score': 0.0,
            'coherence_score': 0.0,
            'overall_health': 'unknown'
        }
        
        # Check constraint violations
        violations = 0
        if hasattr(self, 'constraints'):
            for constraint in self.constraints:
                try:
                    if hasattr(self, '_evaluate_constraint') and not self._evaluate_constraint(constraint):
                        violations += 1
                except:
                    violations += 1
                    
        health['constraint_violations'] = violations
        
        # Calculate stability score
        if hasattr(self, 'state_history') and len(self.state_history) > 1:
            stability_scores = []
            for qty_name in self.quantities.keys():
                stability = self._analyze_magnitude_stability(qty_name)
                if stability == 'highly_stable':
                    stability_scores.append(1.0)
                elif stability == 'moderately_stable':
                    stability_scores.append(0.7)
                elif stability == 'somewhat_unstable':
                    stability_scores.append(0.4)
                else:
                    stability_scores.append(0.1)
                    
            health['stability_score'] = sum(stability_scores) / len(stability_scores) if stability_scores else 0.0
            
        # Calculate coherence score (consistency of relationships)
        if hasattr(self, '_analysis_cache') and 'relationships' in self._analysis_cache:
            relationships = self._analysis_cache.get('relationships', {})
            positive_rels = len([r for r in relationships.values() if 'positive' in r.lower()])
            negative_rels = len([r for r in relationships.values() if 'negative' in r.lower()])
            total_rels = max(1, len(relationships))
            
            # Higher coherence when relationships are balanced
            coherence = 1.0 - abs(positive_rels - negative_rels) / total_rels
            health['coherence_score'] = coherence
        else:
            health['coherence_score'] = 0.5  # Neutral if no relationship data
            
        # Calculate overall health
        constraint_health = 1.0 - min(1.0, violations / max(1, len(getattr(self, 'constraints', []))))
        overall = (constraint_health + health['stability_score'] + health['coherence_score']) / 3
        
        if overall > 0.8:
            health['overall_health'] = 'excellent'
        elif overall > 0.6:
            health['overall_health'] = 'good'
        elif overall > 0.4:
            health['overall_health'] = 'fair'
        else:
            health['overall_health'] = 'poor'
            
        return health
        
    def get_pattern_summary(self) -> Dict[str, Any]:
        """
        Get summary of all recognized patterns
        
        Returns:
            Dict: Pattern analysis summary
        """
        
        patterns = self.recognize_patterns()
        
        pattern_types = defaultdict(int)
        high_confidence_patterns = 0
        total_entities = set()
        
        for pattern in patterns:
            pattern_types[pattern.pattern_type] += 1
            if pattern.confidence > 0.7:
                high_confidence_patterns += 1
            total_entities.update(pattern.entities_involved)
            
        return {
            'total_patterns': len(patterns),
            'pattern_types': dict(pattern_types),
            'high_confidence_patterns': high_confidence_patterns,
            'entities_with_patterns': len(total_entities),
            'most_common_pattern': max(pattern_types.keys(), key=pattern_types.get) if pattern_types else None,
            'system_health': self._assess_system_health()
        }
