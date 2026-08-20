import os
import sqlite3
from django.conf import settings

class SQLiteProvisionBuilder:
    @staticmethod
    def build(tenant_id: str) -> dict:
        storage_dir = os.path.join(
            settings.BASE_DIR, "tenants/infrastructure/storage/tenants"
        )
        os.makedirs(storage_dir, exist_ok=True)
        db_path = os.path.join(storage_dir, f"db_{tenant_id}.sqlite3")

        # Inicializa o arquivo e ativa modo WAL para o hardware do Compaq CQ42
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        conn.commit()
        conn.close()

        return {
            "engine": "sqlite",
            "path": db_path
        }    
        