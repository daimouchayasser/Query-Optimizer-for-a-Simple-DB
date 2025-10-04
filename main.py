"""
Main application for the Query Optimizer for Simple DB

This module demonstrates the usage of the SQL parser and query optimizer.
"""

from sql_parser import SQLParser
from query_optimizer import QueryOptimizer


def main():
    """Main function to demonstrate the query optimizer."""
    print("Query Optimizer for Simple DB")
    print("=" * 40)
    print()
    
    # Initialize components
    parser = SQLParser()
    optimizer = QueryOptimizer()
    
    # Example queries to demonstrate optimization
    example_queries = [
        "SELECT * FROM users WHERE age > 25 AND country = 'US'",
        "SELECT * FROM products WHERE category = 'electronics' AND price < 1000 AND rating > 4",
        "SELECT * FROM employees WHERE department = 'IT' AND salary > 50000 AND status = 'active'",
        "SELECT * FROM orders WHERE country = 'US' AND age > 18 AND status = 'completed'",
        "SELECT * FROM customers WHERE gender = 'M' AND country = 'Canada' AND age > 30"
    ]
    
    for i, query in enumerate(example_queries, 1):
        print(f"EXAMPLE {i}")
        print("-" * 20)
        print(f"Query: {query}")
        print()
        
        try:
            # Parse the query
            parsed_query = parser.parse(query)
            print(f"Parsed successfully:")
            print(f"  Table: {parsed_query.table_name}")
            print(f"  Conditions: {len(parsed_query.conditions)}")
            for j, cond in enumerate(parsed_query.conditions, 1):
                print(f"    {j}. {cond.original_text}")
            print()
            
            # Optimize the query
            optimized_query = optimizer.optimize(parsed_query)
            
            # Show optimization results
            print("OPTIMIZATION RESULTS:")
            print(optimized_query.optimization_summary)
            print()
            
            # Show execution plan
            print("EXECUTION PLAN:")
            for step in optimized_query.execution_plan:
                print(f"  Step {step['step']}: {step['description']}")
            print()
            
            # Show detailed explanation
            print("DETAILED EXPLANATION:")
            explanation = optimizer.explain_optimization(parsed_query)
            print(explanation)
            print("\n" + "="*80 + "\n")
            
        except Exception as e:
            print(f"Error processing query: {e}")
            print("\n" + "="*80 + "\n")
            continue


def interactive_mode():
    """Interactive mode for testing custom queries."""
    print("Interactive Query Optimizer")
    print("=" * 30)
    print("Enter SQL queries to optimize (type 'quit' to exit)")
    print("Format: SELECT * FROM table WHERE condition1 AND condition2")
    print()
    
    parser = SQLParser()
    optimizer = QueryOptimizer()
    
    while True:
        try:
            query = input("Enter query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not query:
                continue
            
            # Parse and optimize
            parsed_query = parser.parse(query)
            optimized_query = optimizer.optimize(parsed_query)
            
            print("\nOPTIMIZATION RESULTS:")
            print(optimized_query.optimization_summary)
            print()
            
            print("EXECUTION PLAN:")
            for step in optimized_query.execution_plan:
                print(f"  Step {step['step']}: {step['description']}")
            print()
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Please check your query format and try again.")
            print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        main()
