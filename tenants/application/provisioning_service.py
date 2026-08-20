from tenants.application.cache_service import TenantCacheService
from tenants.domain.entities.tenant import Tenant
from tenants.infrastructure.provisioning.creator import TenantCreator
from tenants.infrastructure.registry.tenant_repository import DjangoTenantRepository

class ProvisioningService:
    def __init__(self, tenant_repo=None, cache_service=None):
        self.creator = TenantCreator()
        self.tenant_repo = tenant_repo or DjangoTenantRepository()
        self.cache_service = cache_service or TenantCacheService()

    def execute(self, tenant_id: str, company_name: str, plan_type: str, mysql_config: dict = None) -> dict:
        db_config = self.creator.create(
            tenant_id=tenant_id,
            plan_type=plan_type,
            mysql_config=mysql_config
        )

        tenant_entity = Tenant(
            id=tenant_id,
            name=company_name,
            plan=plan_type,
            db_engine=db_config.get("engine", "sqlite"),
            db_config=db_config,
            is_active=True
        )
        saved_tenant = self.tenant_repo.save(tenant_entity)

        # Invalida o cache para garantir atualizações em tempo real
        self.cache_service.invalidate(tenant_id)

        return {
            "tenant_id": saved_tenant.id,
            "company_name": saved_tenant.name,
            "plan": saved_tenant.plan,
            "db_config": saved_tenant.db_config
        }