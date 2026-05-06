import os
import json
import requests
from database import logger, safe_execution, SessionLocal
from models import PatentOpportunity

class PatentProcessor:
    def __init__(self):
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model_name = os.getenv("MODEL_NAME", "mistral-nemo")

    @safe_execution
    def process_pending(self):
        """Busca patentes pendentes e as processa via LLM."""
        session = SessionLocal()
        try:
            pending_patents = session.query(PatentOpportunity).filter(
                PatentOpportunity.status == 'pending'
            ).all()

            if not pending_patents:
                logger.info("📭 Nenhuma patente pendente para processamento.")
                return

            logger.info(f"⚙️ Processando {len(pending_patents)} patentes...")

            for patent in pending_patents:
                self._process_single_patent(session, patent)
        
        finally:
            session.close()

    def _process_single_patent(self, session, patent):
        """Processa uma única patente e atualiza o banco."""
        logger.info(f"🧠 Analisando: {patent.title} (ID: {patent.id})")
        
        prompt = self._build_prompt(patent.title, patent.description)
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json().get("response")
                data = json.loads(result)
                
                # Atualizando campos
                patent.niche = data.get("niche")
                patent.concept = data.get("concept")
                patent.modern_inputs = data.get("modern_inputs")
                patent.investment_tier = data.get("investment_tier")
                patent.mvp_complexity = data.get("mvp_complexity")
                patent.time_to_market = data.get("time_to_market")
                patent.status = 'processed'
                
                session.commit()
                logger.info(f"✅ Sucesso: {patent.title} processada.")
            else:
                logger.error(f"❌ Erro Ollama ({response.status_code}): {response.text}")
                patent.status = 'failed'
                session.commit()

        except Exception as e:
            logger.error(f"❌ Falha ao processar {patent.id}: {str(e)}")
            patent.status = 'failed'
            session.commit()

    def _build_prompt(self, title, description):
        """Constrói o prompt estruturado para o Mistral-Nemo."""
        return f"""
        Você é um especialista em Inteligência Competitiva e Inovação.
        Sua tarefa é analisar uma patente técnica e transformá-la em uma oportunidade de negócio para 2026.

        Título da Patente: {title}
        Descrição Técnica: {description}

        Responda EXCLUSIVAMENTE em formato JSON com os seguintes campos:
        - niche: Categoria de mercado (ex: Agro, Pet, HealthTech, Green Logistics).
        - concept: Um resumo de 2 frases explicando o que o produto faz para um leigo.
        - modern_inputs: Lista de materiais ou tecnologias de 2026 que substituem os originais.
        - investment_tier: "Baixo", "Médio" ou "Alto".
        - mvp_complexity: Escala de 1 a 5 (1=fácil, 5=complexo).
        - time_to_market: Estimativa em meses (ex: "6 meses").

        JSON:
        """
