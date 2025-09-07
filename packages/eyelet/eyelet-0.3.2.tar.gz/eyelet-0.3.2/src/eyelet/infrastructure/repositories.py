"""Repository implementations for data persistence"""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from eyelet.domain.models import Hook, HookExecution, HookType, Template
from eyelet.infrastructure.database import get_db_path, init_db


class HookRepository(ABC):
    """Abstract repository for hooks"""

    @abstractmethod
    def save(self, hook: Hook) -> Hook:
        pass

    @abstractmethod
    def get(self, hook_id: str) -> Hook | None:
        pass

    @abstractmethod
    def get_all(self) -> list[Hook]:
        pass

    @abstractmethod
    def delete(self, hook_id: str) -> bool:
        pass


class InMemoryHookRepository(HookRepository):
    """In-memory implementation for testing"""

    def __init__(self):
        self.hooks: dict[str, Hook] = {}

    def save(self, hook: Hook) -> Hook:
        if not hook.id:
            hook.id = f"{hook.type}_{hook.matcher or 'default'}_{len(self.hooks)}"
        self.hooks[hook.id] = hook
        return hook

    def get(self, hook_id: str) -> Hook | None:
        return self.hooks.get(hook_id)

    def get_all(self) -> list[Hook]:
        return list(self.hooks.values())

    def delete(self, hook_id: str) -> bool:
        if hook_id in self.hooks:
            del self.hooks[hook_id]
            return True
        return False


class ExecutionRepository(ABC):
    """Abstract repository for hook executions"""

    @abstractmethod
    def save(self, execution: HookExecution) -> HookExecution:
        pass

    @abstractmethod
    def get(self, execution_id: int) -> HookExecution | None:
        pass

    @abstractmethod
    def get_recent(
        self, hook_type: HookType | None = None, limit: int = 100, offset: int = 0
    ) -> list[HookExecution]:
        pass

    @abstractmethod
    def get_stats(self) -> dict[str, Any]:
        pass


class SQLiteExecutionRepository(ExecutionRepository):
    """SQLite implementation for execution persistence"""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or get_db_path()
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        init_db(self.engine)

    def save(self, execution: HookExecution) -> HookExecution:
        with Session(self.engine):
            # Convert to DB model and save
            # This is simplified - actual implementation would use SQLAlchemy models
            execution.id = 1  # Placeholder
            return execution

    def get(self, execution_id: int) -> HookExecution | None:
        # Placeholder implementation
        return None

    def get_recent(
        self, hook_type: HookType | None = None, limit: int = 100, offset: int = 0
    ) -> list[HookExecution]:
        # Placeholder implementation
        return []

    def get_stats(self) -> dict[str, Any]:
        # Placeholder implementation
        return {"total_executions": 0, "success_rate": 0.0, "average_duration_ms": 0}


class TemplateRepository(ABC):
    """Abstract repository for templates"""

    @abstractmethod
    def get(self, template_id: str) -> Template | None:
        pass

    @abstractmethod
    def get_all(self) -> list[Template]:
        pass

    @abstractmethod
    def save(self, template: Template) -> Template:
        pass


class FileTemplateRepository(TemplateRepository):
    """File-based template repository"""

    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_default_templates()

    def get(self, template_id: str) -> Template | None:
        template_file = self.template_dir / f"{template_id}.json"
        if not template_file.exists():
            return None

        try:
            with open(template_file) as f:
                data = json.load(f)
            return Template(**data)
        except Exception:
            return None

    def get_all(self) -> list[Template]:
        templates = []
        for template_file in self.template_dir.glob("*.json"):
            template = self.get(template_file.stem)
            if template:
                templates.append(template)
        return templates

    def save(self, template: Template) -> Template:
        template_file = self.template_dir / f"{template.id}.json"
        with open(template_file, "w") as f:
            json.dump(template.model_dump(), f, indent=2, default=str)
        return template

    def _ensure_default_templates(self):
        """Create default templates if they don't exist"""
        default_templates = [
            Template(
                id="bash-validator",
                name="Bash Command Validator",
                description="Validate bash commands before execution",
                category="security",
                hooks=[
                    Hook(
                        type=HookType.PRE_TOOL_USE,
                        matcher="Bash",
                        handler={"type": "workflow", "workflow": "bash-validation"},
                        description="Validate bash commands for safety",
                    )
                ],
                tags=["security", "validation", "bash"],
            ),
            Template(
                id="observability",
                name="Full Observability",
                description="Log all tool usage for monitoring",
                category="monitoring",
                hooks=[
                    Hook(
                        type=HookType.PRE_TOOL_USE,
                        matcher=".*",
                        handler={
                            "type": "command",
                            "command": "eyelet execute --log-only",
                        },
                        description="Log all tool usage",
                    ),
                    Hook(
                        type=HookType.POST_TOOL_USE,
                        matcher=".*",
                        handler={
                            "type": "command",
                            "command": "eyelet execute --log-result",
                        },
                        description="Log tool results",
                    ),
                ],
                tags=["monitoring", "logging", "observability"],
            ),
        ]

        for template in default_templates:
            if not (self.template_dir / f"{template.id}.json").exists():
                self.save(template)
