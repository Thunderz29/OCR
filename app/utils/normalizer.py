import re


def normalize_text(text):

    if text is None:
        return None

    text = text.upper()

    replacements = {
        "“": "",
        "”": "",
        "\"": "",
        "'": "",
        "`": "",
        "‘": "",
        "’": "",

        "—": "-",
        "–": "-",

        "|": "I",
        "\\": "/",

        "\t": " ",
        "\n": " ",
        "\r": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Hilangkan spasi berlebih
    text = re.sub(r"\s+", " ", text)

    # Hilangkan spasi sebelum/ sesudah slash
    text = re.sub(r"\s*/\s*", "/", text)

    # Hilangkan spasi sebelum koma/titik
    text = re.sub(r"\s+([.,])", r"\1", text)

    return text.strip()