from tenants.domain.context.tenant_context import TenantContext

class MultiTenantRouter:
    # Registra 'accounts' como app do Banco Mestre junto com 'tenants'
    MASTER_APPS = {"tenants", "accounts", "organizations"}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.MASTER_APPS:
            return "default"
        context = TenantContext.get()
        return context.db_alias if context else "default"

    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.MASTER_APPS:
            return db == "default"
        return db != "default"