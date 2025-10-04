"""
SQL Parser for Simple Database Query Optimizer

This module provides functionality to parse SQL SELECT queries with WHERE clauses
and extract the components needed for query optimization.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Condition:
    """Represents a single condition in a WHERE clause."""
    column: str
    operator: str
    value: Any
    original_text: str


@dataclass
class ParsedQuery:
    """Represents a parsed SQL SELECT query."""
    table_name: str
    conditions: List[Condition]
    original_query: str


class SQLParser:
    """Parser for SQL SELECT queries with WHERE clauses."""
    
    def __init__(self):
        # Regex patterns for parsing SQL
        self.select_pattern = r'SELECT\s+\*\s+FROM\s+(\w+)'
        self.where_pattern = r'WHERE\s+(.+)'
        self.condition_pattern = r'(\w+)\s*([=<>!]+)\s*([\'"]?)([^\'"\s]+)\3'
        
    def parse(self, query: str) -> ParsedQuery:
        """
        Parse a SQL SELECT query and extract table name and conditions.
        
        Args:
            query: SQL query string (e.g., "SELECT * FROM users WHERE age > 25 AND country = 'US'")
            
        Returns:
            ParsedQuery object containing parsed components
            
        Raises:
            ValueError: If the query format is invalid
        """
        query = query.strip()
        
        # Extract table name
        table_match = re.search(self.select_pattern, query, re.IGNORECASE)
        if not table_match:
            raise ValueError("Invalid SELECT query format. Expected: SELECT * FROM table_name")
        
        table_name = table_match.group(1)
        
        # Extract WHERE clause
        where_match = re.search(self.where_pattern, query, re.IGNORECASE)
        if not where_match:
            raise ValueError("Query must contain a WHERE clause")
        
        where_clause = where_match.group(1)
        
        # Parse conditions
        conditions = self._parse_conditions(where_clause)
        
        return ParsedQuery(
            table_name=table_name,
            conditions=conditions,
            original_query=query
        )
    
    def _parse_conditions(self, where_clause: str) -> List[Condition]:
        """
        Parse individual conditions from the WHERE clause.
        
        Args:
            where_clause: The WHERE clause string
            
        Returns:
            List of Condition objects
        """
        conditions = []
        
        # Split by AND (case insensitive)
        condition_parts = re.split(r'\s+AND\s+', where_clause, flags=re.IGNORECASE)
        
        for part in condition_parts:
            part = part.strip()
            if not part:
                continue
                
            # Parse individual condition
            condition = self._parse_single_condition(part)
            if condition:
                conditions.append(condition)
        
        return conditions
    
    def _parse_single_condition(self, condition_str: str) -> Optional[Condition]:
        """
        Parse a single condition string.
        
        Args:
            condition_str: Single condition string (e.g., "age > 25")
            
        Returns:
            Condition object or None if parsing fails
        """
        match = re.match(self.condition_pattern, condition_str.strip())
        if not match:
            return None
        
        column, operator, quote, value = match.groups()
        
        # Clean up the value
        if quote:
            value = value  # Keep as string if quoted
        else:
            # Try to convert to appropriate type
            try:
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                value = str(value)  # Keep as string if conversion fails
        
        return Condition(
            column=column,
            operator=operator,
            value=value,
            original_text=condition_str.strip()
        )
