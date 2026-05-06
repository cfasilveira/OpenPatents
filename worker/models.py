from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class PatentOpportunity(Base):
    __tablename__ = 'opportunities'

    id = Column(String, primary_key=True) # ID da Patente
    title = Column(String, nullable=False)
    niche = Column(String)                # Nicho (Agro, Pet, etc)
    concept = Column(Text)                # Explicação simples
    modern_inputs = Column(Text)          # Insumos 2026
    investment_tier = Column(String)      # Baixo/Médio/Alto
    mvp_complexity = Column(Integer)      # 1-5
    time_to_market = Column(String)       # Prazo
    description = Column(Text)            # Texto bruto da patente
    pdf_url = Column(String)
    status = Column(String, default='pending') # pending, processed, fail
    source_query = Column(String)         # Nicho que originou a busca
    patent_date = Column(String)          # Data de concessão da patente
    created_at = Column(DateTime, default=datetime.utcnow)