from dataclasses import dataclass

@dataclass
class TenantConnection:
    engine: str
    database: str
    host: str | None = None
    port: int | None = None