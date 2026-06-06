import re


def validate_crmv(crmv: str) -> bool:
    """
    Valida formato CRMV.

    Formato esperado: CRMV-UF XXXXX
    Exemplo: CRMV-SP 12345
    """
    pattern = r"^CRMV-[A-Z]{2}\s\d{4,6}$"
    return bool(re.match(pattern, crmv))


def validate_brazilian_state(state: str) -> bool:
    """Valida UF brasileira."""
    valid_states = {
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
        "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
        "RS", "RO", "RR", "SC", "SP", "SE", "TO",
    }
    return state.upper() in valid_states
