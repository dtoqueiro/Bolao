"""
Utilitário de limpeza e validação de telefone.

Remove formatação de telefones brasileiros (espaços, parênteses, traços,
código de país) e valida que o resultado tem exatamente 11 dígitos
numéricos (DDD + número celular).
"""
import re


def limpar_telefone(raw: str) -> str:
    """Limpa e valida um número de telefone brasileiro.

    Aceita formatos como:
        - (11) 99999-8888
        - +55 11 99999-8888
        - 55 11 99999-8888
        - 0055 11 99999-8888
        - 11.99999.8888
        - 11 99999 8888

    Args:
        raw: String bruta com o telefone em qualquer formato.

    Returns:
        String de 11 dígitos numéricos (DDD + número).

    Raises:
        ValueError: Se o telefone não pode ser limpo para 11 dígitos.
    """
    if not raw or not raw.strip():
        raise ValueError("Telefone inválido: valor vazio.")

    # Remove tudo que não é dígito
    somente_digitos = re.sub(r"\D", "", raw.strip())

    # Remove código de país 55 do início (se tiver 13 dígitos: 55 + 11 dígitos)
    if len(somente_digitos) == 13 and somente_digitos.startswith("55"):
        somente_digitos = somente_digitos[2:]

    # Remove código de país 0055 do início (se tiver 15 dígitos: 0055 + 11 dígitos)
    if len(somente_digitos) == 15 and somente_digitos.startswith("0055"):
        somente_digitos = somente_digitos[4:]

    # Validação final: deve ter exatamente 11 dígitos
    if len(somente_digitos) != 11:
        raise ValueError(
            f"Telefone deve ter exatamente 11 dígitos após limpeza. "
            f"Obtido: {len(somente_digitos)} dígitos a partir de '{raw}'."
        )

    return somente_digitos
