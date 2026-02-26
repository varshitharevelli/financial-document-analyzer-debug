"""
Custom tools for financial document analysis
"""

import os
import re
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
load_dotenv()

# Import CrewAI tool decorator
from crewai import Agent, Task, Crew
from crewai.tools import tool

# Try to import SerperDevTool
try:
    from crewai_tools import SerperDevTool
    SEARCH_AVAILABLE = True
except ImportError:
    try:
        from crewai_tools.tools.serper_dev_tool import SerperDevTool
        SEARCH_AVAILABLE = True
    except ImportError:
        SEARCH_AVAILABLE = False
        print("Warning: SerperDevTool not available. Search functionality disabled.")
        SerperDevTool = None

# PDF Processing
try:
    from pypdf import PdfReader
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("Warning: pypdf not installed. PDF support disabled.")

# Excel/CSV Processing
try:
    import pandas as pd
    EXCEL_SUPPORT = True
except ImportError:
    EXCEL_SUPPORT = False
    print("Warning: pandas not installed. Excel/CSV support disabled.")

# Text Processing
try:
    import chardet
    CHARDET_SUPPORT = True
except ImportError:
    CHARDET_SUPPORT = False
    print("Warning: chardet not installed. Using default encoding.")

from pathlib import Path

# ============================================
# SEARCH TOOL
# ============================================
# Initialize search tool
if SEARCH_AVAILABLE and os.getenv("SERPER_API_KEY"):
    try:
        serper_tool = SerperDevTool()

        @tool("Internet Search")
        def search_tool(query: str) -> str:
            """Search the internet for current financial information, market data, and news"""
            return serper_tool.run(query)
    except Exception as e:
        print(f"Warning: Could not initialize search tool: {e}")
        search_tool = None
else:
    print("Warning: SERPER_API_KEY not found or SerperDevTool not available. Search tool disabled.")
    search_tool = None

