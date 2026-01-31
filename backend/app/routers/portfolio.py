
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request, Form
from fastapi.responses import JSONResponse
import pandas as pd
import io
import os
import tempfile
import numpy as np  # Added for NaN handling
from ..services.pdf_parser import parse_cam_pdf
from ..services.portfolio_service import analyze_portfolio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from ..core.database import get_db
from ..models import PortfolioSnapshot, User
import datetime
import math
from starlette.concurrency import run_in_threadpool

def clean_nans(obj):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return 0.0
    elif isinstance(obj, dict):
        return {k: clean_nans(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nans(i) for i in obj]
    elif isinstance(obj, (np.integer, int)):
        return int(obj)
    elif isinstance(obj, (np.floating, float)):
        if np.isnan(obj) or np.isinf(obj):
            return 0.0
        return float(obj)
    return obj

router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"],
)



from ..core.deps import get_current_user

@router.post("/analyze")
async def analyze_report(
    file: UploadFile = File(...),
    password: str = Form(None), 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user) # <--- SECURE: Verifies JWT Token
):
    email = user.email

    if not file.filename.lower().endswith(('.pdf', '.xls', '.xlsx')):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload PDF or Excel.")

    # 1. Parse content
    contents = await file.read()
    
    try:
        data = []
        if file.filename.lower().endswith('.pdf'):
            # Save properly to temp file for pdfplumber
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(contents)
                tmp_path = tmp.name
            
            try:
                data = parse_cam_pdf(tmp_path, password)
            except ValueError as ve:
                raise HTTPException(status_code=400, detail=str(ve))
            finally:
                os.unlink(tmp_path)
                
        else:
            # Excel
            df = pd.read_excel(io.BytesIO(contents))
            data = df.to_dict(orient='records')
            
        if not data:
             raise HTTPException(status_code=400, detail="Could not extract any transactions.")

        # 2. Analyze (Heavier sync tasks run in threadpool)
        df = pd.DataFrame(data)
        result = await run_in_threadpool(analyze_portfolio, df)
        
        # Clean NaNs
        result = clean_nans(result)

        # 3. Save to DB
        # Find user
        res = await db.execute(select(User).filter(User.email == email))
        user = res.scalars().first()
        
        if not user:
            # Fallback: Auto-create user if auth sync failed
            # We assume email is valid since it came from Auth session
            user = User(
                email=email, 
                name=email.split('@')[0], # Fallback name
                created_at=datetime.datetime.now()
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        if user:
            # Save Snapshot
            snapshot_data = clean_nans(result) # Ensure snapshot is also clean
            new_snapshot = PortfolioSnapshot(
                user_id=user.id,
                total_value=result.get("current_valuation", 0),
                total_invested=result.get("total_investment", 0),
                xirr=result.get("xirr", 0),
                data=snapshot_data
            )
            db.add(new_snapshot)
            await db.commit()
    
        return JSONResponse(content=result)
        
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_portfolio(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # User is already verified and gathered by get_current_user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Get latest snapshot
    res = await db.execute(
        select(PortfolioSnapshot)
        .filter(PortfolioSnapshot.user_id == user.id)
        .order_by(desc(PortfolioSnapshot.upload_date))
        .limit(1)
    )
    snapshot = res.scalars().first()
    
    if not snapshot:
        return JSONResponse(content=None) # No data
        
    return JSONResponse(content=snapshot.data)
