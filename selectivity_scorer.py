"""
Selectivity Scorer for Query Optimization

This module provides functionality to score the selectivity of WHERE conditions
to help optimize query execution order.
"""

from typing import Dict, Any
from dataclasses import dataclass
from sql_parser import Condition


@dataclass
class SelectivityScore:
    """Represents the selectivity score for a condition."""
    condition: Condition
    score: float
    reasoning: str


class SelectivityScorer:
    """Scores the selectivity of WHERE conditions for query optimization."""
    
    def __init__(self):
        # Predefined selectivity scores for different types of conditions
        # Lower scores indicate higher selectivity (more selective)
        self.selectivity_rules = {
            # Equality conditions (most selective)
            '=': 0.1,
            '==': 0.1,
            
            # Range conditions (moderately selective)
            '>': 0.3,
            '>=': 0.3,
            '<': 0.3,
            '<=': 0.3,
            
            # Inequality conditions (less selective)
            '!=': 0.5,
            '<>': 0.5,
            
            # Pattern matching (least selective)
            'LIKE': 0.7,
            'ILIKE': 0.7,
        }
        
        # Column-specific selectivity modifiers
        # These represent domain knowledge about data distribution
        self.column_modifiers = {
            # High cardinality columns (more selective)
            'id': 0.1,
            'email': 0.1,
            'username': 0.1,
            'ssn': 0.1,
            'phone': 0.1,
            
            # Medium cardinality columns
            'country': 0.2,
            'state': 0.2,
            'city': 0.2,
            'department': 0.2,
            'category': 0.2,
            
            # Low cardinality columns (less selective)
            'gender': 0.4,
            'status': 0.4,
            'type': 0.4,
            'level': 0.4,
            
            # Very low cardinality columns (least selective)
            'age': 0.6,
            'salary': 0.6,
            'score': 0.6,
            'rating': 0.6,
        }
        
        # Value-specific selectivity modifiers
        # Common values that are less selective
        self.value_modifiers = {
            # Common countries
            'US': 0.3,
            'USA': 0.3,
            'United States': 0.3,
            
            # Common status values
            'active': 0.3,
            'enabled': 0.3,
            'true': 0.3,
            '1': 0.3,
            
            # Common age ranges
            '18': 0.4,
            '21': 0.4,
            '25': 0.4,
            '30': 0.4,
            '35': 0.4,
            '40': 0.4,
            '50': 0.4,
        }
    
    def score_condition(self, condition: Condition) -> SelectivityScore:
        """
        Calculate the selectivity score for a given condition.
        
        Args:
            condition: The condition to score
            
        Returns:
            SelectivityScore object with score and reasoning
        """
        # Start with base operator selectivity
        base_score = self.selectivity_rules.get(condition.operator, 0.5)
        
        # Apply column modifier
        column_modifier = self.column_modifiers.get(condition.column.lower(), 0.3)
        
        # Apply value modifier
        value_key = str(condition.value).lower()
        value_modifier = self.value_modifiers.get(value_key, 1.0)
        
        # Calculate final score (lower is more selective)
        final_score = base_score * column_modifier * value_modifier
        
        # Generate reasoning
        reasoning = self._generate_reasoning(condition, base_score, column_modifier, value_modifier)
        
        return SelectivityScore(
            condition=condition,
            score=final_score,
            reasoning=reasoning
        )
    
    def _generate_reasoning(self, condition: Condition, base_score: float, 
                           column_modifier: float, value_modifier: float) -> str:
        """Generate human-readable reasoning for the selectivity score."""
        reasoning_parts = []
        
        # Operator reasoning
        if condition.operator in ['=', '==']:
            reasoning_parts.append("equality condition (highly selective)")
        elif condition.operator in ['>', '>=', '<', '<=']:
            reasoning_parts.append("range condition (moderately selective)")
        elif condition.operator in ['!=', '<>']:
            reasoning_parts.append("inequality condition (less selective)")
        else:
            reasoning_parts.append(f"operator '{condition.operator}' (moderate selectivity)")
        
        # Column reasoning
        if column_modifier <= 0.1:
            reasoning_parts.append(f"column '{condition.column}' has high cardinality")
        elif column_modifier <= 0.2:
            reasoning_parts.append(f"column '{condition.column}' has medium cardinality")
        else:
            reasoning_parts.append(f"column '{condition.column}' has low cardinality")
        
        # Value reasoning
        if value_modifier < 1.0:
            reasoning_parts.append(f"value '{condition.value}' is common (less selective)")
        elif value_modifier > 1.0:
            reasoning_parts.append(f"value '{condition.value}' is uncommon (more selective)")
        
        return "; ".join(reasoning_parts)
    
    def get_optimization_recommendation(self, conditions: list[Condition]) -> str:
        """
        Get a recommendation for the optimal order of conditions.
        
        Args:
            conditions: List of conditions to analyze
            
        Returns:
            String recommendation
        """
        if not conditions:
            return "No conditions to optimize"
        
        if len(conditions) == 1:
            return "Only one condition - no optimization needed"
        
        # Score all conditions
        scored_conditions = [self.score_condition(cond) for cond in conditions]
        
        # Sort by selectivity (lower score = more selective)
        sorted_conditions = sorted(scored_conditions, key=lambda x: x.score)
        
        # Generate recommendation
        recommendation = "Recommended execution order (most selective first):\n"
        for i, scored_cond in enumerate(sorted_conditions, 1):
            recommendation += f"{i}. {scored_cond.condition.original_text} "
            recommendation += f"(score: {scored_cond.score:.3f})\n"
            recommendation += f"   Reasoning: {scored_cond.reasoning}\n"
        
        return recommendation
