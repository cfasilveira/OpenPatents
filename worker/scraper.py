import os
import requests
from database import logger, safe_execution, SessionLocal
from models import PatentOpportunity

# Mapeamento de nichos PT-BR → palavras-chave em inglês para a API
NICHE_KEYWORDS = {
    "Agro":        "agriculture crop farming soil irrigation precision harvest",
    "Saúde":       "medical health treatment therapy diagnostic drug pharmaceutical",
    "Beleza":      "cosmetic beauty skincare haircare personal care fragrance",
    "Mecânica":    "mechanical engine automotive vehicle transmission gear pump",
    "Energia":     "energy solar wind renewable battery storage power generation",
    "Pet":         "animal pet veterinary livestock feed supplement care",
    "Logística":   "logistics packaging transport supply chain delivery warehouse",
    "Alimentos":   "food beverage preservation processing flavoring nutrition",
    "Construção":  "construction building material insulation structure concrete",
    "Eletrônica":  "electronic sensor semiconductor circuit embedded IoT device",
}

EUROPE_PMC_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


class PatentScraper:
    def __init__(self):
        pass # Europe PMC não precisa de API Key

    def _get_headers(self):
        return {
            "Accept": "application/json",
        }

    @safe_execution
    def search_by_niche(self, niche: str, limit: int = 10) -> dict:
        """
        Busca patentes reais na Europe PMC API pelo nicho selecionado.
        Insere no banco apenas patentes ainda não cadastradas (idempotente).
        Retorna { "inserted": N, "skipped": N, "error": None | str }
        """
        keywords = NICHE_KEYWORDS.get(niche)
        if not keywords:
            logger.error(f"❌ Nicho desconhecido: '{niche}'. Opções: {list(NICHE_KEYWORDS.keys())}")
            return {"inserted": 0, "skipped": 0, "error": f"Nicho '{niche}' não encontrado."}

        logger.info(f"🔍 Buscando {limit} patentes para o nicho '{niche}'...")

        query = f'SRC:PAT AND ({" OR ".join(keywords.split())})'
        params = {
            "query": query,
            "format": "json",
            "resultType": "core",
            "pageSize": limit,
        }

        try:
            response = requests.get(
                EUROPE_PMC_URL,
                params=params,
                headers=self._get_headers(),
                timeout=20,
            )
        except requests.exceptions.Timeout:
            logger.error("❌ Timeout ao contatar Europe PMC API.")
            return {"inserted": 0, "skipped": 0, "error": "Timeout na API externa."}
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ Erro de conexão com Europe PMC: {e}")
            return {"inserted": 0, "skipped": 0, "error": "Erro de conexão."}

        if response.status_code != 200:
            logger.error(f"❌ Europe PMC retornou HTTP {response.status_code}: {response.text[:200]}")
            return {"inserted": 0, "skipped": 0, "error": f"Erro HTTP {response.status_code}."}

        data = response.json()
        patents = data.get("resultList", {}).get("result", [])

        if not patents:
            logger.warning(f"⚠️  Nenhuma patente encontrada para o nicho '{niche}'.")
            return {"inserted": 0, "skipped": 0, "error": None}

        return self._save_to_db(patents, niche)

    def _save_to_db(self, patents: list, niche: str) -> dict:
        """Salva patentes no banco, pulando duplicatas."""
        session = SessionLocal()
        inserted = 0
        skipped = 0
        try:
            for p in patents:
                patent_id = p.get("id", "")
                existing = session.get(PatentOpportunity, patent_id)
                if existing:
                    logger.debug(f"↩️  Patente {patent_id} já existe. Pulando.")
                    skipped += 1
                    continue

                abstract = p.get("abstractText") or ""
                new_patent = PatentOpportunity(
                    id=patent_id,
                    title=p.get("title", "Sem título"),
                    description=abstract[:3000],  # Limitar para o LLM
                    source_query=niche,
                    patent_date=p.get("firstPublicationDate"),
                    status="pending",
                )
                session.add(new_patent)
                inserted += 1
                logger.info(f"➕ Enfileirada: [{patent_id}] {new_patent.title[:60]}")

            session.commit()
            logger.info(f"✅ Busca concluída: {inserted} novas | {skipped} duplicatas ignoradas.")
            return {"inserted": inserted, "skipped": skipped, "error": None}
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Erro ao salvar no banco: {e}")
            return {"inserted": 0, "skipped": 0, "error": str(e)}
        finally:
            session.close()




def get_available_niches() -> list:
    """Retorna a lista de nichos disponíveis."""
    return list(NICHE_KEYWORDS.keys())
