"""
Utilitário de normalização de nomes.

Normaliza nomes para comparação case-insensitive e sem acentos,
permitindo identificação flexível de participantes.
"""
import re
import unicodedata


def normalizar_nome(raw: str) -> str:
    """Normaliza um nome removendo acentos, convertendo para minúsculas
    e colapsando espaços múltiplos.

    Args:
        raw: Nome bruto com possíveis acentos, maiúsculas e espaços extras.

    Returns:
        Nome normalizado em minúsculas, sem acentos, com espaços simples.
    """
    if not raw:
        return ""

    # Remove acentos via decomposição Unicode (NFKD)
    nfkd = unicodedata.normalize("NFKD", raw)
    sem_acentos = "".join(c for c in nfkd if not unicodedata.combining(c))

    # Minúsculas
    lower = sem_acentos.lower()

    # Colapsa whitespace (espaços, tabs, etc.) em espaço simples e faz trim
    normalizado = re.sub(r"\s+", " ", lower).strip()

    return normalizado


def nomes_correspondem(nome_input: str, nome_cadastrado: str) -> bool:
    """Verifica se dois nomes correspondem após normalização.

    Comparação exata após normalização (sem busca parcial).

    Args:
        nome_input: Nome digitado pelo usuário.
        nome_cadastrado: Nome armazenado no banco de dados.

    Returns:
        True se os nomes normalizados forem idênticos.
    """
    n1 = normalizar_nome(nome_input)
    n2 = normalizar_nome(nome_cadastrado)

    if not n1 or not n2:
        return False

    return n1 == n2
