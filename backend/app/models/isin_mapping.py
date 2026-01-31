
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from ..core.database import Base

class ISINMapping(Base):
    __tablename__ = "isin_mappings"

    isin = Column(String, primary_key=True, index=True)
    scheme_code = Column(String, index=True)
    scheme_name = Column(String)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
