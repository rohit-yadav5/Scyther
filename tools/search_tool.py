class SearchTool:
    def __init__(self, search_service):
        self.search_service = search_service

    def search(self, root: str, pattern: str):
        return self.search_service.search(root, pattern)
