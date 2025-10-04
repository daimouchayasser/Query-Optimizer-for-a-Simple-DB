#!/usr/bin/env python3
"""
Demo script for the Query Optimizer for Simple DB

This script demonstrates the query optimization functionality with a specific example.
"""

from sql_parser import SQLParser
from query_optimizer import QueryOptimizer


def demo_query_optimization():
    """Demonstrate query optimization with a specific example."""
    print("Query Optimizer for Simple DB - Demo")
    print("=" * 50)
    print()
    
    # Initialize components
    parser = SQLParser()
    optimizer = QueryOptimizer()
    
    # Demo query
    query = "SELECT * FROM users WHERE id = 123 AND age > 25 AND country = 'US'"
    
    print(f"Demo Query: {query}")
    print()
    
    try:
        # Parse the query
        print("1. PARSING QUERY")
        print("-" * 20)
        parsed_query = parser.parse(query)
        print(f"✓ Table: {parsed_query.table_name}")
        print(f"✓ Conditions: {len(parsed_query.conditions)}")
        for i, cond in enumerate(parsed_query.conditions, 1):
            print(f"  {i}. {cond.original_text}")
        print()
        
        # Optimize the query
        print("2. OPTIMIZING QUERY")
        print("-" * 20)
        optimized_query = optimizer.optimize(parsed_query)
        print("✓ Query optimization completed")
        print()
        
        # Show optimization results
        print("3. OPTIMIZATION RESULTS")
        print("-" * 25)
        print(optimized_query.optimization_summary)
        print()
        
        # Show execution plan
        print("4. EXECUTION PLAN")
        print("-" * 20)
        for step in optimized_query.execution_plan:
            print(f"  Step {step['step']}: {step['description']}")
        print()
        
        # Show detailed explanation
        print("5. DETAILED EXPLANATION")
        print("-" * 25)
        explanation = optimizer.explain_optimization(parsed_query)
        print(explanation)
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    demo_query_optimization()
