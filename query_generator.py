"""
Custom SQL Query Generator

A rule-based system to generate SQL queries from natural language descriptions
without external API dependencies.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class QueryTemplate:
    """Represents a SQL query template"""
    pattern: str
    template: str
    description: str

class SQLQueryGenerator:
    """Generate SQL queries from natural language descriptions"""
    
    def __init__(self):
        self.schema_info = {}
        self.query_templates = self._load_query_templates()
        
    def set_schema(self, schema_ddl: str):
        """Parse and store database schema information"""
        self.schema_info = self._parse_schema(schema_ddl)
    
    def generate_query(self, description: str) -> str:
        """Generate SQL query from natural language description"""
        description = description.lower().strip()
        
        # Try to match against known patterns
        for template in self.query_templates:
            match = re.search(template.pattern, description)
            if match:
                return self._apply_template(template, description, match)
        
        # Fallback: construct basic query
        return self._construct_basic_query(description)
    
    def _parse_schema(self, schema_ddl: str) -> Dict:
        """Parse schema DDL to extract table and column information"""
        schema_info = {'tables': {}, 'relationships': []}
        
        # Simple regex-based parsing for CREATE TABLE statements
        table_pattern = r'CREATE TABLE\s+(\w+)\s*\((.*?)\)'
        
        for match in re.finditer(table_pattern, schema_ddl, re.DOTALL | re.IGNORECASE):
            table_name = match.group(1).lower()
            columns_str = match.group(2)
            
            columns = []
            # Extract column definitions
            column_lines = [line.strip() for line in columns_str.split(',')]
            for line in column_lines:
                if line:
                    parts = line.split()
                    if parts:
                        column_name = parts[0].lower()
                        column_type = parts[1] if len(parts) > 1 else 'unknown'
                        is_primary = 'primary' in line.lower() and 'key' in line.lower()
                        columns.append({
                            'name': column_name,
                            'type': column_type,
                            'is_primary': is_primary
                        })
            
            schema_info['tables'][table_name] = {'columns': columns}
        
        return schema_info
    
    def _load_query_templates(self) -> List[QueryTemplate]:
        """Load predefined query templates"""
        templates = [
            # Top N queries
            QueryTemplate(
                pattern=r"(?:get|find|show|select).*?(?:top|first|\d+).*?(?:most|highest|best|largest).*?(\w+)",
                template="SELECT * FROM {table} ORDER BY {column} DESC LIMIT {limit};",
                description="Get top N records with highest values"
            ),
            
            # Count queries
            QueryTemplate(
                pattern=r"(?:count|how many).*?(\w+)",
                template="SELECT COUNT(*) FROM {table};",
                description="Count records in a table"
            ),
            
            # Average queries
            QueryTemplate(
                pattern=r"(?:average|avg|mean).*?(\w+)",
                template="SELECT AVG({column}) FROM {table};",
                description="Calculate average of a column"
            ),
            
            # Sum queries
            QueryTemplate(
                pattern=r"(?:sum|total).*?(\w+)",
                template="SELECT SUM({column}) FROM {table};",
                description="Calculate sum of a column"
            ),
            
            # Filter by value
            QueryTemplate(
                pattern=r"(?:find|get|show|select).*?(\w+).*?(?:where|with).*?(\w+).*?(?:is|equals?|=).*?['\"]?(\w+)['\"]?",
                template="SELECT * FROM {table} WHERE {column} = '{value}';",
                description="Filter records by specific value"
            ),
            
            # Join queries
            QueryTemplate(
                pattern=r"(?:join|combine|merge).*?(\w+).*?(?:and|with).*?(\w+)",
                template="SELECT * FROM {table1} t1 JOIN {table2} t2 ON t1.id = t2.{table1}_id;",
                description="Join two tables"
            ),
            
            # Group by queries
            QueryTemplate(
                pattern=r"(?:group by|grouped by|group).*?(\w+)",
                template="SELECT {column}, COUNT(*) FROM {table} GROUP BY {column};",
                description="Group records by a column"
            ),
            
            # Date range queries
            QueryTemplate(
                pattern=r"(?:between|from).*?(\d{4}-\d{2}-\d{2}).*?(?:to|and).*?(\d{4}-\d{2}-\d{2})",
                template="SELECT * FROM {table} WHERE {date_column} BETWEEN '{start_date}' AND '{end_date}';",
                description="Filter by date range"
            ),
            
            # Recent records
            QueryTemplate(
                pattern=r"(?:recent|latest|newest|last).*?(\w+)",
                template="SELECT * FROM {table} ORDER BY {date_column} DESC LIMIT 10;",
                description="Get recent records"
            ),
            
            # Minimum/Maximum queries
            QueryTemplate(
                pattern=r"(?:minimum|min|smallest|lowest).*?(\w+)",
                template="SELECT MIN({column}) FROM {table};",
                description="Find minimum value"
            ),
            
            QueryTemplate(
                pattern=r"(?:maximum|max|largest|highest).*?(\w+)",
                template="SELECT MAX({column}) FROM {table};",
                description="Find maximum value"
            ),
        ]
        
        return templates
    
    def _apply_template(self, template: QueryTemplate, description: str, match) -> str:
        """Apply a template to generate SQL query"""
        query = template.template
        
        # Extract table names and columns from the description and schema
        table_names = self._extract_table_names(description)
        column_names = self._extract_column_names(description)
        
        # Fill in template placeholders
        if '{table}' in query:
            table = table_names[0] if table_names else 'your_table'
            query = query.replace('{table}', table)
        
        if '{table1}' in query and '{table2}' in query:
            table1 = table_names[0] if len(table_names) > 0 else 'table1'
            table2 = table_names[1] if len(table_names) > 1 else 'table2'
            query = query.replace('{table1}', table1).replace('{table2}', table2)
        
        if '{column}' in query:
            column = column_names[0] if column_names else 'your_column'
            query = query.replace('{column}', column)
        
        if '{limit}' in query:
            # Extract number from description
            numbers = re.findall(r'\d+', description)
            limit = numbers[0] if numbers else '5'
            query = query.replace('{limit}', limit)
        
        if '{value}' in query:
            # Extract the value from the matched groups
            if len(match.groups()) >= 3:
                value = match.group(3)
                query = query.replace('{value}', value)
        
        if '{start_date}' in query and '{end_date}' in query:
            dates = re.findall(r'\d{4}-\d{2}-\d{2}', description)
            start_date = dates[0] if len(dates) > 0 else '2024-01-01'
            end_date = dates[1] if len(dates) > 1 else '2024-12-31'
            query = query.replace('{start_date}', start_date).replace('{end_date}', end_date)
        
        if '{date_column}' in query:
            # Look for date-related column names
            date_columns = ['created_at', 'updated_at', 'order_date', 'date', 'timestamp']
            date_column = next((col for col in date_columns if col in description), 'created_at')
            query = query.replace('{date_column}', date_column)
        
        return query
    
    def _construct_basic_query(self, description: str) -> str:
        """Construct a basic query when no template matches"""
        table_names = self._extract_table_names(description)
        column_names = self._extract_column_names(description)
        
        # Default to simple SELECT
        table = table_names[0] if table_names else 'your_table_name'
        
        if column_names:
            columns = ', '.join(column_names)
        else:
            columns = '*'
        
        query = f"SELECT {columns} FROM {table}"
        
        # Add basic WHERE clause if we can infer conditions
        conditions = self._extract_conditions(description)
        if conditions:
            query += f" WHERE {conditions[0]}"
        
        query += ";"
        
        return query
    
    def _extract_table_names(self, description: str) -> List[str]:
        """Extract likely table names from description"""
        table_names = []
        
        # Check against known schema tables
        for table_name in self.schema_info.get('tables', {}):
            if table_name in description:
                table_names.append(table_name)
        
        # Common table name patterns
        common_tables = ['users', 'orders', 'products', 'customers', 'items', 'sales', 
                        'employees', 'companies', 'accounts', 'transactions', 'payments']
        
        for table in common_tables:
            if table in description and table not in table_names:
                table_names.append(table)
        
        return table_names
    
    def _extract_column_names(self, description: str) -> List[str]:
        """Extract likely column names from description"""
        column_names = []
        
        # Check against known schema columns
        for table_info in self.schema_info.get('tables', {}).values():
            for column in table_info.get('columns', []):
                if column['name'] in description:
                    column_names.append(column['name'])
        
        # Common column patterns
        common_columns = {
            'name': ['name', 'username', 'first_name', 'last_name'],
            'email': ['email', 'email_address'],
            'amount': ['amount', 'price', 'cost', 'total', 'sum'],
            'date': ['date', 'created_at', 'updated_at', 'timestamp'],
            'id': ['id', 'user_id', 'order_id', 'product_id'],
            'status': ['status', 'state', 'condition'],
            'count': ['count', 'quantity', 'number']
        }
        
        for key, variants in common_columns.items():
            for variant in variants:
                if variant in description and variant not in column_names:
                    column_names.append(variant)
        
        return column_names
    
    def _extract_conditions(self, description: str) -> List[str]:
        """Extract WHERE conditions from description"""
        conditions = []
        
        # Look for equality conditions
        equality_pattern = r"(\w+)\s+(?:is|equals?|=)\s+['\"]?(\w+)['\"]?"
        matches = re.findall(equality_pattern, description)
        for column, value in matches:
            conditions.append(f"{column} = '{value}'")
        
        # Look for comparison conditions
        comparison_patterns = [
            (r"(\w+)\s+(?:greater than|>)\s+(\d+)", lambda m: f"{m[0]} > {m[1]}"),
            (r"(\w+)\s+(?:less than|<)\s+(\d+)", lambda m: f"{m[0]} < {m[1]}"),
            (r"(\w+)\s+(?:at least|>=)\s+(\d+)", lambda m: f"{m[0]} >= {m[1]}"),
        ]
        
        for pattern, formatter in comparison_patterns:
            matches = re.findall(pattern, description)
            for match in matches:
                conditions.append(formatter(match))
        
        return conditions

def suggest_query_improvements(query: str, schema_info: Dict) -> str:
    """Suggest improvements to a generated query"""
    suggestions = []
    query_lower = query.lower()
    
    if 'select *' in query_lower:
        suggestions.append("• Consider specifying column names instead of using SELECT *")
    
    if 'where' not in query_lower:
        suggestions.append("• Add WHERE conditions to filter results if needed")
    
    if 'limit' not in query_lower and 'order by' in query_lower:
        suggestions.append("• Consider adding LIMIT to restrict the number of results")
    
    if suggestions:
        return "Query generated successfully! Consider these improvements:\n\n" + "\n".join(suggestions)
    
    return "Query generated successfully and looks good!"