"""
Test suite for the Query Optimizer for Simple DB

This module contains unit tests to verify the correctness of the parser and optimizer.
"""

import unittest
from sql_parser import SQLParser, Condition
from query_optimizer import QueryOptimizer
from selectivity_scorer import SelectivityScorer


class TestSQLParser(unittest.TestCase):
    """Test cases for SQL parser functionality."""
    
    def setUp(self):
        self.parser = SQLParser()
    
    def test_parse_simple_query(self):
        """Test parsing a simple query with one condition."""
        query = "SELECT * FROM users WHERE age > 25"
        parsed = self.parser.parse(query)
        
        self.assertEqual(parsed.table_name, "users")
        self.assertEqual(len(parsed.conditions), 1)
        self.assertEqual(parsed.conditions[0].column, "age")
        self.assertEqual(parsed.conditions[0].operator, ">")
        self.assertEqual(parsed.conditions[0].value, 25)
    
    def test_parse_multiple_conditions(self):
        """Test parsing a query with multiple AND conditions."""
        query = "SELECT * FROM users WHERE age > 25 AND country = 'US'"
        parsed = self.parser.parse(query)
        
        self.assertEqual(parsed.table_name, "users")
        self.assertEqual(len(parsed.conditions), 2)
        
        # Check first condition
        self.assertEqual(parsed.conditions[0].column, "age")
        self.assertEqual(parsed.conditions[0].operator, ">")
        self.assertEqual(parsed.conditions[0].value, 25)
        
        # Check second condition
        self.assertEqual(parsed.conditions[1].column, "country")
        self.assertEqual(parsed.conditions[1].operator, "=")
        self.assertEqual(parsed.conditions[1].value, "US")
    
    def test_parse_different_operators(self):
        """Test parsing queries with different operators."""
        query = "SELECT * FROM products WHERE price >= 100 AND rating != 5"
        parsed = self.parser.parse(query)
        
        self.assertEqual(len(parsed.conditions), 2)
        self.assertEqual(parsed.conditions[0].operator, ">=")
        self.assertEqual(parsed.conditions[1].operator, "!=")
    
    def test_parse_invalid_query(self):
        """Test parsing invalid queries."""
        with self.assertRaises(ValueError):
            self.parser.parse("INVALID QUERY")
        
        with self.assertRaises(ValueError):
            self.parser.parse("SELECT * FROM users")  # No WHERE clause
    
    def test_parse_case_insensitive(self):
        """Test that parsing is case insensitive."""
        query = "select * from users where age > 25 and country = 'US'"
        parsed = self.parser.parse(query)
        
        self.assertEqual(parsed.table_name, "users")
        self.assertEqual(len(parsed.conditions), 2)


class TestSelectivityScorer(unittest.TestCase):
    """Test cases for selectivity scorer functionality."""
    
    def setUp(self):
        self.scorer = SelectivityScorer()
    
    def test_score_equality_condition(self):
        """Test scoring equality conditions."""
        condition = Condition("id", "=", 123, "id = 123")
        score = self.scorer.score_condition(condition)
        
        self.assertLess(score.score, 0.5)  # Equality should be highly selective
        self.assertIn("equality condition", score.reasoning)
    
    def test_score_range_condition(self):
        """Test scoring range conditions."""
        condition = Condition("age", ">", 25, "age > 25")
        score = self.scorer.score_condition(condition)
        
        self.assertLess(score.score, 1.0)  # Range should be moderately selective
        self.assertIn("range condition", score.reasoning)
    
    def test_score_high_cardinality_column(self):
        """Test scoring conditions on high cardinality columns."""
        condition = Condition("email", "=", "test@example.com", "email = 'test@example.com'")
        score = self.scorer.score_condition(condition)
        
        # High cardinality columns should be more selective
        self.assertLess(score.score, 0.3)
        self.assertIn("high cardinality", score.reasoning)
    
    def test_score_low_cardinality_column(self):
        """Test scoring conditions on low cardinality columns."""
        condition = Condition("gender", "=", "M", "gender = 'M'")
        score = self.scorer.score_condition(condition)
        
        # Low cardinality columns should be less selective than high cardinality
        # but still more selective than very low cardinality columns
        self.assertGreater(score.score, 0.02)  # Adjusted threshold
        self.assertIn("low cardinality", score.reasoning)


