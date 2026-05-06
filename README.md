# OpenPatents 🚀

O **OpenPatents** é um ecossistema de inteligência competitiva projetado para minerar dados públicos de patentes e tecnologias expiradas, transformando descrições técnicas complexas em **oportunidades de negócio viáveis** para o cenário de 2026.

## 📋 Funcionalidades

- **Extração Dinâmica:** Busca patentes reais via Europe PMC API (sem necessidade de API Key).
- **Triagem por Nicho:** Filtros inteligentes para Agro, Saúde, Pet, Energia, Mecânica e mais.
- **Análise de Viabilidade por IA:** Utiliza **Ollama (Mistral-Nemo)** para calcular custos de insumos, tempo de desenvolvimento (MVP) e complexidade.
- **Dashboard Intuitivo:** Interface minimalista para visualização clara das oportunidades geradas.

## 🛠️ Stack Tecnológica

- **Backend:** FastAPI (Python 3.12+)
- **Worker:** Processamento assíncrono com Ollama
- **Database:** PostgreSQL
- **Frontend:** Vite + Vanilla JS/CSS
- **Gerenciador de Pacotes:** `uv` (Python) e `npm` (JS)

## 🚀 Como Rodar

1. **Requisitos:** Docker (para o Postgres), Ollama (com o modelo `mistral-nemo`) e Python/Node instalados.
2. **Configuração:**
   - Clone o repositório.
   - Configure o arquivo `.env` na raiz com suas credenciais do banco e URL do Ollama.
3. **Serviços:**
   - **API:** `cd api && uv run python main.py`
   - **Worker:** `cd worker && uv run python main.py`
   - **Frontend:** `cd frontend && npm run dev`

---
Desenvolvido como um projeto de Inteligência de Mercado e Inovação.
