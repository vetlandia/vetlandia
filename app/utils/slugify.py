import re
import unicodedata


def slugify(text: str) -> str:
    """
    Converte texto em slug URL-friendly.

    Exemplo:
        slugify("Dra. Maria Silva - São Paulo") -> "dra-maria-silva-sao-paulo"
    """
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")

    text = text.lower()

    text = re.sub(r"[^a-z0-9\s-]", "", text)

    text = re.sub(r"[\s-]+", "-", text)

    text = text.strip("-")

    return text
