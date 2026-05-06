import logging
import sys
import os
from functools import wraps

# Garante que a pasta de logs exista um nível acima (na raiz do workspace)
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, 'worker.log')

# Configuração de Log focada em CyberOps
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(module)s | %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout) # Mostra no terminal do Antigravity também
    ]
)

logger = logging.getLogger("OpenPatents")

def safe_execution(func):
    """
    Decorator de Engenharia de Software:
    1. Loga a tentativa de execução.
    2. Captura falhas (Fail-Fast).
    3. Retorna None (Early Return) para evitar crash do sistema.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"❌ FALHA CRÍTICA em [{func.__name__}]: {str(e)}")
            return None 
    return wrapper
    