from abc import ABC, abstractmethod
from typing import Optional
from tenants.domain.entities.tenant import Tenant

class ITenantRepository(ABC):
    @abstractmethod
    def save(self, tenant: Tenant) -> Tenant:
        pass
    
    @abstractmethod
    def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
        pass
