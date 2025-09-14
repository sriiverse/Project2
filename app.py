import streamlit as st
import os
from sql_optimizer_engine import SQLOptimizerEngine, format_analysis_result
from query_generator import SQLQueryGenerator, suggest_query_improvements

# Configure Streamlit page
st.set_page_config(
    page_title="Custom SQL Assistant",
    page_icon="🔧",
    layout="wide"
)

# Initialize our custom engines
optimizer = SQLOptimizerEngine()
query_generator = SQLQueryGenerator()

def get_optimization_suggestion(schema: str, query: str) -> str:
    """
    Uses our custom SQL optimization engine to analyze and suggest improvements.
    """
    try:
        # Set schema for the optimizer
        optimizer.set_schema(schema)
        
        # Analyze the query
        analysis = optimizer.analyze_query(query)
        
        # Format and return results
        return format_analysis_result(analysis)
    except Exception as e:
        return f"An error occurred while analyzing the query: {e}"

def generate_query_from_prompt(schema: str, prompt: str) -> str:
    """
    Uses our custom query generator to create SQL from natural language.
    """
    try:
        # Set schema for the query generator
        query_generator.set_schema(schema)
        
        # Generate the query
        generated_query = query_generator.generate_query(prompt)
        
        return generated_query
    except Exception as e:
        return f"An error occurred while generating the query: {e}"

# Main Streamlit App
st.title("🔧 Custom SQL Assistant")
st.markdown("Made and developed by Sudhanshu Sinha")

# --- App Mode Selection ---
st.write("## 1. Select a Mode")
app_mode = st.radio(
    "What would you like to do?",
    ("Optimize Query", "Generate Query"),
    horizontal=True,
    label_visibility="collapsed"
)

# --- Shared UI Elements ---
st.write("## 2. Provide Database Schema")
# Sample schema for user convenience
sample_schema = '''CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    product_name VARCHAR(100),
    amount DECIMAL(10, 2),
    order_date DATE
);
'''
schema_text = st.text_area(
    "Paste your `CREATE TABLE` statements here.",
    value=sample_schema,
    height=200
)

# --- Mode-Specific UI ---
if app_mode == "Optimize Query":
    st.write("## 3. Enter Your SQL Query")
    # Sample query for user convenience
    sample_query = "SELECT u.username, o.product_name, o.amount\nFROM users u\nJOIN orders o ON u.user_id = o.user_id\nWHERE u.username = 'john_doe';"
    prompt_text = st.text_area(
        "Enter the SQL query you want to optimize.",
        value=sample_query,
        height=150
    )
    button_label = "🚀 Optimize Query"

else: # Generate Query Mode
    st.write("## 3. Describe the Query to Generate")
    sample_prompt = "Get the top 5 users who have spent the most money."
    prompt_text = st.text_area(
        "Describe what the query should do in plain English.",
        value=sample_prompt,
        height=150
    )
    button_label = "✨ Generate Query"

# --- Button and Processing Logic ---
if st.button(button_label):
    if not schema_text.strip() or not prompt_text.strip():
        st.error("Schema and the prompt/query fields must be filled out.")
    else:
        with st.spinner("The AI is thinking! 🤔"):
            try:
                st.write("## 4. Results")
                if app_mode == "Optimize Query":
                    result = get_optimization_suggestion(schema_text, prompt_text)
                    st.markdown(result)
                else: # Generate Query
                    result = generate_query_from_prompt(schema_text, prompt_text)
                    st.code(result, language='sql')
                    
                    # Add improvement suggestions for generated queries
                    improvement_suggestions = suggest_query_improvements(result, {})
                    st.info(improvement_suggestions)
                    
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

# --- Footer ---
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and **Custom Rule-Based SQL Analysis** - No external APIs required!")
