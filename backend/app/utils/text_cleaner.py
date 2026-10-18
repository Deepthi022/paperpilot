import re

def clean_text(text: str) -> str:
    # Re-join words split by a hyphen at the end of a line
    text = re.sub(r"-\n(\w)", r"\1", text)
    # Turn single line breaks inside paragraphs into spaces
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    # Collapse repeated spaces and extra blank lines
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()