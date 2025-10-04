# Query Optimizer for Simple DB

A Python-based SQL parser and query optimizer that demonstrates rule-based optimization techniques for simple database queries. The system parses `SELECT * FROM table WHERE condition1 AND condition2` queries and reorders conditions based on selectivity scores to improve query performance.

## Features

- **SQL Parser**: Parses SELECT queries with WHERE clauses containing multiple AND conditions
- **Selectivity Scoring**: Assigns selectivity scores to conditions based on operator type, column cardinality, and value frequency
- **Rule-based Optimization**: Reorders conditions to apply the most selective filters first
- **Execution Planning**: Generates step-by-step execution plans for optimized queries
- **Detailed Explanations**: Provides comprehensive explanations of optimization decisions

## Architecture

The system consists of four main components:

### 1. SQL Parser (`sql_parser.py`)
- Parses SQL SELECT queries with WHERE clauses
- Extracts table names and individual conditions
- Handles various operators (=, >, <, >=, <=, !=, <>, LIKE)
- Supports case-insensitive parsing

### 2. Selectivity Scorer (`selectivity_scorer.py`)
- Calculates selectivity scores for WHERE conditions
- Uses rule-based scoring based on:
  - **Operator type**: Equality (=) > Range (>, <) > Inequality (!=)
  - **Column cardinality**: High cardinality columns (id, email) are more selective
  - **Value frequency**: Common values (US, active) are less selective

### 3. Query Optimizer (`query_optimizer.py`)
- Applies rule-based optimization to reorder conditions
- Creates execution plans for optimized queries
- Generates optimization summaries and explanations

### 4. Main Application (`main.py`)
- Demonstrates the system with example queries
- Provides interactive mode for testing custom queries
- Shows optimization results and execution plans

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Query-Optimizer-for-a-Simple-DB
```

2. Ensure Python 3.7+ is installed

3. No additional dependencies required - uses only Python standard library

## Usage

### Running Examples

```bash
python main.py
```

This will run through several example queries and show the optimization process.

### Interactive Mode

```bash
python main.py --interactive
```

This allows you to enter custom SQL queries and see how they are optimized.

### Running Tests

```bash
python test_optimizer.py
```

## Example Usage

```python
from sql_parser import SQLParser
from query_optimizer import QueryOptimizer

# Initialize components
parser = SQLParser()
optimizer = QueryOptimizer()

# Parse a query
query = "SELECT * FROM users WHERE age > 25 AND country = 'US'"
parsed_query = parser.parse(query)

# Optimize the query
optimized_query = optimizer.optimize(parsed_query)

# View results
print("Optimized conditions:", optimized_query.optimized_conditions)
print("Execution plan:", optimized_query.execution_plan)
print("Summary:", optimized_query.optimization_summary)
```

## Optimization Rules

The system applies the following optimization rules:

### 1. Selectivity-Based Reordering
Conditions are reordered based on their selectivity scores, with the most selective conditions applied first.

### 2. Operator Selectivity
- **Equality operators** (=, ==): Most selective (score: 0.1)
- **Range operators** (>, <, >=, <=): Moderately selective (score: 0.3)
- **Inequality operators** (!=, <>): Less selective (score: 0.5)
- **Pattern matching** (LIKE, ILIKE): Least selective (score: 0.7)

### 3. Column Cardinality
- **High cardinality** (id, email, username): More selective (modifier: 0.1)
- **Medium cardinality** (country, state, department): Moderately selective (modifier: 0.2)
- **Low cardinality** (gender, status, type): Less selective (modifier: 0.4)
- **Very low cardinality** (age, salary, score): Least selective (modifier: 0.6)

### 4. Value Frequency
Common values like 'US', 'active', 'true' receive higher scores (less selective), while uncommon values receive lower scores (more selective).

## Example Optimizations

### Example 1: Basic Reordering
**Original Query:**
```sql
SELECT * FROM users WHERE age > 25 AND country = 'US'
```

**Optimized Query:**
```sql
-- country = 'US' is applied first (more selective)
-- age > 25 is applied second (less selective)
```

**Reasoning:** Equality conditions on medium-cardinality columns are more selective than range conditions on low-cardinality columns.

### Example 2: Complex Query
**Original Query:**
```sql
SELECT * FROM products WHERE category = 'electronics' AND price < 1000 AND rating > 4
```

**Optimized Query:**
```sql
-- category = 'electronics' (equality, medium cardinality)
-- price < 1000 (range, low cardinality)  
-- rating > 4 (range, low cardinality)
```

## Performance Benefits

The optimization provides several performance benefits:

1. **Reduced I/O Operations**: Most selective conditions filter data early, reducing the amount of data processed in subsequent operations.

2. **Lower Memory Usage**: Smaller intermediate result sets require less memory.

3. **Faster Execution**: Especially beneficial with large datasets where the difference between scanning 1% vs 50% of rows is significant.

4. **Better Index Utilization**: When database indexes are available, more selective conditions can better utilize them.

## Limitations

- **Simple Query Format**: Only supports `SELECT * FROM table WHERE condition1 AND condition2` format
- **Rule-based Only**: Uses predefined rules rather than cost-based optimization
- **No Statistics**: Doesn't use actual database statistics for selectivity estimation
- **Limited Operators**: Supports basic comparison operators but not complex expressions

## Future Enhancements

- Support for OR conditions and complex WHERE clauses
- Cost-based optimization using actual database statistics
- Support for JOIN operations
- Integration with actual database systems
- Machine learning-based selectivity estimation

## Testing

The project includes comprehensive unit tests covering:
- SQL parsing functionality
- Selectivity scoring accuracy
- Query optimization correctness
- Integration testing

Run tests with:
```bash
python test_optimizer.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is open source and available under the MIT License.
