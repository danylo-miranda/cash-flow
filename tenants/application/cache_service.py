from typing import Optional
from django.core.cache import cache
from tenants.domain.entities.tenant import Tenant
from tenants.infrastructure.registry.tenant_repository import DjangoTenantRepository

class TenantCacheService:
    CACHE_PREFIX = "tenant_meta_"
    CACHE_TIMEOUT = 300
    
    def __init__(self, repository=None):
        self.repo = repository or DjangoTenantRepository()

    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        cache_key = f"{self.CACHE_PREFIX}{tenant_id}"
        tenant = cache.get(cache_key)
        
        if tenant is None:
            tenant = self.repo.get_by_id(tenant_id)
            if tenant:
                cache.set(cache_key, tenant, timeout=self.CACHE_TIMEOUT)
        return tenant        
    
    def invalidate(self, tenant_id: str) -> None:
        cache_key = f"{self.CACHE_PREFIX}{tenant_id}"
        cache.delete(cache_key)