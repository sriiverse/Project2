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
        """Load comprehensive predefined query templates with better pattern matching"""
        templates = [
            # Top N queries - Enhanced patterns
            QueryTemplate(
                pattern=r"(?:get|find|show|select|list)\s+(?:the\s+)?(?:top|first|\d+)\s+(?:\d+\s+)?(?:most|highest|best|largest|biggest)\s+(?:\w+\s+)*?(?:by|in)\s+(\w+)",
                template="SELECT * FROM {table} ORDER BY {column} DESC LIMIT {limit};",
                description="Get top N records with highest values"
            ),
            
            # Enhanced specific top N with numbers
            QueryTemplate(
                pattern=r"(?:get|find|show|select)\s+(?:the\s+)?(\d+)\s+(?:top|best|highest|largest)\s+(\w+)\s+(?:by|with|having)\s+(?:the\s+)?(?:most|highest|largest)\s+(\w+)",
                template="SELECT * FROM {table} ORDER BY {column} DESC LIMIT {limit};",
                description="Get specific number of top records"
            ),
            
            # Count queries - Multiple variations
            QueryTemplate(
                pattern=r"(?:count|how many|number of|total)\s+(?:\w+\s+)*?(\w+)(?:\s+are\s+there|\s+exist|\s+do\s+we\s+have)?",
                template="SELECT COUNT(*) FROM {table};",
                description="Count records in a table"
            ),
            
            # Conditional count
            QueryTemplate(
                pattern=r"(?:count|how many)\s+(\w+)\s+(?:where|with|having)\s+(\w+)\s+(?:is|=|equals?)\s+['\"]?(\w+)['\"]?",
                template="SELECT COUNT(*) FROM {table} WHERE {column} = '{value}';",
                description="Count records with condition"
            ),
            
            # Average queries - Enhanced
            QueryTemplate(
                pattern=r"(?:average|avg|mean)\s+(?:\w+\s+)*?(\w+)\s+(?:of|for|in)\s+(\w+)",
                template="SELECT AVG({column}) FROM {table};",
                description="Calculate average of a column"
            ),
            
            # Sum queries - Enhanced
            QueryTemplate(
                pattern=r"(?:sum|total|add up|calculate)\s+(?:all\s+)?(?:the\s+)?(\w+)\s+(?:of|for|in|from)\s+(\w+)",
                template="SELECT SUM({column}) FROM {table};",
                description="Calculate sum of a column"
            ),
            
            # Filter by value - Multiple patterns
            QueryTemplate(
                pattern=r"(?:find|get|show|select|list)\s+(?:all\s+)?(\w+)\s+(?:where|with|having)\s+(\w+)\s+(?:is|equals?|=)\s+['\"]?(\w+)['\"]?",
                template="SELECT * FROM {table} WHERE {column} = '{value}';",
                description="Filter records by specific value"
            ),
            
            # Enhanced filter with multiple conditions
            QueryTemplate(
                pattern=r"(?:find|get|show)\s+(\w+)\s+where\s+(\w+)\s+(?:is|=)\s+['\"]?(\w+)['\"]?\s+and\s+(\w+)\s+(?:is|=)\s+['\"]?(\w+)['\"]?",
                template="SELECT * FROM {table} WHERE {column} = '{value}' AND {column2} = '{value2}';",
                description="Filter with multiple conditions"
            ),
            
            # Join queries - Enhanced patterns
            QueryTemplate(
                pattern=r"(?:join|combine|merge|connect)\s+(\w+)\s+(?:and|with|to)\s+(\w+)(?:\s+(?:on|using|by)\s+(\w+))?",
                template="SELECT * FROM {table1} t1 JOIN {table2} t2 ON t1.{join_column} = t2.{join_column};",
                description="Join two tables"
            ),
            
            # Group by queries - Enhanced
            QueryTemplate(
                pattern=r"(?:group|group by|grouped by)\s+(\w+)\s+(?:by|using)\s+(\w+)",
                template="SELECT {column}, COUNT(*) FROM {table} GROUP BY {column};",
                description="Group records by a column"
            ),
            
            # Aggregate with grouping
            QueryTemplate(
                pattern=r"(?:sum|total|count|average)\s+(?:of\s+)?(\w+)\s+(?:by|for each|grouped by)\s+(\w+)\s+(?:in|from)\s+(\w+)",
                template="SELECT {group_column}, {aggregate}({column}) FROM {table} GROUP BY {group_column};",
                description="Aggregate data with grouping"
            ),
            
            # Date range queries - Enhanced
            QueryTemplate(
                pattern=r"(?:between|from)\s+(\d{4}-\d{2}-\d{2})\s+(?:to|and|until)\s+(\d{4}-\d{2}-\d{2})",
                template="SELECT * FROM {table} WHERE {date_column} BETWEEN '{start_date}' AND '{end_date}';",
                description="Filter by date range"
            ),
            
            # Recent records - Multiple patterns
            QueryTemplate(
                pattern=r"(?:recent|latest|newest|last|most recent)\s+(?:\d+\s+)?(\w+)",
                template="SELECT * FROM {table} ORDER BY {date_column} DESC LIMIT {limit};",
                description="Get recent records"
            ),
            
            # Time-based queries
            QueryTemplate(
                pattern=r"(?:today's|yesterday's|this week's|this month's)\s+(\w+)",
                template="SELECT * FROM {table} WHERE DATE({date_column}) = CURRENT_DATE;",
                description="Get records from specific time period"
            ),
            
            # Minimum/Maximum queries - Enhanced
            QueryTemplate(
                pattern=r"(?:minimum|min|smallest|lowest)\s+(\w+)\s+(?:in|from|of)\s+(\w+)",
                template="SELECT MIN({column}) FROM {table};",
                description="Find minimum value"
            ),
            
            QueryTemplate(
                pattern=r"(?:maximum|max|largest|highest|biggest)\s+(\w+)\s+(?:in|from|of)\s+(\w+)",
                template="SELECT MAX({column}) FROM {table};",
                description="Find maximum value"
            ),
            
            # Existence queries
            QueryTemplate(
                pattern=r"(?:does|do|is there|are there)\s+(?:any\s+)?(\w+)\s+(?:where|with)\s+(\w+)\s+(?:is|=)\s+['\"]?(\w+)['\"]?",
                template="SELECT EXISTS(SELECT 1 FROM {table} WHERE {column} = '{value}');",
                description="Check if records exist"
            ),
            
            # Distinct queries
            QueryTemplate(
                pattern=r"(?:unique|distinct|different)\s+(\w+)\s+(?:in|from)\s+(\w+)",
                template="SELECT DISTINCT {column} FROM {table};",
                description="Get unique values"
            ),
        ]
        
        return templates
    
    def _apply_template(self, template: QueryTemplate, description: str, match) -> str:
        """Apply a template to generate SQL query with enhanced placeholder handling"""
        query = template.template
        
        # Extract table names and columns from the description and schema
        table_names = self._extract_table_names(description)
        column_names = self._extract_column_names(description)
        
        # Enhanced placeholder replacement with fallbacks
        replacements = self._build_replacement_dict(description, table_names, column_names, match)
        
        # Apply all replacements
        for placeholder, value in replacements.items():
            query = query.replace(placeholder, value)
        
        # Final validation and cleanup
        query = self._validate_and_clean_query(query, description)
        
        return query
    
    def _build_replacement_dict(self, description: str, table_names: List[str], column_names: List[str], match) -> Dict[str, str]:
        """Build a comprehensive dictionary of placeholder replacements"""
        replacements = {}
        
        # Table replacements
        if table_names:
            replacements['{table}'] = table_names[0]
            if len(table_names) > 1:
                replacements['{table1}'] = table_names[0]
                replacements['{table2}'] = table_names[1]
            else:
                replacements['{table1}'] = table_names[0]
                replacements['{table2}'] = self._guess_related_table(table_names[0])
        else:
            # Smart table guessing based on common patterns
            guessed_table = self._guess_table_from_description(description)
            replacements['{table}'] = guessed_table
            replacements['{table1}'] = guessed_table
            replacements['{table2}'] = self._guess_related_table(guessed_table)
        
        # Column replacements
        if column_names:
            replacements['{column}'] = column_names[0]
            if len(column_names) > 1:
                replacements['{column2}'] = column_names[1]
        else:
            # Smart column guessing
            guessed_column = self._guess_column_from_description(description)
            replacements['{column}'] = guessed_column
        
        # Limit/Number replacements
        numbers = re.findall(r'\d+', description)
        limit_value = numbers[0] if numbers else self._guess_reasonable_limit(description)
        replacements['{limit}'] = limit_value
        
        # Value replacements from match groups
        if match and match.groups():
            groups = match.groups()
            if len(groups) >= 1:
                replacements['{value}'] = groups[-1] if groups[-1] else 'example_value'
            if len(groups) >= 2:
                replacements['{value2}'] = groups[-1] if len(groups) > 2 else groups[-1]
        
        # Date replacements
        dates = re.findall(r'\d{4}-\d{2}-\d{2}', description)
        if dates:
            replacements['{start_date}'] = dates[0]
            replacements['{end_date}'] = dates[1] if len(dates) > 1 else dates[0]
        else:
            replacements['{start_date}'] = '2024-01-01'
            replacements['{end_date}'] = '2024-12-31'
        
        # Date column replacements
        date_column = self._find_date_column(description, table_names)
        replacements['{date_column}'] = date_column
        
        # Join column replacements
        join_column = self._guess_join_column(table_names)
        replacements['{join_column}'] = join_column
        
        # Aggregate function replacements
        aggregate_func = self._determine_aggregate_function(description)
        replacements['{aggregate}'] = aggregate_func
        
        # Group column
        group_column = column_names[1] if len(column_names) > 1 else column_names[0] if column_names else 'group_column'
        replacements['{group_column}'] = group_column
        
        return replacements
    
    def _guess_table_from_description(self, description: str) -> str:
        """Intelligently guess table name from description"""
        # Check for plurals that might indicate table names
        plural_indicators = ['users', 'orders', 'products', 'customers', 'items', 'sales', 
                           'employees', 'companies', 'accounts', 'transactions', 'payments',
                           'invoices', 'contracts', 'projects', 'tasks', 'reviews', 'posts']
        
        for indicator in plural_indicators:
            if indicator in description.lower():
                return indicator
        
        # If no specific table found, use a generic name based on context
        if any(word in description.lower() for word in ['user', 'person', 'people', 'customer']):
            return 'users'
        elif any(word in description.lower() for word in ['order', 'purchase', 'buy']):
            return 'orders'
        elif any(word in description.lower() for word in ['product', 'item', 'good']):
            return 'products'
        else:
            return 'main_table'
    
    def _guess_related_table(self, table1: str) -> str:
        """Guess a related table based on the first table"""
        table_relationships = {
            'users': 'orders',
            'customers': 'orders',
            'orders': 'products',
            'products': 'categories',
            'employees': 'departments',
            'companies': 'employees'
        }
        return table_relationships.get(table1, 'related_table')
    
    def _guess_column_from_description(self, description: str) -> str:
        """Intelligently guess column name from description context"""
        # Amount/Money related
        if any(word in description.lower() for word in ['money', 'spent', 'cost', 'price', 'amount', 'total', 'sum']):
            return 'amount'
        
        # Name related
        elif any(word in description.lower() for word in ['name', 'called', 'named']):
            return 'name'
        
        # Date related
        elif any(word in description.lower() for word in ['date', 'time', 'when', 'created', 'updated']):
            return 'created_at'
        
        # Status related
        elif any(word in description.lower() for word in ['status', 'state', 'condition']):
            return 'status'
        
        # Count related
        elif any(word in description.lower() for word in ['count', 'number', 'quantity']):
            return 'quantity'
        
        else:
            return 'id'  # Safe default
    
    def _guess_reasonable_limit(self, description: str) -> str:
        """Determine reasonable limit based on context"""
        if any(word in description.lower() for word in ['top', 'best', 'highest']):
            return '10'
        elif any(word in description.lower() for word in ['few', 'some']):
            return '5'
        elif any(word in description.lower() for word in ['many', 'all']):
            return '100'
        else:
            return '10'
    
    def _find_date_column(self, description: str, table_names: List[str]) -> str:
        """Find appropriate date column based on schema and context"""
        # Check schema for actual date columns
        for table_name in table_names:
            if table_name in self.schema_info.get('tables', {}):
                table_info = self.schema_info['tables'][table_name]
                for column in table_info.get('columns', []):
                    column_name = column['name']
                    if any(date_indicator in column_name.lower() for date_indicator in 
                          ['date', 'time', 'created', 'updated', 'timestamp']):
                        return column_name
        
        # Fallback based on context
        if 'created' in description.lower():
            return 'created_at'
        elif 'updated' in description.lower():
            return 'updated_at'
        elif 'order' in description.lower():
            return 'order_date'
        else:
            return 'created_at'
    
    def _guess_join_column(self, table_names: List[str]) -> str:
        """Guess appropriate join column based on table names"""
        if len(table_names) >= 2:
            # Common join patterns
            table1, table2 = table_names[0], table_names[1]
            
            # If first table is users/customers, likely join on user_id
            if table1 in ['users', 'customers']:
                return 'user_id'
            elif table2 in ['users', 'customers']:
                return 'user_id'
            
            # Default to id
            return 'id'
        
        return 'id'
    
    def _determine_aggregate_function(self, description: str) -> str:
        """Determine appropriate aggregate function from description"""
        if any(word in description.lower() for word in ['sum', 'total', 'add']):
            return 'SUM'
        elif any(word in description.lower() for word in ['count', 'number', 'how many']):
            return 'COUNT'
        elif any(word in description.lower() for word in ['average', 'avg', 'mean']):
            return 'AVG'
        elif any(word in description.lower() for word in ['max', 'maximum', 'highest', 'largest']):
            return 'MAX'
        elif any(word in description.lower() for word in ['min', 'minimum', 'lowest', 'smallest']):
            return 'MIN'
        else:
            return 'COUNT'
    
    def _validate_and_clean_query(self, query: str, description: str) -> str:
        """Validate and clean the generated query"""
        # Remove any remaining unreplaced placeholders
        placeholder_pattern = r'\{\w+\}'
        remaining_placeholders = re.findall(placeholder_pattern, query)
        
        for placeholder in remaining_placeholders:
            # Replace with sensible defaults
            default_value = self._get_default_for_placeholder(placeholder)
            query = query.replace(placeholder, default_value)
        
        # Ensure query ends with semicolon
        if not query.strip().endswith(';'):
            query = query.strip() + ';'
        
        return query
    
    def _get_default_for_placeholder(self, placeholder: str) -> str:
        """Get default value for any remaining placeholder"""
        defaults = {
            '{table}': 'your_table',
            '{table1}': 'table1',
            '{table2}': 'table2',
            '{column}': 'your_column',
            '{column2}': 'column2',
            '{value}': 'your_value',
            '{value2}': 'value2',
            '{limit}': '10',
            '{date_column}': 'created_at',
            '{join_column}': 'id',
            '{aggregate}': 'COUNT',
            '{group_column}': 'group_column',
            '{start_date}': '2024-01-01',
            '{end_date}': '2024-12-31'
        }
        return defaults.get(placeholder, 'unknown')
    
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
