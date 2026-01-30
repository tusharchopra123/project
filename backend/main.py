from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import shutil
import os
from parser import parse_cam_pdf
from models import analyze_portfolio

app = FastAPI(title="Finance Portfolio Analysis")

# Configure CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Finance Portfolio Analysis API"}

@app.post("/api/analyze")
async def analyze_cam(file: UploadFile = File(...), password: str = Form(None)):
    """
    Upload a CAM PDF and get portfolio analysis.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")
    
    temp_file = f"temp_{file.filename}"
    try:
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Parse PDF
        # parse_cam_pdf returns list of dicts
        transactions = parse_cam_pdf(temp_file, password=password)
        
        if not transactions:
            return {"status": "error", "message": "No transactions found or failed to parse."}

        # Convert to DataFrame for model analysis
        df = pd.DataFrame(transactions)
        
        # Run analysis
        analysis_result = analyze_portfolio(df)
        
        # Sanitize for JSON (NaN/Inf handling)
        def sanitize(obj):
            if isinstance(obj, float):
                if obj != obj or obj == float('inf') or obj == float('-inf'):
                    return 0.0
                return obj
            if isinstance(obj, dict):
                return {k: sanitize(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [sanitize(x) for x in obj]
            return obj
        
        return {
            "status": "success",
            "data": sanitize(analysis_result),
            "transactions": sanitize(transactions[:5]) # Return first 5 for preview
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
