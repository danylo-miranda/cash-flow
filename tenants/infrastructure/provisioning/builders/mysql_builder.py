import mysql.connector

class MySQLProvisionBuilder:
    @staticmethod
    def build(tenant_id: str, config: dict) -> dict:
        db_name = f"tenant_{tenant_id}"
        
        # Conecta no host MySQL via Tailscale para criar o schema do cliente
        connection = mysql.connector.connect(
            host=config["host"],
            port=config.get("port", 3306),
            user=config["admin_user"],
            password=config["admin_password"]
        )
        cursor = connection.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        )
        cursor.close()
        connection.close()

        return {
            "engine": "mysql",
            "name": db_name,
            "user": config["user"],
            "password": config["password"],
            "host": config["host"],
            "port": config.get("port", 3306)
        }