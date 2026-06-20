class EditTool:
    def __init__(self, file_service):
        self.file_service = file_service

    def edit(self, path: str, content: str):
        return self.file_service.write(path, content)