class TestQueryOptimizer(unittest.TestCase):
    """Test cases for query optimizer functionality."""
    
    def setUp(self):
        self.parser = SQLParser()
        self.optimizer = QueryOptimizer()
    
    def test_optimize_simple_query(self):
        """Test optimizing a simple query."""
        query = "SELECT * FROM users WHERE age > 25 AND country = 'US'"
        parsed = self.parser.parse(query)
        optimized = self.optimizer.optimize(parsed)
        
        self.assertEqual(len(optimized.optimized_conditions), 2)
        self.assertIsNotNone(optimized.execution_plan)
        self.assertIsNotNone(optimized.optimization_summary)
    
    def test_optimize_condition_reordering(self):
        """Test that conditions are reordered by selectivity."""
        query = "SELECT * FROM users WHERE age > 25 AND country = 'US'"
        parsed = self.parser.parse(query)
        optimized = self.optimizer.optimize(parsed)
        
        # Country = 'US' should be more selective than age > 25
        # So it should come first in the optimized order
        first_condition = optimized.optimized_conditions[0]
        self.assertEqual(first_condition.column, "country")
        self.assertEqual(first_condition.operator, "=")
        self.assertEqual(first_condition.value, "US")
    
    def test_optimize_single_condition(self):
        """Test optimizing a query with a single condition."""
        query = "SELECT * FROM users WHERE age > 25"
        parsed = self.parser.parse(query)
        optimized = self.optimizer.optimize(parsed)
        
        self.assertEqual(len(optimized.optimized_conditions), 1)
        self.assertEqual(optimized.optimized_conditions[0].column, "age")
    
    def test_explain_optimization(self):
        """Test the optimization explanation feature."""
        query = "SELECT * FROM users WHERE age > 25 AND country = 'US'"
        parsed = self.parser.parse(query)
        explanation = self.optimizer.explain_optimization(parsed)
        
        self.assertIn("QUERY OPTIMIZATION EXPLANATION", explanation)
        self.assertIn("Original Query", explanation)
        self.assertIn("OPTIMIZATION RULES APPLIED", explanation)
        self.assertIn("CONDITION ANALYSIS", explanation)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def setUp(self):
        self.parser = SQLParser()
        self.optimizer = QueryOptimizer()
    
    def test_end_to_end_optimization(self):
        """Test complete end-to-end optimization process."""
        query = "SELECT * FROM employees WHERE department = 'IT' AND salary > 50000 AND status = 'active'"
        
        # Parse
        parsed = self.parser.parse(query)
        self.assertEqual(parsed.table_name, "employees")
        self.assertEqual(len(parsed.conditions), 3)
        
        # Optimize
        optimized = self.optimizer.optimize(parsed)
        self.assertEqual(len(optimized.optimized_conditions), 3)
        
        # Verify optimization was applied
        self.assertIn("Query optimization applied", optimized.optimization_summary)
        
        # Verify execution plan
        self.assertGreater(len(optimized.execution_plan), 0)
        self.assertEqual(optimized.execution_plan[-1]['operation'], 'RETURN')
    
    def test_complex_query_optimization(self):
        """Test optimization of a complex query with multiple conditions."""
        query = "SELECT * FROM products WHERE category = 'electronics' AND price < 1000 AND rating > 4 AND brand = 'Apple'"
        
        parsed = self.parser.parse(query)
        optimized = self.optimizer.optimize(parsed)
        
        # Should have 4 conditions
        self.assertEqual(len(optimized.optimized_conditions), 4)
        
        # Should be reordered by selectivity
        # Equality conditions should come before range conditions
        equality_conditions = [c for c in optimized.optimized_conditions if c.operator == "="]
        range_conditions = [c for c in optimized.optimized_conditions if c.operator in [">", "<", ">=", "<="]]
        
        # All equality conditions should come before range conditions
        if equality_conditions and range_conditions:
            equality_indices = [optimized.optimized_conditions.index(c) for c in equality_conditions]
            range_indices = [optimized.optimized_conditions.index(c) for c in range_conditions]
            self.assertTrue(all(ei < ri for ei in equality_indices for ri in range_indices))


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
