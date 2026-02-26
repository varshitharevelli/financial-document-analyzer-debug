from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
import asyncio
from typing import Optional

from crewai import Crew, Process
from agents import financial_analyst, document_verifier, risk_assessor, investment_advisor, report_generator
from tasks import verify_document, extract_financial_data, analyze_financial_health, investment_recommendations, generate_report


app = FastAPI(
    title="Financial Document Analyzer",
    description="API for analyzing financial documents using CrewAI",
    version="1.0.0"
)

# Configuration
UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".csv", ".xlsx", ".xls"}


def validate_file_extension(filename: str) -> bool:
    """Validate if the file extension is allowed"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS


async def run_crew(query: str, file_path: str) -> str:
    """Execute the CrewAI agents for financial analysis"""
    try:
        # Use the actual agent instances directly
        financial_crew = Crew(
            agents=[document_verifier, financial_analyst],
            tasks=[verify_document, extract_financial_data, analyze_financial_health,
                   investment_recommendations, generate_report],
            process=Process.sequential,
            verbose=True,
            memory=True
        )

        # Execute with proper parameters
        result = financial_crew.kickoff(
            inputs={
                'query': query,
                'file_path': file_path
            }
        )

        # Handle different result types
        if hasattr(result, 'final_output'):
            return result.final_output
        elif isinstance(result, dict):
            return result.get('output', str(result))
        else:
            return str(result)

    except Exception as e:
        raise Exception(f"Crew execution failed: {str(e)}")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Financial Document Analyzer API is running",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "upload_dir_exists": os.path.exists(UPLOAD_DIR),
        "upload_dir_writable": os.access(UPLOAD_DIR, os.W_OK) if os.path.exists(UPLOAD_DIR) else False
    }


@app.post("/analyze")
async def analyze_document(
        file: UploadFile = File(..., description="Financial document to analyze"),
        query: Optional[str] = Form(
            default="Analyze this financial document and provide: 1) Key financial metrics 2) Risk assessment 3) Investment recommendations",
            description="Analysis query or instructions"
        )
):
    """
    Analyze a financial document and get comprehensive investment insights

    - **file**: PDF, Excel, CSV, or text file containing financial data
    - **query**: Optional custom analysis instructions
    """

    # Validate file extension
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Generate unique file ID and path
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    safe_filename = f"doc_{file_id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    try:
        # Ensure upload directory exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Save uploaded file with proper error handling
        try:
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail="Empty file uploaded")

            with open(file_path, "wb") as f:
                f.write(content)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")

        # Process the document
        try:
            # Add timeout to prevent hanging
            response = await asyncio.wait_for(
                run_crew(query=query.strip(), file_path=file_path),
                timeout=300  # 5 minute timeout
            )
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Analysis timed out")

        return {
            "status": "success",
            "query": query,
            "analysis": response,
            "file_processed": file.filename,
            "file_id": file_id,
            "message": "Document analyzed successfully"
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error here
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing financial document: {str(e)}"
        )

    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Cleaned up file: {file_path}")
            except Exception as e:
                print(f"Warning: Could not delete {file_path}: {str(e)}")


# Add a batch processing endpoint for multiple files
@app.post("/analyze/batch")
async def analyze_multiple_documents(
        files: list[UploadFile] = File(...),
        query: Optional[str] = Form(default="Analyze these financial documents")
):
    """
    Analyze multiple financial documents in batch
    """
    results = []

    for file in files:
        try:
            # Reuse single document analysis logic
            result = await analyze_document(file=file, query=query)
            results.append({
                "filename": file.filename,
                "status": "success",
                "result": result
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "failed",
                "error": str(e)
            })

    return {
        "batch_status": "completed",
        "total_files": len(files),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "results": results
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )