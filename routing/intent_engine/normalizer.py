import re


class Normalizer:
    SYNONYMS = {
        "repo": "repository",
        "project": "repository",
        "folder": "directory",
        "folders": "directories",
    }

    @classmethod
    def normalize(cls, text: str):
        text = text.lower()
        text = re.sub(r"[^\w\s.]", " ", text)
        words = []
        for word in text.split():
            words.append(cls.SYNONYMS.get(word, word))
        return re.sub(r"\s+", " ", " ".join(words)).strip()
