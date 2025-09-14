"""
Custom SQL Query Optimizer Engine

A rule-based SQL optimization system that analyzes SQL queries and provides
performance improvement suggestions without external API dependencies.
"""

import re
import sqlparse
from sqlparse import sql, tokens as T
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class OptimizationLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class OptimizationSuggestion:
    """Represents a single optimization suggestion"""
    level: OptimizationLevel
    category: str
    issue: str
    suggestion: str
    optimized_query: Optional[str] = None
    index_recommendation: Optional[str] = None

@dataclass
class QueryAnalysisResult:
    """Complete analysis result for a SQL query"""
    original_query: str
    suggestions: List[OptimizationSuggestion]
    performance_score: int  # 0-100 (higher is better)
    complexity_analysis: Dict[str, any]

class SQLOptimizerEngine:
    """Main SQL optimization engine"""
    
    def __init__(self):
        self.schema_info = {}
        self.optimization_rules = self._load_optimization_rules()
    
    def set_schema(self, schema_ddl: str):
        """Parse and store database schema information"""
        self.schema_info = self._parse_schema(schema_ddl)
    
    def analyze_query(self, query: str) -> QueryAnalysisResult:
        """Analyze a SQL query and provide optimization suggestions"""
        # Parse the SQL query
        parsed = sqlparse.parse(query)[0]
        
        suggestions = []
        complexity_analysis = {}
        
        # Run all optimization checks
        suggestions.extend(self._check_select_star(parsed))
        suggestions.extend(self._check_missing_where_clause(parsed))
        suggestions.extend(self._check_non_sargable_predicates(parsed))
        suggestions.extend(self._check_function_in_where(parsed))
        suggestions.extend(self._check_implicit_conversions(parsed))
        suggestions.extend(self._check_unnecessary_joins(parsed))
        suggestions.extend(self._check_missing_indexes(parsed))
        suggestions.extend(self._check_subquery_optimization(parsed))
        suggestions.extend(self._check_order_by_without_limit(parsed))
        suggestions.extend(self._check_like_wildcards(parsed))
        
        # Calculate performance score
        performance_score = self._calculate_performance_score(suggestions)
        
        # Analyze complexity
        complexity_analysis = self._analyze_complexity(parsed)
        
        return QueryAnalysisResult(
            original_query=query,
            suggestions=suggestions,
            performance_score=performance_score,
            complexity_analysis=complexity_analysis
        )
    
    def generate_optimized_query(self, query: str) -> str:
        """Generate an optimized version of the query"""
        analysis = self.analyze_query(query)
        optimized = query
        
        # Apply automatic optimizations
        for suggestion in analysis.suggestions:
            if suggestion.optimized_query:
                optimized = suggestion.optimized_query
                break  # Apply the first available optimization
        
        return optimized
    
    def _parse_schema(self, schema_ddl: str) -> Dict:
        """Parse schema DDL to extract table and column information"""
        schema_info = {'tables': {}, 'indexes': []}
        
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
    
    def _check_select_star(self, parsed) -> List[OptimizationSuggestion]:
        """Check for SELECT * usage"""
        suggestions = []
        query_str = str(parsed).lower()
        
        if 'select *' in query_str:
            suggestions.append(OptimizationSuggestion(
                level=OptimizationLevel.MEDIUM,
                category="Column Selection",
                issue="Using SELECT * retrieves all columns",
                suggestion="Specify only the columns you need to reduce data transfer and improve performance",
                optimized_query=self._suggest_specific_columns(str(parsed))
            ))
        
        return suggestions
    
    def _check_missing_where_clause(self, parsed) -> List[OptimizationSuggestion]:
        """Check for queries without WHERE clauses"""
        suggestions = []
        query_str = str(parsed).lower()
        
        # Check if it's a SELECT without WHERE
        if 'select' in query_str and 'where' not in query_str and 'limit' not in query_str:
            suggestions.append(OptimizationSuggestion(
                level=OptimizationLevel.HIGH,
                category="Data Filtering",
                issue="Query lacks WHERE clause and may return all rows",
                suggestion="Add appropriate WHERE conditions to limit the result set and improve performance"
            ))
        
        return suggestions
    
    def _check_non_sargable_predicates(self, parsed) -> List[OptimizationSuggestion]:
        """Check for non-SARGable predicates that prevent index usage"""
        suggestions = []
        query_str = str(parsed).lower()
        
        # Check for leading wildcards in LIKE
        if re.search(r"like\s+['\"]%", query_str):
            suggestions.append(OptimizationSuggestion(
                level=OptimizationLevel.HIGH,
                category="Index Usage",
                issue="LIKE with leading wildcard (%) prevents index usage",
                suggestion="Consider using full-text search or restructuring the query to avoid leading wildcards"
            ))
        
        return suggestions
    
    def _check_function_in_where(self, parsed) -> List[OptimizationSuggestion]:
        """Check for functions applied to columns in WHERE clauses"""
        suggestions = []
        query_str = str(parsed).lower()
        
        # Common functions that prevent index usage
        functions = ['upper', 'lower', 'substring', 'year', 'month', 'day']
        
        for func in functions:
            if re.search(rf'where.*{func}\s*\(', query_str):
                suggestions.append(OptimizationSuggestion(
                    level=OptimizationLevel.MEDIUM,
                    category="Index Usage",
                    issue=f"Function {func.upper()}() in WHERE clause prevents index usage",
                    suggestion=f"Consider using computed columns or restructuring to avoid {func.upper()}() in WHERE clause"
                ))
        
        return suggestions
    
    def _check_implicit_conversions(self, parsed) -> List[OptimizationSuggestion]:
        """Check for potential implicit data type conversions"""
        suggestions = []
        query_str = str(parsed)
        
        # Look for quoted numbers (potential string to number conversion)
        if re.search(r"=\s*['\"][0-9]+['\"]", query_str):
            suggestions.append(OptimizationSuggestion(
                level=OptimizationLevel.LOW,
                category="Data Types",
                issue="Potential implicit conversion between string and numeric types",
                suggestion="Ensure data types match to avoid implicit conversions that can prevent index usage"
            ))
        
        return suggestions
    
    def _check_unnecessary_joins(self, parsed) -> List[OptimizationSuggestion]:
        """Check for potentially unnecessary joins"""
        suggestions = []
        query_str = str(parsed).lower()
        
        # Count joins
        join_count = len(re.findall(r'\bjoin\b', query_str))
        
        if join_count > 3:
            suggestions.append(OptimizationSuggestion(
                level=OptimizationLevel.MEDIUM,
                category="Query Structure",
                issue=f"Query has {join_count} joins which may impact performance",
                suggestion="Review if all joins are necessary. Consider breaking complex queries into simpler ones or using CTEs"
            ))
        
        return suggestions
    
    def _check_missing_indexes(self, parsed) -> List[OptimizationSuggestion]:
        """Suggest indexes based on WHERE and JOIN conditions"""
        suggestions = []
        query_str = str(parsed).lower()
        
        # Extract table and column names from WHERE conditions
        where_matches = re.findall(r'where\s+.*?(\w+)\.(\w+)\s*=', query_str)
        join_matches = re.findall(r'on\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)', query_str)
        
        recommended_indexes = set()
        
        # Suggest indexes for WHERE conditions
        for table, column in where_matches:
            index_name = f"idx_{table}_{column}"
            recommended_indexes.add(f"CREATE INDEX {index_name} ON {table}({column});")
        
        # Suggest indexes for JOIN conditions
        for t1, c1, t2, c2 in join_matches:
            index1 = f"idx_{t1}_{c1}"
            index2 = f"idx_{t2}_{c2}"
            recommended_indexes.add(f"CREATE INDEX {index1} ON {t1}({c1});")
            recommended_indexes.add(f"CREATE INDEX {index2} ON {t2}({c2});")
        
        if recommended_indexes:
            suggestions.append(OptimizationSuggestion(
                level=OptimizationLevel.HIGH,
                category="Indexing",
                issue="Query may benefit from additional indexes",
                suggestion="Consider creating the following indexes to improve query performance",
                index_recommendation="\n".join(recommended_indexes)
            ))
        
        return suggestions
    
    def _check_subquery_optimization(self, parsed) -> List[OptimizationSuggestion]:
        """Check for subqueries that could be optimized"""
        suggestions = []
        query_str = str(parsed).lower()
        
        # Check for EXISTS subqueries that could be JOINs
        if 'exists' in query_str and 'select' in query_str:
            suggestions.append(OptimizationSuggestion(
                level=OptimizationLevel.MEDIUM,
                category="Query Structure",
                issue="EXISTS subquery detected",
                suggestion="Consider converting EXISTS subquery to JOIN for better performance in some cases"
            ))
        
        # Check for IN with subqueries
        if re.search(r'in\s*\(\s*select', query_str):
            suggestions.append(OptimizationSuggestion(
                level=OptimizationLevel.MEDIUM,
                category="Query Structure",
                issue="IN with subquery detected",
                suggestion="Consider using JOIN or EXISTS instead of IN with subquery for better performance"
            ))
        
        return suggestions
    
    def _check_order_by_without_limit(self, parsed) -> List[OptimizationSuggestion]:
        """Check for ORDER BY without LIMIT"""
        suggestions = []
        query_str = str(parsed).lower()
        
        if 'order by' in query_str and 'limit' not in query_str and 'top' not in query_str:
            suggestions.append(OptimizationSuggestion(
                level=OptimizationLevel.LOW,
                category="Data Retrieval",
                issue="ORDER BY without LIMIT may sort unnecessary rows",
                suggestion="If you don't need all sorted results, consider adding LIMIT to reduce sorting overhead"
            ))
        
        return suggestions
    
    def _check_like_wildcards(self, parsed) -> List[OptimizationSuggestion]:
        """Check for inefficient LIKE patterns"""
        suggestions = []
        query_str = str(parsed).lower()
        
        # Check for patterns that start and end with wildcards
        if re.search(r"like\s+['\"]%.*%['\"]", query_str):
            suggestions.append(OptimizationSuggestion(
                level=OptimizationLevel.MEDIUM,
                category="Search Optimization",
                issue="LIKE with wildcards on both ends requires full table scan",
                suggestion="Consider using full-text search capabilities for better performance on text searches"
            ))
        
        return suggestions
    
    def _calculate_performance_score(self, suggestions: List[OptimizationSuggestion]) -> int:
        """Calculate a performance score based on issues found"""
        base_score = 100
        
        for suggestion in suggestions:
            if suggestion.level == OptimizationLevel.CRITICAL:
                base_score -= 25
            elif suggestion.level == OptimizationLevel.HIGH:
                base_score -= 15
            elif suggestion.level == OptimizationLevel.MEDIUM:
                base_score -= 10
            elif suggestion.level == OptimizationLevel.LOW:
                base_score -= 5
        
        return max(0, base_score)
    
    def _analyze_complexity(self, parsed) -> Dict:
        """Analyze query complexity"""
        query_str = str(parsed).lower()
        
        return {
            'join_count': len(re.findall(r'\bjoin\b', query_str)),
            'subquery_count': len(re.findall(r'\bselect\b', query_str)) - 1,
            'where_conditions': len(re.findall(r'\band\b|\bor\b', query_str)) + 1,
            'has_order_by': 'order by' in query_str,
            'has_group_by': 'group by' in query_str,
            'has_having': 'having' in query_str
        }
    
    def _suggest_specific_columns(self, query: str) -> str:
        """Suggest replacing SELECT * with specific columns"""
        # This is a simplified example - in practice, you'd need schema info
        return query.replace('SELECT *', 'SELECT column1, column2, column3  -- Replace with actual column names')
    
    def _load_optimization_rules(self) -> Dict:
        """Load predefined optimization rules"""
        return {
            'avoid_select_star': True,
            'require_where_clause': True,
            'check_index_usage': True,
            'optimize_joins': True,
            'detect_n_plus_one': True
        }

