from django.db import connections


class DynamicTenantTestMixin:
    """
    Mixin para desativar a restrição de banco de dados estático do Django Test Runner
    quando o teste registra novos bancos dinamicamente em runtime.
    """
    @classmethod
    def _add_databases_failures(cls):
        pass

    @classmethod
    def _remove_databases_failures(cls):
        pass


def cleanup_tenant_connection(alias: str):
    """Fecha a conexão do tenant e remove o registro do handler do Django de forma segura."""
    try:
        if alias in connections:
            connections[alias].close()
    except Exception:
        pass

    connections.databases.pop(alias, None)

    if hasattr(connections, "_connections"):
        try:
            delattr(connections._connections, alias)
        except AttributeError:
            pass