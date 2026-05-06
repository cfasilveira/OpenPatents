import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import PatentOpportunity


def view_database():
    session = SessionLocal()
    try:
        patents = session.query(PatentOpportunity).all()
        
        if not patents:
            print("\n📭 O banco de dados está vazio.")
            return

        print("\n=== CONTEÚDO DO BANCO DE DADOS (OpenPatents) ===\n")
        
        # Cabeçalho da Tabela Markdown
        print("| ID | Título | Nicho | Status | MVP | Prazo |")
        print("|:---|:---|:---|:---|:---|:---|")
        
        for p in patents:
            print(f"| {p.id} | {p.title[:40]}... | {p.niche} | {p.status} | {p.mvp_complexity}/5 | {p.time_to_market} |")
        
        print("\n\n=== DETALHE DA ÚLTIMA ANÁLISE IA ===\n")
        last = patents[-1]
        print(f"Título: {last.title}")
        print(f"Descrição Bruta: {last.description[:100]}...")
        print(f"Conceito IA: {last.concept}")
        print(f"Insumos 2026: {last.modern_inputs}")
        
    finally:
        session.close()

if __name__ == "__main__":
    view_database()