# ============================================
# FINANCIAL DOCUMENT TOOL
# ============================================
class FinancialDocumentTool:
    """Tool for reading and extracting data from financial documents"""

    @staticmethod
    def read_data(file_path: str) -> str:
        """
        Read and extract text content from financial documents.
        Supports PDF, TXT, CSV, and Excel files.

        Args:
            file_path (str): Path to the financial document

        Returns:
            str: Extracted text content from the document
        """
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                return f"ERROR: File not found: {file_path}"

            # Get file extension
            file_extension = Path(file_path).suffix.lower()

            # Process based on file type
            if file_extension == '.pdf':
                return FinancialDocumentTool._read_pdf(file_path)
            elif file_extension == '.txt':
                return FinancialDocumentTool._read_text(file_path)
            elif file_extension in ['.csv', '.xlsx', '.xls']:
                return FinancialDocumentTool._read_spreadsheet(file_path)
            else:
                return f"ERROR: Unsupported file type: {file_extension}"

        except Exception as e:
            return f"ERROR: Error reading document {file_path}: {str(e)}"

    @staticmethod
    def _read_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        if not PDF_SUPPORT:
            return "PDF support not available. Install pypdf package."

        try:
            reader = PdfReader(file_path)
            full_text = []

            for page_num, page in enumerate(reader.pages, 1):
                try:
                    text = page.extract_text()
                    if text:
                        text = FinancialDocumentTool._clean_text(text)
                        full_text.append(f"--- Page {page_num} ---\n{text}")
                except Exception as e:
                    full_text.append(f"--- Page {page_num} [Error extracting: {str(e)}] ---")

            return "\n\n".join(full_text)

        except Exception as e:
            return f"PDF processing failed: {str(e)}"

    @staticmethod
    def _read_text(file_path: str) -> str:
        """Read and extract text from plain text file"""
        try:
            if CHARDET_SUPPORT:
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                    encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
            else:
                encoding = 'utf-8'

            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                content = f.read()

            return FinancialDocumentTool._clean_text(content)

        except Exception as e:
            return f"Text file processing failed: {str(e)}"

    @staticmethod
    def _read_spreadsheet(file_path: str) -> str:
        """Read and extract data from spreadsheet files"""
        if not EXCEL_SUPPORT:
            return "Excel/CSV support not available. Install pandas package."

        try:
            file_extension = Path(file_path).suffix.lower()

            if file_extension == '.csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            output_lines = []
            output_lines.append(f"--- Spreadsheet Data: {Path(file_path).name} ---")
            output_lines.append(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
            output_lines.append("\nFirst 50 rows preview:")
            output_lines.append(df.head(50).to_string())

            return "\n".join(output_lines)

        except Exception as e:
            return f"Spreadsheet processing failed: {str(e)}"

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""

        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        text = text.strip()

        return text

# Create the document reader tool using the decorator
@tool("Read Financial Document")
def document_reader_tool(file_path: str) -> str:
    """Read and extract text content from financial documents (PDF, TXT, CSV, Excel)"""
    return FinancialDocumentTool.read_data(file_path)

# ============================================
# INVESTMENT ANALYSIS TOOL
# ============================================
class InvestmentTool:
    """Tools for investment analysis and recommendations"""

    @staticmethod
    def analyze_investment(financial_data: str) -> Dict[str, Any]:
        """
        Analyze financial data and generate investment insights.

        Args:
            financial_data (str): Extracted financial document content

        Returns:
            Dict: Structured investment analysis
        """
        try:
            metrics = InvestmentTool._extract_financial_metrics(financial_data)
            ratios = InvestmentTool._calculate_investment_ratios(metrics)
            investment_score = InvestmentTool._calculate_investment_score(metrics, ratios)
            recommendations = InvestmentTool._generate_recommendations(metrics, ratios, investment_score)

            return {
                "status": "success",
                "extracted_metrics": metrics,
                "calculated_ratios": ratios,
                "investment_score": investment_score,
                "recommendations": recommendations
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Investment analysis failed"
            }

    @staticmethod
    def _extract_financial_metrics(text: str) -> Dict[str, Any]:
        """Extract key financial metrics from text"""
        metrics = {}

        revenue_patterns = [
            r'revenue[:\s]*\$?([\d,]+\.?\d*)\s*(million|billion|thousand)?',
            r'sales[:\s]*\$?([\d,]+\.?\d*)\s*(million|billion|thousand)?'
        ]

        for pattern in revenue_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = float(match.group(1).replace(',', ''))
                metrics['revenue'] = value
                break

        profit_patterns = [
            r'net\s+income[:\s]*\$?([\d,]+\.?\d*)',
            r'net\s+profit[:\s]*\$?([\d,]+\.?\d*)'
        ]

        for pattern in profit_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metrics['net_income'] = float(match.group(1).replace(',', ''))
                break

        return metrics

    @staticmethod
    def _calculate_investment_ratios(metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate investment ratios from metrics"""
        ratios = {}

        if 'revenue' in metrics and 'net_income' in metrics and metrics['revenue']:
            ratios['profit_margin'] = round((metrics['net_income'] / metrics['revenue']) * 100, 2)

        return ratios

    @staticmethod
    def _calculate_investment_score(metrics: Dict, ratios: Dict) -> float:
        """Calculate overall investment score (0-100)"""
        score = 50

        if ratios.get('profit_margin', 0) > 15:
            score += 15
        elif ratios.get('profit_margin', 0) > 10:
            score += 10
        elif ratios.get('profit_margin', 0) > 5:
            score += 5

        return max(0, min(100, score))

    @staticmethod
    def _generate_recommendations(metrics: Dict, ratios: Dict, score: float) -> List[str]:
        """Generate investment recommendations"""
        recommendations = []

        if score >= 80:
            recommendations.append("STRONG BUY: Company shows excellent financial metrics")
        elif score >= 60:
            recommendations.append("BUY: Company shows good financial health")
        elif score >= 40:
            recommendations.append("HOLD: Company shows average financial metrics")
        else:
            recommendations.append("SELL/AVOID: Company shows concerning financial metrics")

        return recommendations

# Create investment analysis tool using the decorator
@tool("Analyze Investment")
def investment_analysis_tool(financial_data: str) -> str:
    """Analyze financial data and generate investment insights and recommendations"""
    result = InvestmentTool.analyze_investment(financial_data)
    return str(result)

# ============================================
# RISK ASSESSMENT TOOL
# ============================================
class RiskTool:
    """Tools for financial risk assessment"""

    @staticmethod
    def assess_risk(financial_data: str) -> Dict[str, Any]:
        """
        Assess financial risks based on document analysis.

        Args:
            financial_data (str): Extracted financial document content

        Returns:
            Dict: Structured risk assessment
        """
        try:
            risk_assessment = {
                "financial_risks": [],
                "market_risks": [],
                "overall_risk_level": "medium",
                "risk_score": 50,
                "risk_factors": []
            }

            if "debt" in financial_data.lower():
                risk_assessment["financial_risks"].append({
                    "risk": "Debt levels need review",
                    "severity": "medium"
                })
                risk_assessment["risk_score"] += 10
                risk_assessment["risk_factors"].append("High debt levels")

            if "volatile" in financial_data.lower() or "uncertainty" in financial_data.lower():
                risk_assessment["market_risks"].append({
                    "risk": "Market volatility",
                    "severity": "medium"
                })
                risk_assessment["risk_score"] += 5
                risk_assessment["risk_factors"].append("Market volatility")

            if risk_assessment["risk_score"] >= 70:
                risk_assessment["overall_risk_level"] = "high"
            elif risk_assessment["risk_score"] >= 40:
                risk_assessment["overall_risk_level"] = "medium"
            else:
                risk_assessment["overall_risk_level"] = "low"

            return risk_assessment

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Risk assessment failed"
            }

# Create risk assessment tool using the decorator
@tool("Assess Financial Risk")
def risk_assessment_tool(financial_data: str) -> str:
    """Assess financial risks based on document analysis"""
    result = RiskTool.assess_risk(financial_data)
    return str(result)

# ============================================
# EXPORT ALL TOOLS
# ============================================
__all__ = [
    'search_tool',
    'document_reader_tool',
    'investment_analysis_tool',
    'risk_assessment_tool'
]

# For testing when running directly
if __name__ == "__main__":
    print("Tools module loaded successfully!")
    print(f"Search tool available: {search_tool is not None}")
    print(f"Document reader tool: {document_reader_tool is not None}")
    print(f"Investment analysis tool: {investment_analysis_tool is not None}")
    print(f"Risk assessment tool: {risk_assessment_tool is not None}")