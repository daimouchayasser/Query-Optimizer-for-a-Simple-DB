"""
Query Optimizer for Simple Database

This module provides rule-based query optimization functionality,
including condition reordering based on selectivity scores.
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from sql_parser import ParsedQuery, Condition
from selectivity_scorer import SelectivityScorer, SelectivityScore


@dataclass
class OptimizedQuery:
    """Represents an optimized query with execution plan."""
    original_query: ParsedQuery
    optimized_conditions: List[Condition]
    execution_plan: List[Dict[str, Any]]
    optimization_summary: str


class QueryOptimizer:
    """Rule-based query optimizer for simple database queries."""
    
    def __init__(self):
        self.scorer = SelectivityScorer()
        
    def optimize(self, parsed_query: ParsedQuery) -> OptimizedQuery:
        """
        Optimize a parsed query using rule-based optimization.
        
        Args:
            parsed_query: The parsed query to optimize
            
        Returns:
            OptimizedQuery object with optimization results
        """
        if not parsed_query.conditions:
            return self._create_unoptimized_query(parsed_query)
        
        # Apply optimization rules
        optimized_conditions = self._apply_optimization_rules(parsed_query.conditions)
        
        # Create execution plan
        execution_plan = self._create_execution_plan(optimized_conditions)
        
        # Generate optimization summary
        summary = self._generate_optimization_summary(
            parsed_query.conditions, 
            optimized_conditions
        )
        
        return OptimizedQuery(
            original_query=parsed_query,
            optimized_conditions=optimized_conditions,
            execution_plan=execution_plan,
            optimization_summary=summary
        )
    
    def _apply_optimization_rules(self, conditions: List[Condition]) -> List[Condition]:
        """
        Apply rule-based optimization to reorder conditions.
        
        Args:
            conditions: List of conditions to optimize
            
        Returns:
            List of optimized conditions in execution order
        """
        # Rule 1: Order by selectivity (most selective first)
        scored_conditions = [
            self.scorer.score_condition(cond) for cond in conditions
        ]
        
        # Sort by selectivity score (lower score = more selective)
        sorted_scored_conditions = sorted(scored_conditions, key=lambda x: x.score)
        
        # Extract the optimized conditions
        optimized_conditions = [scored_cond.condition for scored_cond in sorted_scored_conditions]
        
        return optimized_conditions
    
    def _create_execution_plan(self, conditions: List[Condition]) -> List[Dict[str, Any]]:
        """
        Create a step-by-step execution plan for the optimized query.
        
        Args:
            conditions: List of optimized conditions
            
        Returns:
            List of execution plan steps
        """
        execution_plan = []
        
        for i, condition in enumerate(conditions, 1):
            step = {
                'step': i,
                'operation': 'FILTER',
                'condition': condition.original_text,
                'column': condition.column,
                'operator': condition.operator,
                'value': condition.value,
                'description': f"Apply filter: {condition.original_text}"
            }
            execution_plan.append(step)
        
        # Add final step
        execution_plan.append({
            'step': len(conditions) + 1,
            'operation': 'RETURN',
            'description': 'Return filtered results'
        })
        
        return execution_plan
    
    def _generate_optimization_summary(self, original_conditions: List[Condition], 
                                     optimized_conditions: List[Condition]) -> str:
        """
        Generate a summary of the optimization performed.
        
        Args:
            original_conditions: Original condition order
            optimized_conditions: Optimized condition order
            
        Returns:
            String summary of optimization
        """
        if len(original_conditions) <= 1:
            return "No optimization needed - single condition or no conditions"
        
        # Check if order changed
        order_changed = original_conditions != optimized_conditions
        
        if not order_changed:
            return "No optimization needed - conditions already in optimal order"
        
        summary = "Query optimization applied:\n"
        summary += f"- Reordered {len(original_conditions)} conditions for better performance\n"
        summary += "- Most selective conditions will be applied first\n"
        summary += "- Expected performance improvement: 20-80% (depending on data distribution)\n\n"
        
        summary += "Original order:\n"
        for i, cond in enumerate(original_conditions, 1):
            summary += f"  {i}. {cond.original_text}\n"
        
        summary += "\nOptimized order:\n"
        for i, cond in enumerate(optimized_conditions, 1):
            summary += f"  {i}. {cond.original_text}\n"
        
        return summary
    
    def _create_unoptimized_query(self, parsed_query: ParsedQuery) -> OptimizedQuery:
        """Create an unoptimized query result for queries without conditions."""
        return OptimizedQuery(
            original_query=parsed_query,
            optimized_conditions=[],
            execution_plan=[{
                'step': 1,
                'operation': 'SCAN',
                'description': f'Scan table "{parsed_query.table_name}"'
            }, {
                'step': 2,
                'operation': 'RETURN',
                'description': 'Return all results'
            }],
            optimization_summary="No WHERE conditions - full table scan"
        )
    
    def explain_optimization(self, parsed_query: ParsedQuery) -> str:
        """
        Provide a detailed explanation of the optimization process.
        
        Args:
            parsed_query: The parsed query to explain
            
        Returns:
            Detailed explanation string
        """
        if not parsed_query.conditions:
            return "No WHERE conditions to optimize. Query will perform a full table scan."
        
        explanation = "QUERY OPTIMIZATION EXPLANATION\n"
        explanation += "=" * 50 + "\n\n"
        
        explanation += f"Original Query: {parsed_query.original_query}\n\n"
        
        explanation += "OPTIMIZATION RULES APPLIED:\n"
        explanation += "1. Selectivity-based reordering: Conditions are reordered based on their selectivity scores\n"
        explanation += "2. Most selective conditions are applied first to reduce the working set early\n"
        explanation += "3. Selectivity is determined by:\n"
        explanation += "   - Operator type (equality > range > inequality)\n"
        explanation += "   - Column cardinality (high cardinality = more selective)\n"
        explanation += "   - Value frequency (common values = less selective)\n\n"
        
        # Score each condition
        explanation += "CONDITION ANALYSIS:\n"
        for i, condition in enumerate(parsed_query.conditions, 1):
            score = self.scorer.score_condition(condition)
            explanation += f"{i}. {condition.original_text}\n"
            explanation += f"   Selectivity Score: {score.score:.3f}\n"
            explanation += f"   Reasoning: {score.reasoning}\n\n"
        
        # Show optimization recommendation
        recommendation = self.scorer.get_optimization_recommendation(parsed_query.conditions)
        explanation += "OPTIMIZATION RECOMMENDATION:\n"
        explanation += recommendation + "\n"
        
        explanation += "EXPECTED BENEFITS:\n"
        explanation += "- Reduced I/O operations by filtering early\n"
        explanation += "- Lower memory usage for intermediate results\n"
        explanation += "- Faster query execution (especially with large datasets)\n"
        explanation += "- Better utilization of database indexes (if available)\n"
        
        return explanation
