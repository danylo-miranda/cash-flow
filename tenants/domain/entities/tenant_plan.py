from dataclasses import dataclass

@dataclass
class TenantPlan:
    name: str
    engine: str
    max_users: int
    max_storage: int