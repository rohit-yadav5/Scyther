class PermissionManager:
    def __init__(self, state):
        self.state = state

    def set_permission(self, permission_id: str):
        self.state.current_permission = permission_id
        return self.state.current_permission
