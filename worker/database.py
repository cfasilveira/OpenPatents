import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from logger_base import logger, safe_execution

# Carrega variáveis de ambiente
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def validate_env():
    """Valida se todas as variáveis de ambiente necessárias estão presentes."""
    required = ['DB_USER', 'DB_PASS', 'DB_HOST', 'DB_PORT', 'DB_NAME', 'OLLAMA_URL', 'MODEL_NAME']
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        raise EnvironmentError(f"❌ Variáveis de ambiente faltando: {', '.join(missing)}")

validate_env()

DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

@safe_execution
def get_engine():
    engine = create_engine(DB_URL)
    # Teste de Handshake (Fail-Fast)
    with engine.connect() as conn:
        logger.info("📡 Conexão com Postgres validada via SQLAlchemy.")
    return engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())