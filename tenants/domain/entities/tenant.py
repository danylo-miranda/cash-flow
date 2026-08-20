from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class Tenant:
    id: str
    name: str
    plan: str
    db_engine: str
    db_config: Dict[str, Any]
    is_active: bool =True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @staticmethod
    def from_model(model) -> "Tenant":
        return Tenant(
            id=model.id,
            name=model.name,
            plan=model.plan,
            db_engine=model.db_engine,
            db_config=model.db_config,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )