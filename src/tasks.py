"""
Financial Document Analysis Tasks - Simplified Version
"""

from crewai import Task
from agents import financial_analyst, document_verifier
from tools import document_reader_tool, investment_analysis_tool, risk_assessment_tool

# ============================================
# DOCUMENT VERIFICATION TASK
# ============================================
verify_document = Task(
    description="""
    Verify and validate the uploaded financial document.
    
    Tasks:
    1. Check if the file exists and can be read at path: {file_path}
    2. Identify the document type (PDF, TXT, CSV, Excel)
    3. Extract basic company information if available
    4. Note any issues with the document format
    
    User query: {query}
    """,

    expected_output="A verification report with document type, validity status, and basic metadata",

    agent=document_verifier,
    tools=[document_reader_tool],
    async_execution=False
)

# ============================================
# FINANCIAL DATA EXTRACTION TASK
# ============================================
extract_financial_data = Task(
    description="""
    Extract key financial data from the document at path: {file_path}
    
    Look for these specific metrics:
    - Revenue/Sales figures
    - Net Income/Profit
    - Total Assets
    - Total Liabilities/Debt
    - Cash and Cash Equivalents
    - Operating Cash Flow
    
    Format the data in a structured way.
    """,

    expected_output="Structured financial data with key metrics in JSON format",

    agent=financial_analyst,
    tools=[document_reader_tool],
    async_execution=False
)

# ============================================
# FINANCIAL ANALYSIS TASK
# ============================================
analyze_financial_health = Task(
    description="""
    Analyze the financial health based on extracted data.
    
    Calculate and interpret:
    - Profit margins (gross, operating, net)
    - Debt-to-equity ratio
    - Current ratio (liquidity)
    - Return on Assets (ROA)
    - Return on Equity (ROE)
    
    Provide a financial health score (0-100).
    User query context: {query}
    """,

    expected_output="Financial analysis with key ratios, health score, and assessment",

    agent=financial_analyst,
    tools=[investment_analysis_tool],
    async_execution=False
)

# ============================================
# INVESTMENT RECOMMENDATIONS TASK
# ============================================
investment_recommendations = Task(
    description="""
    Provide investment recommendations based on the financial analysis.
    
    Include:
    - Investment thesis (2-3 sentences)
    - Clear Buy/Hold/Sell recommendation
    - Key risks to consider
    - Suggested time horizon (short/medium/long-term)
    - Target price range if applicable
    
    Base recommendations on actual financial data, not speculation.
    User query: {query}
    """,

    expected_output="Investment recommendations with rationale and risk assessment",

    agent=financial_analyst,
    tools=[investment_analysis_tool, risk_assessment_tool],
    async_execution=False
)

# ============================================
# FINAL REPORT GENERATION TASK
# ============================================
generate_report = Task(
    description="""
    Generate a comprehensive financial analysis report.
    
    The report should include:
    
    1. EXECUTIVE SUMMARY
       - Company overview
       - Key findings
       - Primary recommendation
    
    2. FINANCIAL HIGHLIGHTS
       - Key metrics table
       - Notable trends
    
    3. DETAILED ANALYSIS
       - Profitability analysis
       - Liquidity position
       - Solvency assessment
    
    4. RISK ASSESSMENT
       - Key risks identified
       - Risk level (Low/Medium/High)
    
    5. INVESTMENT THESIS
       - Recommendation
       - Rationale
       - Time horizon
    
    Format the report professionally with clear sections.
    User query: {query}
    """,

    expected_output="A complete, well-structured financial analysis report",

    agent=financial_analyst,
    tools=[],
    async_execution=False
)

# Export all tasks
__all__ = [
    'verify_document',
    'extract_financial_data',
    'analyze_financial_health',
    'investment_recommendations',
    'generate_report'
]