from typing import Any

class StateManager:
    def __init__(self):
        self.DATA: dict[str, dict[str, Any]] = {}
        self.STATE: dict[str, str] = {}

        
    async def set_state(self, user_id: str, state: str):
        self.STATE[user_id] = state
    
    
    async def get_state(self, user_id: str):
        return self.STATE.get(user_id)

    
    async def remove_state(self, user_id: str):
        self.STATE.pop(user_id, None)

        
    async def set_data(self, user_id: str, **data):
        if user_id not in self.DATA:
            self.DATA[user_id] = {}
        self.DATA[user_id].update(data)

    
    async def get_data(self, user_id: str, key: str = None):
        data = self.DATA.get(user_id, {})
        return data.get(key) if key else data


    async def remove_data(self, user_id: str, key: str = None):
        if key:
            return self.DATA.get(user_id, {}).pop(key, None)
        return self.DATA.pop(user_id, None)