def format_analysis_result(analysis: QueryAnalysisResult) -> str:
    """Format the analysis result as markdown for display"""
    result = f"# SQL Query Analysis Report\n\n"
    result += f"**Performance Score:** {analysis.performance_score}/100\n\n"
    
    if analysis.suggestions:
        result += f"## 🔍 Query Analysis\n\n"
        
        # Group suggestions by category
        categories = {}
        for suggestion in analysis.suggestions:
            if suggestion.category not in categories:
                categories[suggestion.category] = []
            categories[suggestion.category].append(suggestion)
        
        for category, suggestions in categories.items():
            result += f"### {category}\n\n"
            
            for suggestion in suggestions:
                # Level emoji
                level_emoji = {
                    OptimizationLevel.CRITICAL: "🚨",
                    OptimizationLevel.HIGH: "⚠️",
                    OptimizationLevel.MEDIUM: "⚡",
                    OptimizationLevel.LOW: "💡"
                }
                
                result += f"{level_emoji.get(suggestion.level, '📝')} **{suggestion.level.value.title()} Priority**\n\n"
                result += f"**Issue:** {suggestion.issue}\n\n"
                result += f"**Recommendation:** {suggestion.suggestion}\n\n"
                
                if suggestion.optimized_query:
                    result += f"**Optimized Query:**\n```sql\n{suggestion.optimized_query}\n```\n\n"
                
                if suggestion.index_recommendation:
                    result += f"**Index Recommendations:**\n```sql\n{suggestion.index_recommendation}\n```\n\n"
                
                result += "---\n\n"
    else:
        result += "## ✅ Great Job!\n\nYour query looks well-optimized. No major issues detected.\n\n"
    
    # Complexity analysis
    complexity = analysis.complexity_analysis
    result += f"## 📊 Complexity Analysis\n\n"
    result += f"- **Joins:** {complexity.get('join_count', 0)}\n"
    result += f"- **Subqueries:** {complexity.get('subquery_count', 0)}\n"
    result += f"- **WHERE Conditions:** {complexity.get('where_conditions', 0)}\n"
    result += f"- **Has ORDER BY:** {'Yes' if complexity.get('has_order_by') else 'No'}\n"
    result += f"- **Has GROUP BY:** {'Yes' if complexity.get('has_group_by') else 'No'}\n"
    result += f"- **Has HAVING:** {'Yes' if complexity.get('has_having') else 'No'}\n\n"
    
    return result