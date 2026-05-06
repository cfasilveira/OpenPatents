import os
import sys
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Carregar variáveis de ambiente da raiz do projeto
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Adicionar o diretório worker ao path para importar o scraper
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'worker'))
from scraper import PatentScraper, get_available_niches

# ──────────────────────────── Banco de Dados ────────────────────────────
DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class PatentOpportunity(Base):
    __tablename__ = 'opportunities'
    id = Column(String, primary_key=True)
    title = Column(String)
    niche = Column(String)
    concept = Column(Text)
    modern_inputs = Column(Text)
    investment_tier = Column(String)
    mvp_complexity = Column(Integer)
    time_to_market = Column(String)
    description = Column(Text)
    pdf_url = Column(String)
    status = Column(String)
    source_query = Column(String)
    patent_date = Column(String)
    created_at = Column(DateTime)


# ──────────────────────────── FastAPI App ────────────────────────────
app = FastAPI(title="OpenPatents API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ──────────────────────────── Schemas ────────────────────────────
class SearchRequest(BaseModel):
    niche: str
    limit: int = 10


# ──────────────────────────── Endpoints ────────────────────────────
@app.get("/niches")
def list_niches():
    """Retorna os nichos disponíveis para pesquisa."""
    return {"niches": get_available_niches()}


@app.post("/search")
def trigger_search(req: SearchRequest):
    """
    Dispara uma busca de patentes reais na PatentsView API para o nicho selecionado.
    As patentes encontradas são salvas no banco com status='pending' para processamento da IA.
    """
    if req.limit < 1 or req.limit > 50:
        raise HTTPException(status_code=400, detail="Limite deve ser entre 1 e 50.")

    scraper = PatentScraper()
    result = scraper.search_by_niche(niche=req.niche, limit=req.limit)

    if result is None:
        raise HTTPException(status_code=500, detail="Erro interno no scraper.")

    return {
        "niche": req.niche,
        "inserted": result.get("inserted", 0),
        "skipped": result.get("skipped", 0),
        "demo_mode": result.get("demo", False),
        "error": result.get("error"),
    }


@app.get("/opportunities")
def list_opportunities(niche: str = None, db: Session = Depends(get_db)):
    """Lista patentes processadas, com filtro opcional por nicho."""
    query = db.query(PatentOpportunity).filter(PatentOpportunity.status == 'processed')
    if niche:
        query = query.filter(PatentOpportunity.source_query == niche)
    return query.order_by(PatentOpportunity.created_at.desc()).all()


@app.get("/opportunities/pending")
def list_pending(db: Session = Depends(get_db)):
    """Lista patentes ainda aguardando análise da IA."""
    return db.query(PatentOpportunity).filter(
        PatentOpportunity.status == 'pending'
    ).count()


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Retorna contagens gerais do banco."""
    total = db.query(PatentOpportunity).count()
    processed = db.query(PatentOpportunity).filter(PatentOpportunity.status == 'processed').count()
    pending = db.query(PatentOpportunity).filter(PatentOpportunity.status == 'pending').count()
    failed = db.query(PatentOpportunity).filter(PatentOpportunity.status == 'failed').count()
    return {
        "total": total,
        "processed": processed,
        "pending": pending,
        "failed": failed,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

