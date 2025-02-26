from typing import Optional
from .persistent_memory import PersistentMemory

class MemoryManager:
    _instance = None
    _memory = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MemoryManager, cls).__new__(cls)
            cls._memory = PersistentMemory()
        return cls._instance

    @classmethod
    def get_memory(cls) -> PersistentMemory:
        if cls._instance is None:
            cls._instance = MemoryManager()
        return cls._memory

    @classmethod
    def track_feature(cls, feature_name: str, description: str) -> None:
        memory = cls.get_memory()
        memory.set_current_feature(feature_name)
        memory.start_task(
            task_id=f"feature-{feature_name}",
            description=description
        )

    @classmethod
    def track_label_creation(cls, upc: str, product_name: str) -> None:
        memory = cls.get_memory()
        memory.update_user_preferences(
            coding_style=None,
            communication_prefs=None,
            project_priorities=["recent_labels"]
        )
        # Store last used UPC and product name
        memory.memory["context_retention"]["user_preferences"]["recent_labels"] = {
            "last_upc": upc,
            "last_product": product_name
        }
        memory._save_memory()

    @classmethod
    def track_window_state(cls, window_position: tuple, is_transparent: bool) -> None:
        memory = cls.get_memory()
        memory.memory["context_retention"]["user_preferences"]["window_state"] = {
            "position": window_position,
            "is_transparent": is_transparent
        }
        memory._save_memory()

    @classmethod
    def get_last_window_state(cls) -> Optional[dict]:
        memory = cls.get_memory()
        return memory.memory["context_retention"]["user_preferences"].get("window_state")
