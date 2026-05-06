import os
import requests
import time
from database import logger, safe_execution, SessionLocal
from models import PatentOpportunity

from processor import PatentProcessor

@safe_execution
def test_ollama_connection():
    # Fail-First: Verifica se o serviço ollama está de pé antes de processar
    url = f"{os.getenv('OLLAMA_URL')}/api/tags"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            logger.info("📡 Ollama Service está Online.")
            return True
    except Exception as e:
        logger.error(f"❌ Erro ao conectar no Ollama: {e}")
    return False

def start_processing():
    """Loop principal de processamento."""
    logger.info("🚀 Iniciando Módulo de Processamento...")
    processor = PatentProcessor()
    
    while True:
        processor.process_pending()
        logger.info("💤 Aguardando novos registros (60s)...")
        time.sleep(60)


if __name__ == "__main__":
    if test_ollama_connection():
        start_processing()
    else:
        logger.error("❌ Abortando: Infraestrutura de IA não detectada.")