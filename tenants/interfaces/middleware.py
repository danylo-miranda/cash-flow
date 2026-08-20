from django.http import JsonResponse
from tenants.application.cache_service import TenantCacheService
from tenants.domain.context.tenant_context import TenantContext, TenantContextData
from tenants.infrastructure.database.connection import DynamicConnectionManager

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.cache_service = TenantCacheService()

    def __call__(self, request):
        tenant_id = request.headers.get("X-Tenant-ID")

        if not tenant_id or request.path.startswith("/admin/"):
            return self.get_response(request)

        # 1. Busca metadados via Cache -> Banco Mestre
        tenant = self.cache_service.get_tenant(tenant_id)
        if not tenant or not tenant.is_active:
            return JsonResponse({"error": "Tenant inválido ou inativo."}, status=403)

        # 2. Injeta alias de conexão
        db_alias = DynamicConnectionManager.register_tenant_db(tenant.id, tenant.db_config)

        context_data = TenantContextData(
            tenant_id=tenant.id,
            company_name=tenant.name,
            plan_type=tenant.plan,
            db_alias=db_alias,
            db_engine=tenant.db_engine
        )

        token = TenantContext.set(context_data)

        try:
            response = self.get_response(request)
        finally:
            TenantContext.clear(token)

        return response