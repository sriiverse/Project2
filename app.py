import streamlit as st
import os
from sql_optimizer_engine import SQLOptimizerEngine, format_analysis_result
from query_generator import SQLQueryGenerator, suggest_query_improvements

# Configure Streamlit page with modern settings
st.set_page_config(
    page_title="Custom SQL Assistant | Sudhanshu Sinha",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize our custom engines
optimizer = SQLOptimizerEngine()
query_generator = SQLQueryGenerator()

# Custom CSS for modern dark theme styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Global dark theme */
    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container styling */
    .main {
        padding-top: 2rem;
        background: transparent;
    }
    
    /* Override Streamlit's default backgrounds */
    .block-container {
        background: transparent;
    }
    
    /* Custom header styling */
    .custom-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .custom-header h1 {
        font-size: 3rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .custom-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 0;
    }
    
    /* Card styling - Dark theme */
    .card {
        background: rgba(25, 35, 45, 0.8);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 1.5rem;
        color: #ffffff;
    }
    
    /* Feature cards */
    .feature-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
    }
    
    .feature-card h3 {
        margin-bottom: 0.5rem;
        font-size: 1.2rem;
    }
    
    .feature-card p {
        margin-bottom: 0;
        opacity: 0.9;
        font-size: 0.9rem;
    }
    
    /* Mode selector styling - Dark theme */
    .mode-selector {
        background: rgba(30, 40, 55, 0.6);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #667eea;
        margin-bottom: 2rem;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Step indicators */
    .step-indicator {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 0.8rem 1.2rem;
        border-radius: 25px;
        display: inline-block;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    /* Success/Error message styling - Dark theme */
    .success-message {
        background: rgba(30, 50, 60, 0.7);
        backdrop-filter: blur(8px);
        color: #a8edea;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #4facfe;
        border: 1px solid rgba(255,255,255,0.1);
        margin: 1rem 0;
    }
    
    /* Code block styling */
    .stCodeBlock {
        background: #1e1e1e;
        border-radius: 10px;
        border: none;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Text area styling - Dark theme */
    .stTextArea textarea {
        border-radius: 10px;
        border: 2px solid rgba(255,255,255,0.2) !important;
        font-family: 'Monaco', 'Consolas', monospace;
        background: rgba(15, 25, 35, 0.8) !important;
        color: #ffffff !important;
        backdrop-filter: blur(5px);
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Radio button styling - Dark theme */
    .stRadio > div {
        background: rgba(25, 35, 45, 0.6);
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 3px 15px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(5px);
    }
    
    .stRadio > div > label {
        color: #ffffff !important;
    }
    
    /* Footer styling */
    .custom-footer {
        background: linear-gradient(135deg, #2c3e50 0%, #4a6741 100%);
        color: white;
        text-align: center;
        padding: 2rem;
        border-radius: 15px;
        margin-top: 3rem;
    }
    
    /* Metrics styling - Dark theme */
    .metric-card {
        background: rgba(20, 30, 40, 0.7);
        backdrop-filter: blur(8px);
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.4);
        text-align: center;
        border-top: 4px solid #667eea;
        border: 1px solid rgba(255,255,255,0.1);
        color: #ffffff;
    }
    
    /* Animation for loading */
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    
    .loading {
        animation: pulse 2s infinite;
    }
    
    /* Dark theme overrides for Streamlit components */
    .stSelectbox > div > div {
        background: rgba(20, 30, 40, 0.8) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: #ffffff !important;
    }
    
    .stMarkdown {
        color: #ffffff;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #ffffff;
    }
    
    .stSpinner {
        color: #667eea !important;
    }
    
    /* Code block dark styling */
    .stCodeBlock {
        background: rgba(15, 20, 30, 0.9) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    
    /* Info/warning boxes dark styling */
    .stInfo {
        background: rgba(30, 50, 60, 0.7) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(75, 172, 254, 0.3) !important;
        color: #ffffff !important;
    }
    
    .stError {
        background: rgba(60, 30, 30, 0.7) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(255, 107, 107, 0.3) !important;
        color: #ffffff !important;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .custom-header h1 {
            font-size: 2rem;
        }
        .card {
            padding: 1rem;
        }
        .stApp {
            background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
        }
    }
</style>
""", unsafe_allow_html=True)

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

# Modern Header
st.markdown("""
<div class="custom-header">
    <h1>🚀 Custom SQL Assistant</h1>
    <p>Made and developed by Sudhanshu Sinha</p>
    <p style="margin-top: 0.5rem; font-size: 1rem; opacity: 0.8;">Professional SQL optimization and query generation tool</p>
</div>
""", unsafe_allow_html=True)

# Feature Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>⚡ Fast Analysis</h3>
        <p>Instant SQL optimization suggestions</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>🌍 No APIs</h3>
        <p>Completely self-contained system</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h3>🔒 Privacy First</h3>
        <p>Your data never leaves the app</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="feature-card">
        <h3>📨 Smart Generation</h3>
        <p>Natural language to SQL</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Modern Mode Selection
st.markdown("""
<div class="card">
    <div class="step-indicator">🎯 Step 1: Choose Your Task</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="mode-selector">', unsafe_allow_html=True)
app_mode = st.radio(
    "What would you like to do today?",
    ("Optimize Query", "Generate Query"),
    horizontal=True,
    help="Select whether you want to optimize an existing query or generate a new one from description"
)
st.markdown('</div>', unsafe_allow_html=True)

# Schema Input Section
st.markdown("""
<div class="card">
    <div class="step-indicator">📋 Step 2: Provide Database Schema</div>
    <p style="color: #666; margin-bottom: 1rem;">Paste your database schema below to get context-aware suggestions</p>
</div>
""", unsafe_allow_html=True)

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

# Schema input with improved styling
col1, col2 = st.columns([3, 1])
with col1:
    schema_text = st.text_area(
        "Database Schema (CREATE TABLE statements)",
        value=sample_schema,
        height=200,
        help="Paste your CREATE TABLE statements here for better analysis",
        placeholder="Paste your CREATE TABLE statements..."
    )

with col2:
    st.markdown("""
    <div class="metric-card">
        <h4 style="color: #667eea; margin-bottom: 0.5rem;">📊 Schema Info</h4>
        <p style="font-size: 0.9rem; color: #666; margin-bottom: 0;">Detected tables and relationships will appear here after analysis</p>
    </div>
    
    <div class="metric-card" style="margin-top: 1rem;">
        <h4 style="color: #667eea; margin-bottom: 0.5rem;">📝 Tips</h4>
        <ul style="font-size: 0.85rem; color: #666; text-align: left; padding-left: 1rem;">
            <li>Include all relevant tables</li>
            <li>Include primary/foreign keys</li>
            <li>Add column data types</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Mode-Specific UI with Modern Design
if app_mode == "Optimize Query":
    st.markdown("""
    <div class="card">
        <div class="step-indicator">📝 Step 3: Enter Your SQL Query</div>
        <p style="color: #666; margin-bottom: 1rem;">Paste your SQL query below to get comprehensive optimization suggestions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sample query for user convenience
    sample_query = "SELECT u.username, o.product_name, o.amount\nFROM users u\nJOIN orders o ON u.user_id = o.user_id\nWHERE u.username = 'john_doe';"
    
    col1, col2 = st.columns([3, 1])
    with col1:
        prompt_text = st.text_area(
            "SQL Query to Optimize",
            value=sample_query,
            height=150,
            help="Enter your SQL query here for analysis and optimization suggestions",
            placeholder="SELECT * FROM your_table WHERE..."
        )
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #f5576c; margin-bottom: 0.5rem;">🔧 Analysis</h4>
            <p style="font-size: 0.85rem; color: #666;">We'll check for:</p>
            <ul style="font-size: 0.8rem; color: #666; text-align: left; padding-left: 1rem;">
                <li>Performance issues</li>
                <li>Index suggestions</li>
                <li>Query complexity</li>
                <li>Best practices</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    button_label = "🚀 Analyze & Optimize Query"

else: # Generate Query Mode
    st.markdown("""
    <div class="card">
        <div class="step-indicator">🧠 Step 3: Describe Your Query</div>
        <p style="color: #666; margin-bottom: 1rem;">Describe what you want to achieve in plain English</p>
    </div>
    """, unsafe_allow_html=True)
    
    sample_prompt = "Get the top 5 users who have spent the most money."
    
    col1, col2 = st.columns([3, 1])
    with col1:
        prompt_text = st.text_area(
            "Natural Language Description",
            value=sample_prompt,
            height=150,
            help="Describe what you want to query in plain English",
            placeholder="Get all users who..."
        )
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #4facfe; margin-bottom: 0.5rem;">✨ Examples</h4>
            <ul style="font-size: 0.8rem; color: #666; text-align: left; padding-left: 1rem;">
                <li>"Top 10 customers by revenue"</li>
                <li>"Count users by country"</li>
                <li>"Orders from last month"</li>
                <li>"Average order amount"</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    button_label = "✨ Generate SQL Query"

# Modern Processing Section
st.markdown("<br>", unsafe_allow_html=True)

# Centered button with modern styling
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    process_button = st.button(button_label, use_container_width=True)

if process_button:
    if not schema_text.strip() or not prompt_text.strip():
        st.markdown("""
        <div class="card" style="border-left: 5px solid #ff6b6b;">
            <h4 style="color: #ff6b6b; margin-bottom: 0.5rem;">⚠️ Missing Information</h4>
            <p style="color: #666; margin-bottom: 0;">Please fill in both the database schema and your query/description to proceed.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Modern loading indicator
        st.markdown("""
        <div class="card loading">
            <div style="text-align: center; padding: 2rem;">
                <h3 style="color: #667eea; margin-bottom: 1rem;">🚀 Processing Your Request</h3>
                <p style="color: #666;">Analyzing your query and generating suggestions...</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            # Results Header
            st.markdown("""
            <div class="card">
                <div class="step-indicator">🎆 Step 4: Results & Analysis</div>
            </div>
            """, unsafe_allow_html=True)
            
            if app_mode == "Optimize Query":
                result = get_optimization_suggestion(schema_text, prompt_text)
                
                # Display results in a modern card
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(result)
                st.markdown('</div>', unsafe_allow_html=True)
                
            else: # Generate Query
                result = generate_query_from_prompt(schema_text, prompt_text)
                
                # Generated Query Display
                st.markdown("""
                <div class="card">
                    <h3 style="color: #667eea; margin-bottom: 1rem;">🎆 Generated SQL Query</h3>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.code(result, language='sql')
                    
                with col2:
                    # Query stats
                    query_lines = len(result.split('\n'))
                    query_chars = len(result)
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4 style="color: #4facfe; margin-bottom: 0.5rem;">📊 Query Stats</h4>
                        <p style="font-size: 0.9rem; color: #666;">Lines: {query_lines}</p>
                        <p style="font-size: 0.9rem; color: #666;">Characters: {query_chars}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Add improvement suggestions
                improvement_suggestions = suggest_query_improvements(result, {})
                st.markdown("""
                <div class="success-message">
                    <h4 style="margin-bottom: 0.5rem;">💡 Suggestions</h4>
                """, unsafe_allow_html=True)
                st.write(improvement_suggestions)
                st.markdown('</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.markdown(f"""
            <div class="card" style="border-left: 5px solid #ff6b6b;">
                <h4 style="color: #ff6b6b; margin-bottom: 0.5rem;">🚫 Error Occurred</h4>
                <p style="color: #666;">An unexpected error occurred: {e}</p>
                <p style="color: #666; font-size: 0.9rem;">Please check your input and try again.</p>
            </div>
            """, unsafe_allow_html=True)

# Modern Footer
st.markdown("""
<div class="custom-footer">
    <h3 style="margin-bottom: 1rem;">🚀 Custom SQL Assistant</h3>
    <div style="display: flex; justify-content: center; gap: 2rem; margin-bottom: 1rem; flex-wrap: wrap;">
        <div style="text-align: center;">
            <h4 style="color: #4facfe; margin-bottom: 0.5rem;">⚡ Performance</h4>
            <p style="font-size: 0.9rem; opacity: 0.9;">Instant Analysis</p>
        </div>
        <div style="text-align: center;">
            <h4 style="color: #f093fb; margin-bottom: 0.5rem;">🔒 Privacy</h4>
            <p style="font-size: 0.9rem; opacity: 0.9;">100% Local</p>
        </div>
        <div style="text-align: center;">
            <h4 style="color: #a8edea; margin-bottom: 0.5rem;">🌍 Zero Cost</h4>
            <p style="font-size: 0.9rem; opacity: 0.9;">No API Limits</p>
        </div>
        <div style="text-align: center;">
            <h4 style="color: #fed6e3; margin-bottom: 0.5rem;">🧠 Smart</h4>
            <p style="font-size: 0.9rem; opacity: 0.9;">Rule-Based AI</p>
        </div>
    </div>
    <hr style="border: none; height: 1px; background: rgba(255,255,255,0.2); margin: 1.5rem 0;">
    <p style="margin-bottom: 0.5rem;">Made with ❤️ using <strong>Streamlit</strong> and <strong>Custom Rule-Based Analysis</strong></p>
    <p style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 0;">Developed by <strong>Sudhanshu Sinha</strong> | No external APIs required!</p>
    <div style="margin-top: 1rem;">
        <p style="font-size: 0.8rem; opacity: 0.7;">🎆 Professional SQL optimization and query generation tool for developers</p>
    </div>
</div>

<!-- Additional spacing -->
<div style="height: 2rem;"></div>
""", unsafe_allow_html=True)
