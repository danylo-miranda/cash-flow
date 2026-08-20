from django.core.management import call_command
from tenants.infrastructure.database.connection import DynamicConnectionManager
from tenants.infrastructure.provisioning.builders.sqlite_builder import SQLiteProvisionBuilder
from tenants.infrastructure.provisioning.builders.mysql_builder import MySQLProvisionBuilder


class TenantCreator:
    def create(self, tenant_id: str, plan_type: str, mysql_config: dict = None) -> dict:
        if plan_type == "FREE":
            db_config = SQLiteProvisionBuilder.build(tenant_id)
        elif plan_type == "STARTER":
            if not mysql_config:
                raise ValueError("Configurações do MySQL são obrigatórias para o plano STARTER.")
            db_config = MySQLProvisionBuilder.build(tenant_id, mysql_config)
        else:
            raise ValueError(f"Plano desconhecido: {plan_type}")

        # Configurações essenciais do runner de testes
        if "TEST" not in db_config:
            db_config["TEST"] = {
                "CHARSET": None,
                "COLLATION": None,
                "MIGRATE": True,
                "MIRROR": None,
                "NAME": db_config.get("NAME") or db_config.get("path"),
            }

        # Injeta o novo banco dinamicamente no Django
        db_alias = DynamicConnectionManager.register_tenant_db(tenant_id, db_config)

        # Executa as migrações no banco do tenant
        call_command("migrate", database=db_alias, interactive=False)

        return db_config