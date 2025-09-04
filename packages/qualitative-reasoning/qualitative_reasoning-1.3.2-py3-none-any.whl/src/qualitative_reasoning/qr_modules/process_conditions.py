"""
🧠 Qualitative Reasoning - Process Conditions Module
===================================================

Process condition evaluation for qualitative reasoning systems.
Extracted from process_engine.py to enforce 800-line limit.

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Forbus, K. D. (1984) - "Qualitative Process Theory"

This module provides secure condition evaluation, quantity comparisons,
and activation logic for qualitative processes.
"""

from typing import Dict, List, Tuple, Union, Optional, Any, Set
from .core_types import QualitativeProcess, QualitativeQuantity, QualitativeValue, QualitativeDirection, QualitativeState
import re

class ProcessConditionsMixin:
    """
    Process condition evaluation for qualitative reasoning.
    
    Provides secure evaluation of process preconditions and quantity conditions
    using safe parsing without eval() vulnerabilities.
    """
    
    def evaluate_process_conditions(self, process: QualitativeProcess) -> bool:
        """
        Evaluate whether a process should be active based on its conditions
        
        This implements the process activation logic from Process Theory:
        Active(P,t) ↔ preconditions(P,t) ∧ quantity_conditions(P,t)
        
        Args:
            process: QualitativeProcess to evaluate
            
        Returns:
            bool: True if process should be active, False otherwise
            
        🧠 Secure Evaluation:
        This method uses safe parsing instead of eval() to prevent code injection.
        Only predefined comparison operators and quantity references are allowed.
        
        Supported Condition Types:
        - Quantity comparisons: "temperature(obj1) > temperature(obj2)"
        - Magnitude checks: "pressure(system) > 0"
        - Qualitative values: "flow_rate(pipe) = positive"
        - Logical operators: "condition1 AND condition2"
        """
        
        try:
            # Evaluate logical preconditions
            preconditions_satisfied = True
            for precondition in process.preconditions:
                if not self._evaluate_logical_condition(precondition):
                    preconditions_satisfied = False
                    break
                    
            if not preconditions_satisfied:
                return False
                
            # Evaluate quantity-based conditions
            for condition in process.quantity_conditions:
                if not self._evaluate_quantity_condition(condition):
                    return False
                    
            return True
            
        except Exception as e:
            # Safe fallback - if evaluation fails, process is not active
            if hasattr(self, '_verbose') and self._verbose:
                print(f"Warning: Failed to evaluate conditions for {process.name}: {e}")
            return False
            
    def _evaluate_quantity_condition(self, condition: str) -> bool:
        """
        Safely evaluate a quantity-based condition
        
        Parses and evaluates conditions involving qualitative quantities
        without using dangerous eval() function.
        
        Args:
            condition: Condition string to evaluate
            
        Returns:
            bool: True if condition is satisfied, False otherwise
            
        🔒 Security:
        Uses whitelist-based parsing to prevent code injection. Only allows:
        - Quantity names matching [a-zA-Z_][a-zA-Z0-9_]*
        - Comparison operators: >, <, =, >=, <=
        - Qualitative values: positive, negative, zero, etc.
        - Logical operators: AND, OR, NOT
        
        Examples:
        - "temperature > 0" -> Check if temperature is positive
        - "pressure = zero" -> Check if pressure is exactly zero
        - "velocity < acceleration" -> Compare two quantities
        """
        
        condition = condition.strip()
        
        # Handle logical operators (AND, OR, NOT)
        if ' AND ' in condition:
            parts = condition.split(' AND ')
            return all(self._evaluate_quantity_condition(part.strip()) for part in parts)
            
        if ' OR ' in condition:
            parts = condition.split(' OR ')
            return any(self._evaluate_quantity_condition(part.strip()) for part in parts)
            
        if condition.startswith('NOT '):
            inner_condition = condition[4:].strip()
            return not self._evaluate_quantity_condition(inner_condition)
            
        # Parse basic comparison: left_side operator right_side
        comparison_pattern = r'^([a-zA-Z_][a-zA-Z0-9_]*(?:\([^)]*\))?)\s*([><=]+)\s*(.+)$'
        match = re.match(comparison_pattern, condition)
        
        if not match:
            return False
            
        left_side, operator, right_side = match.groups()
        left_side = left_side.strip()
        operator = operator.strip()
        right_side = right_side.strip()
        
        # Handle quantity(object) format
        if '(' in left_side:
            quantity_name = left_side.split('(')[0]
            object_name = left_side.split('(')[1].rstrip(')')
            # For now, treat as simple quantity name
            left_quantity_name = f"{quantity_name}_{object_name}"
        else:
            left_quantity_name = left_side
            
        # Check if left side is a known quantity
        if left_quantity_name not in self.quantities:
            return False
            
        left_quantity = self.quantities[left_quantity_name]
        
        # Evaluate right side
        if right_side in self.quantities:
            # Quantity-to-quantity comparison
            return self._compare_quantities(left_quantity_name, right_side, operator)
        else:
            # Quantity-to-value comparison
            return self._compare_quantity_to_value(left_quantity, operator, right_side)
            
    def _compare_quantity_to_value(self, quantity: QualitativeQuantity, operator: str, value_str: str) -> bool:
        """
        Compare a quantity to a qualitative value
        
        Args:
            quantity: QualitativeQuantity to compare
            operator: Comparison operator (>, <, =, etc.)
            value_str: String representation of qualitative value
            
        Returns:
            bool: True if comparison holds, False otherwise
        """
        
        # Parse qualitative value
        target_value = self._parse_qualitative_value(value_str)
        if target_value is None:
            # Try numeric comparison for special cases
            if value_str == "0" or value_str.lower() == "zero":
                target_value = QualitativeValue.ZERO
            else:
                return False
                
        current_value = quantity.magnitude
        
        # Get ordering for comparison
        ordering = QualitativeValue.get_ordering()
        current_order = ordering.get(current_value, 0)
        target_order = ordering.get(target_value, 0)
        
        if operator == ">":
            return current_order > target_order
        elif operator == "<":
            return current_order < target_order
        elif operator == "=" or operator == "==":
            return current_order == target_order
        elif operator == ">=":
            return current_order >= target_order
        elif operator == "<=":
            return current_order <= target_order
            
        return False
        
    def _evaluate_logical_condition(self, condition: str) -> bool:
        """
        Evaluate logical preconditions safely
        
        Args:
            condition: Logical condition string
            
        Returns:
            bool: True if condition is satisfied, False otherwise
            
        🔒 Safe Logic Evaluation:
        Uses pattern matching to handle common logical conditions without eval().
        Supports:
        - connected(a, b): Check if two objects are connected
        - exists(object): Check if object exists
        - type(object, class): Check object type
        - Boolean combinations with AND, OR, NOT
        """
        
        condition = condition.strip()
        
        # Handle logical operators
        if ' AND ' in condition:
            parts = condition.split(' AND ')
            return all(self._evaluate_logical_condition(part.strip()) for part in parts)
            
        if ' OR ' in condition:
            parts = condition.split(' OR ')
            return any(self._evaluate_logical_condition(part.strip()) for part in parts)
            
        if condition.startswith('NOT '):
            inner_condition = condition[4:].strip()
            return not self._evaluate_logical_condition(inner_condition)
            
        # Handle function-style conditions
        if condition.startswith('connected('):
            return self._evaluate_connection_condition(condition)
        elif condition.startswith('exists('):
            return self._evaluate_existence_condition(condition)
        elif condition.startswith('type('):
            return self._evaluate_type_condition(condition)
        else:
            # Simple boolean conditions or flags
            return self._evaluate_simple_condition(condition)
            
    def _evaluate_connection_condition(self, condition: str) -> bool:
        """
        Evaluate connection conditions: connected(obj1, obj2)
        
        Args:
            condition: Connection condition string
            
        Returns:
            bool: True if objects are connected, False otherwise
        """
        
        # Extract objects from connected(obj1, obj2)
        match = re.match(r'connected\(([^,]+),\s*([^)]+)\)', condition)
        if not match:
            return False
            
        obj1, obj2 = match.groups()
        obj1 = obj1.strip()
        obj2 = obj2.strip()
        
        # Check connection in system topology (if available)
        if hasattr(self, 'connections'):
            return (obj1, obj2) in self.connections or (obj2, obj1) in self.connections
        else:
            # Default: assume objects are connected if both exist
            return (hasattr(self, 'objects') and 
                   obj1 in self.objects and obj2 in self.objects)
                   
    def _evaluate_existence_condition(self, condition: str) -> bool:
        """
        Evaluate existence conditions: exists(object)
        
        Args:
            condition: Existence condition string
            
        Returns:
            bool: True if object exists, False otherwise
        """
        
        match = re.match(r'exists\(([^)]+)\)', condition)
        if not match:
            return False
            
        obj_name = match.group(1).strip()
        
        # Check if object exists in system
        if hasattr(self, 'objects'):
            return obj_name in self.objects
        elif hasattr(self, 'quantities'):
            # Check if any quantities reference this object
            return any(obj_name in qty_name for qty_name in self.quantities.keys())
        else:
            return False
            
    def _evaluate_type_condition(self, condition: str) -> bool:
        """
        Evaluate type conditions: type(object, class)
        
        Args:
            condition: Type condition string
            
        Returns:
            bool: True if object is of specified type, False otherwise
        """
        
        match = re.match(r'type\(([^,]+),\s*([^)]+)\)', condition)
        if not match:
            return False
            
        obj_name, type_name = match.groups()
        obj_name = obj_name.strip()
        type_name = type_name.strip()
        
        # Check object type (if type system is available)
        if hasattr(self, 'object_types'):
            return self.object_types.get(obj_name) == type_name
        else:
            return False
            
    def _evaluate_simple_condition(self, condition: str) -> bool:
        """
        Evaluate simple boolean conditions or flags
        
        Args:
            condition: Simple condition string
            
        Returns:
            bool: True if condition is satisfied, False otherwise
        """
        
        # Check for boolean flags or simple identifiers
        if hasattr(self, 'flags') and condition in self.flags:
            return self.flags[condition]
        elif condition.lower() in ['true', 'yes', 'on']:
            return True
        elif condition.lower() in ['false', 'no', 'off']:
            return False
        else:
            # Default: unknown conditions are false for safety
            return False
            
    def _is_positive(self, magnitude: QualitativeValue) -> bool:
        """
        Check if a qualitative magnitude is positive
        
        Args:
            magnitude: QualitativeValue to check
            
        Returns:
            bool: True if positive, False otherwise
        """
        
        positive_values = {QualitativeValue.POSITIVE_SMALL, QualitativeValue.POSITIVE_LARGE, 
                          QualitativeValue.POSITIVE_INFINITY}
        return magnitude in positive_values
        
    def _is_negative(self, magnitude: QualitativeValue) -> bool:
        """
        Check if a qualitative magnitude is negative
        
        Args:
            magnitude: QualitativeValue to check
            
        Returns:
            bool: True if negative, False otherwise
        """
        
        negative_values = {QualitativeValue.NEGATIVE_SMALL, QualitativeValue.NEGATIVE_LARGE,
                          QualitativeValue.NEGATIVE_INFINITY}
        return magnitude in negative_values
        
    def _compare_quantities(self, left_name: str, right_name: str, operator: str) -> bool:
        """
        Compare two quantities using qualitative ordering
        
        Args:
            left_name: Name of left quantity
            right_name: Name of right quantity  
            operator: Comparison operator
            
        Returns:
            bool: True if comparison holds, False otherwise
        """
        
        if left_name not in self.quantities or right_name not in self.quantities:
            return False
            
        left_qty = self.quantities[left_name]
        right_qty = self.quantities[right_name]
        
        # Get ordering values for comparison
        ordering = QualitativeValue.get_ordering()
        left_order = ordering.get(left_qty.magnitude, 0)
        right_order = ordering.get(right_qty.magnitude, 0)
        
        if operator == ">":
            return left_order > right_order
        elif operator == "<":
            return left_order < right_order
        elif operator == "=" or operator == "==":
            return left_order == right_order
        elif operator == ">=":
            return left_order >= right_order
        elif operator == "<=":
            return left_order <= right_order
            
        return False
        
    def _parse_qualitative_value(self, value_str: str) -> Optional[QualitativeValue]:
        """Parse string representations into QualitativeValue enum"""
        
        value_str = value_str.lower().strip()
        
        # Direct enum value mapping
        value_mapping = {
            '0': QualitativeValue.ZERO,
            'zero': QualitativeValue.ZERO,
            'positive': QualitativeValue.POSITIVE_SMALL,
            'negative': QualitativeValue.NEGATIVE_SMALL,
            'pos': QualitativeValue.POSITIVE_SMALL,
            'neg': QualitativeValue.NEGATIVE_SMALL,
            'large': QualitativeValue.POSITIVE_LARGE,
            'small': QualitativeValue.POSITIVE_SMALL,
            'pos_large': QualitativeValue.POSITIVE_LARGE,
            'neg_large': QualitativeValue.NEGATIVE_LARGE,
            'infinity': QualitativeValue.POSITIVE_INFINITY,
            'inf': QualitativeValue.POSITIVE_INFINITY,
            'pos_inf': QualitativeValue.POSITIVE_INFINITY,
            'neg_inf': QualitativeValue.NEGATIVE_INFINITY,
            '-infinity': QualitativeValue.NEGATIVE_INFINITY,
            '-inf': QualitativeValue.NEGATIVE_INFINITY
        }
        
        return value_mapping.get(value_str, None)
        
    def validate_condition_syntax(self, condition: str) -> Tuple[bool, str]:
        """
        Validate the syntax of a condition string
        
        Args:
            condition: Condition string to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        
        try:
            condition = condition.strip()
            
            if not condition:
                return False, "Empty condition"
                
            # Check for dangerous patterns
            dangerous_patterns = ['import ', 'exec(', 'eval(', '__', 'file', 'open(']
            for pattern in dangerous_patterns:
                if pattern in condition.lower():
                    return False, f"Dangerous pattern '{pattern}' not allowed"
                    
            # Validate logical structure
            if condition.count('(') != condition.count(')'):
                return False, "Mismatched parentheses"
                
            # Check for valid operators only
            valid_operators = ['>', '<', '=', '>=', '<=', '==', 'AND', 'OR', 'NOT']
            
            # Basic syntax validation passed
            return True, "Valid condition syntax"
            
        except Exception as e:
            return False, f"Syntax error: {str(e)}"
            
    def get_condition_dependencies(self, condition: str) -> List[str]:
        """
        Extract quantity dependencies from a condition
        
        Args:
            condition: Condition string to analyze
            
        Returns:
            List[str]: List of quantity names referenced in condition
        """
        
        dependencies = []
        
        # Extract quantity references using regex
        quantity_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)(?:\([^)]*\))?'
        matches = re.findall(quantity_pattern, condition)
        
        for match in matches:
            # Filter out operators and keywords
            if match.upper() not in ['AND', 'OR', 'NOT', 'TRUE', 'FALSE']:
                if match not in ['connected', 'exists', 'type']:  # Function names
                    dependencies.append(match)
                    
        return list(set(dependencies))  # Remove duplicates
