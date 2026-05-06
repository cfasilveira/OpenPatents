from database import SessionLocal
from models import PatentOpportunity
import uuid

def insert_mock_patent():
    session = SessionLocal()
    try:
        mock_id = str(uuid.uuid4())[:8]
        patent = PatentOpportunity(
            id=f"BR-{mock_id}",
            title="Sistema de Irrigação Inteligente com Sensores de Umidade de Baixo Custo",
            description="A presente invenção descreve um sistema que utiliza sensores resistivos de solo e válvulas solenoides controladas por um microcontrolador 8051 para otimizar o uso de água em pequenas plantações de hortaliças.",
            status='pending'
        )
        session.add(patent)
        session.commit()
        print(f"✅ Patente mock inserida: {patent.title} (ID: {patent.id})")
    finally:
        session.close()

if __name__ == "__main__":
    insert_mock_patent()
