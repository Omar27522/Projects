import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Union

class PersistentMemory:
    """Manages persistent memory of project state and progress across sessions."""
    
    def __init__(self, storage_path: str = ".windsurf_memory"):
        self.storage_path = storage_path
        self.memory = self._load_memory()

    def _load_memory(self) -> Dict:
        """Load memory from storage file or create new if doesn't exist."""
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        return {
            "active_tasks": {},
            "progress_tracking": {
                "current_feature": None,
                "last_action": None,
                "next_steps": [],
                "blockers": [],
                "completion_criteria": []
            },
            "context_retention": {
                "codebase_knowledge": {
                    "key_files": [],
                    "important_functions": [],
                    "design_decisions": []
                },
                "user_preferences": {
                    "coding_style": {},
                    "communication_preferences": {},
                    "project_priorities": []
                }
            }
        }

    def _save_memory(self):
        """Save current memory state to storage file."""
        with open(self.storage_path, 'w') as f:
            json.dump(self.memory, f, indent=4)

    def start_task(self, task_id: str, description: str, priority: str = "medium") -> None:
        """Start tracking a new task."""
        self.memory["active_tasks"][task_id] = {
            "status": "in_progress",
            "priority": priority,
            "context": {"description": description},
            "last_updated": datetime.now().isoformat()
        }
        self._save_memory()

    def update_task_status(self, task_id: str, status: str, context: Optional[Dict] = None) -> None:
        """Update status and context of an existing task."""
        if task_id in self.memory["active_tasks"]:
            self.memory["active_tasks"][task_id].update({
                "status": status,
                "last_updated": datetime.now().isoformat()
            })
            if context:
                self.memory["active_tasks"][task_id]["context"].update(context)
            self._save_memory()

    def set_current_feature(self, feature: str) -> None:
        """Set the currently active feature being worked on."""
        self.memory["progress_tracking"]["current_feature"] = feature
        self.memory["progress_tracking"]["last_action"] = datetime.now().isoformat()
        self._save_memory()

    def add_next_step(self, step: str) -> None:
        """Add a next step to the progress tracking."""
        self.memory["progress_tracking"]["next_steps"].append(step)
        self._save_memory()

    def add_blocker(self, blocker: str) -> None:
        """Add a blocker to the progress tracking."""
        self.memory["progress_tracking"]["blockers"].append(blocker)
        self._save_memory()

    def update_codebase_knowledge(self, 
                                key_files: Optional[List[str]] = None,
                                important_functions: Optional[List[str]] = None,
                                design_decisions: Optional[List[str]] = None) -> None:
        """Update knowledge about the codebase."""
        if key_files:
            self.memory["context_retention"]["codebase_knowledge"]["key_files"].extend(key_files)
        if important_functions:
            self.memory["context_retention"]["codebase_knowledge"]["important_functions"].extend(important_functions)
        if design_decisions:
            self.memory["context_retention"]["codebase_knowledge"]["design_decisions"].extend(design_decisions)
        self._save_memory()

    def update_user_preferences(self, 
                              coding_style: Optional[Dict] = None,
                              communication_prefs: Optional[Dict] = None,
                              project_priorities: Optional[List[str]] = None) -> None:
        """Update user preferences and priorities."""
        if coding_style:
            self.memory["context_retention"]["user_preferences"]["coding_style"].update(coding_style)
        if communication_prefs:
            self.memory["context_retention"]["user_preferences"]["communication_preferences"].update(communication_prefs)
        if project_priorities:
            self.memory["context_retention"]["user_preferences"]["project_priorities"] = project_priorities
        self._save_memory()

    def get_current_state(self) -> Dict:
        """Get the complete current state of work and context."""
        return self.memory

    def get_active_feature(self) -> Optional[str]:
        """Get the currently active feature being worked on."""
        return self.memory["progress_tracking"]["current_feature"]

    def get_next_steps(self) -> List[str]:
        """Get the list of next steps."""
        return self.memory["progress_tracking"]["next_steps"]

    def get_blockers(self) -> List[str]:
        """Get the list of current blockers."""
        return self.memory["progress_tracking"]["blockers"]
