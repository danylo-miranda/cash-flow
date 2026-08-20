import os
from django.db import connections
from django.conf import settings

class DynamicConnectionManager:
    @staticmethod
    def register_tenant_db(tenant_id: str, db_config: dict) -> str:
        alias = f"tenant_{tenant_id}"
        if alias in connections.databases:
            return alias

        engine_type = db_config.get("engine", "sqlite")

        # Configurações padrão necessárias para evitar KeyError no Django Backend
        base_config = {
            "TIME_ZONE": getattr(settings, "TIME_ZONE", None),
            "AUTOCOMMIT": True,
            "CONN_MAX_AGE": 0,
            "CONN_HEALTH_CHECKS": False,
            "ATOMIC_REQUESTS": True,
        }

        if engine_type == "sqlite":
            default_path = os.path.join(
                settings.BASE_DIR, f"tenants/infrastructure/storage/tenants/db_{tenant_id}.sqlite3"
            )
            db_path = db_config.get("path", default_path)
            base_config.update({
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": db_path,
                "USER": "",
                "PASSWORD": "",
                "HOST": "",
                "PORT": "",
                "OPTIONS": {
                    "timeout": 20,
                },
            })
        elif engine_type == "mysql":
            base_config.update({
                "ENGINE": "django.db.backends.mysql",
                "NAME": db_config["name"],
                "USER": db_config["user"],
                "PASSWORD": db_config["password"],
                "HOST": db_config["host"],
                "PORT": str(db_config.get("port", 3306)),
                "OPTIONS": {
                    "charset": "utf8mb4",
                    "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
                },
            })

        connections.databases[alias] = base_config
        return alias