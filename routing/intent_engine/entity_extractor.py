import re


class EntityExtractor:
    FILENAME_PATTERN = re.compile(r"\b[\w.\-]+\.[a-zA-Z0-9]+\b")
    LANGUAGE_EXTENSIONS = {
        "python": ".py",
        "json": ".json",
        "javascript": ".js",
        "typescript": ".ts",
        "markdown": ".md",
    }

    @classmethod
    def extract(cls, text: str):
        filenames = cls.FILENAME_PATTERN.findall(text)
        entities = {}
        number_match = re.search(r"\b(\d+)\b", text)
        if number_match:
            entities["depth"] = int(number_match.group(1))

        if filenames:
            entities["filenames"] = filenames
            extensions = sorted({f".{name.split('.')[-1]}" for name in filenames if "." in name})
            if extensions:
                entities["extension"] = extensions[0] if len(extensions) == 1 else extensions

        for language, extension in cls.LANGUAGE_EXTENSIONS.items():
            if language in text.lower():
                entities["extension"] = extension
                break

        return entities
