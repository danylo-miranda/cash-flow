from typing import Optional
from tenants.domain.entities.tenant import Tenant
from tenants.domain.repositories.tenant_repository import ITenantRepository
from tenants.models import TenantModel

class DjangoTenantRepository(ITenantRepository):
    def save(self, tenant: Tenant) -> Tenant:
        obj, _ = TenantModel.objects.using("default").update_or_create(
            id=tenant.id,
            defaults={
                "name": tenant.name,
                "plan": tenant.plan,
                "db_engine": tenant.db_engine,
                "db_config": tenant.db_config,
                "is_active": tenant.is_active,
            }
        )
        tenant.created_at = obj.created_at
        tenant.updated_at = obj.updated_at
        return tenant

    def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
        try:
            obj = TenantModel.objects.using("default").get(id=tenant_id)
            return Tenant(
                id=obj.id,
                name=obj.name,
                plan=obj.plan,
                db_engine=obj.db_engine,
                db_config=obj.db_config,
                is_active=obj.is_active,
                created_at=obj.created_at,
                updated_at=obj.updated_at,
            )
        except TenantModel.DoesNotExist:
            return None