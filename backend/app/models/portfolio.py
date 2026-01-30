
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_value = Column(Float)
    total_invested = Column(Float)
    xirr = Column(Float)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Store the full JSON analysis blob for easy retrieval
    # In a real app, we might normalize this further (Holdings table, etc.)
    # But for now, JSON storage is efficient for "saving state"
    data = Column(JSON) 

    user = relationship("User", backref="snapshots")
