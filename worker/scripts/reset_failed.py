import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, logger
from models import PatentOpportunity

def reset_failed_patents():
    session = SessionLocal()
    try:
        failed_patents = session.query(PatentOpportunity).filter(
            PatentOpportunity.status == 'failed'
        ).all()
        
        if not failed_patents:
            logger.info("📭 Nenhuma patente com status 'failed' para redefinir.")
            return 0
            
        count = len(failed_patents)
        for p in failed_patents:
            p.status = 'pending'
            
        session.commit()
        logger.info(f"🔄 Sucesso: {count} patentes redefinidas de 'failed' para 'pending'.")
        return count
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Erro ao redefinir patentes: {e}")
        return 0
    finally:
        session.close()

if __name__ == "__main__":
    reset_failed_patents()
