import os
import time
from main import test_ollama_connection
from processor import PatentProcessor
from database import SessionLocal, logger
from models import PatentOpportunity

def test_run():
    if test_ollama_connection():
        logger.info("🧪 Iniciando teste de processamento...")
        processor = PatentProcessor()
        processor.process_pending()
        
        # Verificar resultado
        session = SessionLocal()
        patent = session.query(PatentOpportunity).first()
        if patent and patent.status == 'processed':
            logger.info(f"✨ RESULTADO DA IA PARA '{patent.title}':")
            logger.info(f"   - Nicho: {patent.niche}")
            logger.info(f"   - Conceito: {patent.concept}")
            logger.info(f"   - Insumos: {patent.modern_inputs}")
            logger.info(f"   - Investimento: {patent.investment_tier}")
        else:
            logger.error("❌ A patente não foi processada corretamente.")
        session.close()
    else:
        logger.error("❌ Ollama Offline.")

if __name__ == "__main__":
    test_run()
